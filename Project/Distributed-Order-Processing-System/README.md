# Distributed Order Processing System (FastAPI + PostgreSQL)

## Steps

1. Run PostgreSQL
2. Execute:
   psql -U postgres -f setup_database.sql

3. Start services:
   cd product-service
   uvicorn app:app --port 8001

   cd order-service
   uvicorn app:app --port 8000

4. Initialize:
   curl -X POST http://localhost:8001/init-data
   curl -X POST http://localhost:8000/init-data

5. Run tests:
   python test_system.py