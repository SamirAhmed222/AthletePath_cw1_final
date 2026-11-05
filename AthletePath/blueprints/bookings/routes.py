"""Bookings API endpoints."""
from basic_auth import api_auth_required
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from extensions import db, client

bp = Blueprint("bookings", __name__)

@bp.route("/api/bookings", methods=["GET"])
def get_bookings():
    bookings = list(db["Bookings"].find({}, {"_id": 0}))
    return jsonify(bookings), 200


@bp.route("/api/bookings", methods=["POST"])
@api_auth_required
def create_booking():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    if not data.get("athlete_id"):
        return jsonify({"error": "Athlete ID is required"}), 400

    if not data.get("event_id"):
        return jsonify({"error": "Event ID is required"}), 400

    data.pop("_id", None)
    data.pop("booking_id", None)

    data["status"] = "Pending"
    data["data_origin"] = "user_created"

    result = db["Bookings"].insert_one(data)

    return jsonify({
        "message": "Booking created successfully",
        "booking_id": str(result.inserted_id)
    }), 201


@bp.route("/api/bookings/<booking_id>", methods=["PUT"])
@api_auth_required
def update_booking(booking_id):
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        booking_object_id = ObjectId(booking_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Invalid booking ID"}), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "Valid JSON data is required"}), 400

    # Only allow booking status and attendance updates
    allowed_fields = {"status", "attendance_status"}
    updates = {key: value for key, value in data.items()
               if key in allowed_fields}

    if not updates:
        return jsonify({
            "error": "Provide status or attendance_status"
        }), 400

    result = db["Bookings"].update_one(
        {
            "_id": booking_object_id,
            "data_origin": "user_created"
        },
        {"$set": updates}
    )

    if result.matched_count == 0:
        return jsonify({
            "error": "User-created booking not found"
        }), 404

    return jsonify({
        "message": "Booking updated successfully",
        "booking_id": booking_id
    }), 200


@bp.route("/api/bookings/<booking_id>", methods=["DELETE"])
@api_auth_required
def delete_booking(booking_id):
    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        booking_object_id = ObjectId(booking_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Invalid booking ID"}), 400

    result = db["Bookings"].delete_one({
        "_id": booking_object_id,
        "data_origin": "user_created"
    })

    if result.deleted_count == 0:
        return jsonify({
            "error": "User-created booking not found"
        }), 404

    return jsonify({
        "message": "Booking deleted successfully",
        "booking_id": booking_id
    }), 200

