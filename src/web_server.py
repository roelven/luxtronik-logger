import uvicorn
from src.web import api_app as app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
