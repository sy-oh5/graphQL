

# 🎬 FastAPI + GraphQL 기반 영화 관리 API

이 프로젝트는 **FastAPI + GraphQL**을 활용하여 **영화, 배우(캐릭터), 출연 정보를 관리**하는 API입니다.  
SQLAlchemy와 SQLite(`demo.db`)를 기반으로 동작하며, **별도의 데이터베이스 설정 없이 바로 실행 가능**합니다.

---

## 🛠 실행 방법

### ✅ 1. 프로젝트 클론 & 가상환경 설정
- **Python 버전:** `Python 3.11`
```bash
git clone https://github.com/your-repo/movie-project.git
cd movie-project
python3 -m venv venv
source venv/bin/activate
pip install fastapi strawberry-graphql sqlalchemy uvicorn
```

### ✅ 2. 서버 실행
```bash
uvicorn main:app --reload
```

+ 실행 후, GraphQL API 테스트: http://127.0.0.1:8000/graphql
