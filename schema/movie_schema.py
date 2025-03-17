import enum
import strawberry
from typing import List, Optional

from sqlalchemy.orm import joinedload

from database import SessionLocal
from models import Movie, Casting, Character, RoleEnum, GenderEnum

@strawberry.type
class Character:
    id: int
    name: str
    sex: GenderEnum
    birth_year: Optional[int]
    nationality: Optional[str]

@strawberry.type
class CastingType:
    id: int
    character: Character
    role: RoleEnum
    screen_name: Optional[str]

@strawberry.type
class MovieType:
    id: int
    title: str
    year: int
    castings: List[CastingType]

@strawberry.input
class CastingInput:
    character_id: Optional[int]  # ✅ 캐릭터 ID가 없을 수도 있음
    name: Optional[str]  # ✅ 캐릭터 이름 (없으면 새로 추가)
    sex: GenderEnum  # ✅ 성별 추가
    birth_year: Optional[int]  # ✅ 출생 연도 추가
    nationality: Optional[str]  # ✅ 국적 추가
    role: RoleEnum  # ✅ 역할
    screen_name: Optional[str]  # 극 중 캐릭터 이름 (배우만 해당)

@strawberry.type
class Query:
    @strawberry.field
    def get_movies(
        self,
        id: Optional[int] = None,
        title: Optional[str] = None,
        year: Optional[int] = None,
        director: Optional[str] = None,  # ✅ 특정 감독 검색
        actor: Optional[str] = None  # ✅ 특정 배우 검색
    ) -> List[MovieType]:
        db = SessionLocal()
        query = db.query(Movie).options(joinedload(Movie.castings).joinedload(Casting.character))

        # ✅ 동적 필터링 적용
        if id is not None:
            query = query.filter(Movie.id == id)
        if title is not None:
            query = query.filter(Movie.title.ilike(f"%{title}%"))
        if year is not None:
            query = query.filter(Movie.year == year)

        # ✅ 감독 검색 (Casting에서 role=DIRECTOR)
        if director is not None:
            query = query.join(Casting).join(Character).filter(
                Casting.role == RoleEnum.DIRECTOR,
                Character.name.ilike(f"%{director}%")
            )

        # ✅ 특정 배우 검색 (Casting에서 role≠DIRECTOR)
        if actor is not None:
            query = query.join(Casting).join(Character).filter(
                Casting.role != RoleEnum.DIRECTOR,
                Character.name.ilike(f"%{actor}%")
            )

        movies = query.all()
        db.close()

        return [
            MovieType(
                id=m.id,
                title=m.title,
                year=m.year,
                castings=[
                    CastingType(
                        id=c.id,
                        character=Character(
                            id=c.character.id,
                            name=c.character.name,
                            sex=c.character.sex.name,
                            birth_year=c.character.birth_year,
                            nationality=c.character.nationality,
                        ),
                        role=RoleEnum[c.role.name],  # ✅ ENUM 변환
                        screen_name=c.screen_name
                    ) for c in m.castings
                ]
            ) for m in movies
        ]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_movie(
        self,
        title: str,
        year: int,
        castings: List[CastingInput]
    ) -> MovieType:
        db = SessionLocal()
        new_movie = Movie(title=title, year=year)
        db.add(new_movie)
        db.commit()
        db.refresh(new_movie)

        # ✅ 캐스팅 정보 등록 (캐릭터 자동 추가 기능 포함)
        if castings:
            for casting in castings:
                # ✅ 캐릭터 ID가 없으면 새로운 캐릭터 추가
                if casting.character_id is None:
                    if not casting.name:
                        raise ValueError("Character name cannot be empty.")

                    new_character = Character(
                        name=casting.name,
                        sex=GenderEnum[casting.sex.name],  # ✅ ENUM 변환 (MALE/FEMALE)
                        birth_year=casting.birth_year,  # ✅ 출생 연도 저장
                        nationality=casting.nationality  # ✅ 국적 저장
                    )
                    db.add(new_character)
                    db.commit()
                    db.refresh(new_character)
                    character_id = new_character.id
                else:
                    character_id = casting.character_id

                new_casting = Casting(
                    movie_id=new_movie.id,
                    character_id=character_id,
                    role=RoleEnum[casting.role.name],  # ✅ ENUM 변환
                    screen_name=casting.screen_name
                )
                db.add(new_casting)
            db.commit()

        db.refresh(new_movie)
        db.close()

        return MovieType(
            id=new_movie.id,  # ✅ 올바른 키워드 인자 사용 (`=`)
            title=new_movie.title,
            year=new_movie.year,
            castings=[]
        )

    @strawberry.mutation
    def update_movie(
            self,
            id: int,
            title: Optional[str] = None,
            year: Optional[int] = None,
            castings: Optional[List[CastingInput]] = None
    ) -> MovieType:
        db = SessionLocal()
        movie = (
            db.query(Movie)
            .options(joinedload(Movie.castings).joinedload(Casting.character))
            .filter(Movie.id == id)
            .first()
        )

        if not movie:
            raise ValueError(f"Movie with ID {id} not found")

        # ✅ 제목 및 연도 수정
        if title:
            movie.title = title
        if year:
            movie.year = year

        # ✅ 캐스팅 수정 (기존 캐스팅 삭제 후 새로운 캐스팅 추가)
        if castings:
            db.query(Casting).filter(Casting.movie_id == id).delete()  # 기존 캐스팅 삭제
            for casting in castings:
                if casting.character_id is None:
                    if not casting.name:
                        raise ValueError("Character name cannot be empty.")

                    new_character = Character(
                        name=casting.name,
                        sex=GenderEnum[casting.sex.name],
                        birth_year=casting.birth_year,
                        nationality=casting.nationality
                    )
                    db.add(new_character)
                    db.commit()
                    db.refresh(new_character)
                    character_id = new_character.id
                else:
                    character_id = casting.character_id

                new_casting = Casting(
                    movie_id=id,
                    character_id=character_id,
                    role=RoleEnum[casting.role.name],
                    screen_name=casting.screen_name
                )
                db.add(new_casting)

        db.commit()
        db.refresh(movie)
        db.close()

        return MovieType(
            id=movie.id,
            title=movie.title,
            year=movie.year,
            castings=[
                CastingType(
                    id=c.id,
                    character=Character(
                        id=c.character.id,
                        name=c.character.name,
                        sex=GenderEnum[c.character.sex.name],
                        birth_year=c.character.birth_year,
                        nationality=c.character.nationality,
                    ),
                    role=RoleEnum[c.role.name],
                    screen_name=c.screen_name
                ) for c in movie.castings
            ]
        )

    @strawberry.mutation
    def delete_movie(self, id: int) -> bool:
        db = SessionLocal()
        movie = db.query(Movie).filter(Movie.id == id).first()

        if not movie:
            raise ValueError(f"Movie with ID {id} not found")

        # ✅ 관련 캐스팅 먼저 삭제
        db.query(Casting).filter(Casting.movie_id == id).delete()

        # ✅ 영화 삭제
        db.delete(movie)
        db.commit()
        db.close()

        return True  # ✅ 성공적으로 삭제되었음을 반환
