from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    status: str

tasks=[
    Task(id=1,title="Prepare report",status="Pending"),
    Task(id=2,title="Review invoice",status="Completed"),
    Task(id=3,title="Update dashboard",status="Pending"),
]

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{id}")
def get_task(id:int):
    for it in tasks:
        if it.id==id:
            return it
# #changing this line
#             return {"id":1001,"title":it.title,"status":it.status}
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks")
def add_task(task:Task):
    tasks.append(task)
    return {
        "message": "Task added",
        "task": task
    }

@app.put("/tasks/{id}")
def update_task(id:int,updated_task:Task):
    for index,task in enumerate(tasks):
        if task.id==id:
            tasks[index]=updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{id}")
def delete_task(id:int):
    for index,task in enumerate(tasks):
        if task.id==id:
            deleted=tasks.pop(index)
            return {
                "message": "Task deleted",
                "task":task
            }
    raise HTTPException(status_code=404, detail="Task not found")


# {
#         "id":1,
#         "title":"Prepare report",
#         "status":"Pending"
# }
# {
#         "id":2,
#         "title":"Review invoice",
#         "status":"Completed"
#     },
#     {
#         "id":3,
#         "title":"Update dashboard",
#         "status":"Pending"
#     }