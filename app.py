import os
import pymysql
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_db():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/")
def home():
    return jsonify({"message": "Student CRUD API is running!"})

@app.route("/dbtest")
def dbtest():
    try:
        conn = get_db()
        conn.close()
        return jsonify({"status": "DB connected successfully!"})
    except Exception as e:
        return jsonify({"status": "DB FAILED", "error": str(e)}), 500

# ── CREATE ───────────────────────────────────────────────
@app.route("/api/students", methods=["POST"])
def create_student():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    errors = []
    if not data.get("name") or len(data["name"].strip()) < 2:
        errors.append("Name must be at least 2 characters.")
    if not data.get("email") or "@" not in data["email"]:
        errors.append("A valid email is required.")
    if not str(data.get("age", "")).isdigit() or not (1 <= int(data["age"]) <= 120):
        errors.append("Age must be a number between 1 and 120.")
    if not data.get("course") or len(data["course"].strip()) < 2:
        errors.append("Course must be at least 2 characters.")
    if errors:
        return jsonify({"errors": errors}), 422
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO student (name, email, age, course) VALUES (%s, %s, %s, %s)",
            (data["name"], data["email"], int(data["age"]), data["course"])
        )
        conn.commit()
        new_id = cur.lastrowid
        cur.close()
        conn.close()
        return jsonify({"message": "Student created", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── READ ALL ─────────────────────────────────────────────
@app.route("/api/students", methods=["GET"])
def get_students():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM student")
        students = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(students), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── READ ONE ─────────────────────────────────────────────
@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM student WHERE id = %s", (student_id,))
        student = cur.fetchone()
        cur.close()
        conn.close()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        return jsonify(student), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── UPDATE ───────────────────────────────────────────────
@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM student WHERE id = %s", (student_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"error": "Student not found"}), 404
        fields, values = [], []
        for key in ["name", "email", "age", "course"]:
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])
        values.append(student_id)
        cur.execute(f"UPDATE student SET {', '.join(fields)} WHERE id = %s", values)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Student updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── DELETE ───────────────────────────────────────────────
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM student WHERE id = %s", (student_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"error": "Student not found"}), 404
        cur.execute("DELETE FROM student WHERE id = %s", (student_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Student deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)