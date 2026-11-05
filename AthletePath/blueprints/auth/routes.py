"""Auth API endpoints."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from extensions import db, client

bp = Blueprint("auth", __name__)

@bp.route("/api/register", methods=["POST"])
def register():
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400

    if db["Users"].find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    user = {
        "name": name,
        "email": email,
        "password_hash": generate_password_hash(password),
        "role": "Athlete",
        "account_status": "active"
    }

    result = db["Users"].insert_one(user)

    return jsonify({
        "message": "Registration successful",
        "user_id": str(result.inserted_id)
    }), 201


@bp.route("/api/login", methods=["POST"])
def login():
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = db["Users"].find_one({"email": email})

    if not user or not user.get("password_hash"):
        return jsonify({"error": "Invalid email or password"}), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    if user.get("account_status") != "active":
        return jsonify({"error": "Account is not active"}), 403

    token = create_access_token(identity=str(user["_id"]))

    return jsonify({
        "message": "Login successful",
        "access_token": token,
        "role": user.get("role", "Athlete")
    }), 200

