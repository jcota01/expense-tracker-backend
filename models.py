from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum
from database import Base


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	username = Column(String)
	password = Column(String)