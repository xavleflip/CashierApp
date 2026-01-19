from database_handler import Database, rupiah
from receipt_printer import ReceiptPrinter

import calendar
from datetime import datetime
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox, QGroupBox, QComboBox, QSpinBox,
    QScrollArea, QFrame, QSizePolicy
)


# -------------------- Tab 2: View Orders --------------------
class ViewOrdersWidget(QWidget):
    """Widget for viewing orders, order details, and sales analytics."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.current_order_id = None
        self.current_order_no = None
        
        # Initialize receipt printer with store configuration
        self.receipt_printer = ReceiptPrinter(
            nama_toko="WARUNG SARAPAN MAK UDE",
            alamat="Jl. Adi Sucipto Gg. Hj. Aminah",
            no_telp="Tel: (021) 1234-5678"
        )

        # Main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ==================== SCROLL AREA WRAPPER ====================
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Content widget inside scroll area
        content_widget = QWidget()
        content_widget.setObjectName("scrollContent")
        vlayout = QVBoxLayout(content_widget)
        vlayout.setSpacing(12)
        vlayout.setContentsMargins(16, 16, 16, 16)

        # ==================== ORDERS TABLE SECTION ====================
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
        self.tbl_orders.setMinimumHeight(250)
        self.tbl_orders.setMaximumHeight(350)
        self.tbl_orders.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        vlayout.addWidget(self.tbl_orders)

        # ==================== ORDER DETAIL SECTION ====================
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
        self.tbl_detail.setMinimumHeight(320)
        self.tbl_detail.setMaximumHeight(550)
        self.tbl_detail.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.tbl_detail.setVisible(False)
        vlayout.addWidget(self.tbl_detail)

        # ==================== ACTION BUTTONS SECTION ====================
        btn_layout = QHBoxLayout()
        
        self.btn_print = QPushButton("CETAK STRUK")
        self.btn_print.setFixedHeight(45)
        self.btn_print.setEnabled(False)  # Disabled sampai ada order dipilih
        self.btn_print.clicked.connect(self.on_print_clicked)
        btn_layout.addWidget(self.btn_print)
        
        self.btn_delete = QPushButton("HAPUS PESANAN")
        self.btn_delete.setFixedHeight(45)
        self.btn_delete.setObjectName("dangerButton")  # Use danger style from QSS
        self.btn_delete.setEnabled(False)  # Disabled sampai ada order dipilih
        self.btn_delete.clicked.connect(self.on_delete_clicked)
        btn_layout.addWidget(self.btn_delete)
        
        btn_layout.addStretch(1)
        vlayout.addLayout(btn_layout)

        # ==================== SALES ANALYTICS SECTION ====================
        analytics_group = QGroupBox("GRAFIK PENJUALAN")
        analytics_layout = QVBoxLayout(analytics_group)

        # Month/Year selector row
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Bulan:"))
        
        self.cmb_month = QComboBox()
        months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                  "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        self.cmb_month.addItems(months)
        self.cmb_month.setCurrentIndex(datetime.now().month - 1)
        filter_layout.addWidget(self.cmb_month)
        
        filter_layout.addWidget(QLabel("Tahun:"))
        self.spn_year = QSpinBox()
        self.spn_year.setRange(2020, 2050)
        self.spn_year.setValue(datetime.now().year)
        filter_layout.addWidget(self.spn_year)
        
        filter_layout.addStretch(1)
        analytics_layout.addLayout(filter_layout)

        # Matplotlib chart canvas with fixed minimum height
        self.figure = Figure(figsize=(8, 3), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setMinimumHeight(280)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        analytics_layout.addWidget(self.canvas)

        vlayout.addWidget(analytics_group)

        # Add stretch at the end to push content up
        vlayout.addStretch(1)

        # Set the content widget in the scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # ==================== SIGNAL CONNECTIONS ====================
        self.cmb_month.currentIndexChanged.connect(self.refresh_sales_chart)
        self.spn_year.valueChanged.connect(self.refresh_sales_chart)
        self.tbl_orders.itemSelectionChanged.connect(self.on_order_selected)

        self.reload_orders()
        self.refresh_sales_chart()  # Initial chart render


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
        self.btn_delete.setEnabled(False)

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
        self.btn_delete.setEnabled(True)

    def on_delete_clicked(self):
        """Handler untuk tombol hapus pesanan."""
        if self.current_order_id is None:
            QMessageBox.warning(self, "Peringatan", "Pilih pesanan terlebih dahulu.")
            return

        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus pesanan {self.current_order_no}?\n\n"
            "Tindakan ini tidak dapat dibatalkan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.db.delete_order(self.current_order_id)
                QMessageBox.information(self, "Sukses", f"Pesanan {self.current_order_no} berhasil dihapus.")
                self.reload_orders()
                self.refresh_sales_chart()  # Refresh chart after deletion
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal menghapus pesanan:\n{e}")

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

    # ==================== SALES ANALYTICS ====================

    def refresh_sales_chart(self):
        """Refresh the sales bar chart based on selected month/year."""
        month = self.cmb_month.currentIndex() + 1  # 1-indexed
        year = self.spn_year.value()
        
        # Get month name for title
        month_names = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                       "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        month_name = month_names[month - 1]
        
        # Get number of days in the month
        _, num_days = calendar.monthrange(year, month)
        
        # Fetch sales data from database
        sales_data = self.db.get_monthly_sales(month, year)
        sales_dict = {day: total for day, total in sales_data}
        
        # Zero-fill missing days
        days = list(range(1, num_days + 1))
        totals = [sales_dict.get(day, 0) for day in days]
        
        # Clear and redraw the figure
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Create bar chart
        bars = ax.bar(days, totals, color='#4A90D9', edgecolor='#2E5D8C', linewidth=0.5)
        
        # Style the chart
        ax.set_xlabel('Tanggal', fontsize=9)
        ax.set_ylabel('Total Penjualan (Rp)', fontsize=9)
        ax.set_title(f'GRAFIK PENJUALAN: {month_name} {year}', fontsize=11, fontweight='bold')
        
        # X-axis: show all days but rotate labels if crowded
        ax.set_xticks(days)
        ax.set_xticklabels(days, rotation=45 if num_days > 20 else 0, ha='right' if num_days > 20 else 'center', fontsize=7)
        
        # Y-axis: format as currency
        ax.yaxis.set_major_formatter(lambda x, p: f'Rp{x/1000:.0f}K' if x >= 1000 else f'Rp{x:.0f}')
        
        # Add grid lines for readability
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Tight layout to prevent label cutoff
        self.figure.tight_layout()
        
        # Redraw the canvas
        self.canvas.draw()

    # ==================== PRINTING FUNCTIONALITY ====================

    def on_print_clicked(self):
        """Handler untuk tombol cetak struk."""
        if self.current_order_id is None:
            QMessageBox.warning(self, "Peringatan", "Pilih pesanan terlebih dahulu.")
            return

        try:
            # Fetch order data from database
            order = self.db.get_order_by_id(self.current_order_id)
            if order is None:
                raise ValueError(f"Order dengan ID {self.current_order_id} tidak ditemukan.")
            
            items = self.db.list_order_items(self.current_order_id)
            
            # Delegate printing to ReceiptPrinter
            self.receipt_printer.print_receipt(self, order, items)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mencetak struk:\n{e}")
