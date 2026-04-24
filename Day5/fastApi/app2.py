import uvicorn
import fastapi

app = fastapi.FastAPI()

@app.get("/")
async def fx():
	return {"Key1": "Welcome to FastAPI"}

if __name__ == "__main__":
	uvicorn.run("app2:app",reload=True)