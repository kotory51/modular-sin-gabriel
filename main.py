from PyQt6.QtWidgets import QApplication
from core.router import Router
from database.users_db import init_db
import sys

if __name__ == "__main__":
    
    init_db()

    app = QApplication(sys.argv)

    router = Router(app)
    router.mostrar_login()

    sys.exit(app.exec())
