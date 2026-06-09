from collections import defaultdict
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
	sys.path.insert(0, str(ROOT))

from models.db import Base, SessionLocal, engine
from models.inventory_items import InventoryHistory, InventoryItem
from models.projects import Project
from models.users import User

def load_example_fixtures() -> None:
	Base.metadata.create_all(bind = engine)

	with SessionLocal() as db:
		# Reset only fixture-managed tables for predictable re-runs.
		db.query(InventoryHistory).delete()
		db.query(InventoryItem).delete()
		db.query(User).delete()
		db.query(Project).delete()
		db.commit()

		computer_shop = Project(name = "computer shop")
		garage = Project(name = "garage")
		db.add_all([computer_shop, garage])
		db.flush()

		projects_by_name = {
			computer_shop.name: computer_shop,
			garage.name: garage,
		}

		users = [
			User(username = "leroy_jenkin", password = "lj123", role = "admin", project_id = computer_shop.id),
			User(username = "jeffanie_jefferson", password = "jj1234", role = "member", project_id = computer_shop.id),
			User(username = "johnny_johnson", password = "19", role = "member", project_id = computer_shop.id),

			User(username = "bob", password = "12bob", role = "member", project_id = computer_shop.id),

			User(username = "jeremy_hammond", password = "jh199", role = "admin", project_id = garage.id),
			User(username = "richard_may", password = "rm001", role = "member", project_id = garage.id),
			User(username = "james_clarkson", password = "jc", role = "member", project_id = garage.id),
		]

		db.add_all(users)
		db.flush()

		users_by_name = {user.username: user for user in users}

		item_unit_prices = {
			("computer shop", "Gaming Laptop"): 1499.99,
			("computer shop", "Mechanical Keyboard"): 119.00,
			("computer shop", "27 inch screen"): 249.99,
			("computer shop", "HDMI cable"): 19.99,
			("computer shop", "Linux License"): 19.99,

			("garage", "Motor Oil 5W-30"): 29.50,
			("garage", "Flux Capacitor"): 99.99,
			("garage", "Elbow Oil"): 29.50,
			("garage", "Brake Pads"): 64.99,
		}

		inventory_history_entries = [
			{
				"project_name": "computer shop",
				"item_name": "Gaming Laptop",
				"quantity_change": 10,
				"user_name": "leroy_jenkin",
				"created_at": datetime(2025, 1, 5, 9, 15),
			},
			{
				"project_name": "computer shop",
				"item_name": "Mechanical Keyboard",
				"quantity_change": 120,
				"user_name": "jeffanie_jefferson",
				"created_at": datetime(2025, 2, 2, 11, 0),
			},
			{
				"project_name": "computer shop",
				"item_name": "Gaming Laptop",
				"quantity_change": -1,
				"user_name": "johnny_johnson",
				"created_at": datetime(2025, 3, 12, 14, 45),
			},
			{
				"project_name": "computer shop",
				"item_name": "Mechanical Keyboard",
				"quantity_change": -1,
				"user_name": "jeffanie_jefferson",
				"created_at": datetime(2025, 4, 1, 10, 20),
			},
			{
				"project_name": "computer shop",
				"item_name": "27 inch screen",
				"quantity_change": 12,
				"user_name": "johnny_johnson",
				"created_at": datetime(2025, 5, 9, 16, 10),
			},
			{
				"project_name": "computer shop",
				"item_name": "27 inch screen",
				"quantity_change": -1,
				"user_name": "jeffanie_jefferson",
				"created_at": datetime(2025, 6, 18, 13, 5),
			},
			{
				"project_name": "computer shop",
				"item_name": "Gaming Laptop",
				"quantity_change": -2,
				"user_name": "leroy_jenkin",
				"created_at": datetime(2025, 7, 7, 9, 40),
			},
			{
				"project_name": "computer shop",
				"item_name": "HDMI cable",
				"quantity_change": 10,
				"user_name": "leroy_jenkin",
				"created_at": datetime(2025, 8, 14, 8, 55),
			},
			{
				"project_name": "computer shop",
				"item_name": "HDMI cable",
				"quantity_change": -2,
				"user_name": "johnny_johnson",
				"created_at": datetime(2025, 9, 3, 12, 30),
			},
			{
				"project_name": "computer shop",
				"item_name": "Linux License",
				"quantity_change": 12,
				"user_name": "johnny_johnson",
				"created_at": datetime(2025, 9, 3, 12, 45),
			},

			{
				"project_name": "garage",
				"item_name": "Motor Oil 5W-30",
				"quantity_change": 50,
				"user_name": "jeremy_hammond",
				"created_at": datetime(2025, 9, 20, 15, 0),
			},
			{
				"project_name": "garage",
				"item_name": "Flux Capacitor",
				"quantity_change": 12,
				"user_name": "james_clarkson",
				"created_at": datetime(2025, 10, 5, 10, 10),
			},
			{
				"project_name": "garage",
				"item_name": "Motor Oil 5W-30",
				"quantity_change": -2,
				"user_name": "richard_may",
				"created_at": datetime(2025, 10, 28, 17, 25),
			},
			{
				"project_name": "garage",
				"item_name": "Elbow Oil",
				"quantity_change": 50,
				"user_name": "jeremy_hammond",
				"created_at": datetime(2025, 11, 11, 9, 5),
			},
			{
				"project_name": "garage",
				"item_name": "Elbow Oil",
				"quantity_change": -3,
				"user_name": "james_clarkson",
				"created_at": datetime(2025, 11, 29, 14, 0),
			},
			{
				"project_name": "garage",
				"item_name": "Brake Pads",
				"quantity_change": -1,
				"user_name": "richard_may",
				"created_at": datetime(2025, 12, 9, 11, 40),
			},
			{
				"project_name": "garage",
				"item_name": "Brake Pads",
				"quantity_change": 10,
				"user_name": "jeremy_hammond",
				"created_at": datetime(2025, 12, 22, 13, 35),
			},
			{
				"project_name": "garage",
				"item_name": "Brake Pads",
				"quantity_change": -2,
				"user_name": "james_clarkson",
				"created_at": datetime(2026, 1, 6, 16, 15),
			},
			{
				"project_name": "garage",
				"item_name": "Motor Oil 5W-30",
				"quantity_change": -1,
				"user_name": "richard_may",
				"created_at": datetime(2026, 1, 31, 10, 50),
			},
			{
				"project_name": "garage",
				"item_name": "Brake Pads",
				"quantity_change": 5,
				"user_name": "jeremy_hammond",
				"created_at": datetime(2026, 1, 31, 10, 55),
			},
		]

		item_totals = defaultdict(int)
		item_metadata = {}

		for entry in inventory_history_entries:
			item_key = (entry["project_name"], entry["item_name"])
			item_totals[item_key] += entry["quantity_change"]
			if item_key not in item_metadata:
				item_metadata[item_key] = {
					"unit_price": item_unit_prices[item_key],
					"created_by_user_name": entry["user_name"],
				}

		items = []
		for (project_name, item_name), current_quantity in item_totals.items():
			metadata = item_metadata[(project_name, item_name)]
			items.append(
				InventoryItem(
					name = item_name,
					initial_quantity = current_quantity,
					current_quantity = current_quantity,
					unit_price = metadata["unit_price"],
					created_by_user_id = users_by_name[metadata["created_by_user_name"]].id,
					project_id = projects_by_name[project_name].id,
				)
			)

		db.add_all(items)
		db.flush()

		items_by_key = {
			(projects_by_name[project.name].name, item.name): item
			for project in projects_by_name.values()
			for item in items
			if item.project_id == project.id
		}

		inventory_history = []
		for entry in inventory_history_entries:
			project_name = entry["project_name"]
			item_name = entry["item_name"]
			history_record = InventoryHistory(
				item_id = items_by_key[(project_name, item_name)].id,
				quantity_change = entry["quantity_change"],
				note = entry.get("note", ""),
				created_by_user_id = users_by_name[entry["user_name"]].id,
				project_id = projects_by_name[project_name].id,
			)
			if "created_at" in entry:
				history_record.created_at = entry["created_at"]
			inventory_history.append(history_record)

		db.add_all(inventory_history)
		db.commit()

if __name__ == "__main__":
	load_example_fixtures()
