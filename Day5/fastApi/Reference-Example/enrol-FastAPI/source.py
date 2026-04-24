from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import uvicorn

app = FastAPI()

# Template configuration
templates = Jinja2Templates(directory="templates")


def get_db_connection():
    con = sqlite3.connect("senroll.db")
    con.row_factory = sqlite3.Row
    return con


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "sindex.html",
        {"request": request}
    )


@app.get("/add", response_class=HTMLResponse)
def add(request: Request):
    return templates.TemplateResponse(
        "sadd.html",
        {"request": request}
    )


@app.post("/savedetails", response_class=HTMLResponse)
def save_details(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    number: str = Form(...),
    college_name: str = Form(...),
    city: str = Form(...),
    state: str = Form(...)
):
    msg = "msg"
    con = None
    try:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO ens
            (name, email, address, number, college_name, city, state)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, email, address, number, college_name, city, state)
        )
        con.commit()
        msg = "Your Details have been Successfully Submitted"
    except Exception as e:
        if con:
            con.rollback()
        msg = "Sorry! Please fill all the details in the form"
    finally:
        if con:
            con.close()

    return templates.TemplateResponse(
        "ssuccess.html",
        {"request": request, "msg": msg}
    )


@app.get("/view", response_class=HTMLResponse)
def view(request: Request):
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM ens")
    rows = cur.fetchall()
    con.close()

    return templates.TemplateResponse(
        "sview.html",
        {"request": request, "rows": rows}
    )


@app.get("/data")
def data_response():
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM ens")
    rows = [dict(row) for row in cur.fetchall()]
    con.close()

    return JSONResponse({"students": rows})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=1234, reload = True)
