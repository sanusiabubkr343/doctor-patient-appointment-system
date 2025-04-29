from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.routers import users

app = FastAPI(
    title="La Hospital",
    description="Doctor Management System with patient booking appointments",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    prefix="/api/v1",
    contact={
        "name": "Sanusi Abubakr",
        "email": "sanusiabubakr343@gmail.com",
    },
)
# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.on_event("startup")
async def startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)
