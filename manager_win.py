import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout

from db import get_connection, show_error
from ui.main_window_ui import Ui_MainWindow
from product_card import ProductCard
from order_card import OrderCard


class ManagerWin(QMainWindow, Ui_MainWindow):
    def __init__(self, user=None):
        super().__init__()
        self.setupUi(self)

        if user is None:
            user = (0, "Тестовый", "Менеджер", "", "Менеджер")

        self.user = user
        self.products_layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.orders_layout = QVBoxLayout(self.scrollAreaWidgetContents_orders)

        self.setup_manager_interface()
        self.init_signals()

        self.load_products()
        self.load_orders()

    def db_query(self, query, params=()):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(query, params)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows

    def setup_manager_interface(self):
        try:
            self.label_user.setText(f"{self.user[1]} {self.user[2]} {self.user[3]}")
            self.label_role.setText(self.user[4])

            self.comboBox_sort.clear()
            self.comboBox_sort.addItems([
                "Без сортировки",
                "По количеству по возрастанию",
                "По количеству по убыванию"
            ])

            self.comboBox_supplier.clear()
            self.comboBox_supplier.addItem("Все поставщики", 0)

            suppliers = self.db_query("""
                SELECT supplier_id, supplier_name
                FROM suppliers
                ORDER BY supplier_name
            """)

            for supplier in suppliers:
                self.comboBox_supplier.addItem(supplier[1], supplier[0])

            self.pushButton_add.hide()
            self.pushButton_edit.hide()
            self.pushButton_delete.hide()

            self.pushButton_add_order.hide()
            self.pushButton_edit_order.hide()
            self.pushButton_delete_order.hide()

        except Exception:
            show_error(self, "Ошибка при настройке окна менеджера")

    def init_signals(self):
        self.lineEdit_search.textChanged.connect(self.load_products)
        self.comboBox_supplier.currentIndexChanged.connect(self.load_products)
        self.comboBox_sort.currentIndexChanged.connect(self.load_products)

        self.pushButton_refresh.clicked.connect(self.refresh_products)
        self.pushButton_refresh_orders.clicked.connect(self.load_orders)

        self.pushButton_exit.clicked.connect(self.close)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def load_products(self):
        try:
            self.clear_layout(self.products_layout)

            search = self.lineEdit_search.text().strip()
            supplier_id = self.comboBox_supplier.currentData()
            sort_text = self.comboBox_sort.currentText()

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
                WHERE 1=1
            """

            params = []

            if search:
                query += """
                    AND (
                        p.product_name LIKE %s
                        OR p.product_description LIKE %s
                        OR p.article LIKE %s
                        OR c.category_name LIKE %s
                        OR m.manufacturer_name LIKE %s
                        OR s.supplier_name LIKE %s
                    )
                """
                text = f"%{search}%"
                params.extend([text, text, text, text, text, text])

            if supplier_id != 0:
                query += " AND p.supplier_id = %s"
                params.append(supplier_id)

            if sort_text == "По количеству по возрастанию":
                query += " ORDER BY p.stock_quantity ASC"
            elif sort_text == "По количеству по убыванию":
                query += " ORDER BY p.stock_quantity DESC"
            else:
                query += " ORDER BY p.product_id"

            products = self.db_query(query, params)

            for product in products:
                card = ProductCard(product, self)
                self.products_layout.addWidget(card)

            self.products_layout.addStretch()

        except Exception:
            show_error(self, "Ошибка при загрузке товаров")

    def refresh_products(self):
        self.lineEdit_search.clear()
        self.comboBox_supplier.setCurrentIndex(0)
        self.comboBox_sort.setCurrentIndex(0)
        self.load_products()

    def load_orders(self):
        try:
            self.clear_layout(self.orders_layout)

            orders = self.db_query("""
                SELECT
                    o.order_id,
                    o.order_article,
                    st.status_name,
                    pp.address,
                    o.order_date,
                    o.delivery_date
                FROM orders o
                JOIN statuses st ON st.status_id = o.status_id
                JOIN pickup_points pp ON pp.pickup_point_id = o.pickup_point_id
                JOIN users u ON u.user_id = o.user_id
                ORDER BY o.order_id
            """)

            for order in orders:
                card = OrderCard(order, self)
                self.orders_layout.addWidget(card)

            self.orders_layout.addStretch()

        except Exception:
            show_error(self, "Ошибка при загрузке заказов")

    def select_product_card(self, card):
        pass

    def select_order_card(self, card):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ManagerWin()
    win.show()
    sys.exit(app.exec())