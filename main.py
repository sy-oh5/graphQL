from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from schema import schema
from database import engine, Base

app = FastAPI()

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

graphql_app = GraphQLRouter(schema)

app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI + GraphQL!"}
