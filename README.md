

# 🎬 FastAPI + GraphQL 기반 영화 관리 API

이 프로젝트는 **FastAPI + GraphQL**을 활용하여 **영화, 배우(캐릭터), 출연 정보를 관리**하는 API입니다.  
SQLAlchemy와 SQLite(`demo.db`)를 기반으로 동작하며, **별도의 데이터베이스 설정 없이 바로 실행 가능**합니다.

---

## 🛠 실행 방법

###  1. 프로젝트 클론 & 가상환경 설정
- **Python 버전:** `Python 3.11`
```bash
git clone https://github.com/sy-oh5/graphQL.git
cd movie
python -m venv venv #가상환경 생성 - 최초 실행시
source venv/bin/activate #가상환경 실행
pip install fastapi strawberry-graphql sqlalchemy uvicorn
```

###  2. 서버 실행
```bash
uvicorn main:app --reload
```

+ 실행 후, GraphQL API 테스트: http://127.0.0.1:8000/graphql
---
<img width="1673" alt="image" src="https://github.com/user-attachments/assets/1e2c6ccf-b6e4-4271-aa97-c22862072c01" />

+ 좌측 explorer에서 확인 가능
