import uvicorn
import fastapi

app = fastapi.FastAPI()

@app.get("/")
def fx():
	return "Hello"

# execute as    python -m uvicorn app1:app --reload