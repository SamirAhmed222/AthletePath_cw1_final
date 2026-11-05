
"""Tasks API endpoints."""

import json

from flask import Blueprint, jsonify, request
from bson import ObjectId
from bson.errors import InvalidId

from basic_auth import api_auth_required
from extensions import db

bp = Blueprint("tasks", __name__)


@bp.route("/api/tasks", methods=["GET"])
@api_auth_required
def get_tasks():
    tasks = list(db["Tasks"].find({}, {"_id": 0}))
    return jsonify(tasks), 200


@bp.route("/api/tasks", methods=["POST"])
@api_auth_required
def create_task():
    # Accept form data from Postman or a JSON request
    data = (
        request.form.to_dict()
        if request.form
        else request.get_json(silent=True)
    )

    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "Task details are required"
        }), 400

    # Check the athlete ID
    if (
        not isinstance(data.get("athlete_id"), str)
        or not data["athlete_id"].strip()
    ):
        return jsonify({
            "error": "Athlete ID is required"
        }), 400

    # Check the completion status
    if data.get("completion_status") not in [
        "Pending", "In Progress", "Completed"
    ]:
        return jsonify({
            "error": "Completion status must be Pending, In Progress, or Completed"
        }), 400

    # Convert form values to the correct data types
    try:
        if "duration_minutes" in data:
            data["duration_minutes"] = int(data["duration_minutes"])

        if (
            "exercise_details" in data
            and isinstance(data["exercise_details"], str)
        ):
            data["exercise_details"] = json.loads(
                data["exercise_details"]
            )

        if data.get("completed_at") == "":
            data["completed_at"] = None

    except (ValueError, TypeError, json.JSONDecodeError):
        return jsonify({
            "error": "Invalid task data"
        }), 400

    # Prevent clients from setting a MongoDB ID
    data.pop("_id", None)

    # Identify records created through the API
    data["data_origin"] = "user_created"

    # Save the task in MongoDB
    result = db["Tasks"].insert_one(data)

    return jsonify({
        "message": "Task created successfully",
        "task_id": str(result.inserted_id)
    }), 201


@bp.route("/api/tasks/<task_id>", methods=["PUT"])
@api_auth_required
def update_task(task_id):
    # Validate the MongoDB task ID
    try:
        task_object_id = ObjectId(task_id)
    except (InvalidId, TypeError):
        return jsonify({
            "error": "Invalid task ID"
        }), 400

    # Accept form data or JSON
    data = (
        request.form.to_dict()
        if request.form
        else request.get_json(silent=True)
    )

    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "Task update details are required"
        }), 400

    # Only allow these fields to be updated
    allowed_fields = {
        "completion_status",
        "completed_at",
        "duration_minutes",
        "description",
        "exercise_details"
    }

    updates = {
        key: value
        for key, value in data.items()
        if key in allowed_fields
    }

    if not updates:
        return jsonify({
            "error": "No valid fields provided for update"
        }), 400

    # Validate completion status
    if "completion_status" in updates:
        if updates["completion_status"] not in [
            "Pending", "In Progress", "Completed"
        ]:
            return jsonify({
                "error": "Invalid completion status"
            }), 400

    # Convert form values to the correct data types
    try:
        if "duration_minutes" in updates:
            updates["duration_minutes"] = int(
                updates["duration_minutes"]
            )

        if (
            "exercise_details" in updates
            and isinstance(updates["exercise_details"], str)
        ):
            updates["exercise_details"] = json.loads(
                updates["exercise_details"]
            )

        if updates.get("completed_at") == "":
            updates["completed_at"] = None

    except (ValueError, TypeError, json.JSONDecodeError):
        return jsonify({
            "error": "Invalid task update data"
        }), 400

    # Update only a user-created task
    result = db["Tasks"].update_one(
        {
            "_id": task_object_id,
            "data_origin": "user_created"
        },
        {"$set": updates}
    )

    if result.matched_count == 0:
        return jsonify({
            "error": "User-created task not found"
        }), 404

    return jsonify({
        "message": "Task updated successfully",
        "task_id": task_id
    }), 200


@bp.route("/api/tasks/<task_id>", methods=["DELETE"])
@api_auth_required
def delete_task(task_id):
    # Validate the MongoDB task ID
    try:
        task_object_id = ObjectId(task_id)
    except (InvalidId, TypeError):
        return jsonify({
            "error": "Invalid task ID"
        }), 400

    # Delete only user-created tasks
    result = db["Tasks"].delete_one({
        "_id": task_object_id,
        "data_origin": "user_created"
    })

    if result.deleted_count == 0:
        return jsonify({
            "error": "User-created task not found"
        }), 404

    return jsonify({
        "message": "Task deleted successfully",
        "task_id": task_id
    }), 200
