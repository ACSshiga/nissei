from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, projects, worklogs, invoices, materials, checklists, masters

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Nissei 工数管理システム",
    description="工数管理と請求処理のためのシステム",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Nissei 工数管理システム API"}

# Include routers (will be created next)
app.include_router(auth.router, prefix="/api/auth", tags=["認証"])
app.include_router(projects.router, tags=["案件管理"])
app.include_router(worklogs.router, prefix="/api/worklogs", tags=["工数入力"])
app.include_router(invoices.router, prefix="/api/invoices", tags=["請求"])
app.include_router(materials.router, prefix="/api/materials", tags=["資料"])
app.include_router(checklists.router, prefix="/api/checklists", tags=["注意点"])
app.include_router(masters.router, tags=["マスタ"])