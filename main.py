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
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
    "http://localhost:5173",
    "https://proposite-project-admin-frontend.vercel.app/"
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

@app.get("/test-users")
async def test_users(db: AsyncSession = Depends(get_db)):
    try:
        from app.models.user import User

        result = await db.execute(select(User))
        users = result.scalars().all()

        return {
            "status": "✅ OK",
            "user_count": len(users),
            "users": [{"email": u.email, "name": u.name} for u in users],
        }
    except Exception as e:
        return {
            "status": "❌ Error",
            "error": str(e),
        }


@app.get("/test-login-debug")
async def test_login_debug(db: Session = Depends(get_db)):
    try:
        from app.models.user import User
        user = db.query(User).filter(User.email == "p@m.com").first()
        
        if not user:
            return {"error": "User not found"}
        
        # Intentar verificar password
        password_ok = user.check_password("12341234")
        
        return {
            "user_exists": True,
            "has_password_hash": bool(user.password_hash),
            "password_check": password_ok
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000)
