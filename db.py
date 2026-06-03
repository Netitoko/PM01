import pymysql
import traceback
from PyQt6.QtWidgets import QMessageBox

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "shop_demo",
    "charset": "utf8mb4"
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def show_error(parent, text="Произошла ошибка"):
    QMessageBox.critical(parent, "Ошибка", text)
    print(traceback.format_exc())