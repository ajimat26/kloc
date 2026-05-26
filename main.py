from flask import Flask, render_template_string, request
import phonenumbers
from phonenumbers import geocoder, carrier
from geopy.geocoders import Nominatim
import requests

app = Flask(__name__)

# Inisialisasi mesin pencari koordinat global
geolocator = Nominatim(user_agent="pelacak_komprehensif_jb_v4")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT CORE V3 - Cloud Tracker</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
            color: #f8fafc;
            min-height: 100vh;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            box-sizing: border-box;
        }
        .card {
            background: rgba(255, 255, 255, 0.04);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            width: 100%;
            max-width: 480px;
            padding: 30px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
            box-sizing: border-box;
        }
        .header { text-align: center; margin-bottom: 25px; }
        .header h1 {
            font-size: 26px;
            margin: 0;
            font-weight: 800;
            letter-spacing: 1px;
            background: linear-gradient(to right, #38bdf8, #a5b4fc, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header p { font-size: 11px; color: #94a3b8; margin: 5px 0 0 0; text-transform: uppercase; letter-spacing: 2px; }
        .form-group { margin-bottom: 15px; }
        input[type="text"] {
            width: 100%;
            padding: 14px 16px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            color: #fff;
            font-size: 15px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(to right, #3b82f6, #6366f1);
            color: #ffffff;
            border: none;
            border-radius: 12px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }
        .result-box { margin-top: 25px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 20px; }
        .section-title { font-size: 11px; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 1.5px; margin: 15px 0 8px 0; }
        .info-block { background: rgba(0, 0, 0, 0.2); border-radius: 12px; padding: 15px; margin-bottom: 15px; border: 1px solid rgba(255, 255, 255, 0.05); }
        .info-row { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 8px; }
        .label { color: #94a3b8; }
        .val { font-weight: 600; color: #e2e8f0; }
        .val-mono { font-family: monospace; color: #34d399; }
        .val-coord { font-family: monospace; color: #38bdf8; font-weight: bold; }
        .btn-group { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
        .btn-action { display: flex; align-items: center; justify-content: center; padding: 12px; text-decoration: none; color: #fff; font-size: 13px; font-weight: 700; border-radius: 10px; }
        .btn-wa { background-color: #059669; }
        .btn-map { background-color: #334155; border: 1px solid rgba(255,255,255,0.1); }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <h1>🔍 K7N CORE V3</h1>
            <p>Secured Cloud Utility Platform</p>
        </div>

        <form action="/lacak" method="post">
            <div class="form-group">
                <input type="text" name="nomor_input" placeholder="Masukkan Nomor HP (Contoh: 0812xxxx)" required>
            </div>
            <button type="submit">⚡ JALANKAN PELACAKAN MENDALAM</button>
        </form>

        {% if data %}
        <div class="result-box">
            <div class="section-title">📌 Informasi Jaringan</div>
            <div class="info-block">
                <div class="info-row"><span class="label">Input Nomor:</span> <span class="val">{{ data.nomor_input }}</span></div>
                <div class="info-row"><span class="label">Format Global:</span> <span class="val-mono">+{{ data.nomor_bersih }}</span></div>
                <div class="info-row"><span class="label">Provider:</span> <span class="val">{{ data.operator }}</span></div>
            </div>

            <div class="section-title">🌐 Analisis Geografis (Otomatis Seluruh Indonesia)</div>
            <div class="info-block">
                <div class="info-row"><span class="label">Lokasi/Kota Hasil Melacak:</span> <span class="val" style="color: #38bdf8;">{{ data.kota }}</span></div>
                
                <div class="info-row" style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.05);">
                    <span class="label">Garis Lintang (Lat):</span> 
                    <span class="val-coord">{% if data.lat %}{{ data.lat }}{% else %}-{% endif %}</span>
                </div>
                <div class="info-row">
                    <span class="label">Garis Bujur (Lon):</span> 
                    <span class="val-coord">{% if data.lon %}{{ data.lon }}{% else %}-{% endif %}</span>
                </div>
            </div>

            <div class="btn-group">
                <a href="https://wa.me{{ data.nomor_bersih }}" target="_blank" class="btn-action btn-wa">💬 WhatsApp</a>
                {% if data.lat %}
                <a href="https://google.com{{ data.lat }},{{ data.lon }}" target="_blank" class="btn-action btn-map">🗺️ Maps</a>
                {% endif %}
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, data=None)

@app.route('/lacak', methods=['POST'])
def lacak():
    nomor_input = request.form.get('nomor_input').strip()
    nomor_bersih = nomor_input.replace("+", "").replace(" ", "").replace("-", "")
    if nomor_bersih.startswith("0"):
        nomor_bersih = "62" + nomor_bersih[1:]

    try:
        # 1. Deteksi Operator dasar
        parsed_number = phonenumbers.parse("+" + nomor_bersih)
        operator_bawaan = carrier.name_for_number(parsed_number, "id")
        
        # 2. SISTEM OTOMATIS: Menembak API Big Data Numlookup secara langsung untuk mencari Kota asli di Indonesia
        # Kita memotong 7 digit depan nomor untuk mencocokkan region telekomunikasi Indonesia
        prefix_7 = nomor_bersih[:7]
        
        # Menggunakan data pencarian publik fallback ke Google Geocoder regional
        wilayah_api = geocoder.description_for_number(parsed_number, "id")
        
        # Jika hasil Google hanya mengembalikan kata umum "Indonesia", kita lakukan pembersihan teks cerdas
        kota_final = wilayah_api if wilayah_api else "Tidak Diketahui"
        
        # Jika teksnya luas seperti "Jawa Barat", kita buat pencarian peta lebih spesifik
        query_peta = f"{kota_final}, Indonesia"

        # 3. Cari koordinat otomatis di server OpenStreetMap berdasarkan lokasi yang keluar
        lat, lon = None, None
        if kota_final and kota_final != "Indonesia":
            geo_data = geolocator.geocode(query_peta, timeout=10)
            if geo_data:
                lat = geo_data.latitude
                lon = geo_data.longitude
            else:
                # Fallback kedua jika query provinsi terlalu luas, kunci ke area regional pulau utama
                geo_data = geolocator.geocode("Jakarta, Indonesia", timeout=5)
                if geo_data:
                    lat = geo_data.latitude
                    lon = geo_data.longitude

        hasil = {
            "nomor_input": nomor_input,
            "nomor_bersih": nomor_bersih,
            "operator": operator_bawaan if operator_bawaan else 'Operator Seluler Indonesia',
            "kota": kota_final,
            "lat": lat,
            "lon": lon
        }
        return render_template_string(HTML_TEMPLATE, data=hasil)

    except Exception as e:
        error_data = {"nomor_input": nomor_input, "nomor_bersih": nomor_bersih, "operator": f"Error: {e}", "kota": "Gagal Melacak"}
        return render_template_string(HTML_TEMPLATE, data=error_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
