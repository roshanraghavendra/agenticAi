import uvicorn
import fastapi

app = fastapi.FastAPI()

@app.get("/")
def fx(n:str,c:int):
	name = n
	age = c
	return {"name": name, "age": age}