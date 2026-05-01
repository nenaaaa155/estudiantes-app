from fastapi import FastAPI, HTTPException
from database import Base, engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from models import User, Student
import random
import time

app = FastAPI()

# CORS (para frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# -------------------------
# FUNCION GENERAR OTP
# -------------------------
def generate_otp():
    return str(random.randint(100000, 999999))

# -------------------------
# ENVIAR OTP
# -------------------------
@app.post("/auth/send-otp")
def send_otp(email: str):
    db = SessionLocal()
    try:
        otp = generate_otp()
        current_time = int(time.time())

        user = db.query(User).filter(User.email == email).first()

        if not user:
            user = User(email=email, otp=otp, otp_created_at=current_time)
            db.add(user)
        else:
            user.otp = otp
            user.otp_created_at = current_time

        db.commit()

        print("OTP:", otp)  # 🔥 para pruebas

        return {"message": "OTP enviado"}

    finally:
        db.close()

# -------------------------
# VERIFICAR OTP
# -------------------------
@app.post("/auth/verify-otp")
def verify_otp(email: str, otp: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        current_time = int(time.time())

        if user.otp != otp:
            raise HTTPException(status_code=400, detail="OTP incorrecto")

        if current_time - user.otp_created_at > 300:
            raise HTTPException(status_code=400, detail="OTP expirado")

        return {"message": "Login exitoso"}

    finally:
        db.close()

# -------------------------
# CRUD ESTUDIANTES
# -------------------------

# Obtener todos
@app.get("/students")
def get_students():
    db = SessionLocal()
    try:
        return db.query(Student).all()
    finally:
        db.close()

# Crear estudiante
@app.post("/students")
def create_student(name: str, age: int, grade: int):
    if age <= 0 or grade <= 0:
        raise HTTPException(status_code=400, detail="Datos inválidos")

    db = SessionLocal()
    try:
        student = Student(name=name, age=age, grade=grade)
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    finally:
        db.close()

# Actualizar estudiante
@app.put("/students/{id}")
def update_student(id: int, name: str, age: int, grade: int):
    db = SessionLocal()
    try:
        student = db.get(Student, id)

        if not student:
            raise HTTPException(status_code=404, detail="No encontrado")

        student.name = name
        student.age = age
        student.grade = grade

        db.commit()
        db.refresh(student)

        return student
    finally:
        db.close()

# Eliminar estudiante
@app.delete("/students/{id}")
def delete_student(id: int):
    db = SessionLocal()
    try:
        student = db.get(Student, id)

        if not student:
            raise HTTPException(status_code=404, detail="No encontrado")

        db.delete(student)
        db.commit()

        return {"message": "Eliminado"}
    finally:
        db.close()