# Bot-GIWA

Bot otomatis untuk melakukan **swap** dan **add liquidity** di jaringan GIWA.

## ✨ Fitur
- Swap otomatis (jumlah random setiap eksekusi)
- Add liquidity setelah swap
- Bisa looping (tentukan berapa kali swap + LP dijalankan)
- Support banyak wallet (isi di file `privatekey.txt`)

---

## 📦 Cara Install di VPS

### 1. Clone repo
```bash
git clone https://github.com/username/Bot-giwa.git
cd Bot-giwa

2. Install dependencies

Update VPS dan install Python:

apt update && apt upgrade -y
apt install python3 python3-pip git -y

Install library Python:

pip3 install -r requirements.txt

> Jika requirements.txt belum ada, install manual:



pip3 install web3 colorama

3. Tambah private key

Buat file privatekey.txt di folder project:

nano privatekey.txt

Isi dengan private key wallet kamu.
Format: satu baris satu private key.
Contoh:

0xabc1234567890abcdef...
0xdef9876543210fedcba...

Simpan dengan CTRL+O lalu keluar dengan CTRL+X.


---

▶️ Cara Menjalankan

Jalankan bot dengan:

python3 run.py

Saat dijalankan, akan muncul pertanyaan:

Mau berapa kali swap + LP per wallet?

Contoh input 5 → maka bot akan menjalankan swap + LP sebanyak 5 kali untuk setiap wallet di privatekey.txt.


---

📂 Struktur Project

Bot-giwa/
│── run.py              # Script utama bot
│── privatekey.txt      # File berisi private keys (jangan dishare!)
│── requirements.txt    # Dependencies Python
│── README.md           # Dokumentasi project


---

⚠️ Disclaimer

Gunakan script ini dengan risiko ditanggung sendiri.
Pastikan kamu paham konsekuensi transaksi on-chain, termasuk biaya gas dan potensi kerugian.
