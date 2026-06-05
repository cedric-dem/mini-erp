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


