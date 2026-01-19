import sqlite3

from datetime import datetime


def rupiah(n: int) -> str:
    return f"Rp{n:,}".replace(",", ".")

class Database:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def close(self):
        self.conn.close()

    def init_schema(self):
        cur = self.conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            total INTEGER NOT NULL
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            price INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            note TEXT,
            subtotal INTEGER NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
        );
        """)

        self.conn.commit()

    def generate_order_no(self) -> str:
        """
        Format: ORD-YYYYMMDD-001 (reset tiap hari)
        """
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"ORD-{today}-"

        cur = self.conn.cursor()
        row = cur.execute(
            "SELECT order_no FROM orders WHERE order_no LIKE ? ORDER BY id DESC LIMIT 1",
            (prefix + "%",)
        ).fetchone()

        if row is None:
            seq = 1
        else:
            last_no = row["order_no"]          # contoh: ORD-20260105-007
            last_seq = int(last_no.split("-")[-1])
            seq = last_seq + 1

        return f"{prefix}{seq:03d}"

    def create_order(self, items: list[dict]) -> tuple[int, str]:
        """
        items: [{name, price, qty, note}]
        return: (order_id, order_no)
        """
        if not items:
            raise ValueError("items kosong")

        order_no = self.generate_order_no()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total = 0
        for it in items:
            total += int(it["price"]) * int(it["qty"])

        cur = self.conn.cursor()
        try:
            cur.execute("BEGIN;")

            cur.execute(
                "INSERT INTO orders(order_no, created_at, total) VALUES(?, ?, ?)",
                (order_no, created_at, total)
            )
            order_id = cur.lastrowid

            rows = []
            for it in items:
                price = int(it["price"])
                qty = int(it["qty"])
                subtotal = price * qty
                note = (it.get("note") or "").strip()
                rows.append((order_id, it["name"], price, qty, note, subtotal))

            cur.executemany(
                "INSERT INTO order_items(order_id, item_name, price, qty, note, subtotal) VALUES(?, ?, ?, ?, ?, ?)",
                rows
            )

            cur.execute("COMMIT;")
            return order_id, order_no
        except Exception:
            cur.execute("ROLLBACK;")
            raise

    def get_order_by_id(self, order_id: int):
        """
        Mengambil data order berdasarkan ID.
        Return: sqlite3.Row atau None jika tidak ditemukan.
        """
        cur = self.conn.cursor()
        return cur.execute("""
            SELECT id, order_no, created_at, total
            FROM orders
            WHERE id = ?
        """, (order_id,)).fetchone()

    def list_orders(self):
        cur = self.conn.cursor()
        return cur.execute("""
            SELECT id, order_no, created_at, total
            FROM orders
            ORDER BY id DESC
        """).fetchall()

    def list_order_items(self, order_id: int):
        cur = self.conn.cursor()
        return cur.execute("""
            SELECT item_name, price, qty, note, subtotal
            FROM order_items
            WHERE order_id = ?
            ORDER BY id ASC
        """, (order_id,)).fetchall()

    def get_monthly_sales(self, month: int, year: int) -> list[tuple[int, int]]:
        cur = self.conn.cursor()
        rows = cur.execute("""
            SELECT CAST(strftime('%d', created_at) AS INTEGER) AS day,
                   SUM(total) AS daily_total
            FROM orders
            WHERE strftime('%Y', created_at) = ?
              AND strftime('%m', created_at) = ?
            GROUP BY day
            ORDER BY day
        """, (str(year), f"{month:02d}")).fetchall()
        return [(row[0], row[1]) for row in rows]

    def delete_order(self, order_id: int) -> bool:
        cur = self.conn.cursor()
        try:
            cur.execute("BEGIN;")
            
            # First, delete all items associated with this order
            cur.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
            
            # Then, delete the order header
            cur.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            
            cur.execute("COMMIT;")
            return True
        except Exception:
            cur.execute("ROLLBACK;")
            raise

