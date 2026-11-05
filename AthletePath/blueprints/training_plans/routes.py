"""Training Plans API endpoints."""
from basic_auth import api_auth_required
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from extensions import db, client

bp = Blueprint("training_plans", __name__)

@bp.route("/api/training-plans", methods=["GET"])
def get_training_plans():
    plans = list(db["TrainingPlans"].find({}, {"_id": 0}))
    return jsonify(plans), 200


@bp.route("/api/training-plans", methods=["POST"])
@api_auth_required
def create_training_plan():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    if not data.get("title"):
        return jsonify({"error": "Plan title is required"}), 400

    if not data.get("athlete_id"):
        return jsonify({"error": "Athlete ID is required"}), 400

    if not data.get("coach_id"):
        return jsonify({"error": "Coach ID is required"}), 400

    if "weekly_frequency" in data:
        frequency = data["weekly_frequency"]
        if (isinstance(frequency, bool)
                or not isinstance(frequency, int)
                or not 1 <= frequency <= 7):
            return jsonify({
                "error": "Weekly frequency must be between 1 and 7"
            }), 400

    if "assigned_task_ids" in data:
        if not isinstance(data["assigned_task_ids"], list):
            return jsonify({
                "error": "Assigned task IDs must be a list"
            }), 400

    # Protect original dataset identifiers
    data.pop("_id", None)
    data.pop("plan_id", None)

    data["status"] = "Draft"
    data["data_origin"] = "user_created"

    result = db["TrainingPlans"].insert_one(data)

    return jsonify({
        "message": "Training plan created successfully",
        "plan_id": str(result.inserted_id)
    }), 201


@bp.route("/api/training-plans/<plan_id>", methods=["PUT"])
@api_auth_required
def update_training_plan(plan_id):
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        plan_object_id = ObjectId(plan_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Invalid training plan ID"}), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Valid JSON data is required"}), 400

    # Only allow these training plan fields to be updated
    allowed_fields = {
        "title", "start_date", "end_date",
        "weekly_frequency", "assigned_task_ids",
        "status", "plan_details"
    }

    updates = {
        key: value for key, value in data.items()
        if key in allowed_fields
    }

    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    if "title" in updates and not updates["title"]:
        return jsonify({"error": "Plan title cannot be empty"}), 400

    if "weekly_frequency" in updates:
        frequency = updates["weekly_frequency"]
        if (isinstance(frequency, bool)
                or not isinstance(frequency, int)
                or not 1 <= frequency <= 7):
            return jsonify({
                "error": "Weekly frequency must be between 1 and 7"
            }), 400

    if "assigned_task_ids" in updates:
        if not isinstance(updates["assigned_task_ids"], list):
            return jsonify({
                "error": "Assigned task IDs must be a list"
            }), 400

    result = db["TrainingPlans"].update_one(
        {
            "_id": plan_object_id,
            "data_origin": "user_created"
        },
        {"$set": updates}
    )

    if result.matched_count == 0:
        return jsonify({
            "error": "User-created training plan not found"
        }), 404

    return jsonify({
        "message": "Training plan updated successfully",
        "plan_id": plan_id
    }), 200


@bp.route("/api/training-plans/<plan_id>", methods=["DELETE"])
@api_auth_required
def delete_training_plan(plan_id):
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        plan_object_id = ObjectId(plan_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Invalid training plan ID"}), 400

    result = db["TrainingPlans"].delete_one({
        "_id": plan_object_id,
        "data_origin": "user_created"
    })

    if result.deleted_count == 0:
        return jsonify({
            "error": "User-created training plan not found"
        }), 404

    return jsonify({
        "message": "Training plan deleted successfully",
        "plan_id": plan_id
    }), 200

