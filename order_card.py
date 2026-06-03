import traceback
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QMessageBox, QLabel
from ui.order_card_ui import Ui_OrderForm

class OrderCard(QWidget, Ui_OrderForm):
    def __init__(self, order_data, parent_window=None):
        super().__init__()
        self.setupUi(self)

        self.order_data = order_data
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
            article = self.order_data[1]
            status = self.order_data[2]
            pickup = self.order_data[3]
            order_date = self.order_data[4]
            delivery_date = self.order_data[5]

            self.label_id.setText(f"Артикул заказа: {article}")
            self.label_status.setText(f"Статус заказа: {status}")
            self.label_pickup.setText(f"Адрес пункта выдачи: {pickup}")
            self.label_order_date.setText(f"Дата заказа: {order_date}")
            self.label_delivery_date.setText(f"Дата доставки:\n{delivery_date}")

        except Exception as error:
            self.show_error(error)

    def mousePressEvent(self, event):
        if self.parent_window:
            self.parent_window.select_order_card(self)