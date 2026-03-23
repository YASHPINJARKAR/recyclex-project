from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import random
import shutil
import os
from typing import List, Dict, Any
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# ✅ STATIC FILES
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ✅ CORS (PRODUCTION FIX)
origins = [
    "https://recyclex-frontend.onrender.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # only allow your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ DATABASE
def get_db():
    conn = sqlite3.connect("recyclex.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    pincode TEXT,
    role TEXT,
    eco_points INTEGER DEFAULT 0,
    co2_saved REAL DEFAULT 0.0,
    credits REAL DEFAULT 0.0,
    landmark TEXT,
    live_location TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pickups(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    scrap_type TEXT,
    address TEXT,
    status TEXT,
    lat REAL,
    lon REAL,
    admin_id INTEGER,
    scrap_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scrap(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER,
    image TEXT,
    type TEXT,
    price REAL,
    status TEXT,
    buyer_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ✅ MODELS
class Register(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    address: str
    city: str
    state: str
    pincode: str
    role: str
    landmark: str = ""
    live_location: str = ""

class Login(BaseModel):
    email: str
    password: str

class Pickup(BaseModel):
    user_id: int
    scrap_type: str
    address: str

# ✅ ROUTES

@app.post("/register")
def register(user: Register):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO users
        (name,email,password,phone,address,city,state,pincode,role,landmark,live_location)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)
        """,
        (user.name, user.email, user.password, user.phone,
         user.address, user.city, user.state, user.pincode,
         user.role, user.landmark, user.live_location))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        conn.close()

    return {"message": "Registration successful"}

@app.post("/login")
def login(data: Login):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email, role, eco_points, co2_saved, credits FROM users WHERE email=? AND password=?",
        (data.email, data.password)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "message": "Login Success",
            "user": dict(user)
        }

    raise HTTPException(status_code=400, detail="Invalid Credentials")

@app.post("/book")
def book_pickup(pickup: Pickup):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO pickups(user_id,scrap_type,address,status,lat,lon) VALUES(?,?,?,?,?,?)",
        (pickup.user_id, pickup.scrap_type, pickup.address, "Pending", 0.0, 0.0)
    )

    conn.commit()
    conn.close()
    return {"message": "Pickup Booked"}

@app.get("/pickups")
def get_pickups():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pickups")
    data = cursor.fetchall()

    conn.close()
    return [dict(row) for row in data]

@app.get("/marketplace")
def get_marketplace():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.image, s.type, s.price, s.status, u.address, u.city 
        FROM scrap s
        JOIN users u ON s.seller_id = u.id
        WHERE s.status IN ('available', 'bidded')
    """)

    data = cursor.fetchall()
    conn.close()
    return [dict(row) for row in data]

@app.post("/upload_scrap")
async def upload_scrap(file: UploadFile = File(...), seller_id: int = 1):
    path = f"uploads/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    scrap_type = random.choice(["Plastic", "Metal", "Paper", "E-Waste"])

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET eco_points = eco_points + 10 WHERE id=?", (seller_id,))

    cursor.execute("""
    INSERT INTO scrap(seller_id,image,type,price,status)
    VALUES(?,?,?,?,?)
    """, (seller_id, path, scrap_type, 0.0, "available"))

    conn.commit()
    conn.close()

    return {"type": scrap_type, "message": "Scrap uploaded successfully!"}