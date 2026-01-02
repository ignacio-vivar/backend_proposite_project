from app.models.user import User, UserType, USER_TYPE
from app.models.assignature import Assignature, CurrentAssignatures
from app.models.grade import  Status, Toe, TaskSubmission, Tasks
from app.models.student import Student
from app.database.database import Base, engine, SessionLocal
from random import choice, randint
from datetime import datetime, timedelta, timezone, date
from app.core.security import hash_password
from zoneinfo import ZoneInfo

# Crear una sesión para interactuar con la base de datos
db = SessionLocal()

# Borra todas las tablas
Base.metadata.drop_all(bind=engine)

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)
# Función para insertar médicos con sus specialties

def crear_users(db):
    for name, id in USER_TYPE.items():
        exists = db.query(UserType).filter(UserType.id == id).first()
        if not exists:
            user_type = UserType(id=id, name=name.capitalize()) 
            db.add(user_type)
    db.commit()

    users = [
        {"email": "p@m.com", "name": "Juan Pérez", "password": "12341234", "user_type_id": 1},
        {"email": "analopez@gmai.com", "name": "Ana López", "password": "12341234", "user_type_id": 1},
        {"email": "m@m.com", "name": "Carlos García", "password": "12341234", "user_type_id": 2},
        {"email": "mariasmith@gmai.com", "name": "María Smith", "password": "12341234", "user_type_id": 2},
        {"email": "admin@gmail.com", "name": "Administrador", "password": "12341234", "user_type_id": 3}
    ]

    for user_data in users:
        if not db.query(User).filter(User.email == user_data["email"]).first():
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                user_type_id=user_data["user_type_id"]
            )
            user.set_password(user_data["password"])
            db.add(user)

    db.commit()

def create_student(db):
    students_data = [
        {"group" : 1, "year" : 2025, "active": True, "user_id" : 1},
        {"group" : 2, "year" : 2025, "active": True, "user_id" : 2},
        {"group" : 3, "year" : 2025, "active": True, "user_id" : 3},
    ]

    for s_data in students_data:
        exists = db.query(Student).filter(Student.user_id == s_data["user_id"]).first()
        if not exists:
            student = Student(**s_data)
            db.add(student)

    db.commit()

def init_assignatures_to_students(db):
    students = db.query(Student).all()
    for student in students:
        # Verificar si ya tiene CurrentAssignatures
        existing = db.query(CurrentAssignatures).filter(
            CurrentAssignatures.student_id == student.id
        ).first()
        
        if not existing:
            # Crear relación vacía
            current_assignatures = CurrentAssignatures(student_id=student.id)
            db.add(current_assignatures)
    
    db.commit()
    
# Función para insertar asignatures 

def create_assignatures(db):
    assignatures = [{"name": "Electrónica de Potencia", "tag": "E.P."},
                    {"name": "Tecnología de Control", "tag" : "T.C."},
                    {"name" : "Tecnología de Energía", "tag" : "T.E"},
                    {"name" : "Control Númerico y Computalizado", "tag" : "CNC"}]

    for assignature in assignatures:
        if not db.query(Assignature).filter(Assignature.name == assignature["name"]).first():
            assignature = Assignature(name=assignature["name"], tag=assignature["tag"])
            db.add(assignature)
    db.commit()

# Función para agregar asignatures
def create_assigments(db):
    
    assigments = [{"description": "Trabajo Práctico N°2", "deadtime":date(2025,8,10), "type_of_evaluation": Toe.TP, "assignature_id" : 1},
                {"description": "Trabajo Práctico N°4", "deadtime":date(2025,8,15), "type_of_evaluation": Toe.TP, "assignature_id" : 2}]

    for iter_assig in assigments:
        exists = db.query(Tasks).filter_by(
            description=iter_assig["description"],
            deadtime=iter_assig["deadtime"],
            type_of_evaluation=iter_assig["type_of_evaluation"],
            assignature_id=iter_assig["assignature_id"]
        ).first()

        if not exists:
            assigment = Tasks(**iter_assig)
            db.add(assigment)

    db.commit()

def create_test_submissions(db):
    """
    Crea submissions de prueba para testing
    """
    # Primero asegurarte que existan tasks y students
    task1 = db.query(Tasks).filter(Tasks.id == 1).first()
    task2 = db.query(Tasks).filter(Tasks.id == 2).first()
    student1 = db.query(Student).filter(Student.id == 1).first()
    student2 = db.query(Student).filter(Student.id == 2).first()
    
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
        # Verificar que no exista
        exists = db.query(TaskSubmission).filter(
            TaskSubmission.student_id == submission_data["student_id"],
            TaskSubmission.task_id == submission_data["task_id"]
        ).first()
        
        if not exists:
            submission = TaskSubmission(**submission_data)
            db.add(submission)
        else:
            print(f"⚠️ Submission ya existe: student {submission_data['student_id']}, task {submission_data['task_id']}")
    
    db.commit()
    print("✅ Test submissions creadas")
# Función para llenar la base de datos con datos de prueba
def llenar_base_de_datos():
    try:
        crear_users(db)
        create_assignatures(db)
        create_assigments(db)
        create_student(db)
        create_test_submissions(db)
        init_assignatures_to_students(db)
        print("Base de datos de prueba completada")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    finally:
        db.close()

# Ejecutar el script
if __name__ == "__main__":
    llenar_base_de_datos()
    
