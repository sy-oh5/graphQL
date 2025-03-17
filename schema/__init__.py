import strawberry
from strawberry import Schema
from schema.movie_schema import Query as MovieQuery, Mutation as MovieMutation
from schema.character_schema import Query as CharacterQuery, Mutation as CharacterMutation

@strawberry.type
class Query(MovieQuery, CharacterQuery):
    pass

@strawberry.type
class Mutation(MovieMutation, CharacterMutation):
    pass

schema = Schema(query=Query, mutation=Mutation)
