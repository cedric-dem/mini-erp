from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from models.db import Base, engine
from routes.auth import router as auth_router
from routes.dashboard import router as dashboard_router
from routes.inventory import router as inventory_router

app = FastAPI(title = "Mini ERP", version = "0.1.0")
app.add_middleware(SessionMiddleware, secret_key = "mini-erp-dev-secret", same_site = "lax")
app.mount("/static", StaticFiles(directory = "static"), name = "static")

Base.metadata.create_all(bind = engine)

app.include_router(auth_router)
app.include_router(inventory_router)
app.include_router(dashboard_router)
