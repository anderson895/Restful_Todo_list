from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flask_cors import CORS
from flasgger import Swagger
from models import db, User, Task
from api.routes import api 
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"
CORS(app)

# ====== Database Config ======
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ====== Initialize Extensions ======
db.init_app(app)
swagger = Swagger(app)

# ====== Register Blueprints ======
app.register_blueprint(api)

# ====== Traditional HTML Routes ======

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("index.html")

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user_name = session.get("user_name", "User")  

    tasks = Task.query.filter_by(user_id=user_id).all()

    return render_template(
        "home.html",
        tasks=tasks,
        name=user_name,
        current_year=datetime.now().year
    )

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


# ====== Run Server ======
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
