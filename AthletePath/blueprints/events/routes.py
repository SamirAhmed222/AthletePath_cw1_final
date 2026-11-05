"""Events API endpoints."""
from basic_auth import api_auth_required
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from extensions import db, client

bp = Blueprint("events", __name__)

@bp.route("/api/events", methods=["GET"])
def get_events():
    events = list(db["Events"].find({}, {"_id": 0}))
    return jsonify(events), 200


@bp.route("/api/events", methods=["POST"])
@api_auth_required
def create_event():
    data = request.form.to_dict() if request.form else request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    if not data.get("title"):
        return jsonify({"error": "Event title is required"}), 400

    data.pop("_id", None)
    data["data_origin"] = "user_created"
    try:
        if "capacity" in data:
            data["capacity"] = int(data["capacity"])
    except (ValueError, TypeError):
        return jsonify({"error": "Capacity must be a number"}), 400

    result = db["Events"].insert_one(data)

    return jsonify({
        "message": "Event created successfully",
        "event_id": str(result.inserted_id)
    }), 201


@bp.route("/api/events/<event_id>", methods=["PUT"])
@api_auth_required
def update_event(event_id):
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        event_object_id = ObjectId(event_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Invalid event ID"}), 400

    data = request.form.to_dict() if request.form else request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Valid JSON data is required"}), 400

    # Prevent changes to protected fields
    data.pop("_id", None)
    data.pop("data_origin", None)

    if not data:
        return jsonify({"error": "No fields to update"}), 400

    if "title" in data and not data["title"]:
        return jsonify({"error": "Event title cannot be empty"}), 400

    result = db["Events"].update_one(
        {
            "_id": event_object_id,
            "data_origin": "user_created"
        },
        {"$set": data}
    )

    if result.matched_count == 0:
        return jsonify({"error": "User-created event not found"}), 404

    return jsonify({
        "message": "Event updated successfully",
        "event_id": event_id
    }), 200


@bp.route("/api/events/<event_id>", methods=["DELETE"])
@api_auth_required
def delete_event(event_id):
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        event_object_id = ObjectId(event_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Invalid event ID"}), 400

    result = db["Events"].delete_one({
        "_id": event_object_id,
        "data_origin": "user_created"
    })

    if result.deleted_count == 0:
        return jsonify({
            "error": "User-created event not found"
        }), 404

    return jsonify({
        "message": "Event deleted successfully",
        "event_id": event_id
    }), 200 

