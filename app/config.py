import os


class Config:
    DATABASE_PATH = os.getenv("DATABASE_PATH", "project_database.db")
    EXCEL_FILE_PATH = os.getenv("EXCEL_FILE_PATH", "data/rawdata.xlsx")
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/data_loading_log.txt")
    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DATABASE_PATH = os.path.join(PROJECT_ROOT, "instance", "project_database.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
