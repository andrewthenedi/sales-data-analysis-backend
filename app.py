from flask import Flask, jsonify, request, send_from_directory, abort, render_template
from flask_cors import CORS
import sqlite3
import pandas as pd
import os
from werkzeug.utils import secure_filename
from load_data import format_order_time_pst

app = Flask(__name__)
CORS(app, resources={r"/sales/*": {"origins": "http://localhost:3000"}})

# Configuration
DATABASE_PATH = "project_database.db"
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {"xlsx", "csv"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload folder exists


# Helper Functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def secure_file_save(file):
    if not file:
        abort(400, description="No file part")
    if file.filename == "":
        abort(400, description="No selected file")
    if not allowed_file(file.filename):
        abort(400, description="File type not allowed")
    filename = secure_filename(file.filename)
    filepath = os.path.join("./uploads", filename)
    file.save(filepath)
    return filepath


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
