"""Allow registered athletes to authenticate with HTTP Basic or an existing JWT."""
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request
from werkzeug.security import check_password_hash
from extensions import db


def api_auth_required(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        if request.authorization and request.authorization.type.lower() == "basic":
            credentials = request.authorization
            email = (credentials.username or "").strip().lower()
            password = credentials.password or ""
            if not email or not password:
                return jsonify({"error": "Valid Basic Auth credentials required"}), 401
            user = db["Users"].find_one({"email": email})
            if (not user or not user.get("password_hash")
                    or not check_password_hash(user["password_hash"], password)):
                return jsonify({"error": "Invalid email or password"}), 401
            if user.get("account_status") != "active":
                return jsonify({"error": "Account is not active"}), 403
            return view(*args, **kwargs)
        # Preserve the previous Bearer JWT behaviour for existing Postman tests.
        verify_jwt_in_request()
        return view(*args, **kwargs)
    return decorated
