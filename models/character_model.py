import enum

from sqlalchemy import Column, Integer, String, Enum
from database import Base

class GenderEnum(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # 배우 이름
    sex = Column(Enum(GenderEnum), nullable=False)  # 성별 (예: Male / Female)
    birth_year = Column(Integer)  # 출생 연도
    nationality = Column(String)  # 국적
