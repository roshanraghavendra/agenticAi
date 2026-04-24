import uvicorn
import fastapi
from fastapi.responses import HTMLResponse

app = fastapi.FastAPI()

@app.get("/", response_class=HTMLResponse)
def f1():
	return "<h1> <font color=green> Welcome to FastAPI </font> </h1>"


@app.get("/mypage")
def f2():
	return HTMLResponse(content="<h2> <font color= blue> Webpage response </font> </h2>")

@app.get("/myview")
def f3():
	return HTMLResponse(
		content="<h2> Webpage response </h2>",	
		status_code=201,
		headers={"K1":"Wegpage"}
	)