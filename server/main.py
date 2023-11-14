from fastapi import FastAPI, Request, Depends, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlite3 import Connection, Row, connect
from typing import Generator

app = FastAPI()

templates = Jinja2Templates(directory="templates")

SQLALCHEMY_DATABASE_URL = "C:/Users/Leila/Desktop/NorbertFenk/phase1/database/nl.db"

class Database:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self._conn = None

    def connect(self) -> Connection:
        if not self._conn or not self._conn.in_transaction:
            self._conn = connect(self.db_url, check_same_thread=False)
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()

db_instance = Database(SQLALCHEMY_DATABASE_URL)

def get_db() -> Generator[Connection, None, None]:
    try:
        db = db_instance.connect()
        yield db
    finally:
        db_instance.close()

# CRUD
@app.get("/")
async def root(request: Request, db: Connection = Depends(get_db), accept: str = Header(default='text/html')):
    if "text/html" in accept:
        welcome_text = "Welcome to my recipe app! Enjoy your meal."
    
        cursor = db.execute("SELECT * FROM recipt")
        recipes = cursor.fetchall()

        recipes_data = [{"title": recipe[1], "ingred": recipe[2], "quantity": recipe[3], "mesure": recipe[4], "description": recipe[5]} for recipe in recipes]

        #print("Recipes Data:", recipes_data)
        return templates.TemplateResponse(
            "index.html", {"request": request, "welcome_text": welcome_text, "recipes": recipes_data}
        )
    else:
        return {"Welcome to my recipe app! Enjoy your meal."}

@app.post("/recipt/")
async def create_item(title: str = None, ingred: str = None, quantity: int = None, mesure: str = None, description: str = None, db: Connection = Depends(get_db)):
    cursor = db.execute("INSERT INTO recipt (title, ingred, quantity, mesure, description) VALUES (?, ?, ?, ?, ?)", (title, ingred, quantity, mesure, description))
    db.commit()
    return {"title": title, "ingred": ingred, "quantity": quantity, "mesure": mesure, "description": description}

@app.delete("/recipt/{recipt_id}")
async def delete_item(recipt_id: int, db: Connection = Depends(get_db)):
    cursor = db.execute("DELETE FROM recipt WHERE id=?", (recipt_id,))
    db.commit()
    return {"deleted"}
