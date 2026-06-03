import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout

from db import get_connection, show_error
from demo_4.main_window_ui import Ui_MainWindow

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
                SELECT id_поставщика, название_поставщика
                FROM поставщики
                ORDER BY название_поставщика
            """)

            for supplier in suppliers:
                self.comboBox_supplier.addItem(supplier[1], supplier[0])

            # Менеджеру нельзя изменять товары
            self.pushButton_add.hide()
            self.pushButton_edit.hide()
            self.pushButton_delete.hide()

            # Менеджеру нельзя изменять заказы
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
                    t.id_товара,
                    c.название_категории,
                    t.название,
                    t.описание,
                    m.название_производителя,
                    s.название_поставщика,
                    t.цена,
                    t.количество_на_складе,
                    e.название_единицы,
                    t.скидка,
                    t.путь_к_фото
                FROM товары t
                JOIN категории c ON c.id_категории = t.id_категории
                JOIN производители m ON m.id_производителя = t.id_производителя
                JOIN поставщики s ON s.id_поставщика = t.id_поставщика
                JOIN ед_измерения e ON e.id_единицы = t.id_единицы
                WHERE 1=1
            """

            params = []

            if search:
                query += """
                    AND (
                        t.название LIKE %s
                        OR t.описание LIKE %s
                        OR t.артикул LIKE %s
                        OR c.название_категории LIKE %s
                        OR m.название_производителя LIKE %s
                        OR s.название_поставщика LIKE %s
                    )
                """
                text = f"%{search}%"
                params.extend([text, text, text, text, text, text])

            if supplier_id != 0:
                query += " AND t.id_поставщика = %s"
                params.append(supplier_id)

            if sort_text == "По количеству по возрастанию":
                query += " ORDER BY t.количество_на_складе ASC"
            elif sort_text == "По количеству по убыванию":
                query += " ORDER BY t.количество_на_складе DESC"
            else:
                query += " ORDER BY t.id_товара"

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
                    z.id_заказа,
                    z.артикул_заказа,
                    s.название_статуса,
                    pv.адрес,
                    z.дата_заказа,
                    z.дата_выдачи
                FROM заказы z
                JOIN статус s ON s.id_статуса = z.id_статуса
                JOIN пункты_выдачи pv ON pv.id_пункта = z.id_пункта
                JOIN пользователи p ON p.id_пользователя = z.id_пользователя
                ORDER BY z.id_заказа
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