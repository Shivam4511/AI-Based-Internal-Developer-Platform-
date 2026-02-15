"""
Mock Database for IDP Platform
In-memory sample data to demonstrate platform capabilities.
"""
from datetime import datetime, timedelta
import random

# ─── Platform Stats ───────────────────────────────────────────────
PLATFORM_STATS = {
    "total_services": 47,
    "active_developers": 128,
    "uptime_percent": 99.97,
    "deployments_today": 23,
    "total_repos": 156,
    "open_incidents": 2,
    "avg_build_time_sec": 142,
    "code_reviews_pending": 8
}

# ─── Projects ─────────────────────────────────────────────────────
PROJECTS = [
    {
        "id": "proj-001",
        "name": "Payment Gateway Service",
        "description": "Core payment processing microservice handling Stripe, Razorpay, and internal wallet transactions.",
        "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Redis"],
        "status": "active",
        "team_lead": "Arjun Mehta",
        "team_size": 6,
        "last_deploy": "2026-02-13T08:45:00",
        "deploy_count": 342,
        "health": "healthy",
        "repo": "payment-gateway-svc"
    },
    {
        "id": "proj-002",
        "name": "Auth & Identity Gateway",
        "description": "OAuth2/OIDC compliant authentication service with SSO, MFA, and role-based access control.",
        "tech_stack": ["Node.js", "Express", "MongoDB", "JWT"],
        "status": "active",
        "team_lead": "Priya Sharma",
        "team_size": 4,
        "last_deploy": "2026-02-12T16:30:00",
        "deploy_count": 218,
        "health": "healthy",
        "repo": "auth-identity-gw"
    },
    {
        "id": "proj-003",
        "name": "Notification Engine",
        "description": "Multi-channel notification system supporting email, SMS, push, and in-app notifications with template management.",
        "tech_stack": ["Go", "Kafka", "Redis", "SendGrid"],
        "status": "active",
        "team_lead": "Rahul Verma",
        "team_size": 3,
        "last_deploy": "2026-02-11T11:20:00",
        "deploy_count": 156,
        "health": "degraded",
        "repo": "notification-engine"
    },
    {
        "id": "proj-004",
        "name": "Data Analytics Pipeline",
        "description": "ETL pipeline for processing clickstream data, generating business metrics, and feeding ML models.",
        "tech_stack": ["Python", "Apache Spark", "Airflow", "BigQuery"],
        "status": "staging",
        "team_lead": "Sneha Kulkarni",
        "team_size": 5,
        "last_deploy": "2026-02-10T14:00:00",
        "deploy_count": 89,
        "health": "healthy",
        "repo": "data-analytics-pipe"
    },
    {
        "id": "proj-005",
        "name": "Customer Portal Frontend",
        "description": "React-based customer-facing dashboard with order tracking, support tickets, and profile management.",
        "tech_stack": ["React", "TypeScript", "Vite", "TailwindCSS"],
        "status": "active",
        "team_lead": "Vikram Singh",
        "team_size": 7,
        "last_deploy": "2026-02-13T09:15:00",
        "deploy_count": 512,
        "health": "healthy",
        "repo": "customer-portal-fe"
    },
    {
        "id": "proj-006",
        "name": "Legacy CRM Migration",
        "description": "Migration toolkit for transitioning from legacy PHP CRM to modern microservices architecture.",
        "tech_stack": ["Python", "Django", "PostgreSQL", "Docker"],
        "status": "maintenance",
        "team_lead": "Deepa Nair",
        "team_size": 2,
        "last_deploy": "2026-01-28T10:00:00",
        "deploy_count": 34,
        "health": "healthy",
        "repo": "crm-migration-tool"
    }
]

# ─── Codebase Repositories ────────────────────────────────────────
REPOSITORIES = [
    {
        "name": "payment-gateway-svc",
        "language": "Python",
        "framework": "FastAPI",
        "lines_of_code": 18420,
        "contributors": 6,
        "open_prs": 3,
        "last_commit": "2026-02-13T08:30:00",
        "branch_count": 12,
        "test_coverage": 87.3,
        "description": "Core payment processing microservice",
        "sample_files": {
            "main.py": '''from fastapi import FastAPI, HTTPException
from app.routes import payments, webhooks, health
from app.middleware.auth import AuthMiddleware
from app.config import settings

app = FastAPI(title="Payment Gateway", version="2.1.0")

app.add_middleware(AuthMiddleware)
app.include_router(payments.router, prefix="/api/v1/payments")
app.include_router(webhooks.router, prefix="/api/v1/webhooks")
app.include_router(health.router, prefix="/health")

@app.on_event("startup")
async def startup():
    await db.connect()
    await cache.initialize()
''',
            "services/payment_processor.py": '''from typing import Optional
from decimal import Decimal
from app.models import Payment, PaymentStatus
from app.providers import StripeProvider, RazorpayProvider

class PaymentProcessor:
    def __init__(self, provider: str = "stripe"):
        self.provider = self._get_provider(provider)
    
    async def process_payment(
        self, amount: Decimal, currency: str, 
        method: str, metadata: Optional[dict] = None
    ) -> Payment:
        """Process a payment through the configured provider."""
        validated = self._validate_amount(amount, currency)
        result = await self.provider.charge(validated)
        return Payment(
            id=result.id,
            status=PaymentStatus.COMPLETED,
            amount=amount,
            currency=currency
        )
'''
        }
    },
    {
        "name": "auth-identity-gw",
        "language": "JavaScript",
        "framework": "Express",
        "lines_of_code": 12350,
        "contributors": 4,
        "open_prs": 1,
        "last_commit": "2026-02-12T16:15:00",
        "branch_count": 8,
        "test_coverage": 92.1,
        "description": "OAuth2/OIDC authentication gateway",
        "sample_files": {
            "server.js": '''const express = require("express");
const passport = require("passport");
const { rateLimiter } = require("./middleware/rateLimit");
const authRoutes = require("./routes/auth");
const userRoutes = require("./routes/users");

const app = express();
app.use(express.json());
app.use(rateLimiter);
app.use(passport.initialize());

app.use("/auth", authRoutes);
app.use("/api/users", userRoutes);

module.exports = app;
'''
        }
    },
    {
        "name": "notification-engine",
        "language": "Go",
        "framework": "Gin",
        "lines_of_code": 8900,
        "contributors": 3,
        "open_prs": 2,
        "last_commit": "2026-02-11T11:00:00",
        "branch_count": 6,
        "test_coverage": 78.5,
        "description": "Multi-channel notification dispatch system",
        "sample_files": {
            "main.go": '''package main

import (
    "notification-engine/handlers"
    "notification-engine/queue"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()
    q := queue.NewKafkaConsumer()
    
    r.POST("/api/notify", handlers.SendNotification)
    r.GET("/api/templates", handlers.ListTemplates)
    
    go q.StartConsuming()
    r.Run(":8080")
}
'''
        }
    },
    {
        "name": "data-analytics-pipe",
        "language": "Python",
        "framework": "Airflow",
        "lines_of_code": 22100,
        "contributors": 5,
        "open_prs": 4,
        "last_commit": "2026-02-10T13:45:00",
        "branch_count": 15,
        "test_coverage": 71.2,
        "description": "ETL pipeline for business analytics",
        "sample_files": {
            "dags/clickstream_etl.py": '''from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from tasks import extract, transform, load

default_args = {
    "owner": "data-team",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG("clickstream_etl", default_args=default_args,
         schedule_interval="@hourly", start_date=datetime(2026, 1, 1)) as dag:
    
    t1 = PythonOperator(task_id="extract_events", python_callable=extract.run)
    t2 = PythonOperator(task_id="transform_data", python_callable=transform.run)
    t3 = PythonOperator(task_id="load_to_warehouse", python_callable=load.run)
    
    t1 >> t2 >> t3
'''
        }
    },
    {
        "name": "customer-portal-fe",
        "language": "TypeScript",
        "framework": "React",
        "lines_of_code": 31200,
        "contributors": 7,
        "open_prs": 5,
        "last_commit": "2026-02-13T09:00:00",
        "branch_count": 20,
        "test_coverage": 83.7,
        "description": "Customer-facing React dashboard",
        "sample_files": {
            "src/App.tsx": '''import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Dashboard from "./pages/Dashboard";
import Orders from "./pages/Orders";
import Support from "./pages/Support";
import Layout from "./components/Layout";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/support" element={<Support />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  );
}
'''
        }
    },
    {
        "name": "infra-terraform-modules",
        "language": "HCL",
        "framework": "Terraform",
        "lines_of_code": 5600,
        "contributors": 3,
        "open_prs": 1,
        "last_commit": "2026-02-09T17:30:00",
        "branch_count": 4,
        "test_coverage": 0,
        "description": "Shared Terraform modules for cloud infrastructure",
        "sample_files": {
            "modules/eks-cluster/main.tf": '''resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = var.public_access
  }

  tags = merge(var.tags, {
    ManagedBy = "terraform"
    Team      = "platform"
  })
}
'''
        }
    },
    {
        "name": "shared-ui-components",
        "language": "TypeScript",
        "framework": "React",
        "lines_of_code": 14800,
        "contributors": 5,
        "open_prs": 3,
        "last_commit": "2026-02-12T14:20:00",
        "branch_count": 9,
        "test_coverage": 91.4,
        "description": "Shared React component library with Storybook",
        "sample_files": {}
    },
    {
        "name": "crm-migration-tool",
        "language": "Python",
        "framework": "Django",
        "lines_of_code": 9200,
        "contributors": 2,
        "open_prs": 0,
        "last_commit": "2026-01-28T09:50:00",
        "branch_count": 3,
        "test_coverage": 65.0,
        "description": "Legacy CRM to microservices migration toolkit",
        "sample_files": {}
    }
]

# ─── Activity Feed ────────────────────────────────────────────────
ACTIVITY_FEED = [
    {
        "id": "act-001",
        "type": "deploy",
        "title": "Deployed payment-gateway-svc v2.14.3",
        "description": "Hotfix for currency conversion rounding error in JPY transactions.",
        "author": "Arjun Mehta",
        "timestamp": "2026-02-13T08:45:00",
        "project": "Payment Gateway Service",
        "status": "success"
    },
    {
        "id": "act-002",
        "type": "pr_merged",
        "title": "PR #847 merged: Add biometric MFA support",
        "description": "Implemented WebAuthn-based biometric authentication as a second factor option.",
        "author": "Priya Sharma",
        "timestamp": "2026-02-13T07:30:00",
        "project": "Auth & Identity Gateway",
        "status": "success"
    },
    {
        "id": "act-003",
        "type": "deploy",
        "title": "Deployed customer-portal-fe v4.8.0",
        "description": "New order tracking UI with real-time status updates via WebSocket.",
        "author": "Vikram Singh",
        "timestamp": "2026-02-13T09:15:00",
        "project": "Customer Portal Frontend",
        "status": "success"
    },
    {
        "id": "act-004",
        "type": "incident",
        "title": "Notification delivery latency spike",
        "description": "Kafka consumer lag increased to 15k messages. Scaling consumers from 3 to 8.",
        "author": "Rahul Verma",
        "timestamp": "2026-02-13T06:22:00",
        "project": "Notification Engine",
        "status": "investigating"
    },
    {
        "id": "act-005",
        "type": "code_review",
        "title": "Review requested: Refactor ETL error handling",
        "description": "Improved retry logic with exponential backoff and dead-letter queue for failed records.",
        "author": "Sneha Kulkarni",
        "timestamp": "2026-02-12T17:45:00",
        "project": "Data Analytics Pipeline",
        "status": "pending"
    },
    {
        "id": "act-006",
        "type": "pr_merged",
        "title": "PR #1203 merged: Optimize DB connection pooling",
        "description": "Reduced connection pool size from 50 to 20 with lazy initialization, cutting memory by 35%.",
        "author": "Arjun Mehta",
        "timestamp": "2026-02-12T14:20:00",
        "project": "Payment Gateway Service",
        "status": "success"
    },
    {
        "id": "act-007",
        "type": "deploy",
        "title": "Deployed shared-ui-components v3.2.0",
        "description": "New DataTable and Modal components with accessibility improvements.",
        "author": "Vikram Singh",
        "timestamp": "2026-02-12T14:20:00",
        "project": "Shared UI Components",
        "status": "success"
    },
    {
        "id": "act-008",
        "type": "code_review",
        "title": "Review requested: Add rate limiting to auth endpoints",
        "description": "Implementing sliding window rate limiter with Redis backend, 100 req/min per IP.",
        "author": "Priya Sharma",
        "timestamp": "2026-02-12T11:00:00",
        "project": "Auth & Identity Gateway",
        "status": "pending"
    },
    {
        "id": "act-009",
        "type": "incident",
        "title": "CRM migration batch job timeout",
        "description": "Batch processing for legacy customer records exceeding 30-min timeout. Investigating chunking strategy.",
        "author": "Deepa Nair",
        "timestamp": "2026-02-11T16:30:00",
        "project": "Legacy CRM Migration",
        "status": "resolved"
    },
    {
        "id": "act-010",
        "type": "deploy",
        "title": "Deployed data-analytics-pipe v1.9.0",
        "description": "New real-time dashboard metrics pipeline for executive reporting.",
        "author": "Sneha Kulkarni",
        "timestamp": "2026-02-10T14:00:00",
        "project": "Data Analytics Pipeline",
        "status": "success"
    },
    {
        "id": "act-011",
        "type": "pr_merged",
        "title": "PR #332 merged: Terraform EKS module v2",
        "description": "Updated EKS module to support Kubernetes 1.29, added Karpenter autoscaling.",
        "author": "Rahul Verma",
        "timestamp": "2026-02-09T17:30:00",
        "project": "Infrastructure",
        "status": "success"
    },
    {
        "id": "act-012",
        "type": "code_review",
        "title": "Review requested: Payment reconciliation cron",
        "description": "Nightly job to reconcile payment records between Stripe and internal ledger.",
        "author": "Arjun Mehta",
        "timestamp": "2026-02-09T10:15:00",
        "project": "Payment Gateway Service",
        "status": "approved"
    }
]


# ─── Search Helpers ───────────────────────────────────────────────
def search_codebase(query: str = ""):
    """Search repos by name, language, or description."""
    if not query:
        return REPOSITORIES
    q = query.lower()
    return [
        r for r in REPOSITORIES
        if q in r["name"].lower()
        or q in r["language"].lower()
        or q in r["description"].lower()
        or q in r.get("framework", "").lower()
    ]

def get_repo_by_name(name: str):
    """Get a single repo by name."""
    for r in REPOSITORIES:
        if r["name"] == name:
            return r
    return None

def get_projects_by_status(status: str = ""):
    """Filter projects by status."""
    if not status:
        return PROJECTS
    return [p for p in PROJECTS if p["status"] == status.lower()]

def get_activity_by_type(event_type: str = ""):
    """Filter activity by event type."""
    if not event_type:
        return ACTIVITY_FEED
    return [a for a in ACTIVITY_FEED if a["type"] == event_type.lower()]
