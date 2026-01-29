from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title='To-Do')

# ===== Модель =====
class Item(BaseModel):
    title: str
    description: str
    completed: bool = False

conn = sqlite3.connect("todo.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        completed INTEGER DEFAULT 0
    )
""")
conn.commit()

@app.post("/items")
def create_item(item: Item):
    cur.execute(
        "INSERT INTO items (title, description, completed) VALUES (?, ?, ?)",
        (item.title, item.description, int(item.completed))
    )
    conn.commit()

    item_id = cur.lastrowid
    return {"id": item_id, "item": item}

@app.get("/items")
def get_all_items():
    cur.execute("SELECT id, title, description, completed FROM items")
    rows = cur.fetchall()

    items = {
        row[0]: {
            "title": row[1],
            "description": row[2],
            "completed": bool(row[3])
        }
        for row in rows
    }

    return {"items": items}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    cur.execute(
        "SELECT title, description, completed FROM items WHERE id = ?",
        (item_id,)
    )
    row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return {
        "id": item_id,
        "title": row[0],
        "description": row[1],
        "completed": bool(row[2])
    }

@app.put("/items/{item_id}")
def update_item(item_id: int, updated_item: Item):
    cur.execute("SELECT 1 FROM items WHERE id = ?", (item_id,))
    if cur.fetchone() is None:
        raise HTTPException(status_code=404, detail="Item for update not found")

    cur.execute(
        """
        UPDATE items
        SET title = ?, description = ?, completed = ?
        WHERE id = ?
        """,
        (updated_item.title, updated_item.description,
         int(updated_item.completed), item_id)
    )
    conn.commit()

    return {"id": item_id, "item": updated_item}

# ===== DELETE /items/{id} — удаление =====
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    cur.execute("SELECT 1 FROM items WHERE id = ?", (item_id,))
    if cur.fetchone() is None:
        raise HTTPException(status_code=404, detail="Item for delete not found")

    cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()

    return {"id": item_id, "status": "deleted"}
