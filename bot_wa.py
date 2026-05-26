from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# DATABASE SIMULASI: Daftar nomor HP penipu untuk fitur Anti-Scam Bot
DATABASE_PENIPU = [
    "081299998888",
    "085711112222"
]

def kirim_pesan_wa(nomor_tujuan, teks_pesan):
    """
    Fungsi untuk mengirim pesan balik ke WhatsApp.
    Di dunia nyata, Anda bisa menghubungkannya ke penyedia gateway WA API gratis/berbayar
    seperti Fonnte, Woke API, atau mendirikan server local NodeJS (Baileys/Whatsapp-web.js).
    """
    # Contoh format penembakan data ke API Gateway WA
    url_gateway = "https://fonnte.com" 
    headers = {"Authorization": "TOKEN_FONNTE_RAHASIA_ANDA"}
    payload = {
        "target": nomor_tujuan,
        "message": teks_pesan
    }
    try:
        requests.post(url_gateway, data=payload, headers=headers)
    except Exception as e:
        print(f"[-] Gagal mengirim pesan ke WhatsApp: {e}")

# Endpoint Webhook: Tempat menerima chat masuk dari pengguna WhatsApp secara real-time
@app.route('/webhook-wa', methods=['POST'])
def terima_chat_wa():
    data = request.get_json()
    
    # Membaca nomor pengirim dan isi chat pesan dari WhatsApp
    nomor_pengirim = data.get('sender') # Contoh: 6283891019471
    pesan_masuk = data.get('message', '').strip().lower()
    
    print(f"[*] Chat Masuk dari {nomor_pengirim}: {pesan_masuk}")
    
    # ------------------ LOGIKA BALASAN OTOMATIS BOT WA ------------------
    
    # Menu Utama
    if pesan_masuk == "menu" or pesan_masuk == "p":
        balasan = (
            "🛡️ *K7N BOT TRANS SECURITY V3* 🛡️\n\n"
            "Halo! Selamat datang di sistem keamanan transaksi JB. "
            "Silakan balas dengan mengetik perintah di bawah ini:\n\n"
            "1. Ketik *!cek [nomor]* -> Untuk cek database penipu\n"
            "2. Ketik *!rekber* -> Panduan membuat room rekber aman\n"
            "3. Ketik *!bantuan* -> Hubungi admin utama"
        )
        kirim_pesan_wa(nomor_pengirim, balasan)
        
    # Fitur 1: Cek Database Blacklist Penipu
    elif pesan_masuk.startswith("!cek "):
        # Mengambil nomor yang ingin dicek (Contoh: !cek 081299998888)
        nomor_target = pesan_masuk.replace("!cek ", "").strip()
        
        if nomor_target in DATABASE_PENIPU:
            balasan = (
                f"❌ *PERINGATAN BAHAYA!*\n\n"
                f"Nomor *{nomor_target}* TERDAFTAR DI DATABASE PENIPU K7N.\n"
                f"Status: **DILARANG BERTRANSAKSI / BAN**"
            )
        else:
            balasan = (
                f"🟢 *STATUS AMAN*\n\n"
                f"Nomor *{nomor_target}* belum pernah terlaporkan menipu di sistem K7N.\n"
                f"Tetap gunakan rekber admin resmi untuk transaksi aman."
            )
        kirim_pesan_wa(nomor_pengirim, balasan)
        
    # Fitur 2: Informasi Rekber
    elif pesan_masuk == "!rekber":
        balasan = (
            "💼 *PROSEDUR REKBER K7N SYSTEM*\n\n"
            "1. Pembeli melakukan transfer dana ke rekening resmi K7N.\n"
            "2. Admin melakukan verifikasi dana masuk via sistem mutasi otomatis.\n"
            "3. Setelah dana aman, Penjual dipersilakan menyerahkan barang/akun.\n"
            "4. Pembeli mengecek barang. Jika aman, dana dicairkan ke penjual."
        )
        kirim_pesan_wa(nomor_pengirim, balasan)
        
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
