"""Core API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from extensions import db, client

bp = Blueprint("core", __name__)

@bp.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to AthletePath API"
    }), 200


@bp.route("/api/health", methods=["GET"])
def health():
    try:
        client.admin.command("ping")

        return jsonify({
            "status": "Connected to MongoDB",
            "database": "AthletePath"
        }), 200

    except Exception:
        return jsonify({
            "status": "MongoDB connection failed"
        }), 503


@bp.route("/api/athletes", methods=["GET"])
def get_athletes():
    athletes = list(
        db["Users"].find(
            {"role": "Athlete"},
            {"_id": 0, "password_hash": 0}
        )
    )

    return jsonify(athletes), 200

