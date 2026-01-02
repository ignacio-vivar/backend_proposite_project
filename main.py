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

#Remove only testing
@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url="/docs#")

@app.get("/test-db")
async def test_database():
    try:
        from app.database.database import SessionLocal
        from app.models.user import User
        
        db = SessionLocal()
        user_count = db.query(User).count()
        db.close()
        
        return {
            "status": "✅ Conexión exitosa",
            "user_count": user_count,
            "database_url": "Connected to PostgreSQL"
        }
    except Exception as e:
        return {
            "status": "❌ Error",
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)
