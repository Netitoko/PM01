import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QMessageBox
from db import get_connection, show_error
from demo_4.login_ui import Ui_LoginWindow

from admin_win import AdminWin
from manager_win import ManagerWin
from user_win import UserWin
from guest_win import GuestWin

class LoginWin(QMainWindow, Ui_LoginWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.lineEdit.setEchoMode(QLineEdit.EchoMode.Password)

        self.pushButton.clicked.connect(self.try_login)
        self.pushButton_2.clicked.connect(self.next_guest)

    def try_login(self):
        login = self.lineEdit_2.text().strip()
        password = self.lineEdit.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    p.id_пользователя,
                    p.фамилия,
                    p.имя,
                    p.отчество,
                    r.название_роли
                FROM пользователи p
                JOIN роли r ON r.id_роли = p.id_роли
                WHERE p.логин = %s AND p.пароль = %s
            """, (login, password))

            row = cur.fetchone()

            cur.close()
            conn.close()

            if row is None:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
                return

            user_role = row[4]

            if user_role == "Администратор":
                self.next_window = AdminWin(row)

            elif user_role == "Менеджер":
                self.next_window = ManagerWin(row)

            elif user_role == "Авторизованный клиент":
                self.next_window = UserWin(row)

            else:
                QMessageBox.warning(self, "Ошибка", "Неизвестная роль пользователя")
                return

            self.next_window.show()
            self.close()

        except Exception:
            show_error(self, "Ошибка при авторизации")

    def next_guest(self):
        self.next_window = GuestWin()
        self.next_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LoginWin()
    win.show()
    sys.exit(app.exec())