from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from models.db import SessionLocal
from models.inventory_items import InventoryHistory, InventoryItem
from models.users import User

router = APIRouter()

@router.post("/inventory/object/create")
def create_inventory_object_type(
		request: Request,
		name: Annotated[str, Form()],
		initial_quantity: Annotated[int, Form()],
		unit_price: Annotated[float, Form()],
):
	with SessionLocal() as db:
		user_id = request.session.get("user_id")
		if not user_id:
			raise HTTPException(status_code = 401, detail = "Not authenticated")

		user = db.query(User).filter(User.id == user_id).first()
		if not user:
			raise HTTPException(status_code = 404, detail = "User not found")

		item = InventoryItem(
			name = name.strip(),
			current_quantity = initial_quantity,
			unit_price = unit_price,
			created_by_user_id = user.id,
			project_id = user.project_id,
		)
		db.add(item)
		db.flush()

		history = InventoryHistory(
			item_id = item.id,
			quantity_change = initial_quantity,
			note = "Object type created",
			created_by_user_id = user.id,
			project_id = user.project_id,
		)
		db.add(history)
		db.commit()

	return RedirectResponse(url = "/dashboard?page=inventory", status_code = 303)

@router.post("/inventory/move")
def move_inventory(
		request: Request,
		item_id: Annotated[int, Form()],
		movement_type: Annotated[str, Form()],
		quantity: Annotated[int, Form()],
):
	with SessionLocal() as db:
		user_id = request.session.get("user_id")
		if not user_id:
			raise HTTPException(status_code = 401, detail = "Not authenticated")

		user = db.query(User).filter(User.id == user_id).first()
		if not user:
			raise HTTPException(status_code = 404, detail = "User not found")

		item = db.query(InventoryItem).filter(InventoryItem.id == item_id,
											  InventoryItem.project_id == user.project_id).first()
		if not item:
			raise HTTPException(status_code = 404, detail = "Inventory item not found")

		if quantity < 0:
			raise HTTPException(status_code = 400, detail = "Quantity must be positive")

		quantity_change = quantity if movement_type == "add" else -quantity
		if movement_type not in {"add", "delete"}:
			raise HTTPException(status_code = 400, detail = "Invalid movement type")
		if item.current_quantity + quantity_change < 0:
			raise HTTPException(status_code = 400, detail = "Not enough inventory for deletion")

		item.current_quantity += quantity_change
		db.add(InventoryHistory(
			item_id = item.id,
			quantity_change = quantity_change,
			note = "Manual movement",
			created_by_user_id = user.id,
			project_id = user.project_id,
		))
		db.commit()

	return RedirectResponse(url = "/dashboard?page=inventory", status_code = 303)
