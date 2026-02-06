from PyQt6.QtWidgets import QApplication
from core.router import Router
from database.users_db import init_db

from database.devices_service import get_device_service
from database.device_adapter import get_device_adapter

import sys

if __name__ == "__main__":
    
    init_db()
    
    device_service = get_device_service()
    device_adapter = get_device_adapter()

    app = QApplication(sys.argv)

    router = Router(app)
    router.mostrar_login()

    sys.exit(app.exec())
