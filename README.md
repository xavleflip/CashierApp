# 🛒 CashierAPP

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org)
[![Framework](https://img.shields.io/badge/framework-PySide6-green.svg)](https://doc.qt.io/qtforpython/)
[![Database](https://img.shields.io/badge/database-SQLite-lightgrey.svg)](https://www.sqlite.org/)

**CashierAPP** adalah aplikasi manajemen kasir berbasis desktop yang dirancang untuk mempermudah proses pencatatan pesanan pelanggan dan pengelolaan data transaksi secara sistematis ke dalam database.

---

## 🚀 Fitur Utama

Aplikasi ini memiliki dua antarmuka utama yang dirancang untuk efisiensi operasional:

### 1. Tab New Order (Pencatatan Pesanan)
* **Manajemen Menu:** Memilih item menu menggunakan sistem *checkbox* yang intuitif.
* **Detail Pesanan:** Input kuantitas barang secara spesifik untuk setiap pesanan.
* **Custom Notes:** Fitur untuk menambahkan catatan khusus pada setiap item guna meminimalisir kesalahan pelayanan.
* **Automated Storage:** Seluruh pesanan akan langsung tersimpan secara otomatis ke dalam database SQLite.

### 2. Tab View Order (Visualisasi & Riwayat)
* **Data Transaksi:** Menampilkan detail riwayat pesanan yang telah dilakukan secara transparan.
* **Analisis Penjualan:** Dilengkapi dengan grafik statistik penjualan bulanan yang diupdate harian menggunakan **Matplotlib** untuk memantau performa bisnis secara visual.

---

## 🛠️ Arsitektur Teknologi

Aplikasi ini dibangun menggunakan kombinasi teknologi modern untuk menjamin stabilitas dan performa:

* **Language:** **Python** sebagai core logic aplikasi.
* **GUI Framework:** **PySide6 (Qt for Python)** untuk antarmuka yang modern dan responsif.
* **Styling:** Integrasi **HTML** untuk kustomisasi elemen visual tertentu.
* **Visualisasi Data:** **Matplotlib** untuk pembuatan grafik penjualan harian.
* **Database:** **SQLite** untuk penyimpanan data lokal yang ringan dan efisien.

---

## 📸 Antarmuka Aplikasi

> **Tips:** Masukkan file gambar kamu ke folder repositori dan ganti link di bawah ini agar muncul di halaman GitHub.

| Modul Pencatatan Pesanan | Grafik Analisis Penjualan |
| :---: | :---: |
| ![New Order Screen](https://via.placeholder.com/400x250?text=Screenshot+New+Order) | ![Sales Chart](https://via.placeholder.com/400x250?text=Screenshot+Sales+Graph) |

---
