from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from ariadne import QueryType, MutationType, make_executable_schema, gql
from ariadne.asgi import GraphQL
import uvicorn
from fastapi.staticfiles import StaticFiles
import sqlite3

# Initialize FastAPI app
app = FastAPI()

# Define database file and schema
db_file = 'todos.db'

create_table_sql = '''
CREATE TABLE IF NOT EXISTS todolist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    done BOOLEAN NOT NULL
);
'''

def init_db():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()

def fetch_todos():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, done FROM todolist")
        return cursor.fetchall()

def insert_todo(task):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO todolist (task, done) VALUES (?, ?)", (task, False))
        conn.commit()
        return cursor.lastrowid

def update_todo(id, task=None, done=None):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        if task is not None:
            cursor.execute("UPDATE todolist SET task = ? WHERE id = ?", (task, id))
        if done is not None:
            cursor.execute("UPDATE todolist SET done = ? WHERE id = ?", (done, id))
        conn.commit()

def delete_todo(id):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todolist WHERE id = ?", (id,))
        conn.commit()
        return cursor.rowcount > 0

# Define GraphQL schema
type_defs = gql("""
type Todo {
    id: ID!
    task: String!
    done: Boolean!
}

type Query {
    todos: [Todo]
    todo(id: ID!): Todo
}

type Mutation {
    addTodo(task: String!): Todo
    updateTodo(id: ID!, task: String, done: Boolean): Todo
    deleteTodo(id: ID!): Boolean
}
""")

query = QueryType()
mutation = MutationType()

@query.field("todos")
def resolve_todos(*_):
    todos = fetch_todos()
    return [{"id": row[0], "task": row[1], "done": row[2]} for row in todos]

@query.field("todo")
def resolve_todo(_, info, id):
    todos = fetch_todos()
    todo = next(({"id": row[0], "task": row[1], "done": row[2]} for row in todos if row[0] == int(id)), None)
    return todo

@mutation.field("addTodo")
def resolve_add_todo(_, info, task):
    id = insert_todo(task)
    todo = {"id": id, "task": task, "done": False}
    return todo

@mutation.field("updateTodo")
def resolve_update_todo(_, info, id, task=None, done=None):
    todo = resolve_todo(_, info, id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    update_todo(id, task, done)
    todo.update({"task": task if task else todo["task"], "done": done if done is not None else todo["done"]})
    return todo

@mutation.field("deleteTodo")
def resolve_delete_todo(_, info, id):
    deleted = delete_todo(id)
    return deleted

# Create schema
schema = make_executable_schema(type_defs, query, mutation)

# Initialize database
init_db()

app.add_route("/graphql", GraphQL(schema, debug=True))


# Add Static Files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Add GraphQL route
#app.add_route("/graphql", GraphQL(schema, debug=True))

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Automatically start the server when the script is run
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
