from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QMessageBox, QComboBox, QLabel,
    QFileDialog, QTextEdit, QGroupBox, QScrollArea, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import re
import os


def is_valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def is_valid_rfc(rfc: str) -> bool:
    return re.match(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$", rfc.upper()) is not None


class UserDialog(QDialog):

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar / Editar usuario")
        self.resize(950, 650)

        self.data = data or {}

        # ✅ FIX DEFINITIVO
        self.is_edit = bool(self.data.get("usuario"))

        # ---------- SCROLL ----------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        content = QWidget()
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)

        # ---------- CAMPOS ----------
        self.inp_nombre = QLineEdit(self.data.get("nombre", ""))
        self.inp_apellido = QLineEdit(self.data.get("apellido", ""))

        self.inp_usuario = QLineEdit(self.data.get("usuario", ""))
        self.inp_usuario.setReadOnly(self.is_edit)
        self.inp_usuario.setEnabled(True)
        self.inp_usuario.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.inp_usuario.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
            }
        """)

        self.inp_password = QLineEdit()
        self.inp_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.inp_rol = QComboBox()
        self.inp_rol.addItems(["Administrador", "Supervisor", "Chofer"])
        self.inp_rol.setCurrentText(self.data.get("rol", "Chofer"))

        self.inp_telefono = QLineEdit(self.data.get("telefono", ""))
        self.inp_email = QLineEdit(self.data.get("email", ""))
        self.inp_rfc = QLineEdit(self.data.get("rfc", ""))

        self.inp_tipo_sangre = QLineEdit(self.data.get("tipo_sangre", ""))
        self.inp_alergias = QTextEdit(self.data.get("alergias", ""))
        self.inp_enfermedades = QTextEdit(self.data.get("enfermedades", ""))
        self.inp_notas = QTextEdit(self.data.get("notas_medicas", ""))

        for t in (self.inp_alergias, self.inp_enfermedades, self.inp_notas):
            t.setFixedHeight(70)

        self.chk_apto = QCheckBox("Apto para operar")
        self.chk_apto.setChecked(bool(self.data.get("apto_operar", 0)))

        # ---------- DOCUMENTOS ----------
        self.lbl_foto = self._img_label()
        self.lbl_ine = self._img_label()
        self.lbl_licencia = self._img_label()

        self.btn_foto = QPushButton("Subir foto")
        self.btn_ine = QPushButton("Subir INE")
        self.btn_licencia = QPushButton("Subir licencia")

        self.btn_foto.clicked.connect(lambda: self._load_image("foto", self.lbl_foto))
        self.btn_ine.clicked.connect(lambda: self._load_image("ine", self.lbl_ine))
        self.btn_licencia.clicked.connect(lambda: self._load_image("licencia", self.lbl_licencia))

        self._load_existing_images()

        # ---------- GRUPOS ----------
        box_general = QGroupBox("Datos generales")
        f1 = QFormLayout(box_general)
        f1.addRow("Nombre:", self.inp_nombre)
        f1.addRow("Apellido:", self.inp_apellido)
        f1.addRow("Usuario:", self.inp_usuario)
        f1.addRow("Contraseña:", self.inp_password)
        f1.addRow("Rol:", self.inp_rol)

        box_contacto = QGroupBox("Contacto")
        f2 = QFormLayout(box_contacto)
        f2.addRow("Teléfono:", self.inp_telefono)
        f2.addRow("Email:", self.inp_email)
        f2.addRow("RFC:", self.inp_rfc)

        box_medico = QGroupBox("Información médica")
        f3 = QFormLayout(box_medico)
        f3.addRow("Tipo de sangre:", self.inp_tipo_sangre)
        f3.addRow("Alergias:", self.inp_alergias)
        f3.addRow("Enfermedades:", self.inp_enfermedades)
        f3.addRow("Notas médicas:", self.inp_notas)
        f3.addRow("", self.chk_apto)

        box_docs = QGroupBox("Documentos")
        docs = QGridLayout(box_docs)
        docs.addWidget(self.lbl_foto, 0, 0)
        docs.addWidget(self.btn_foto, 1, 0)
        docs.addWidget(self.lbl_ine, 0, 1)
        docs.addWidget(self.btn_ine, 1, 1)
        docs.addWidget(self.lbl_licencia, 0, 2)
        docs.addWidget(self.btn_licencia, 1, 2)

        grid = QGridLayout()
        grid.addWidget(box_general, 0, 0)
        grid.addWidget(box_contacto, 0, 1)
        grid.addWidget(box_medico, 1, 0, 1, 2)
        grid.addWidget(box_docs, 2, 0, 1, 2)

        content_layout.addLayout(grid)
        content_layout.addStretch()

        # ---------- BOTONES ----------
        btn_save = QPushButton("Aceptar")
        btn_cancel = QPushButton("Cancelar")
        btn_save.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(btn_save)
        btns.addWidget(btn_cancel)

        main = QVBoxLayout(self)
        main.addWidget(scroll)
        main.addLayout(btns)

        if not self.is_edit:
            self.inp_usuario.setFocus()

    # ---------- HELPERS ----------

    def _img_label(self):
        lbl = QLabel("Sin imagen")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFixedSize(120, 120)
        lbl.setStyleSheet("border:1px dashed #999;")
        return lbl

    def _load_image(self, field, lbl):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg)"
        )
        if path:
            self.data[field] = path
            pix = QPixmap(path).scaled(
                120, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            lbl.setPixmap(pix)

    def _load_existing_images(self):
        for field, lbl in (
            ("foto", self.lbl_foto),
            ("ine", self.lbl_ine),
            ("licencia", self.lbl_licencia)
        ):
            path = self.data.get(field)
            if path and os.path.exists(path):
                pix = QPixmap(path).scaled(
                    120, 120,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                lbl.setPixmap(pix)

    # ---------- VALIDACIÓN ----------

    def accept(self):
        if not self.inp_nombre.text().strip() \
           or not self.inp_apellido.text().strip() \
           or not self.inp_usuario.text().strip():
            QMessageBox.warning(self, "Error", "Nombre, apellido y usuario son obligatorios")
            return

        if not self.is_edit and not self.inp_password.text().strip():
            QMessageBox.warning(self, "Error", "La contraseña es obligatoria")
            return

        if self.inp_email.text() and not is_valid_email(self.inp_email.text()):
            QMessageBox.warning(self, "Error", "Email inválido")
            return

        if self.inp_rfc.text() and not is_valid_rfc(self.inp_rfc.text()):
            QMessageBox.warning(self, "Error", "RFC inválido")
            return

        super().accept()

    # ---------- DATA (🔥 LO QUE FALTABA) ----------

    def get_data(self):
        completos = all([
            self.inp_nombre.text().strip(),
            self.inp_apellido.text().strip(),
            self.inp_usuario.text().strip(),
            self.data.get("foto"),
            self.data.get("ine"),
            self.data.get("licencia")
        ])

        return {
            "id": self.data.get("id"),
            "nombre": self.inp_nombre.text().strip(),
            "apellido": self.inp_apellido.text().strip(),
            "usuario": self.inp_usuario.text().strip(),
            "password": self.inp_password.text().strip() or self.data.get("password"),
            "rol": self.inp_rol.currentText(),
            "telefono": self.inp_telefono.text().strip(),
            "email": self.inp_email.text().strip(),
            "rfc": self.inp_rfc.text().strip(),
            "tipo_sangre": self.inp_tipo_sangre.text().strip(),
            "alergias": self.inp_alergias.toPlainText().strip(),
            "enfermedades": self.inp_enfermedades.toPlainText().strip(),
            "notas_medicas": self.inp_notas.toPlainText().strip(),
            "apto_operar": 1 if self.chk_apto.isChecked() else 0,
            "foto": self.data.get("foto"),
            "ine": self.data.get("ine"),
            "licencia": self.data.get("licencia"),
            "licencia_num": self.data.get("licencia_num", ""),
            "licencia_exp": self.data.get("licencia_exp", ""),
            "estado_documentos": "Completos" if completos else "Pendiente",
            "synced": self.data.get("synced", 0),
            "last_sync": self.data.get("last_sync")
        }
