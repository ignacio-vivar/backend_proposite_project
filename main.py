import uvicorn 
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users,auth
from app.routers.assignatures.admin import admin_router as assig_adm_r
from app.routers.assignatures.student import student_router as assig_st_r
from app.routers.grades.admin import admin_router as grades_adm_r
from app.routers.grades.student import student_router as grades_st_r
from app.routers.students.admin import admin_router as adm_student
from fastapi.responses import RedirectResponse #Remove only testing

from sqlalchemy.orm import Session

from app.database.database import get_db

app = FastAPI(debug=False)

app.include_router(auth.router, tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(users.router_develop)
app.include_router(users.admin_router)
app.include_router(assig_adm_r)
app.include_router(assig_st_r)
app.include_router(grades_adm_r)
app.include_router(grades_st_r)
app.include_router(adm_student)

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs#")


if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)
