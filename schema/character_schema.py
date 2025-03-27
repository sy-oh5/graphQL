import enum

import strawberry
from typing import List, Optional

from sqlalchemy.orm import joinedload

from database import SessionLocal
from models import RoleEnum, Casting, Movie
from models.character_model import Character, GenderEnum


@strawberry.type
class CharacterMovieCastingType:
    casting_id: int
    movie_id: int
    title: str
    year: int
    screen_name: Optional[str]  #  극 중 이름 추가
    role: RoleEnum  #  역할 (주연, 조연 등) 추가

@strawberry.type
class CharacterType:
    id: int
    name: str
    sex: GenderEnum
    birth_year: Optional[int]
    nationality: Optional[str]
    movies: List[CharacterMovieCastingType]

@strawberry.type
class Query:
    @strawberry.field
    def get_characters(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        sex: Optional[GenderEnum] = None,
        birth_year: Optional[int] = None,
        nationality: Optional[str] = None
    ) -> List[CharacterType]:
        db = SessionLocal()
        query = (
            db.query(Character)
            .outerjoin(Casting)  #  캐스팅 테이블과 조인
            .outerjoin(Movie)  #  영화 테이블과 조인
            .options(joinedload(Character.castings).joinedload(Casting.movie))  #  올바른 관계 로드
        )

        #  동적 필터링 적용
        if id is not None:
            query = query.filter(Character.id == id)
        if name is not None:
            query = query.filter(Character.name.ilike(f"%{name}%"))
        if sex is not None:
            query = query.filter(Character.sex == sex.value)
        if birth_year is not None:
            query = query.filter(Character.birth_year == birth_year)
        if nationality is not None:
            query = query.filter(Character.nationality.ilike(f"%{nationality}%"))

        characters = query.all()
        db.close()

        return [
            CharacterType(
                id=c.id,
                name=c.name,
                sex=GenderEnum[c.sex.name],  #  ENUM 변환
                birth_year=c.birth_year,
                nationality=c.nationality,
                movies=[  #  `c.castings`로 수정 (캐스팅 테이블을 통해 영화 정보 가져오기)
                    CharacterMovieCastingType(
                        casting_id=cast.id,
                        movie_id=cast.movie.id,
                        title=cast.movie.title,
                        year=cast.movie.year,
                        screen_name=cast.screen_name,  #  극 중 이름 추가
                        role=RoleEnum[cast.role.name]  #  역할 추가
                    )
                    for cast in c.castings  #  `c.castings` 사용
                ]
            )
            for c in characters
        ]



@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_character(self, name: str, sex: GenderEnum, birth_year: Optional[int], nationality: Optional[str]) -> CharacterType:
        db = SessionLocal()
        new_character = Character(name=name, sex=sex.value, birth_year=birth_year, nationality=nationality)
        db.add(new_character)
        db.commit()
        db.refresh(new_character)
        db.close()
        return CharacterType(id=new_character.id, name=new_character.name, sex=sex, birth_year=new_character.birth_year, nationality=new_character.nationality)
