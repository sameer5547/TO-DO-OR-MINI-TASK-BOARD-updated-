from flask import Flask, render_template, request, redirect,flash
from storage import load_tasks, save_tasks
from datetime import datetime
VALID_PRIORITY={"low","medium","high"}
VALID_STATUS={"to do","in progress","completed"}

app = Flask(__name__)
app.secret_key="todo-list-secret-key"


@app.route("/")
def home():
    tasks = load_tasks()

    total = len(tasks)

    todo = sum(1 for task in tasks
           if str(task.get("status", "")).strip().lower() == "to do")

    in_progress = sum(1 for task in tasks
           if str(task.get("status", "")).strip().lower() == "in progress")

    completed = sum(1 for task in tasks
    if str(task.get("status", "")).strip().lower() == "completed")

    return render_template(

        "dashboard.html",
        tasks=tasks,
        total=total,
        todo=todo,
        in_progress=in_progress,
        completed=completed
    )
    


@app.route("/tasks/new")
def create_task():
    return render_template("create_task.html")


@app.route("/tasks")
def view_tasks():
    tasks = load_tasks()
    total_tasks=len(tasks)
    task_titles=sorted({task["title"]for task in tasks})

    query = request.args.get("q", "").strip().lower()
    status=request.args.get("status","")
    priority=request.args.get("priority","")
    sort=request.args.get("sort","")
    
    if query:
        tasks =[
            task for task in tasks
            if query in task["title"].lower()
        ]
    if status:
        tasks = [task for task in tasks
        if str(task.get("status", "")).strip().lower() == status.strip().lower()
    ]

    if priority:
        tasks = [task for task in tasks
        if str(task.get("priority", "")).strip().lower() == priority.strip().lower()
    ]
    if sort=="due_date":
        tasks=sorted(
            tasks,
            key=lambda task:(
                 task.get("due_date")is None,
                 task.get("due_date") or"9999-12-31"
            )
        )
    
        

    return render_template(
        "task.html",
        tasks=tasks,
        query=query,
        status=status,
        priority=priority,
        sort=sort,
        total_tasks=total_tasks,
        task_titles=task_titles
    )



@app.route("/tasks", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority").strip().lower()
    due_date = request.form.get("due_date","").strip()
    status = request.form.get("status").strip().lower()

    if not title:
        return "Title is required", 400
    if priority not in VALID_PRIORITY:
        return"invalid priority",400
    if status not in VALID_STATUS:
        return"invalid status",400
    if due_date:
        try:
            datetime.strptime(due_date,"%Y-%m-%d")
        except ValueError:
            return"invalid date",400
    

    tasks = load_tasks()

    new_task = {
    "id": max((int(task["id"]) for task in tasks), default=0) + 1,
    "title": title,
    "description": description,
    "priority": priority.title(),
    "due_date": due_date,
    "status": status.title(),
    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}
        
    tasks.append(new_task)
    save_tasks(tasks)
    flash("task created successfully!","success")

    return redirect("/")


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    tasks = load_tasks()

    task = next(
        (task for task in tasks if str(task["id"]) == str(task_id)),
        None
    )

    if task is None:
        return "Task not found", 404

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "").strip().lower()
        due_date = request.form.get("due_date", "").strip()
        status = request.form.get("status", "").strip().lower()

        # Validate title
        if not title:
            return "Title is required", 400

        # Validate priority
        if priority not in VALID_PRIORITY:
            return "Invalid priority", 400

        # Validate status
        if status not in VALID_STATUS:
            return "Invalid status", 400

        # Validate date
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                return "Invalid date", 400

        # Update task
        task["title"] = title
        task["description"] = description
        task["priority"] = priority
        task["due_date"] = due_date
        task["status"] = status

        save_tasks(tasks)
        flash("task edited successfully!","success")

        return redirect("/tasks")

    return render_template("edit_task.html", task=task)

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    tasks = load_tasks()

    task_found = False
    updated_tasks = []

    for task in tasks:
        if int(task["id"]) == task_id:
            task_found = True
        else:
            updated_tasks.append(task)

    if not task_found:
        return "Task not found", 404

    save_tasks(updated_tasks)

    flash("your task has been deleted sucessfully!","success")

    return redirect("/tasks")

if __name__ == "__main__":
    app.run(debug=True)
     
