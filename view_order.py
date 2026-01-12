from database_handler import Database, rupiah

from PySide6.QtCore import Qt, QSizeF, QMarginsF
from PySide6.QtGui import QPageLayout, QPageSize, QTextDocument, QAction
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox
)


# -------------------- Tab 2: View Orders --------------------
class ViewOrdersWidget(QWidget):
    # Konfigurasi Toko (bisa dipindahkan ke config file)
    STORE_NAME = "WARUNG SARAPAN MAK UDE"
    STORE_ADDRESS = "Jl. Adi Sucipto Gg. Hj. Aminah"
    STORE_PHONE = "Tel: (021) 1234-5678"

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.current_order_id = None
        self.current_order_no = None

        vlayout = QVBoxLayout(self)

        title = QLabel("DAFTAR PESANAN")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        vlayout.addWidget(title)

        # Tabel orders (tampilan awal)
        self.tbl_orders = QTableWidget()
        self.tbl_orders.setColumnCount(3)
        self.tbl_orders.setHorizontalHeaderLabels(["Nomor Pesanan", "Waktu Pesanan", "Total Harga"])
        self.tbl_orders.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbl_orders.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tbl_orders.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tbl_orders.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_orders.setSelectionMode(QTableWidget.SingleSelection)
        self.tbl_orders.setEditTriggers(QTableWidget.NoEditTriggers)
        vlayout.addWidget(self.tbl_orders)

        # Detail label + tabel detail (awalnya disembunyikan)
        self.lbl_detail = QLabel("Detail Pesanan: (pilih salah satu pesanan)")
        self.lbl_detail.setStyleSheet("font-weight: bold;")
        vlayout.addWidget(self.lbl_detail)

        self.tbl_detail = QTableWidget()
        self.tbl_detail.setColumnCount(4)
        self.tbl_detail.setHorizontalHeaderLabels(["Item", "Jumlah", "Catatan", "Subtotal"])
        self.tbl_detail.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tbl_detail.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbl_detail.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tbl_detail.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tbl_detail.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_detail.setVisible(False)
        vlayout.addWidget(self.tbl_detail)

        # Tombol Print Receipt
        btn_layout = QHBoxLayout()
        self.btn_print = QPushButton("🖨️ Cetak Struk")
        self.btn_print.setFixedHeight(35)
        self.btn_print.setEnabled(False)  # Disabled sampai ada order dipilih
        self.btn_print.clicked.connect(self.on_print_clicked)
        btn_layout.addWidget(self.btn_print)
        btn_layout.addStretch(1)
        vlayout.addLayout(btn_layout)

        self.tbl_orders.itemSelectionChanged.connect(self.on_order_selected)

        self.reload_orders()

    def reload_orders(self):
        orders = self.db.list_orders()
        self.tbl_orders.setRowCount(len(orders))

        for r, o in enumerate(orders):
            # Simpan order_id di UserRole cell pertama supaya gampang diambil saat klik
            it_no = QTableWidgetItem(o["order_no"])
            it_no.setData(Qt.UserRole, int(o["id"]))

            it_time = QTableWidgetItem(o["created_at"])
            it_total = QTableWidgetItem(rupiah(int(o["total"])))
            it_total.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.tbl_orders.setItem(r, 0, it_no)
            self.tbl_orders.setItem(r, 1, it_time)
            self.tbl_orders.setItem(r, 2, it_total)

        # Reset detail
        self.current_order_id = None
        self.current_order_no = None
        self.lbl_detail.setText("Detail Pesanan: (pilih salah satu pesanan)")
        self.tbl_detail.setRowCount(0)
        self.tbl_detail.setVisible(False)
        self.btn_print.setEnabled(False)

    def on_order_selected(self):
        items = self.tbl_orders.selectedItems()
        if not items:
            return

        # karena SelectRows, selectedItems bisa banyak; ambil cell kolom 0 dari row terpilih
        row = self.tbl_orders.currentRow()
        if row < 0:
            return

        it_no = self.tbl_orders.item(row, 0)
        order_id = int(it_no.data(Qt.UserRole))
        order_no = it_no.text()

        self.current_order_id = order_id
        self.current_order_no = order_no
        self.load_order_detail(order_id, order_no)
        self.btn_print.setEnabled(True)

    def load_order_detail(self, order_id: int, order_no: str):
        details = self.db.list_order_items(order_id)

        self.lbl_detail.setText(f"Detail Pesanan: {order_no}")
        self.tbl_detail.setVisible(True)
        self.tbl_detail.setRowCount(len(details))

        for r, d in enumerate(details):
            it_name = QTableWidgetItem(d["item_name"])
            it_qty = QTableWidgetItem(str(int(d["qty"])))
            it_qty.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            it_note = QTableWidgetItem(d["note"] or "")
            it_sub = QTableWidgetItem(rupiah(int(d["subtotal"])))
            it_sub.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self.tbl_detail.setItem(r, 0, it_name)
            self.tbl_detail.setItem(r, 1, it_qty)
            self.tbl_detail.setItem(r, 2, it_note)
            self.tbl_detail.setItem(r, 3, it_sub)

    # ==================== PRINTING FUNCTIONALITY ====================

    def on_print_clicked(self):
        """Handler untuk tombol cetak struk."""
        if self.current_order_id is None:
            QMessageBox.warning(self, "Peringatan", "Pilih pesanan terlebih dahulu.")
            return

        try:
            self.print_receipt(self.current_order_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mencetak struk:\n{e}")

    def print_receipt(self, order_id: int):
        """
        Generate dan print struk untuk order tertentu.
        Menggunakan QPrintPreviewDialog untuk preview sebelum print.
        """
        # Ambil data order dari database
        order = self.db.get_order_by_id(order_id)
        if order is None:
            raise ValueError(f"Order dengan ID {order_id} tidak ditemukan.")

        items = self.db.list_order_items(order_id)

        # Generate HTML receipt
        html_content = self._generate_receipt_html(order, items)

        # Setup printer untuk thermal printer (58mm atau 80mm)
        # PENTING: Gunakan ScreenResolution untuk menghindari scaling issue
        printer = QPrinter(QPrinter.ScreenResolution)

        # Konfigurasi ukuran kertas thermal (80mm width - lebih umum)
        # Tinggi dibuat sangat panjang untuk roll paper (continuous feed)
        paper_width_mm = 80
        paper_height_mm = 3000  # Tinggi sangat panjang untuk continuous roll

        custom_size = QPageSize(QSizeF(paper_width_mm, paper_height_mm), QPageSize.Millimeter)
        page_layout = QPageLayout(
            custom_size,
            QPageLayout.Portrait,
            QMarginsF(0, 0, 0, 0),  # ZERO margins - content fills full width
            QPageLayout.Millimeter
        )
        printer.setPageLayout(page_layout)

        # Buat preview dialog
        preview_dialog = QPrintPreviewDialog(printer, self)
        preview_dialog.setWindowTitle(f"Preview Struk - {order['order_no']}")
        preview_dialog.resize(450, 700)

        # Set Fit to Width sebagai default zoom
        # QPrintPreviewDialog menyediakan toolbar actions, kita cari dan trigger FitToWidth
        for action in preview_dialog.findChildren(QAction):
            if action.text() and 'width' in action.text().lower():
                action.trigger()
                break

        # Connect paintRequested signal untuk render dokumen
        preview_dialog.paintRequested.connect(
            lambda p: self._render_receipt_to_printer(p, html_content, paper_width_mm)
        )

        preview_dialog.exec()

    def _generate_receipt_html(self, order, items) -> str:
        """
        Generate HTML string untuk struk/receipt.
        Format: Header -> Items Table -> Footer
        
        PENTING: Qt's QTextDocument hanya mendukung subset HTML4.
        - Tidak support: flexbox, CSS grid, banyak CSS property
        - Gunakan: <table> dengan align attribute, font tag, inline styles sederhana
        """
        order_no = order["order_no"]
        created_at = order["created_at"]
        total = int(order["total"])

        # Build items table rows dengan HTML4 attributes
        items_rows = ""
        for item in items:
            item_name = item["item_name"]
            qty = int(item["qty"])
            price = int(item["price"])
            subtotal = int(item["subtotal"])
            note = item["note"] or ""

            items_rows += f"""
            <tr>
                <td align="left" valign="top">{item_name}</td>
                <td align="center" valign="top">{qty}</td>
                <td align="right" valign="top">{rupiah(price)}</td>
                <td align="right" valign="top">{rupiah(subtotal)}</td>
            </tr>
            """
            # Jika ada catatan, tampilkan di baris terpisah
            if note:
                items_rows += f"""
                <tr>
                    <td colspan="4" align="left">
                        <font size="2" color="#666666">&nbsp;&nbsp;Note: {note}</font>
                    </td>
                </tr>
                """

        # HTML dengan format HTML4 yang compatible dengan Qt Rich Text
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: 'Courier New', Courier, monospace; font-size: 12pt; margin: 0; padding: 0;">

<!-- HEADER - Menggunakan table untuk centering -->
<table width="100%" cellpadding="2" cellspacing="0">
    <tr>
        <td align="center">
            <font size="4"><b>{self.STORE_NAME}</b></font>
        </td>
    </tr>
    <tr>
        <td align="center">
            <font size="2">{self.STORE_ADDRESS}</font>
        </td>
    </tr>
    <tr>
        <td align="center">
            <font size="2">{self.STORE_PHONE}</font>
        </td>
    </tr>
</table>

<!-- Separator -->
<table width="100%" cellpadding="0" cellspacing="0">
    <tr><td><hr></td></tr>
</table>

<!-- ORDER INFO -->
<table width="100%" cellpadding="2" cellspacing="0">
    <tr>
        <td width="40%" align="left"><b>No. Transaksi:</b></td>
        <td width="60%" align="left">{order_no}</td>
    </tr>
    <tr>
        <td align="left"><b>Tanggal:</b></td>
        <td align="left">{created_at}</td>
    </tr>
</table>

<!-- Separator -->
<table width="100%" cellpadding="0" cellspacing="0">
    <tr><td><hr></td></tr>
</table>

<!-- ITEMS TABLE -->
<table width="100%" cellpadding="3" cellspacing="0" border="0">
    <tr>
        <td width="40%" align="left"><b><u>Item</u></b></td>
        <td width="15%" align="center"><b><u>Qty</u></b></td>
        <td width="20%" align="right"><b><u>Harga</u></b></td>
        <td width="25%" align="right"><b><u>Subtotal</u></b></td>
    </tr>
    {items_rows}
</table>

<!-- Separator -->
<table width="100%" cellpadding="0" cellspacing="0">
    <tr><td><hr></td></tr>
</table>

<!-- TOTAL SECTION -->
<table width="100%" cellpadding="3" cellspacing="0">
    <tr>
        <td align="right">
            <font size="4"><b>TOTAL: {rupiah(total)}</b></font>
        </td>
    </tr>
</table>

<!-- Separator -->
<table width="100%" cellpadding="0" cellspacing="0">
    <tr><td><hr></td></tr>
</table>

<!-- FOOTER -->
<table width="100%" cellpadding="2" cellspacing="0">
    <tr>
    </tr>
    <tr>
        <td align="center"><b>*** TERIMA KASIH ***</b></td>
    </tr>
    <tr>
    </tr>
</table>

</body>
</html>
        """
        return html

    def _render_receipt_to_printer(self, printer: QPrinter, html_content: str, paper_width_mm: int):
        """
        Render HTML content ke printer menggunakan QTextDocument.
        """
        document = QTextDocument()

        # Gunakan Point units untuk lebih akurat dengan QTextDocument
        page_rect = printer.pageRect(QPrinter.Point)
        document.setPageSize(page_rect.size())
        
        # Set text width agar content flow sesuai lebar halaman
        document.setTextWidth(page_rect.width())

        # Set HTML content
        document.setHtml(html_content)

        # Print document
        document.print_(printer)
