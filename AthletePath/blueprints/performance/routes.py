"""Performance API endpoints."""
from basic_auth import api_auth_required
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from extensions import db, client

bp = Blueprint("performance", __name__)

@bp.route("/api/performance", methods=["GET"])
def get_performance():
    records = list(db["PerformanceRecords"].find({}, {"_id": 0}))
    return jsonify(records), 200


@bp.route("/api/performance", methods=["POST"])
@api_auth_required
def create_performance():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    if not data.get("athlete_id"):
        return jsonify({"error": "Athlete ID is required"}), 400

    if not data.get("metric_type"):
        return jsonify({"error": "Metric type is required"}), 400

    if "value" not in data or not isinstance(data["value"], (int, float)) or isinstance(data["value"], bool):
        return jsonify({"error": "A numeric value is required"}), 400

    if not data.get("unit"):
        return jsonify({"error": "Unit is required"}), 400

    # Protect original dataset identifiers
    data.pop("_id", None)
    data.pop("record_id", None)

    data["data_origin"] = "user_created"

    result = db["PerformanceRecords"].insert_one(data)

    return jsonify({
        "message": "Performance record created successfully",
        "record_id": str(result.inserted_id)
    }), 201


@bp.route("/api/performance/<record_id>", methods=["PUT"])
@api_auth_required
def update_performance(record_id):
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        record_object_id = ObjectId(record_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Invalid performance record ID"}), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Valid JSON data is required"}), 400

    # Only allow performance measurement fields to be updated
    allowed_fields = {"metric_type", "value", "unit", "notes", "recorded_at"}
    updates = {
        key: value for key, value in data.items()
        if key in allowed_fields
    }

    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400

    if "metric_type" in updates and not updates["metric_type"]:
        return jsonify({"error": "Metric type cannot be empty"}), 400

    if "unit" in updates and not updates["unit"]:
        return jsonify({"error": "Unit cannot be empty"}), 400

    if "value" in updates:
        value = updates["value"]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return jsonify({"error": "Value must be numeric"}), 400

    result = db["PerformanceRecords"].update_one(
        {
            "_id": record_object_id,
            "data_origin": "user_created"
        },
        {"$set": updates}
    )

    if result.matched_count == 0:
        return jsonify({
            "error": "User-created performance record not found"
        }), 404

    return jsonify({
        "message": "Performance record updated successfully",
        "record_id": record_id
    }), 200


@bp.route("/api/performance/<record_id>", methods=["DELETE"])
@api_auth_required
def delete_performance(record_id):
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        record_object_id = ObjectId(record_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Invalid performance record ID"}), 400

    result = db["PerformanceRecords"].delete_one({
        "_id": record_object_id,
        "data_origin": "user_created"
    })

    if result.deleted_count == 0:
        return jsonify({
            "error": "User-created performance record not found"
        }), 404

    return jsonify({
        "message": "Performance record deleted successfully",
        "record_id": record_id
    }), 200


@bp.route("/api/performance/stats", methods=["GET"])
@api_auth_required
def get_performance_stats():
    pipeline = [
        {
            "$match": {
                "value": {"$type": "number"}
            }
        },
        {
            "$group": {
                "_id": {
                    "metric_type": "$metric_type",
                    "unit": "$unit"
                },
                "total_records": {"$sum": 1},
                "average_value": {"$avg": "$value"},
                "maximum_value": {"$max": "$value"},
                "minimum_value": {"$min": "$value"}
            }
        },
        {
            "$sort": {
                "total_records": -1
            }
        }
    ]

    results = list(db["PerformanceRecords"].aggregate(pipeline))

    for result in results:
        result["metric"] = result.pop("_id")

    return jsonify({
        "message": "Performance statistics calculated successfully",
        "statistics": results
    }), 200

