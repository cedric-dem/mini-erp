import json
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlalchemy import distinct, func

from models.db import SessionLocal
from models.inventory_items import InventoryHistory, InventoryItem
from models.projects import Project
from models.users import User
from routes.common import templates

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    page = request.query_params.get("page", "dashboard")
    pages = {
        "dashboard": "dashboard",
        "users-list": "users list",
        "inventory": "inventory",
        "project-history": "project history",
        "settings": "settings",
    }
    normalized_page = page if page in pages else "dashboard"

    with SessionLocal() as db:
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/", status_code=303)

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return RedirectResponse(url="/", status_code=303)

        context = {
            "request": request,
            "normalized_page": normalized_page,
            "current_user": user,
        }

        if normalized_page == "dashboard":
            context["section_template"] = "dashboard_details.html"
            context["user_movements_count"] = (
                db.query(InventoryHistory)
                .filter(
                    InventoryHistory.project_id == user.project_id,
                    InventoryHistory.created_by_user_id == user.id,
                )
                .count()
            )
            context["user_distinct_impacted_objects"] = (
                    db.query(func.count(distinct(InventoryHistory.item_id)))
                    .filter(
                        InventoryHistory.project_id == user.project_id,
                        InventoryHistory.created_by_user_id == user.id,
                    )
                    .scalar()
                    or 0
            )
            project = db.query(Project).filter(Project.id == user.project_id).first()
            context["project_name"] = project.name if project else "Unknown project"
            context["total_inventory_objects"] = (
                db.query(InventoryItem)
                .filter(InventoryItem.project_id == user.project_id)
                .count()
            )
            context["total_project_movements"] = (
                db.query(InventoryHistory)
                .filter(InventoryHistory.project_id == user.project_id)
                .count()
            )
        elif normalized_page == "users-list":
            context["section_template"] = "users_list.html"
            project_users = (
                db.query(User)
                .filter(User.project_id == user.project_id)
                .order_by(User.username)
                .all()
            )
            context["project_users"] = [
                {
                    "username": project_user.username,
                    "role": project_user.role,
                }
                for project_user in project_users
            ]
        elif normalized_page == "inventory":
            context["section_template"] = "inventory_section.html"
            inventory_items = (
                db.query(InventoryItem)
                .filter(InventoryItem.project_id == user.project_id)
                .order_by(InventoryItem.created_at.desc())
                .all()
            )
            context["inventory_items"] = inventory_items
            context["item_names_json"] = {item.id: json.dumps(item.name) for item in inventory_items}
        elif normalized_page == "project-history":
            context["section_template"] = "project_history.html"
            history_rows = (
                db.query(InventoryHistory, InventoryItem.name, User.username)
                .join(InventoryItem, InventoryHistory.item_id == InventoryItem.id)
                .join(User, InventoryHistory.created_by_user_id == User.id)
                .filter(InventoryHistory.project_id == user.project_id)
                .order_by(InventoryHistory.created_at.desc())
                .all()
            )
            context["history_rows"] = history_rows
        else:
            context["section_template"] = "settings.html"

    return templates.TemplateResponse(request=request, name="dashboard.html", context=context)


@router.post("/dashboard/users/accept")
def accept_user(request: Request, target_username: Annotated[str, Form()]):
    with SessionLocal() as db:
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/", status_code=303)

        current_user = db.query(User).filter(User.id == user_id).first()
        if not current_user:
            return RedirectResponse(url="/", status_code=303)

        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can accept users")

        target_user = (
            db.query(User)
            .filter(
                User.username == target_username,
                User.project_id == current_user.project_id,
            )
            .first()
        )
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        if target_user.role == "unvalidated":
            target_user.role = "member"
            db.commit()

    return RedirectResponse(url="/dashboard?page=users-list", status_code=303)
