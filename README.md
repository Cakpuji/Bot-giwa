Bot-GIWA

Bot otomatis untuk melakukan **swap** dan **add liquidity** di jaringan GIWA.

---

## ✨ Fitur
- Swap otomatis (jumlah random setiap eksekusi)
- Add liquidity setelah swap
- Bisa looping (tentukan berapa kali swap + LP dijalankan)
- Support banyak wallet (isi di file `privatekey.txt`)

---

## 📦 Cara Install di VPS

### 1. Clone repo
```bash
git clone https://github.com/Cakpuji/Bot-giwa.git
cd Bot-giwa
```
2. Update VPS dan install Python
```
apt update && apt upgrade -y
apt install python3 python3-pip git -y
```
3. Install library Python
```
pip3 install -r requirements.txt
```
Kalau requirements.txt belum ada, install manual:
```
pip3 install web3 colorama
```
4. Tambah private key
```
nano privatekey.txt
```
Isi dengan private key wallet kamu (satu baris = satu key), contoh:

0xabc123456789abcdef...

0xdef9876543210fedcba...

Simpan file → keluar dengan CTRL+X, lalu tekan Y → Enter.

5. Jalankan bot
```
python3 run.py
```
Saat dijalankan, nanti akan muncul pertanyaan:

Mau berapa kali swap + LP per wallet?

Contoh input 5 → bot akan jalankan swap + LP sebanyak 5 kali per wallet.

Dan akan otomatis restart dalam 24 jam.
