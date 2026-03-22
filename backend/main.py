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
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    credits REAL DEFAULT 0.0
    )
    """)
    
    # Simple migration: Add columns if they don't exist
    columns = [
        ("phone", "TEXT"),
        ("address", "TEXT"),
        ("city", "TEXT"),
        ("state", "TEXT"),
        ("pincode", "TEXT"),
        ("eco_points", "INTEGER DEFAULT 0"),
        ("co2_saved", "REAL DEFAULT 0.0"),
        ("landmark", "TEXT"),
        ("live_location", "TEXT"),
        ("credits", "REAL DEFAULT 0.0")
    ]
    
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    
    for col_name, col_type in columns:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass

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
    
    # Simple migration for new tracking columns
    cursor.execute("PRAGMA table_info(pickups)")
    p_cols = [row[1] for row in cursor.fetchall()]
    if "admin_id" not in p_cols:
        cursor.execute("ALTER TABLE pickups ADD COLUMN admin_id INTEGER")
    if "scrap_id" not in p_cols:
        cursor.execute("ALTER TABLE pickups ADD COLUMN scrap_id INTEGER")
        
    cursor.execute("PRAGMA table_info(scrap)")
    s_cols = [row[1] for row in cursor.fetchall()]
    if "buyer_id" not in s_cols:
        cursor.execute("ALTER TABLE scrap ADD COLUMN buyer_id INTEGER")

    
    conn.commit()
    conn.close()

init_db()

otp_store: Dict[Any, Any] = {}

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
        user.address, user.city, user.state, user.pincode, user.role, user.landmark, user.live_location))
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
    # Join with users to get address for mapping
    cursor.execute("""
        SELECT s.id, s.image, s.type, s.price, s.status, u.address, u.city 
        FROM scrap s
        JOIN users u ON s.seller_id = u.id
        WHERE s.status IN ('available', 'bidded')
    """)
    data = cursor.fetchall()
    conn.close()
    return [dict(row) for row in data]

class Bid(BaseModel):
    scrap_id: int
    amount: float
    admin_id: int

@app.post("/marketplace/bid")
def place_bid(bid: Bid):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE scrap SET price=?, status='bidded', buyer_id=? WHERE id=?", (bid.amount, bid.admin_id, bid.scrap_id))
    conn.commit()
    conn.close()
    return {"message": f"Quote of â‚¹{bid.amount} placed successfully"}

class Approve(BaseModel):
    scrap_id: int

@app.post("/marketplace/approve")
def approve_bid(approve: Approve):
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Update scrap status
    cursor.execute("UPDATE scrap SET status='sold' WHERE id=?", (approve.scrap_id,))
    
    # 2. Add to pickups queue for routing
    cursor.execute("""
        INSERT INTO pickups (user_id, scrap_type, address, status, lat, lon, admin_id, scrap_id)
        SELECT s.seller_id, s.type, u.address, 'Pending', 0.0, 0.0, s.buyer_id, s.id
        FROM scrap s
        JOIN users u ON s.seller_id = u.id
        WHERE s.id = ?
    """, (approve.scrap_id,))
    
    # 3. Add Pandas CO2 impact
    cursor.execute("UPDATE users SET co2_saved = co2_saved + 2.5 WHERE id = (SELECT seller_id FROM scrap WHERE id=?)", (approve.scrap_id,))
    
    # 4. Add scrap price to user credits
    cursor.execute("SELECT seller_id, price FROM scrap WHERE id=?", (approve.scrap_id,))
    scrap_data = cursor.fetchone()
    if scrap_data:
        cursor.execute("UPDATE users SET credits = credits + ? WHERE id=?", (scrap_data['price'], scrap_data['seller_id']))
    
    conn.commit()
    conn.close()
    return {"message": "Quote accepted! Collector is routed."}

class Decline(BaseModel):
    scrap_id: int

@app.post("/marketplace/decline")
def decline_bid(decline: Decline):
    conn = get_db()
    cursor = conn.cursor()
    # Reset scrap to available so admin can rebid with a higher offer
    cursor.execute(
        "UPDATE scrap SET status='available', price=0.0, buyer_id=NULL WHERE id=?",
        (decline.scrap_id,)
    )
    conn.commit()
    conn.close()
    return {"message": "Quote declined. The item is back in the marketplace for a new offer."}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, eco_points, co2_saved, credits FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        # Add unlocked badges dynamically
        user_dict = dict(user)
        user_dict['has_guardian_badge'] = bool(user_dict['eco_points'] >= 100)
        return user_dict
    raise HTTPException(status_code=404, detail="User not found")
    
@app.post("/users/{user_id}/convert-points")
def convert_points(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT eco_points FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    if user['eco_points'] < 100:
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient Eco Points. Need at least 100.")
    
    # 100 points = 1 credit
    cursor.execute("UPDATE users SET eco_points = eco_points - 100, credits = credits + 1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "100 Eco Points converted to 1 Credit!"}

@app.get("/users/{user_id}/history")
def get_user_history(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, 
               u2.name as admin_name, u2.phone as admin_phone, 
               p.status as pickup_status 
        FROM scrap s 
        
        LEFT JOIN users u2 ON s.buyer_id = u2.id 
        LEFT JOIN pickups p ON s.id = p.scrap_id
        WHERE s.seller_id=? ORDER BY s.id DESC
    """, (user_id,))
    data = cursor.fetchall()
    conn.close()
    return [dict(row) for row in data]

@app.get("/admin/history")
def get_admin_history():
    conn = get_db()
    cursor = conn.cursor()
    # Simple mockup assuming admins see all bookings for this hackathon
    cursor.execute("SELECT * FROM pickups ORDER BY id DESC")
    pickups = cursor.fetchall()
    
    # Calculate total expenditure based on scrap price (assuming completed)
    cursor.execute("SELECT SUM(price) as total_spent FROM scrap WHERE status='sold'")
    spent = cursor.fetchone()
    total_spent = spent['total_spent'] if spent['total_spent'] else 0.0
    
    conn.close()
    return {
        "orders_taken_today": len(pickups),
        "total_spent": total_spent,
        "recent_pickups": [dict(row) for row in pickups]
    }

@app.get("/ecommerce/products")
def get_ecommerce_products():
    products = [
        {"id": 1, "name": "Eco-Friendly Bamboo Notebook", "price": 149.0, "image": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=500&q=80", "description": "Made from 100% recycled paper and sustainable bamboo cover.", "rating": 4.8, "reviews": 124},
        {"id": 2, "name": "Recycled Plastic Plant Pot", "price": 299.0, "image": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=500&q=80", "description": "Durable and aesthetic pots made from ocean-bound plastics.", "rating": 4.6, "reviews": 89},
        {"id": 3, "name": "Upcycled Denim Tote Bag", "price": 499.0, "image": "https://images.unsplash.com/photo-1584916201218-f4242ceb4809?w=500&q=80", "description": "Stylish tote bag created from upcycled denim jeans.", "rating": 4.9, "reviews": 210},
        {"id": 4, "name": "Recycled Glass Water Bottle", "price": 399.0, "image": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500&q=80", "description": "Sleek water bottle made from 100% recycled glass.", "rating": 4.7, "reviews": 156},
        {"id": 5, "name": "Reclaimed Wood Desk Organizer", "price": 899.0, "image": "https://images.unsplash.com/photo-1592656094267-764a45160876?w=500&q=80", "description": "Keep your desk tidy with this rustic reclaimed wood organizer.", "rating": 4.5, "reviews": 67},
        {"id": 6, "name": "Eco-friendly Toothbrush Set", "price": 199.0, "image": "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=500&q=80", "description": "Bamboo toothbrushes with biodegradable bristles.", "rating": 4.8, "reviews": 342}
    ]
    return products

try:
    from route_optimizer import optimize_routes
except ImportError:
    def optimize_routes(locations):
        return locations

@app.get("/routes", response_model=List[Dict[str, Any]])
def get_routes() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, u.address, u.landmark, u.city, u.pincode, u.phone, p.lat, p.lon, p.scrap_type, p.status 
        FROM pickups p
        JOIN users u ON p.user_id = u.id
        WHERE p.status='Pending'
    """)
    data: List[Dict[str, Any]] = []
    for row in cursor.fetchall():
        d = {
            "id": row["id"],
            "address": f"{row['address']} {row['landmark'] if row['landmark'] else ''}, {row['city']} - {row['pincode']} (Ph: {row['phone']})",
            "lat": float(row["lat"]) if row["lat"] else 0.0,
            "lon": float(row["lon"]) if row["lon"] else 0.0,
            "scrap_type": row["scrap_type"],
            "status": row["status"]
        }
        data.append(d)
    conn.close()
    
    import random
    for loc in data:
        if loc['lat'] == 0.0 and loc['lon'] == 0.0:
            loc['lat'] = 18.5204 + random.uniform(-0.05, 0.05)
            loc['lon'] = 73.8567 + random.uniform(-0.05, 0.05)
            
    return optimize_routes(data)

try:
    from ai_model import classify
except ImportError:
    def classify(path):
        return random.choice(["Plastic", "Metal", "Paper", "E-Waste"])

@app.post("/upload_scrap")
async def upload_scrap(file: UploadFile = File(...), seller_id: int = 1):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
        
    path = f"uploads/{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    scrap_type = classify(path)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Simple award 10 points
    cursor.execute("UPDATE users SET eco_points = eco_points + 10 WHERE id=?", (seller_id,))
    
    cursor.execute("""
    INSERT INTO scrap(seller_id,image,type,price,status)
    VALUES(?,?,?,?,?)
    """, (seller_id, path, scrap_type, 0.0, "available"))
    
    conn.commit()
    conn.close()

    return {"type": scrap_type, "message": "Scrap uploaded and classified! You earned 10 Eco Points."}
