"""
Receipt Printer Module
Handles receipt HTML generation and printing functionality.
Extracted from ViewOrdersWidget for better separation of concerns.
"""

from database_handler import rupiah

from PySide6.QtCore import QSizeF, QMarginsF
from PySide6.QtGui import QPageLayout, QPageSize, QTextDocument, QAction
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PySide6.QtWidgets import QWidget


class ReceiptPrinter:
    """
    Handles receipt generation and printing for orders.
    Configurable store information and thermal printer settings.
    """

    # Default paper configuration for thermal printers
    DEFAULT_PAPER_WIDTH_MM = 80
    DEFAULT_PAPER_HEIGHT_MM = 3000  # Long for continuous roll

    def __init__(
        self,
        nama_toko: str = "WARUNG SARAPAN MAK UDE",
        alamat: str = "Jl. Adi Sucipto Gg. Hj. Aminah",
        no_telp: str = "Tel: (021) 1234-5678"
    ):
        """
        Initialize ReceiptPrinter with store information.
        
        Args:
            nama_toko: Name of the store for receipt header
            alamat: Store address line
            no_telp: Store phone number
        """
        self.nama_toko = nama_toko
        self.alamat = alamat
        self.no_telp = no_telp

    def print_receipt(self, parent_widget: QWidget, order: dict, items: list) -> None:
        """
        Show print preview dialog for the receipt.
        
        Args:
            parent_widget: Parent widget for the dialog
            order: Order data dictionary with keys: order_no, created_at, total
            items: List of order items with keys: item_name, qty, price, subtotal, note
        """
        html_content = self.generate_receipt_html(order, items)

        # Setup printer for thermal printer (58mm or 80mm)
        # IMPORTANT: Use ScreenResolution to avoid scaling issues
        printer = QPrinter(QPrinter.ScreenResolution)

        # Configure paper size for thermal printer
        # Using shorter height for better preview (will still fit content dynamically)
        paper_height = 300  # Reasonable height for preview
        custom_size = QPageSize(
            QSizeF(self.DEFAULT_PAPER_WIDTH_MM, paper_height),
            QPageSize.Millimeter
        )
        # Add small margins to prevent content from being clipped at edges
        page_layout = QPageLayout(
            custom_size,
            QPageLayout.Portrait,
            QMarginsF(5, 5, 5, 5),  # 5mm margins on all sides
            QPageLayout.Millimeter
        )
        printer.setPageLayout(page_layout)

        # Create preview dialog
        preview_dialog = QPrintPreviewDialog(printer, parent_widget)
        preview_dialog.setWindowTitle(f"Preview Struk - {order['order_no']}")
        preview_dialog.resize(450, 700)

        # Set Fit to Width as default zoom
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
        
        Args:
            order: Order data dictionary
            items: List of order items
            
        Returns:
            HTML string for the receipt
        """
        order_no = order["order_no"]
        created_at = order["created_at"]
        total = int(order["total"])

        # Build items table rows with HTML4 attributes
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
            # If there's a note, show it on a separate row
            if note:
                items_rows += f"""
                <tr>
                    <td colspan="4" align="left">
                        <font size="2" color="#666666">&nbsp;&nbsp;Note: {note}</font>
                    </td>
                </tr>
                """

        # HTML with HTML4 format compatible with Qt Rich Text
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
        """
        Render HTML content to printer using QTextDocument.
        
        Args:
            printer: QPrinter instance
            html_content: HTML string to render
        """
        document = QTextDocument()

        # Use Point units for accuracy with QTextDocument
        page_rect = printer.pageRect(QPrinter.Point)
        document.setPageSize(page_rect.size())

        # Set text width for content flow
        document.setTextWidth(page_rect.width())

        # Set HTML content
        document.setHtml(html_content)

        # Print document
        document.print_(printer)
