import asyncio
from app.models.user import User, UserType, USER_TYPE
from app.models.assignature import Assignature, CurrentAssignatures
from app.models.grade import Status, Toe, TaskSubmission, Tasks
from app.models.student import Student
from app.database.database import Base, engine, AsyncSessionLocal
from datetime import date
from sqlalchemy import select

async def crear_users(db):
    for name, id in USER_TYPE.items():
        result = await db.execute(select(UserType).where(UserType.id == id))
        exists = result.scalars().first()
        if not exists:
            user_type = UserType(id=id, name=name.capitalize())
            db.add(user_type)
    await db.commit()

    users = [
        {"email": "p@m.com", "name": "Juan Pérez", "password": "12341234", "user_type_id": 1},
        {"email": "analopez@gmai.com", "name": "Ana López", "password": "12341234", "user_type_id": 1},
        {"email": "m@m.com", "name": "Carlos García", "password": "12341234", "user_type_id": 2},
        {"email": "mariasmith@gmai.com", "name": "María Smith", "password": "12341234", "user_type_id": 2},
        {"email": "admin@gmail.com", "name": "Administrador", "password": "12341234", "user_type_id": 3}
    ]

    for user_data in users:
        result = await db.execute(select(User).where(User.email == user_data["email"]))
        if not result.scalars().first():
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                user_type_id=user_data["user_type_id"]
            )
            user.set_password(user_data["password"])
            db.add(user)

    await db.commit()

async def create_student(db):
    students_data = [
        {"group": 1, "year": 2025, "active": True, "user_id": 1},
        {"group": 2, "year": 2025, "active": True, "user_id": 2},
        {"group": 3, "year": 2025, "active": True, "user_id": 3},
    ]

    for s_data in students_data:
        result = await db.execute(select(Student).where(Student.user_id == s_data["user_id"]))
        exists = result.scalars().first()
        if not exists:
            student = Student(**s_data)
            db.add(student)

    await db.commit()

async def init_assignatures_to_students(db):
    result = await db.execute(select(Student))
    students = result.scalars().all()
    
    for student in students:
        result = await db.execute(
            select(CurrentAssignatures).where(CurrentAssignatures.student_id == student.id)
        )
        existing = result.scalars().first()
        
        if not existing:
            current_assignatures = CurrentAssignatures(student_id=student.id)
            db.add(current_assignatures)
    
    await db.commit()

async def create_assignatures(db):
    assignatures = [
        {"name": "Electrónica de Potencia", "tag": "E.P."},
        {"name": "Tecnología de Control", "tag": "T.C."},
        {"name": "Tecnología de Energía", "tag": "T.E"},
        {"name": "Control Númerico y Computalizado", "tag": "CNC"}
    ]

    for assignature in assignatures:
        result = await db.execute(select(Assignature).where(Assignature.name == assignature["name"]))
        if not result.scalars().first():
            new_assignature = Assignature(name=assignature["name"], tag=assignature["tag"])
            db.add(new_assignature)
    await db.commit()

async def create_assigments(db):
    assigments = [
        {"description": "Trabajo Práctico N°2", "deadtime": date(2025, 8, 10), "type_of_evaluation": Toe.TP, "assignature_id": 1},
        {"description": "Trabajo Práctico N°4", "deadtime": date(2025, 8, 15), "type_of_evaluation": Toe.TP, "assignature_id": 2}
    ]

    for iter_assig in assigments:
        result = await db.execute(
            select(Tasks).where(
                Tasks.description == iter_assig["description"],
                Tasks.deadtime == iter_assig["deadtime"],
                Tasks.type_of_evaluation == iter_assig["type_of_evaluation"],
                Tasks.assignature_id == iter_assig["assignature_id"]
            )
        )
        exists = result.scalars().first()

        if not exists:
            assigment = Tasks(**iter_assig)
            db.add(assigment)

    await db.commit()

async def create_test_submissions(db):
    result = await db.execute(select(Tasks).where(Tasks.id == 1))
    task1 = result.scalars().first()
    
    result = await db.execute(select(Tasks).where(Tasks.id == 2))
    task2 = result.scalars().first()
    
    result = await db.execute(select(Student).where(Student.id == 1))
    student1 = result.scalars().first()
    
    result = await db.execute(select(Student).where(Student.id == 2))
    student2 = result.scalars().first()
    
    if not all([task1, task2, student1, student2]):
        print("⚠️ Faltan tasks o students. Creá primero las tasks y estudiantes.")
        return
    
    test_submissions = [
        {
            "student_id": student1.id,
            "task_id": task1.id,
            "grade": 6.0,
            "status": Status.PASSED,
            "observation": "Buen trabajo, cumple con los requisitos",
            "submitted_at": date(2025, 10, 15),
            "graded_at": date(2025, 10, 20)
        },
        {
            "student_id": student2.id,
            "task_id": task2.id,
            "grade": 4.0,
            "status": Status.REDO,
            "observation": "Falta profundizar en algunos puntos. Revisar la consigna del ejercicio 3.",
            "submitted_at": date(2025, 10, 16),
            "graded_at": date(2025, 10, 21)
        }
    ]
    
    for submission_data in test_submissions:
        result = await db.execute(
            select(TaskSubmission).where(
                TaskSubmission.student_id == submission_data["student_id"],
                TaskSubmission.task_id == submission_data["task_id"]
            )
        )
        exists = result.scalars().first()
        
        if not exists:
            submission = TaskSubmission(**submission_data)
            db.add(submission)
        else:
            print(f"⚠️ Submission ya existe: student {submission_data['student_id']}, task {submission_data['task_id']}")
    
    await db.commit()
    print("✅ Test submissions creadas")

async def drop_and_create_tables():
    """Borra y recrea todas las tablas"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas recreadas")

async def llenar_base_de_datos():
    try:
        # Primero borrar y recrear tablas
        await drop_and_create_tables()
        
        # Luego llenar con datos
        async with AsyncSessionLocal() as db:
            await crear_users(db)
            await create_assignatures(db)
            await create_assigments(db)
            await create_student(db)
            await create_test_submissions(db)
            await init_assignatures_to_students(db)
            print("✅ Base de datos de prueba completada")
    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cerrar el engine para que el script termine
        await engine.dispose()

# Ejecutar el script
if __name__ == "__main__":
    asyncio.run(llenar_base_de_datos())
