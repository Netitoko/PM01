import os
import traceback
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QMessageBox, QLabel
from PyQt6.QtGui import QPixmap
from ui.product_card_ui import Ui_ProductForm

class ProductCard(QWidget, Ui_ProductForm):
    def __init__(self, product_data, parent_window=None):
        super().__init__()
        self.setupUi(self)

        self.product_data = product_data
        self.parent_window = parent_window

        self.setMaximumHeight(200)
        self.setMinimumHeight(200)

        for label in self.findChildren(QLabel):
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.fill_card()

    def show_error(self, error):
        QMessageBox.critical(
            self,
            "Ошибка",
            f"Ошибка: {error}\n{traceback.format_exc()}"
        )

    def fill_card(self):
        try:
            category = self.product_data[1]
            name = self.product_data[2]
            description = self.product_data[3]
            manufacturer = self.product_data[4]
            supplier = self.product_data[5]
            price = self.product_data[6]
            quantity = self.product_data[7]
            unit = self.product_data[8]
            discount = self.product_data[9]
            img_path = self.product_data[10]

            self.label_title.setText(f"{category} | {name}")
            self.label_description.setText(f"Описание: {description}")
            self.label_manufacturer.setText(f"Производитель: {manufacturer}")
            self.label_supplier.setText(f"Поставщик: {supplier}")
            self.label_price.setText(self.get_price_text(price, discount))
            self.label_quantity.setText(f"Количество на складе: {quantity} {unit}")
            self.label_discount.setText(f"Скидка: {discount or 0}%")

            self.set_card_color(discount, quantity)
            self.load_img(img_path)

        except Exception as error:
            self.show_error(error)

    def get_price_text(self, price, discount):
        price = float(price)
        discount = int(discount) if discount else 0

        if discount > 0:
            new_price = price - price * discount / 100
            return (
                f"<span style='color:red; text-decoration: line-through;'>"
                f"{price:.2f} руб.</span><br>"
                f"<span style='color:black;'>Цена со скидкой: {new_price:.2f} руб.</span>"
            )

        return f"Цена: {price:.2f} руб."

    def set_card_color(self, discount, quantity):
        discount = int(discount) if discount else 0
        quantity = int(quantity) if quantity else 0

        if quantity == 0:
            bg = "#bde0ff"
            text = "black"
        elif discount > 15:
            bg = "#2E8B57"
            text = "white"
        else:
            bg = "white"
            text = "black"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                border: 1px solid #cccccc;
                border-radius: 5px;
            }}
            QLabel {{
                color: {text};
                border: none;
            }}
        """)

    def load_img(self, img_path):
        try:
            if img_path and not str(img_path).startswith("imgs/"):
                img_path = os.path.join("imgs", str(img_path))

            if not img_path or not os.path.exists(img_path):
                img_path = "imgs/picture.png"

            self.label_img.setPixmap(QPixmap(img_path))
            self.label_img.setScaledContents(True)

        except Exception as error:
            self.show_error(error)

    def mousePressEvent(self, event):
        if self.parent_window:
            self.parent_window.select_product_card(self)