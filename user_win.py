import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from db import get_connection, show_error
from demo_4.main_window_ui import Ui_MainWindow
from product_card import ProductCard

class UserWin(QMainWindow, Ui_MainWindow):
    def __init__(self, user=None):
        super().__init__()
        self.setupUi(self)

        if user is None:
            user = (0, "Тестовый", "Клиент", "", "Авторизованный клиент")

        self.user = user
        self.products_layout = QVBoxLayout(self.scrollAreaWidgetContents)

        self.setup_user_interface()
        self.load_products()

    def db_query(self, query, params=()):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(query, params)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return rows

    def setup_user_interface(self):
        try:
            self.label_user.setText(f"{self.user[1]} {self.user[2]} {self.user[3]}")
            self.label_role.setText(self.user[4])

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
            show_error(self, "Ошибка при настройке окна клиента")

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
                ORDER BY t.id_товара
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
    win = UserWin()
    win.show()
    sys.exit(app.exec())