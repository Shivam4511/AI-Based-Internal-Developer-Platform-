from fastapi import FastAPI
from app.api import router

app = FastAPI(title="IDP Chatbot")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "IDP Chatbot API is running. Go to /docs for the Swagger UI."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
