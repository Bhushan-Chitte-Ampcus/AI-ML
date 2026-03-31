from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="To DO Services")

class Todo(BaseModel):
    title: str

todos = []
    
@app.post("/todo")
def create_todo(todo: Todo):
    new_todo = {
        "id": len(todos) + 1,
        "title": todo.title,
        "done": False,
        "created_at": datetime.now()
        }
    
    todos.append(new_todo)
    return new_todo

@app.get("/todo")
def get_todo_details():
    return todos

@app.get("/todo/{todo_id}")
def get_todo(todo_id: int):
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    return {"error": "details not found"}

@app.patch("/todo/{todo_id}")
def mark_todo(todo_id: int):
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = True
            return todo
    return {"error": "todo not found"}

@app.delete("/todo/{todo_id}")
def delete_todo(todo_id: int):
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            return todos.pop(i)
    return {"error": "todo not found"}