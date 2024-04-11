from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
    send_from_directory,
    abort,
    send_file,
)
from werkzeug.utils import secure_filename
from .models import db, Order, City
import pandas as pd
import os
from io import BytesIO
from .utils import allowed_file, load_and_validate_file
from datetime import datetime
from flask_cors import CORS
from sqlalchemy import func

bp = Blueprint("sales", __name__, url_prefix="/sales")
CORS(bp, supports_credentials=True)


@bp.route("/", methods=["GET"])
def get_sales():
    # Collecting filter parameters
    city_name = request.args.get("city")
    district_name = request.args.get("district")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")

    query = db.session.query(Order).join(City, isouter=True)

    # Applying filters
    if city_name:
        query = query.filter(City.city_name == city_name)
    if district_name:
        query = query.filter(City.district_name == district_name)
    if start_date:
        query = query.filter(Order.order_date >= start_date)
    if end_date:
        query = query.filter(Order.order_date <= end_date)
    if start_time:
        query = query.filter(
            db.func.strftime("%H:%M:%S", Order.order_time) >= start_time
        )
    if end_time:
        query = query.filter(db.func.strftime("%H:%M:%S", Order.order_time) <= end_time)

    orders = query.all()
    return jsonify([order.to_dict() for order in orders])


@bp.route("/time_series/cities", methods=["GET"])
def get_sales_time_series_by_city():
    # Input parameters
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    qty_threshold = request.args.get("qty_threshold", default=None, type=int)
    city_names = request.args.get("city_names")

    # Convert city_names from comma-separated string to list if not empty
    city_list = city_names.split(",") if city_names else []

    if not start_date or not end_date:
        abort(400, description="start_date and end_date are required")

    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as e:
        abort(400, description=f"Invalid date format: {e}")

    query = db.session.query(
        City.city_name,
        func.date(Order.order_date).label("date"),
        func.sum(Order.rptg_amt).label("total_sales"),
    ).join(City, City.id == Order.district_city_id)

    # Filters
    query = query.filter(Order.order_date.between(start_date_obj, end_date_obj))

    if city_list:
        query = query.filter(City.city_name.in_(city_list))

    if qty_threshold is not None:
        query = query.filter(Order.order_qty >= qty_threshold)

    query = query.group_by(City.city_name, func.date(Order.order_date))

    sales_time_series = query.all()

    result = [
        {
            "city_name": city_name,
            "date": date,
            "total_sales": float(total_sales),
        }
        for city_name, date, total_sales in sales_time_series
    ]

    return jsonify(result)


@bp.route("/time_series/districts", methods=["GET"])
def get_sales_time_series_by_district():
    # Input parameters
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    qty_threshold = request.args.get("qty_threshold", default=None, type=int)
    city_names = request.args.get("city_names")

    # Convert city_names from comma-separated string to list if not empty
    city_list = city_names.split(",") if city_names else []

    if not start_date or not end_date:
        abort(400, description="start_date and end_date are required")

    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as e:
        abort(400, description=f"Invalid date format: {e}")

    query = db.session.query(
        City.district_name,
        func.date(Order.order_date).label("date"),
        func.sum(Order.rptg_amt).label("total_sales"),
    ).join(City, City.id == Order.district_city_id)

    # Filters
    query = query.filter(Order.order_date.between(start_date_obj, end_date_obj))

    if city_list:
        query = query.filter(City.city_name.in_(city_list))

    if qty_threshold is not None:
        query = query.filter(Order.order_qty >= qty_threshold)

    query = query.group_by(City.district_name, func.date(Order.order_date))

    sales_time_series = query.all()

    result = [
        {
            "district_name": district_name,
            "date": date,
            "total_sales": float(total_sales),
        }
        for district_name, date, total_sales in sales_time_series
    ]

    return jsonify(result)


@bp.route("/download", methods=["GET"])
def download_sales_data():
    # Extracting filter parameters from the query string
    city_names = request.args.get("city_names")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    qty_threshold = request.args.get("qty_threshold", default=None, type=int)

    # Building the base query
    query = db.session.query(Order).join(City, isouter=True)

    # Applying filters
    if city_names:
        city_list = city_names.split(",")
        query = query.filter(City.city_name.in_(city_list))
    if start_date:
        date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        query = query.filter(Order.order_date >= date_obj)
    if end_date:
        date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        query = query.filter(Order.order_date <= date_obj)
    if start_time:
        query = query.filter(func.time(Order.order_time) >= start_time)
    if end_time:
        query = query.filter(func.time(Order.order_time) <= end_time)
    if qty_threshold is not None:
        query = query.filter(Order.order_qty >= qty_threshold)

    # Fetching filtered data
    orders = query.all()

    # Transforming data to a pandas DataFrame for easy CSV/Excel conversion
    data = [order.to_dict() for order in orders]
    df = pd.DataFrame(data)

    output = BytesIO()
    df.to_excel(
        output, sheet_name="Sales Data", index=False
    )  # Save to the BytesIO object
    output.seek(0)

    response = send_file(
        output,
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        download_name="sales_data.xlsx",
    )
    response.headers["Content-Disposition"] = "attachment; filename=sales_data.xlsx"
    return response


@bp.route("/upload", methods=["POST"])
def upload_sales_data():
    if "file" not in request.files:
        abort(400, "No file part")

    file = request.files["file"]
    if file.filename == "":
        abort(400, "No selected file")
    if not allowed_file(file.filename):
        abort(400, "File type not allowed")

    # Save the file securely and return its path
    filepath = file.filename
    file.save(filepath)

    try:
        # Load and validate the uploaded file's data
        df = load_and_validate_file(filepath)

        # Process each row in the DataFrame
        for _, row in df.iterrows():
            unique_order_number = row["unique_order_number"]
            order = Order.query.get(unique_order_number)

            if order:
                # If the order exists and is not locked, or if updating locked status is allowed
                if not order.locked or "update locked logic based on your policy":
                    order.order_date = pd.to_datetime(row["order_date"]).date()
                    order.order_time = pd.to_datetime(row["order_time"]).time()
                    order.district_city_id = row["district_city_id"]
                    order.rptg_amt = row["rptg_amt"]
                    order.currency_cd = row["currency_cd"]
                    order.order_qty = row["order_qty"]
                    order.locked = bool(row["locked"])  # Convert to boolean and assign
            else:
                # Create a new order, including locked status
                new_order = Order(
                    unique_order_number=unique_order_number,
                    order_date=pd.to_datetime(row["order_date"]).date(),
                    order_time=pd.to_datetime(row["order_time"]).time(),
                    district_city_id=row["district_city_id"],
                    rptg_amt=row["rptg_amt"],
                    currency_cd=row["currency_cd"],
                    order_qty=row["order_qty"],
                    locked=bool(row["locked"]),  # Assuming direct assignment is safe
                )
                db.session.add(new_order)

        db.session.commit()  # Commit changes outside the loop

        return jsonify({"message": "File processed successfully"}), 200

    except Exception as e:
        db.session.rollback()  # Rollback changes in case of error
        abort(500, f"Error processing uploaded file: {e}")
    finally:
        # Clean up: remove the processed file
        if os.path.exists(filepath):
            os.remove(filepath)


@bp.route("/lock", methods=["POST"])
def lock_data():
    data = request.get_json()
    unique_order_number = data.get("unique_order_number")
    if not unique_order_number:
        abort(400, "Unique order number required")
    order = Order.query.get(unique_order_number)
    if order:
        order.locked = True
        db.session.commit()
        return jsonify({"status": "Locked"})
    else:
        abort(404, "Order not found")


def init_app(app):
    app.register_blueprint(bp)
