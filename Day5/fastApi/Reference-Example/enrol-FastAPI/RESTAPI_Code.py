from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import uvicorn

app = FastAPI(title="Student Enrollment REST API")


# ------------------ DATABASE ------------------

def get_db_connection():
    con = sqlite3.connect("senroll.db")
    con.row_factory = sqlite3.Row
    return con


# ------------------ MODELS ------------------

class StudentCreate(BaseModel):
    name: str
    email: str
    address: str
    number: str
    college_name: str
    city: str
    state: str


class StudentResponse(StudentCreate):
    id: int


# ------------------ ROUTES ------------------

@app.get("/")
def root():
    return {"message": "Student Enrollment REST API is running"}


# CREATE (POST)
@app.post("/students", status_code=201)
def create_student(student: StudentCreate):
    try:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO ens
            (name, email, address, number, college_name, city, state)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student.name,
                student.email,
                student.address,
                student.number,
                student.college_name,
                student.city,
                student.state
            )
        )
        con.commit()
        return {"message": "Student details saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        con.close()


# READ ALL (GET)
@app.get("/students", response_model=list[StudentResponse])
def get_students():
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM ens")
    rows = cur.fetchall()
    con.close()

    return [dict(row) for row in rows]


# READ ONE (GET)
@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM ens WHERE id = ?", (student_id,))
    row = cur.fetchone()
    con.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return dict(row)


# DELETE (DELETE)
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM ens WHERE id = ?", (student_id,))
    con.commit()

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    con.close()
    return {"message": "Student deleted successfully"}


# ------------------ RUN ------------------

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=1234, reload=True)
