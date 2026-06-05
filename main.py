
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text

from models.db import Base, engine
from routes.auth import router as auth_router
from routes.dashboard import router as dashboard_router
from routes.inventory import router as inventory_router

app = FastAPI(title="Mini ERP", version="0.1.0")
app.add_middleware(SessionMiddleware, secret_key="mini-erp-dev-secret", same_site="lax")
app.mount("/static", StaticFiles(directory="static"), name="static")

def ensure_inventory_schema_compatibility() -> None:
    with engine.begin() as conn:
        columns = [row[1] for row in conn.execute(text("PRAGMA table_info(inventory_items)"))]
        if not columns:
            return
        if "current_quantity" not in columns:
            conn.execute(text("ALTER TABLE inventory_items ADD COLUMN current_quantity INTEGER NOT NULL DEFAULT 0"))
            if "initial_quantity" in columns:
                conn.execute(
                    text("UPDATE inventory_items SET current_quantity = initial_quantity WHERE current_quantity = 0"))


Base.metadata.create_all(bind=engine)
ensure_inventory_schema_compatibility()

app.include_router(auth_router)
app.include_router(inventory_router)
app.include_router(dashboard_router)

