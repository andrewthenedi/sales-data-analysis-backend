from datetime import datetime
import sqlite3
import pandas as pd
from flask import current_app, g, abort
from werkzeug.utils import secure_filename
import os


def get_db_connection():
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db_connection(e=None):
    """
    Closes the database connection again at the end of the request.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def allowed_file(filename):
    """
    Check if the file's extension is allowed.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"csv", "xlsx"}


def load_and_validate_file(filepath):
    """
    Loads an Excel or CSV file into a pandas DataFrame and validates it.
    Implement specific validation based on your application needs.
    """
    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
    else:  # Assume Excel format
        df = pd.read_excel(filepath)

    # Include 'locked' in required columns
    required_columns = {
        "unique_order_number",
        "order_time",  # Assumed corrected name based on routes.py usage
        "order_date",  # Added based on your initial suggestion
        "district_city_id",
        "rptg_amt",
        "currency_cd",
        "order_qty",
        "locked",  # New required column
    }
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        os.remove(filepath)  # Clean up the uploaded file
        abort(
            400, description=f"Missing required columns: {', '.join(missing_columns)}"
        )

    return df


def validate_uploaded_data(df):
    # Update the required columns to include 'order_date' and 'order_time'
    required_columns = {
        "unique_order_number",
        "order_date",
        "order_time",
        "district_city_id",
        "rptg_amt",
        "currency_cd",
        "order_qty",
    }
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            "Uploaded file is missing one or more required columns: "
            + ", ".join(missing_columns)
        )
