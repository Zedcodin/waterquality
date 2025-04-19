from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import aiohttp
import asyncio
from datetime import datetime
import uvicorn

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE = "water_quality.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS readings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  turbidity REAL,
                  temperature REAL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# ESP32 configuration
ESP32_URL = "http://192.168.4.1/data"

async def fetch_esp32_data():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(ESP32_URL, timeout=2) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "turbidity": data.get("turbidity"),
                        "temperature": data.get("temperature")
                    }
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

async def collect_data_periodically():
    init_db()
    while True:
        sensor_data = await fetch_esp32_data()
        if sensor_data is not None:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute(
                "INSERT INTO readings (turbidity, temperature) VALUES (?, ?)",
                (sensor_data["turbidity"], sensor_data["temperature"])
            )
            conn.commit()
            conn.close()
            print(f"Stored data: {sensor_data} at {datetime.now()}")
        await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(collect_data_periodically())
    
@app.get("/test")
def test():
    return {1}

@app.get("/api/readings")
def get_readings(limit: int = 100):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM readings ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    
    return {
        "data": [
            {
                "id": row[0],
                "turbidity": row[1],
                "temperature": row[2],
                "timestamp": row[3]
            } for row in rows
        ]
    }

@app.get("/api/latest")
def get_latest():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "turbidity": row[1],
            "temperature": row[2],
            "timestamp": row[3]
        }
    raise HTTPException(status_code=404, detail="No data available")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)