import os
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

tasks = []
task_id_counter = 1


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    global task_id_counter
    data = request.get_json()
    if not data or "title" not in data or not str(data["title"]).strip():
        return jsonify({"error": "Title is required"}), 400

    new_task = {
        "id": task_id_counter,
        "title": str(data["title"]).strip(),
        "done": bool(data.get("done", False))
    }
    task_id_counter += 1
    tasks.append(new_task)
    return jsonify(new_task), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    if "title" in data:
        title = str(data["title"]).strip()
        if not title:
            return jsonify({"error": "Title cannot be empty"}), 400
        task["title"] = title

    if "done" in data:
        task["done"] = bool(data["done"])

    return jsonify(task), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    tasks.remove(task)
    return jsonify({"message": "Task deleted"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
