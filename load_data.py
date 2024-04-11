import os
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from app import create_app
from app.models import db, City, Order
from app.config import Config

# Load environment variables and configure logging
load_dotenv()
log_file_path = os.path.join(os.path.dirname(__file__), Config.LOG_FILE_PATH)
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
logging.basicConfig(
    filename=log_file_path,
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def create_app_and_initialize_db():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app


def load_data_from_excel_to_db(excel_path):
    app = create_app_and_initialize_db()
    with app.app_context():
        for sheet_name, loader_function in [
            ("city", load_city_data),
            ("data", load_order_data),
        ]:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            df.columns = df.columns.str.lower().str.replace(" ", "_")
            loader_function(df)


def load_city_data(df):
    City.query.delete()
    cities = [
        City(district_name=row["district_name"], city_name=row["city_name"])
        for index, row in df.iterrows()
    ]
    db.session.bulk_save_objects(cities)
    db.session.commit()
    logging.info("City data loaded successfully.")


def load_order_data(df):
    Order.query.delete()
    df = clean_data(df)
    orders = [
        Order(
            unique_order_number=row["unique_order_number"],
            order_time=row["order_time"],
            order_date=row["order_date"],
            district_city_id=row["district_city_id"],
            rptg_amt=row["rptg_amt"],
            currency_cd=row["currency_cd"],
            order_qty=row["order_qty"],
            locked=row.get("locked", False),
        )
        for index, row in df.iterrows()
    ]
    db.session.bulk_save_objects(orders)
    db.session.commit()
    logging.info("Order data loaded successfully.")


def clean_data(df):
    df["order_time_pst"] = pd.to_datetime(
        df["order_time__(pst)"].apply(lambda x: str(x).zfill(6)),
        format="%H%M%S",
        errors="coerce",
    )
    df["order_date"] = pd.to_datetime(
        "today"
    ).date()  # Assuming order date is the current date
    df["order_time"] = df["order_time_pst"].dt.time
    df["rptg_amt"] = (
        df["rptg_amt"].apply(lambda x: np.nan if x == "undefined" else x).astype(float)
    )
    df.fillna({"district_city_id": 0, "order_qty": 0}, inplace=True)
    df.dropna(subset=["unique_order_number", "currency_cd", "rptg_amt"], inplace=True)
    return df


def main():
    excel_path = os.path.join(os.path.dirname(__file__), Config.EXCEL_FILE_PATH)
    load_data_from_excel_to_db(excel_path)


if __name__ == "__main__":
    main()
