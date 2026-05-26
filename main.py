from flask import Flask, render_template_string, request
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Inisialisasi mesin pencari koordinat global
geolocator = Nominatim(user_agent="pelacak_komprehensif_jb")

# DATABASE REFERENSI OPERATOR INDONESIA (PREFIX HLR & ERA RILIS)
DATABASE_MASTER_HLR = {
    "62838910": ("Karawang", "Jawa Barat", "Sekitar 2018 - 2020 (Generasi Baru - Waspada jika akun JB Baru)"),
    "62838911": ("Bekasi", "Jawa Barat", "Sekitar 2018 - 2020 (Generasi Baru)"),
    "6283110": ("Bandung", "Jawa Barat", "Sekitar 2012 - 2015 (Generasi Menengah)"),
    "6281707": ("Yogyakarta", "DI Yogyakarta", "Era 2000 - 2005 (> 20 Tahun Aktif - Legendaris/Tepercaya)"),
    "62811": ("Jakarta", "DKI Jakarta", "Sebelum Tahun 2000 (> 25 Tahun Aktif - Sangat Tepercaya)"),
    "6281210": ("Jakarta", "DKI Jakarta", "Era 2000 - 2005 (> 20 Tahun Aktif - Pengguna Lama)"),
    "6281220": ("Bandung", "Jawa Barat", "Era 2000 - 2005 (> 20 Tahun Aktif)"),
    "6281234": ("Surabaya", "Jawa Timur", "Era 2000 - 2005 (> 20 Tahun Aktif)"),
    "6281320": ("Semarang", "Jawa Tengah", "Era 2005 - 2010 (> 15 Tahun Aktif)"),
    "628211": ("Jabodetabek", "DKI Jakarta / Banten", "Era 2010 - 2015 (Generasi Menengah)"),
    "62852": ("Luar Jawa (Distribusi Umum)", "Multi-Wilayah", "Era 2005 - 2010 (> 15 Tahun Aktif)"),
    "628562": ("Bandung / Priangan", "Jawa Barat", "Era 2004 - 2008 (> 15 Tahun Aktif)"),
    "628564": ("Semarang / DIY", "Jawa Tengah", "Era 2004 - 2008 (> 15 Tahun Aktif)"),
    "628571": ("Jakarta / Bogor", "DKI Jakarta / Jawa Barat", "Era 2008 - 2012 (Generasi Menengah)"),
    "62896": ("Nasional (Tri)", "Multi-Wilayah", "Era 2010 - 2015 (Generasi Menengah)")
}

# Desain Antarmuka yang akan muncul di HP Anda
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sistem Pelacak Jual Beli (JB)</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 15px; background-color: #f8f9fa; color: #333; }
        .card { background: white; padding: 20px; border-radius: 12px; max-width: 500px; margin: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h2 { text-align: center; color: #0056b3; margin-bottom: 20px; }
        input[type="text"] { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ced4da; border-radius: 6px; box-sizing: border-box; font-size: 15px; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 6px; font-weight: bold; font-size: 16px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result-box { background: #e9ecef; padding: 15px; margin-top: 20px; border-radius: 8px; font-size: 14px; line-height: 1.6; }
        .section-title { font-weight: bold; color: #495057; border-bottom: 2px solid #dee2e6; margin-top: 15px; padding-bottom: 3px; }
        a { color: #007bff; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🔍 OSINT CORE V3</h2>
        <form action="/lacak" method="post">
            <input type="text" name="nomor_input" placeholder="Masukkan Nomor HP Target (Contoh: 083891019471)" required>
            <button type="submit">JALANKAN PELACAKAN</button>
        </form>

        {% if data %}
        <div class="result-box">
            <div class="section-title">1. INFORMASI NOMOR UTAMA</div>
            <b>Input Nomor HP:</b> {{ data.nomor_input }}<br>
            <b>Format Standar:</b> +{{ data.nomor_bersih }}<br>
            <b>Penyedia Layanan:</b> {{ data.operator }}<br>
            <b>Zona Waktu:</b> {{ data.zona_waktu }}<br>

            <div class="section-title">2. ANALISIS GEOGRAFIS (HLR ASAL KARTU)</div>
            <b>Kota / Kabupaten:</b> {{ data.kota }}<br>
            <b>Provinsi:</b> {{ data.provinsi }}<br>
            <b>Cakupan Wilayah Bawaan:</b> {{ data.wilayah_bawaan }}<br>

            <div class="section-title">3. REPUTASI AKUN JUAL BELI (JB)</div>
            <b>Estimasi Era Rilis:</b> {{ data.estimasi_usia }}<br>
            <b>Tingkat Kepercayaan:</b> {{ data.kepercayaan }}<br>

            <div class="section-title">4. INTEGRASI LAYANAN CHAT</div>
            <b>Tautan Cek WA:</b> <a href="https://wa.me{{ data.nomor_bersih }}" target="_blank">Hubungi via WhatsApp</a><br>

            <div class="section-title">5. INTEGRASI PEMETAAN DIGITAL</div>
            {% if data.lat %}
            <b>Nama Lokasi Peta:</b> {{ data.alamat_peta }}<br>
            <b>Koordinat Tengah Kota:</b> {{ data.lat }}, {{ data.lon }}<br>
            <b>Tautan Peta:</b> <a href="https://google.com{{ data.lat }},{{ data.lon }}" target="_blank">Buka Google Maps</a>
            {% else %}
            <i>[-] Server peta gagal memuat koordinat daerah ini.</i>
            {% endif %}
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
    
    # Normalisasi nomor ke format 62
    nomor_bersih = nomor_input.replace("+", "").replace(" ", "").replace("-", "")
    if nomor_bersih.startswith("0"):
        nomor_bersih = "62" + nomor_bersih[1:]

    try:
        parsed_number = phonenumbers.parse(nomor_input if nomor_input.startswith("+") else "+" + nomor_bersih)
        operator_bawaan = carrier.name_for_number(parsed_number, "id")
        wilayah_bawaan = geocoder.description_for_number(parsed_number, "id")
        zona_waktu = list(timezone.time_zones_for_number(parsed_number))[0]
        
        kota_terdeteksi = None
        provinsi_terdeteksi = None
        estimasi_usia_nomor = "Data Rilis Tidak Terindeks (Kemungkinan Nomor Baru / Hasil Daur Ulang)"

        for panjang_prefix in [8, 7, 6, 5]:
            prefix_target = nomor_bersih[:panjang_prefix]
            if prefix_target in DATABASE_MASTER_HLR:
                kota_terdeteksi, provinsi_terdeteksi, estimasi_usia_nomor = DATABASE_MASTER_HLR[prefix_target]
                break

        if not kota_terdeteksi:
            kota_terdeteksi = wilayah_bawaan if wilayah_bawaan else "Tidak Diketahui"
            provinsi_terdeteksi = "Tidak Terdeteksi"

        kepercayaan = 'SANGAT TINGGI' if 'Legendaris' in estimasi_usia_nomor or 'Sebelum' in estimasi_usia_nomor else 'MENENGAH / PERLU VERIFIKASI LANJUTAN'

        # Pemetaan Geopy
        lat, lon, alamat_peta = None, None, None
        if kota_terdeteksi and kota_terdeteksi not in ["Indonesia", "Tidak Diketahui"]:
            query_pencarian_peta = f"{kota_terdeteksi}, Indonesia"
            geo_data = geolocator.geocode(query_pencarian_peta, timeout=10)
            if geo_data:
                lat = geo_data.latitude
                lon = geo_data.longitude
                alamat_peta = geo_data.address

        # Bungkus data ke dictionary untuk dikirim ke HTML
        hasil = {
            "nomor_input": nomor_input,
            "nomor_bersih": nomor_bersih,
            "operator": operator_bawaan if operator_bawaan else 'AXIS / XL / Lainnya',
            "zona_waktu": zona_waktu,
            "kota": kota_terdeteksi,
            "provinsi": provinsi_terdeteksi,
            "wilayah_bawaan": wilayah_bawaan,
            "estimasi_usia": estimasi_usia_nomor,
            "kepercayaan": kepercayaan,
            "lat": lat,
            "lon": lon,
            "alamat_peta": alamat_peta
        }
        return render_template_string(HTML_TEMPLATE, data=hasil)

    except Exception as e:
        error_data = {"nomor_input": nomor_input, "nomor_bersih": nomor_bersih, "operator": f"Error: {e}"}
        return render_template_string(HTML_TEMPLATE, data=error_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
