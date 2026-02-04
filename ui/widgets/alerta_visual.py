from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


class AlertBadge(QLabel):
    def __init__(self, text="Sin datos"):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(36)
        self.set_status("neutral")

    def set_status(self, status: str):
        styles = {
            "ok": """
                background:#1ecb4f;
                color:white;
                border-radius:18px;
                font-weight:600;
            """,
            "warn": """
                background:#ff9800;
                color:white;
                border-radius:18px;
                font-weight:600;
            """,
            "alert": """
                background:#f44336;
                color:white;
                border-radius:18px;
                font-weight:600;
            """,
            "neutral": """
                background:#bdbdbd;
                color:white;
                border-radius:18px;
                font-weight:600;
            """
        }
        self.setStyleSheet(styles.get(status, styles["neutral"]))
