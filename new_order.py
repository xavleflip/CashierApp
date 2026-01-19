from database_handler import Database, rupiah

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,QVBoxLayout, QGridLayout, 
    QHBoxLayout,QPushButton, QCheckBox, 
    QLabel,QLineEdit, QFrame, 
    QSpinBox,QMessageBox
)


# -------------------- Tab 1: New Order --------------------
class NewOrderWidget(QWidget):
    order_saved = Signal()  # emit saat order tersimpan

    def __init__(self, db: Database):
        super().__init__()
        self.db = db

        self.menu_data = [
            ("Nasi Kuning", 10000),
            ("Nasi Goreng", 12000),
            ("Mie Tiaw Goreng", 15000),
            ("Bubur Ayam", 8000),
            ("Lontong Sayur", 10000),
            ("Es Teh", 3000),
            ("Teh Hangat", 5000),
            ("Air Mineral", 4000),
            ("Es Jeruk Kecil", 7000),
        ]

        self.rows = []  # {cb, qty, note, price, name}

        vlayout = QVBoxLayout(self)

        title = QLabel("PEMESANAN MENU WARUNG SARAPAN MAK UDE")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 25px;")
        vlayout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        vlayout.addWidget(line)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(8)

        hdr_item = QLabel("Item")
        hdr_qty = QLabel("Jumlah")
        hdr_note = QLabel("Catatan")
        for hdr in (hdr_item, hdr_qty, hdr_note):
            hdr.setStyleSheet("font-weight: bold;")
        grid.addWidget(hdr_item, 0, 0)
        grid.addWidget(hdr_qty, 0, 1)
        grid.addWidget(hdr_note, 0, 2)

        for i, (name, price) in enumerate(self.menu_data, start=1):
            cb = QCheckBox(f"{name} - {rupiah(price)}")

            qty = QSpinBox()
            qty.setMinimum(1)
            qty.setMaximum(10)     
            qty.setValue(1)
            qty.setFixedWidth(80)
            qty.setFixedHeight(40)

            note = QLineEdit()
            note.setPlaceholderText("contoh: tanpa sambal, pedas, dll")
            note.setFixedHeight(40)

            # default terkunci jika belum dicentang
            self.set_row_enabled(qty, note, enabled=False)

            grid.addWidget(cb, i, 0)
            grid.addWidget(qty, i, 1)
            grid.addWidget(note, i, 2)

            row = {"cb": cb, "qty": qty, "note": note, "price": price, "name": name}
            self.rows.append(row)

            cb.toggled.connect(lambda checked, r=row: self.on_item_toggled(checked, r))

        vlayout.addLayout(grid)

        # Bottom controls
        bottom = QHBoxLayout()
        self.btn_total = QPushButton("Hitung Total")
        self.btn_save = QPushButton("Simpan Pesanan")
        self.btn_reset = QPushButton("Reset")

        self.btn_total.clicked.connect(self.hitung)
        self.btn_save.clicked.connect(self.simpan_pesanan)
        self.btn_reset.clicked.connect(self.reset_form)

        self.total = QLabel("Total: Rp0")
        self.total.setStyleSheet("font-weight: bold; font-size: 14px;")

        bottom.addWidget(self.btn_total)
        bottom.addWidget(self.btn_save)
        bottom.addWidget(self.btn_reset)
        bottom.addStretch(1)
        bottom.addWidget(self.total)
        vlayout.addLayout(bottom)

        vlayout.addStretch(1)

    def set_row_enabled(self, qty: QSpinBox, note: QLineEdit, enabled: bool):
        # Jika belum checked -> tidak bisa interaksi
        qty.setEnabled(enabled)

        note.setEnabled(enabled)
        note.setReadOnly(not enabled)

        if not enabled:
            qty.setValue(1)
            note.clear()

    def on_item_toggled(self, checked: bool, row: dict):
        self.set_row_enabled(row["qty"], row["note"], enabled=checked)
        self.hitung()

    def hitung(self):
        total = 0
        for row in self.rows:
            if row["cb"].isChecked():
                total += row["price"] * row["qty"].value()
        self.total.setText(f"Total: {rupiah(total)}")

    def reset_form(self):
        for row in self.rows:
            row["cb"].setChecked(False)
        self.hitung()

    def simpan_pesanan(self):
        items = []
        for row in self.rows:
            if row["cb"].isChecked():
                items.append({
                    "name": row["name"],
                    "price": row["price"],
                    "qty": row["qty"].value(),
                    "note": row["note"].text().strip()
                })

        if not items:
            QMessageBox.information(self, "Info", "Belum ada item yang dipilih.")
            return

        try:
            order_id, order_no = self.db.create_order(items)
            QMessageBox.information(self, "Sukses", f"Pesanan tersimpan!\nNomor: {order_no}")
            self.reset_form()
            self.order_saved.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan pesanan:\n{e}")

