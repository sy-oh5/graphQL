from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from models.movie_model import Movie
from models.character_model import Character
import enum

#  역할(Role) ENUM 정의 (영어 사용)
class RoleEnum(enum.Enum):
    LEAD = "LEAD"  # 주연
    SUPPORTING = "SUPPORTING"  # 조연
    CAMEO = "CAMEO"  # 단역
    DIRECTOR = "DIRECTOR"  # 감독
    OTHER = "OTHER"  # 기타

class Casting(Base):
    __tablename__ = "castings"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)  #  ENUM 적용
    screen_name = Column(String, nullable=True)  #  극 중 캐릭터 이름 (배우만 해당)

    # 관계 설정 (Casting → Movie, Character 연결)
    movie = relationship("Movie", backref="castings")
    character = relationship("Character", backref="castings")
