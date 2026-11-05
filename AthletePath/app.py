"""AthletePath Flask application entry point."""
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
jwt = JWTManager(app)

from blueprints.core.routes import bp as core_bp
from blueprints.auth.routes import bp as auth_bp
from blueprints.goals.routes import bp as goals_bp
from blueprints.tasks.routes import bp as tasks_bp
from blueprints.events.routes import bp as events_bp
from blueprints.bookings.routes import bp as bookings_bp
from blueprints.performance.routes import bp as performance_bp
from blueprints.training_plans.routes import bp as training_plans_bp

for blueprint in (core_bp, auth_bp, goals_bp, tasks_bp, events_bp, bookings_bp, performance_bp, training_plans_bp):
    app.register_blueprint(blueprint)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
