import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating  import Jinja2Templates
from fastapi.responses import HTMLResponse


app = FastAPI()
templates= Jinja2Templates(directory="templates")


@app.get("/", response_class= HTMLResponse)

def fx(request: Request):
	return templates.TemplateResponse(
	"mypage.html",
	{"request":request,"title_var":"FASTAPI_PAGE"}
	)







