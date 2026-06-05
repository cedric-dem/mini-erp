from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models.db import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    initial_quantity = Column(Integer, nullable=False, default=0)
    current_quantity = Column(Integer, nullable=False, default=0)
    unit_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    created_by = relationship("User")
    project = relationship("Project")
    movements = relationship("InventoryHistory", back_populates="item", cascade="all, delete-orphan")


class InventoryHistory(Base):
    __tablename__ = "inventory_history"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    note = Column(String, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    item = relationship("InventoryItem", back_populates="movements")
    created_by = relationship("User")
    project = relationship("Project")
