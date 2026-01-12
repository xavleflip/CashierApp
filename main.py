import sys

from database_handler import Database
from new_order import NewOrderWidget
from view_order import ViewOrdersWidget

from PySide6.QtWidgets import QMainWindow,QApplication, QTabWidget

DB_PATH = "pesanan_warung.db"


class MainWindow(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db

        self.setWindowTitle("Pemesanan Digital")
        self.setFixedSize(900, 650)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setDocumentMode(True)
        tabs.setMovable(False)

        self.new_order_tab = NewOrderWidget(self.db)
        self.view_orders_tab = ViewOrdersWidget(self.db)

        tabs.addTab(self.new_order_tab, "New Order")
        tabs.addTab(self.view_orders_tab, "View Orders")

        # Setelah simpan order -> refresh View Orders dan pindah tab
        self.new_order_tab.order_saved.connect(self.on_order_saved)

        self.tabs = tabs
        self.setCentralWidget(tabs)

    def on_order_saved(self):
        self.view_orders_tab.reload_orders()
        self.tabs.setCurrentWidget(self.view_orders_tab)


def main():
    app = QApplication(sys.argv)

    db = Database(DB_PATH)
    db.init_schema()

    w = MainWindow(db)
    w.show()

    code = app.exec()
    db.close()
    sys.exit(code)


if __name__ == "__main__":
    main()
