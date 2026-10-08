import uvicorn
from backend.app.seed import seed_database

if __name__ == "__main__":
    # Ensure database is seeded before starting server
    seed_database()
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)
