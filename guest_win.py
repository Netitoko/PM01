import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout

from db import get_connection, show_error
from ui.main_window_ui import Ui_MainWindow
from product_card import ProductCard


class GuestWin(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.products_layout = QVBoxLayout(self.scrollAreaWidgetContents)

        self.setup_guest_interface()
        self.load_products()

    def db_query(self, query, params=()):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(query, params)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows

    def setup_guest_interface(self):
        try:
            self.label_user.setText("Гость")
            self.label_role.setText("Гость")

            self.lineEdit_search.hide()
            self.comboBox_supplier.hide()
            self.comboBox_sort.hide()
            self.pushButton_refresh.hide()

            self.pushButton_add.hide()
            self.pushButton_edit.hide()
            self.pushButton_delete.hide()

            self.tabWidget.removeTab(1)

            self.pushButton_exit.clicked.connect(self.close)

        except Exception:
            show_error(self, "Ошибка при настройке окна гостя")

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_products(self):
        try:
            self.clear_layout(self.products_layout)

            query = """
                SELECT
                    p.product_id,
                    c.category_name,
                    p.product_name,
                    p.product_description,
                    m.manufacturer_name,
                    s.supplier_name,
                    p.price,
                    p.stock_quantity,
                    u.unit_name,
                    p.discount,
                    p.image_path
                FROM products p
                JOIN categories c ON c.category_id = p.category_id
                JOIN manufacturers m ON m.manufacturer_id = p.manufacturer_id
                JOIN suppliers s ON s.supplier_id = p.supplier_id
                JOIN units u ON u.unit_id = p.unit_id
                ORDER BY p.product_id
            """

            products = self.db_query(query)

            for product in products:
                card = ProductCard(product, self)
                self.products_layout.addWidget(card)

            self.products_layout.addStretch()

        except Exception:
            show_error(self, "Ошибка при загрузке товаров")

    def select_product_card(self, card):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GuestWin()
    win.show()
    sys.exit(app.exec())