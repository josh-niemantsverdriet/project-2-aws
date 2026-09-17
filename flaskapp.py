import os
import sqlite3
import uuid

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "engr6010-assignment-secret-key"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

DATABASE = os.path.join(
    INSTANCE_DIR,
    "users.db"
)

UPLOAD_FOLDER = os.path.join(
    INSTANCE_DIR,
    "uploads"
)

ALLOWED_EXTENSIONS = {"txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def count_words(filepath):
    with open(
        filepath,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:
        contents = file.read()

    return len(contents.split())


def init_db():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            original_filename TEXT,
            stored_filename TEXT,
            word_count INTEGER
        )
    """)

    columns = [
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(users)"
        ).fetchall()
    ]

    if "original_filename" not in columns:
        connection.execute(
            "ALTER TABLE users ADD COLUMN original_filename TEXT"
        )

    if "stored_filename" not in columns:
        connection.execute(
            "ALTER TABLE users ADD COLUMN stored_filename TEXT"
        )

    if "word_count" not in columns:
        connection.execute(
            "ALTER TABLE users ADD COLUMN word_count INTEGER"
        )

    connection.commit()
    connection.close()


init_db()


@app.route("/")
def home():
    return redirect(url_for("register"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        email = request.form["email"].strip()
        address = request.form["address"].strip()

        uploaded_file = request.files.get("file")

        if not all([
            username,
            password,
            first_name,
            last_name,
            email,
            address
        ]):
            flash("Please complete every field.", "error")
            return render_template("register.html")

        if uploaded_file is None or uploaded_file.filename == "":
            flash("Please select a text file to upload.", "error")
            return render_template("register.html")

        if not allowed_file(uploaded_file.filename):
            flash("Only .txt files may be uploaded.", "error")
            return render_template("register.html")

        connection = get_db_connection()

        existing_user = connection.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing_user:
            connection.close()
            flash("That username is already registered.", "error")
            return render_template("register.html")

        original_filename = secure_filename(uploaded_file.filename)

        unique_filename = (
            f"{uuid.uuid4().hex}_{original_filename}"
        )

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            unique_filename
        )

        uploaded_file.save(filepath)
        word_count = count_words(filepath)
        password_hash = generate_password_hash(password)

        cursor = connection.execute("""
            INSERT INTO users (
                username,
                password,
                first_name,
                last_name,
                email,
                address,
                original_filename,
                stored_filename,
                word_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            password_hash,
            first_name,
            last_name,
            email,
            address,
            original_filename,
            unique_filename,
            word_count
        ))

        connection.commit()
        user_id = cursor.lastrowid
        connection.close()

        session["user_id"] = user_id

        flash(
            "Registration and file upload successful!",
            "success"
        )

        return redirect(url_for("profile"))

    return render_template("register.html")


@app.route("/profile")
def profile():
    user_id = session.get("user_id")

    if user_id is None:
        flash(
            "Please log in to view your information.",
            "error"
        )
        return redirect(url_for("login"))

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    connection.close()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        user=user
    )


@app.route("/download")
def download_file():
    user_id = session.get("user_id")

    if user_id is None:
        flash(
            "Please log in to download your file.",
            "error"
        )
        return redirect(url_for("login"))

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    connection.close()

    if user is None or not user["stored_filename"]:
        flash(
            "No uploaded file was found.",
            "error"
        )
        return redirect(url_for("profile"))

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        user["stored_filename"],
        as_attachment=True,
        download_name=user["original_filename"]
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        connection = get_db_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        connection.close()

        if (
            user is None
            or not check_password_hash(
                user["password"],
                password
            )
        ):
            flash(
                "Incorrect username or password.",
                "error"
            )
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]

        flash(
            "Login successful.",
            "success"
        )

        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
