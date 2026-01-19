from database_handler import rupiah

from PySide6.QtCore import QSizeF, QMarginsF
from PySide6.QtGui import QPageLayout, QPageSize, QTextDocument, QAction
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PySide6.QtWidgets import QWidget


class ReceiptPrinter:
    
    # Default paper configuration for thermal printers
    DEFAULT_PAPER_WIDTH_MM = 80
    DEFAULT_PAPER_HEIGHT_MM = 2500  # Long for continuous roll

    def __init__(
        self,
        nama_toko: str = "WARUNG SARAPAN MAK UDE",
        alamat: str = "Jl. Adi Sucipto Gg. Hj. Aminah",
        no_telp: str = "Tel: (021) 1234-5678"
    ):

        self.nama_toko = nama_toko
        self.alamat = alamat
        self.no_telp = no_telp

    def print_receipt(self, parent_widget: QWidget, order: dict, items: list) -> None:
        #Show print preview dialog for the receipt.
        html_content = self.generate_receipt_html(order, items)
        printer = QPrinter(QPrinter.ScreenResolution)

        # Configure paper size for thermal printer
        paper_height = 300  
        custom_size = QPageSize(
            QSizeF(self.DEFAULT_PAPER_WIDTH_MM, paper_height),
            QPageSize.Millimeter
        )
        # Add small margins to prevent content from being clipped at edges
        page_layout = QPageLayout(
            custom_size,
            QPageLayout.Portrait,
            QMarginsF(5, 5, 5, 5),
            QPageLayout.Millimeter
        )
        printer.setPageLayout(page_layout)

        # preview dialog
        preview_dialog = QPrintPreviewDialog(printer, parent_widget)
        preview_dialog.setWindowTitle(f"Preview Struk - {order['order_no']}")
        preview_dialog.resize(450, 700)

        for action in preview_dialog.findChildren(QAction):
            if action.text() and 'width' in action.text().lower():
                action.trigger()
                break

        # Connect paintRequested signal to render document
        preview_dialog.paintRequested.connect(
            lambda p: self._render_to_printer(p, html_content)
        )

        preview_dialog.exec()

    def generate_receipt_html(self, order: dict, items: list) -> str:
        """
        Generate HTML string for receipt.
        Uses HTML4 format compatible with Qt's QTextDocument.
        (No flexbox, CSS grid - uses tables with align attributes)
        """
        order_no = order["order_no"]
        created_at = order["created_at"]
        total = int(order["total"])

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
            if note:
                items_rows += f"""
                <tr>
                    <td colspan="4" align="left">
                        <font size="2" color="#666666">&nbsp;&nbsp;Note: {note}</font>
                    </td>
                </tr>
                """

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: 'Courier New', Courier, monospace; font-size: 12pt; margin: 0; padding: 0;">

<!-- HEADER - Enhanced prominent styling -->
<table width="100%" cellpadding="4" cellspacing="0">
    <tr>
        <td align="center">
            <font size="2">================================</font>
        </td>
    </tr>
    <tr>
        <td align="center">
            <font size="6"><b>{self.nama_toko}</b></font>
        </td>
    </tr>
    <tr>
        <td align="center">
            <font size="3"><b>{self.alamat}</b></font>
        </td>
    </tr>
    <tr>
        <td align="center">
            <font size="3">{self.no_telp}</font>
        </td>
    </tr>
    <tr>
        <td align="center">
            <font size="2">================================</font>
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

    def _render_to_printer(self, printer: QPrinter, html_content: str) -> None:
        
        #Render HTML content to printer using QTextDocument
        document = QTextDocument()

        # Use Point units for accuracy with QTextDocument
        page_rect = printer.pageRect(QPrinter.Point)
        document.setPageSize(page_rect.size())

        document.setTextWidth(page_rect.width())

        document.setHtml(html_content)
        document.print_(printer)
