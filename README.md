# Bot-GIWA

Bot otomatis untuk melakukan **swap** dan **add liquidity** di jaringan GIWA.

## ✨ Fitur
- Swap otomatis (jumlah random setiap eksekusi)
- Add liquidity setelah swap
- Bisa looping (tentukan berapa kali swap + LP dijalankan)
- Support banyak wallet (isi di file `privatekey.txt`)

## 📦 Cara Install di VPS
```bash
# 1. Clone repo
git clone https://github.com/username/Bot-giwa.git
cd Bot-giwa

# 2. Update VPS dan install Python
apt update && apt upgrade -y
apt install python3 python3-pip git -y

# 3. Install library Python
pip3 install -r requirements.txt
# Jika requirements.txt belum ada, install manual:
pip3 install web3 colorama

# 4. Tambah private key
nano privatekey.txt
# Isi dengan private key wallet kamu (satu baris = satu key), contoh:
# 0xabc1234567890abcdef...
# 0xde9f876543210fedcba...
# Simpan dengan CTRL+O lalu keluar dengan CTRL+X

# 5. Jalankan bot
python3 run.py
# Nanti akan muncul pertanyaan:
# Mau berapa kali swap + LP per wallet?
# Contoh input 5 → bot akan jalankan swap + LP sebanyak 5 kali per wallet
Bot-giwa/
├── run.py            # Script utama bot
├── privatekey.txt    # File berisi private keys (jangan dishare!)
├── requirements.txt  # Dependencies Python
└── README.md         # Dokumentasi project
---

Kalau kamu copy langsung ke **README.md** GitHub → tampilannya rapi, instruksi instalasi langsung dalam 1 blok, nggak kepotong-potong ✅  

Mau aku bikinin sekalian isi `requirements.txt` biar user lain tinggal install tanpa error?
