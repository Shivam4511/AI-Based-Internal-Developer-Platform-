"""
LLM Service — Standard and Codebase-Aware Processing.

Uses smart chunking to stay within Groq's rate limits:
  - Ranks files by relevance to the user's query
  - Caps total context to ~4000 tokens (~16,000 chars)
  - Truncates very large files
  - Only sends the most relevant files
"""
import openai
from openai import OpenAI
import json
import os
from app.core.config import GROK_API_KEY, GROK_BASE_URL
from app.core.prompts import SYSTEM_PROMPT, CODEBASE_AWARE_PROMPT
from app.models import ChatResponse

# ─── Smart Chunking Config ──────────────────────────────────────
MAX_CONTEXT_CHARS = 16000        # ~4000 tokens (4 chars ≈ 1 token)
MAX_FILE_CHARS = 3000            # Truncate individual files at ~750 tokens
MAX_FILES_IN_CONTEXT = 8         # Never send more than 8 files
SKIP_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg',
                   '.woff', '.woff2', '.ttf', '.eot', '.mp4', '.zip',
                   '.tar', '.gz', '.lock', '.map'}


class LLMService:
    def __init__(self):
        if not GROK_API_KEY:
            raise ValueError("GROK_API_KEY is not set in environment variables.")

        self.client = OpenAI(
            api_key=GROK_API_KEY,
            base_url=GROK_BASE_URL
        )

    # ─── Standard Chat (no codebase) ────────────────────────────
    def process_command(self, user_message: str) -> ChatResponse:
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            content = _clean_json(content)
            data = json.loads(content)

            return ChatResponse(
                folder_structure=data.get("folder_structure", ""),
                files=data.get("files", {}),
                explanation=data.get("explanation", "")
            )

        except openai.RateLimitError:
            return ChatResponse(
                explanation="⚠️ API Rate Limit Exceeded. Please wait a few seconds before trying again."
            )
        except openai.APIError as e:
            print(f"LLM API Error: {e}")
            return ChatResponse(
                explanation=f"⚠️ AI Service Error: {e.message}"
            )
        except Exception as e:
            print(f"LLM Error: {e}")
            return ChatResponse(
                explanation=f"I encountered an error processing your request: {str(e)}"
            )

    # ─── Codebase-Aware Chat ────────────────────────────────────
    def process_with_codebase(self, user_message: str, codebase_files: dict) -> ChatResponse:
        """
        Process a user request with uploaded codebase context.
        Uses smart chunking to fit within token limits.

        Args:
            user_message: The user's natural language request
            codebase_files: Dict of {filename: {content, size, type}}
        """
        try:
            # 1. Smart chunk: pick relevant files, respect token budget
            context = self._build_smart_context(user_message, codebase_files)

            # 2. Build the prompt
            # 2. Build the prompt
            full_prompt = CODEBASE_AWARE_PROMPT.replace(
                "{codebase_context}", context
            ).replace(
                "{user_message}", user_message
            )

            # 3. Call LLM
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            content = _clean_json(content)
            data = json.loads(content)

            return ChatResponse(
                files=data.get("files", {}),
                changes=data.get("changes", []),
                explanation=data.get("explanation", "")
            )

        except openai.RateLimitError:
            return ChatResponse(
                explanation="⚠️ API Rate Limit Exceeded. Please wait a few seconds before trying again."
            )
        except openai.APIError as e:
            print(f"LLM Codebase API Error: {e}")
            return ChatResponse(
                explanation=f"⚠️ AI Service Error: {e.message}"
            )
        except Exception as e:
            print(f"LLM Codebase Error: {e}")
            return ChatResponse(
                explanation=f"Error processing codebase request: {str(e)}"
            )

    # ─── Smart Chunking Engine ──────────────────────────────────
    def _build_smart_context(self, query: str, files: dict) -> str:
        """
        Select and format the most relevant files within the token budget.

        Strategy:
          1. Score each file by relevance to the user's query
          2. Sort by score (highest first)
          3. Include files until we hit the token budget
          4. Truncate large files with a [TRUNCATED] marker
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored_files = []
        for path, info in files.items():
            _, ext = os.path.splitext(path.lower())

            # Skip binary / non-code files
            if ext in SKIP_EXTENSIONS:
                continue

            content = info.get("content", "")
            if content.startswith("[Binary file"):
                continue

            score = self._relevance_score(path, content, query_lower, query_words)
            scored_files.append((path, content, score))

        # Sort by relevance score (highest first)
        scored_files.sort(key=lambda x: x[2], reverse=True)

        # Build context within budget
        context_parts = []
        total_chars = 0
        files_included = 0

        # Always include a file manifest first (cheap, very useful for LLM)
        manifest = "### FILE MANIFEST (all files in project):\n"
        manifest += "\n".join(f"  - {p}" for p in sorted(files.keys()))
        manifest += "\n\n"
        context_parts.append(manifest)
        total_chars += len(manifest)

        # Add relevant files
        for path, content, score in scored_files:
            if files_included >= MAX_FILES_IN_CONTEXT:
                break

            # Truncate large files
            if len(content) > MAX_FILE_CHARS:
                content = content[:MAX_FILE_CHARS] + f"\n\n... [TRUNCATED — file is {len(content)} chars, showing first {MAX_FILE_CHARS}]"

            file_block = f"### FILE: {path}\n```\n{content}\n```\n\n"

            # Check budget
            if total_chars + len(file_block) > MAX_CONTEXT_CHARS:
                # If we haven't included any files yet, force-include this one (truncated more)
                if files_included == 0:
                    remaining = MAX_CONTEXT_CHARS - total_chars - 100
                    content = content[:remaining]
                    file_block = f"### FILE: {path}\n```\n{content}\n```\n\n"
                else:
                    break

            context_parts.append(file_block)
            total_chars += len(file_block)
            files_included += 1

        # Add a note about what was included
        total_files = len(files)
        note = f"\n[Context: {files_included}/{total_files} files included based on relevance to your query. Full manifest above.]\n"
        context_parts.append(note)

        return "".join(context_parts)

    def _relevance_score(self, path: str, content: str, query: str, query_words: set) -> float:
        """
        Score a file's relevance to the user's query (0-100).

        Scoring factors:
          - Filename/path match with query words
          - File type importance (entry points score higher)
          - Content keyword matches
          - File size (prefer smaller, more focused files)
        """
        score = 0.0
        path_lower = path.lower()
        basename = os.path.basename(path_lower)

        # 1. Path/filename matches query words (strongest signal)
        for word in query_words:
            if len(word) < 3:
                continue
            if word in path_lower:
                score += 25
            if word in basename:
                score += 15

        # 2. Entry-point / config files get a boost
        important_files = {
            'package.json': 20, 'requirements.txt': 15, 'main.py': 18,
            'app.py': 18, 'index.js': 18, 'server.js': 18, 'app.js': 16,
            'index.ts': 18, 'server.ts': 18, 'app.ts': 16,
            'dockerfile': 10, 'docker-compose.yml': 10,
            '.env': 8, '.env.example': 8, 'readme.md': 5,
            'tsconfig.json': 8, 'vite.config.js': 8, 'vite.config.ts': 8,
            'next.config.js': 8, 'webpack.config.js': 8
        }
        score += important_files.get(basename, 0)

        # 3. Route/API/middleware files get a boost for common queries
        api_keywords = {'route', 'api', 'controller', 'middleware', 'auth',
                        'handler', 'service', 'model', 'schema', 'util'}
        for kw in api_keywords:
            if kw in path_lower:
                score += 5
            if kw in query:
                if kw in path_lower:
                    score += 20  # Double boost if query mentions it AND file matches

        # 4. Content keyword match (lighter weight — just check first 2000 chars)
        content_sample = content[:2000].lower()
        for word in query_words:
            if len(word) >= 4 and word in content_sample:
                score += 3

        # 5. Prefer smaller files (easier for LLM to process)
        if len(content) < 500:
            score += 5
        elif len(content) < 1500:
            score += 3
        elif len(content) > 5000:
            score -= 5

        return score


def _clean_json(content: str) -> str:
    """Strip markdown code fences from LLM output."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()
