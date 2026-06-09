import json
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from models.db import SessionLocal
from models.inventory_items import InventoryHistory, InventoryItem
from models.projects import Project
from models.users import User
from routes.common import templates

router = APIRouter()

DASHBOARD_PAGES = {
	"dashboard": "dashboard",
	"users-list": "users list",
	"inventory": "inventory",
	"project-history": "project history",
	"settings": "settings",
}

def normalize_dashboard_page(page: str) -> str:
	return page if page in DASHBOARD_PAGES else "dashboard"

def redirect_to_login() -> RedirectResponse:
	return RedirectResponse(url = "/", status_code = 303)

def get_current_user_or_redirect(db: Session, request: Request) -> User | RedirectResponse:
	user_id = request.session.get("user_id")
	if not user_id:
		return redirect_to_login()

	user = db.query(User).filter(User.id == user_id).first()
	if not user:
		return redirect_to_login()

	return user

def build_base_dashboard_context(request: Request, normalized_page: str, user: User) -> dict:
	return {
		"request": request,
		"normalized_page": normalized_page,
		"current_user": user,
	}

def add_dashboard_details_context(db: Session, context: dict, user: User) -> None:
	context["section_template"] = "dashboard_details.html"
	context["user_movements_count"] = count_user_movements(db, user)
	context["user_distinct_impacted_objects"] = count_user_distinct_impacted_objects(db, user)
	context["project_name"] = get_project_name(db, user)
	context["total_inventory_objects"] = count_project_inventory_objects(db, user)
	context["total_project_movements"] = count_project_movements(db, user)

def count_user_movements(db: Session, user: User) -> int:
	return (
		db.query(InventoryHistory)
		.filter(
			InventoryHistory.project_id == user.project_id,
			InventoryHistory.created_by_user_id == user.id,
		)
		.count()
	)

def count_user_distinct_impacted_objects(db: Session, user: User) -> int:
	return (
			db.query(func.count(distinct(InventoryHistory.item_id)))
			.filter(
				InventoryHistory.project_id == user.project_id,
				InventoryHistory.created_by_user_id == user.id,
			)
			.scalar()
			or 0
	)

def get_project_name(db: Session, user: User) -> str:
	project = db.query(Project).filter(Project.id == user.project_id).first()
	return project.name if project else "Unknown project"

def count_project_inventory_objects(db: Session, user: User) -> int:
	return (
		db.query(InventoryItem)
		.filter(InventoryItem.project_id == user.project_id)
		.count()
	)

def count_project_movements(db: Session, user: User) -> int:
	return (
		db.query(InventoryHistory)
		.filter(InventoryHistory.project_id == user.project_id)
		.count()
	)

def add_users_list_context(db: Session, context: dict, user: User) -> None:
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

def add_inventory_context(db: Session, context: dict, user: User) -> None:
	context["section_template"] = "inventory_section.html"
	inventory_items = (
		db.query(InventoryItem)
		.filter(InventoryItem.project_id == user.project_id)
		.order_by(InventoryItem.created_at.desc())
		.all()
	)
	context["inventory_items"] = inventory_items
	context["item_names_json"] = {item.id: json.dumps(item.name) for item in inventory_items}

def add_project_history_context(db: Session, context: dict, user: User) -> None:
	context["section_template"] = "project_history.html"
	context["history_rows"] = (
		db.query(InventoryHistory, InventoryItem.name, User.username)
		.join(InventoryItem, InventoryHistory.item_id == InventoryItem.id)
		.join(User, InventoryHistory.created_by_user_id == User.id)
		.filter(InventoryHistory.project_id == user.project_id)
		.order_by(InventoryHistory.created_at.desc())
		.all()
	)

def add_settings_context(context: dict) -> None:
	context["section_template"] = "settings.html"

def add_page_context(db: Session, context: dict, normalized_page: str, user: User) -> None:
	if normalized_page == "dashboard":
		add_dashboard_details_context(db, context, user)
	elif normalized_page == "users-list":
		add_users_list_context(db, context, user)
	elif normalized_page == "inventory":
		add_inventory_context(db, context, user)
	elif normalized_page == "project-history":
		add_project_history_context(db, context, user)
	else:
		add_settings_context(context)

@router.get("/dashboard", response_class = HTMLResponse)
def dashboard(request: Request):
	normalized_page = normalize_dashboard_page(request.query_params.get("page", "dashboard"))

	with SessionLocal() as db:
		user = get_current_user_or_redirect(db, request)
		if isinstance(user, RedirectResponse):
			return user

		context = build_base_dashboard_context(request, normalized_page, user)
		add_page_context(db, context, normalized_page, user)

	return templates.TemplateResponse(request = request, name = "dashboard.html", context = context)

def require_admin(user: User) -> None:
	if user.role != "admin":
		raise HTTPException(status_code = 403, detail = "Only admins can accept users")

def get_project_user_by_username(db: Session, username: str, project_id: int) -> User:
	target_user = (
		db.query(User)
		.filter(
			User.username == username,
			User.project_id == project_id,
		)
		.first()
	)
	if not target_user:
		raise HTTPException(status_code = 404, detail = "User not found")

	return target_user

def accept_pending_user(db: Session, user: User) -> None:
	if user.role == "unvalidated":
		user.role = "member"
		db.commit()

@router.post("/dashboard/users/accept")
def accept_user(request: Request, target_username: Annotated[str, Form()]):
	with SessionLocal() as db:
		current_user = get_current_user_or_redirect(db, request)
		if isinstance(current_user, RedirectResponse):
			return current_user

		require_admin(current_user)
		target_user = get_project_user_by_username(db, target_username, current_user.project_id)
		accept_pending_user(db, target_user)

	return RedirectResponse(url = "/dashboard?page=users-list", status_code = 303)
