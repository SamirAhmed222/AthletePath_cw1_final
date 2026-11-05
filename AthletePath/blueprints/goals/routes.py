"""Goals API endpoints."""
from basic_auth import api_auth_required
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from extensions import db, client

bp = Blueprint("goals", __name__)

@bp.route("/api/goals", methods=["GET"])
@api_auth_required
def get_goals():
    goals = list(db["Goals"].find({}, {"_id": 0}))
    return jsonify(goals), 200


@bp.route("/api/goals", methods=["POST"])
@api_auth_required
def create_goal():
    data = request.form.to_dict() if request.form else request.get_json(silent=True)

    # Check that valid JSON was provided
    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "A JSON object with goal details is required"
        }), 400

    # Check that the goal has a category
    if not isinstance(data.get("category"), str) or not data["category"].strip():
        return jsonify({
            "error": "Goal category is required"
        }), 400
        
        
    
    
    try:
        for field in ("target_value", "current_value"):
            if field in data and data[field] != "":
                data[field] = float(data[field])
    except (ValueError, TypeError):
        return jsonify({"error": "Goal values must be numbers"}), 400
    
    
    # Prevent clients from supplying a MongoDB ID
    data.pop("_id", None)

    # Mark this as user-created data
    data["data_origin"] = "user_created"

    # Save the new goal in MongoDB
    result = db["Goals"].insert_one(data)

    # Return confirmation
    return jsonify({
        "message": "Goal created successfully",
        "goal_id": str(result.inserted_id)
    }), 201


@bp.route("/api/goals/<goal_id>", methods=["PUT"])
@api_auth_required
def update_goal(goal_id):
    from bson import ObjectId
    from bson.errors import InvalidId

    # Read the JSON sent from Postman
    data = request.form.to_dict() if request.form else request.get_json(silent=True)

    # Check that valid JSON was provided
    if not isinstance(data, dict) or not data:
        return jsonify({
            "error": "Valid JSON data is required"
        }), 400

    # Check that the goal ID is valid
    try:
        goal_object_id = ObjectId(goal_id)
    except (InvalidId, TypeError):
        return jsonify({
            "error": "Invalid goal ID"
        }), 400

    # Only allow these goal fields to be updated
    allowed_fields = {
        "category",
        "description",
        "target_value",
        "current_value",
        "status"
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
    try:
        for field in ("target_value", "current_value"):
            if field in updates:
                updates[field] = float(updates[field])
    except (ValueError, TypeError):
        return jsonify({"error": "Goal values must be numbers"}), 400
    # Update the goal in MongoDB
    result = db["Goals"].update_one(
        {"_id": goal_object_id, "data_origin": "user_created"},
        {"$set": updates}
    )

    # Check whether the goal exists
    if result.matched_count == 0:
        return jsonify({
            "error": "User-created goal not found"
        }), 404

    # Return confirmation
    return jsonify({
        "message": "Goal updated successfully",
        "goal_id": goal_id
    }), 200


@bp.route("/api/goals/<goal_id>", methods=["DELETE"])
@api_auth_required
def delete_goal(goal_id):
    from bson import ObjectId
    from bson.errors import InvalidId

    # Check that the goal ID is valid
    try:
        goal_object_id = ObjectId(goal_id)
    except (InvalidId, TypeError):
        return jsonify({
            "error": "Invalid goal ID"
        }), 400

    # Delete only a user-created goal
    result = db["Goals"].delete_one({
        "_id": goal_object_id,
        "data_origin": "user_created"
    })

    # Check whether a goal was deleted
    if result.deleted_count == 0:
        return jsonify({
            "error": "User-created goal not found"
        }), 404

    # Return confirmation
    return jsonify({
        "message": "Goal deleted successfully",
        "goal_id": goal_id
    }), 200

