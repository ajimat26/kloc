from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# =======================================================
# 🔑 KREDENSIAL RESMI CONSOLE GREEN API (SUDAH AKTIF)
# =======================================================
ID_INSTANCE = "7107633020"
API_TOKEN = "a25e578ba41c4a59b87988512df467be5cc5548018a14e9e92"

# DATABASE BLACKLIST: Daftar nomor HP penipu/scammer di komunitas JB
DATABASE_PENIPU = [
    "081299998888",
    "085711112222",
    "089533334444"
]

def kirim_pesan_greenapi(chat_id, teks_pesan):
    """Fungsi utama mengirim pesan WhatsApp balik ke target via Green API"""
    if not chat_id.endswith("@c.us") and not chat_id.endswith("@g.us"):
        chat_id = f"{chat_id}@c.us"
        
    url = f"https://green-api.com{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = {
        "chatId": chat_id,
        "message": teks_pesan
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        res = requests.post(url, json=payload, headers=headers).json()
        print(f"[+] Pesan otomatis sukses terkirim ke: {chat_id}")
    except Exception as e:
        print(f"[-] Gangguan koneksi ke server Green API: {e}")

# =======================================================
# 📡 WEBHOOK ENDPOINT: PARSING CMD TANDA SERU (!)
# =======================================================
@app.route('/webhook-green', methods=['POST'])
def webhook_green():
    try:
        data = request.get_json()
        if not data:
            return "OK", 200
            
        type_webhook = data.get('typeWebhook', '')
        
        # Memastikan event adalah pesan masuk (incomingMessageReceived)
        if type_webhook == 'incomingMessageReceived':
            chat_id = data.get('senderData', {}).get('chatId', '')
            nomor_pengirim = chat_id.replace("@c.us", "").replace("@g.us", "")
            
            message_data = data.get('messageData', {})
            pesan_masuk = ""
            
            # Ekstraksi teks aman dari struktur JSON Green API
            if 'textMessageData' in message_data:
                pesan_masuk = message_data.get('textMessageData', {}).get('textMessage', '')
            elif 'extendedTextMessageData' in message_data:
                pesan_masuk = message_data.get('extendedTextMessageData', {}).get('text', '')
            
            pesan_masuk = pesan_masuk.strip()
            
            # Abaikan jika pesan kosong (bukan format teks)
            if not pesan_masuk:
                return "OK", 200
                
            print(f"\n[🔥 CHAT] Dari {nomor_pengirim}: '{pesan_masuk}'")
            
            # --- SISTEM PARSING PREFIKS TANDA SERU (!) ---
            if pesan_masuk.startswith("!"):
                command = pesan_masuk.lower()
                
                # 1. Perintah !menu
                if command == "!menu":
                    balasan = (
                        "🛡️ *K7N SYSTEM AUTOMATION V3* 🛡️\n\n"
                        "Berikut adalah daftar perintah (CMD) resmi yang bisa digunakan:\n\n"
                        "👉 *!cek [nomor]* -> Cek status penipu/blacklist\n"
                        "👉 *!rekber* -> Prosedur rekening bersama aman\n"
                        "👉 *!rules* -> Aturan dasar grup Jual Beli\n"
                        "👉 *!info* -> Spesifikasi sistem bot"
                    )
                    kirim_pesan_greenapi(chat_id, balasan)
                    
                # 2. Perintah !cek [nomor]
                elif command.startswith("!cek "):
                    nomor_target = pesan_masuk[5:].strip() # Memotong kata '!cek '
                    
                    # Normalisasi format nomor pengetesan
                    if nomor_target.startswith("+62"): nomor_target = "0" + nomor_target[3:]
                    if nomor_target.startswith("62"): nomor_target = "0" + nomor_target[2:]
                    
                    if nomor_target in DATABASE_PENIPU:
                        balasan = (
                            f"❌ *PERINGATAN BAHAYA DETEKSI ARSIP!*\n\n"
                            f"Nomor HP *{nomor_target}* TERDAFTAR DI DATABASE PENIPU K7N.\n"
                            f"Status: *SANGAT BERBAHAYA / BLACKLIST.*\n"
                            f"Batalkan transaksi demi keamanan dana Anda!"
                        )
                    else:
                        balasan = (
                            f"🟢 *STATUS NOMOR AMAN*\n\n"
                            f"Nomor *{nomor_target}* bersih dari catatan laporan penipuan K7N.\n"
                            f"Tetap wajib gunakan Rekber Admin resmi saat bertransaksi."
                        )
                    kirim_pesan_greenapi(chat_id, balasan)
                    
                # 3. Perintah !rekber
                elif command == "!rekber":
                    balasan = (
                        "💼 *SISTEM PANDUAN REKBER K7N* 🛡️\n\n"
                        "1. Pembeli transfer dana ke rekening Admin utama.\n"
                        "2. Admin melakukan pengecekan data mutasi masuk asli secara mandiri.\n"
                        "3. Penjual menyerahkan data akun/barang setelah dana terkonfirmasi aman.\n"
                        "4. Pembeli mengamankan data barang, lalu dana dicairkan ke penjual."
                    )
                    kirim_pesan_greenapi(chat_id, balasan)
                    
                # 4. Perintah !rules
                elif command == "!rules":
                    balasan = (
                        "⚠️ *ATURAN KHUSUS GRUP TRANSAKSI* ⚠️\n\n"
                        "1. Dilarang bertransaksi direct tanpa perantara Rekber.\n"
                        "2. Segala bentuk bukti kirim screenshoot wajib diverifikasi lewat data mutasi bank.\n"
                        "3. Saling menjaga etika berkomunikasi saat proses negosiasi."
                    )
                    kirim_pesan_greenapi(chat_id, balasan)
                    
                # 5. Perintah !info
                elif command == "!info":
                    balasan = (
                        "💻 *SPESIFIKASI CORE BOT SYSTEM*\n\n"
                        "• Engine Base : Python 3.12 (Flask Framework)\n"
                        "• Cloud Core  : GitHub Server Infrastructure\n"
                        "• Webhook App : Green API Cloud Gateway\n"
                        "• Status Code : 🟢 Active / Run Integration"
                    )
                    kirim_pesan_greenapi(chat_id, balasan)
                    
    except Exception as e:
        print(f"[⚠️ ERROR WEBHOOK]: {e}")
        
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
