from sqlalchemy import Column, ForeignKey, Integer, String

from models.db import Base

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key = True, index = True)
	username = Column(String, unique = True, nullable = False, index = True)
	password = Column(String, nullable = False)
	role = Column(String, nullable = False, default = "member")
	project_id = Column(Integer, ForeignKey("projects.id"), nullable = False, index = True)
