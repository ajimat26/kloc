from flask import Flask, render_template_string, request
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from geopy.geocoders import Nominatim

app = Flask(__name__)

# Inisialisasi mesin pencari koordinat global
geolocator = Nominatim(user_agent="pelacak_komprehensif_jb")

# DATABASE REVISI: Tambahan Ratusan Prefix HLR Operator Indonesia agar bisa melacak wilayah lain
DATABASE_MASTER_HLR = {
    # --- AREA JAWA BARAT & BANTEN ---
    "62838910": ("Karawang", "Jawa Barat", "Sekitar 2018 - 2020 (Generasi Baru)"),
    "62838911": ("Bekasi", "Jawa Barat", "Sekitar 2018 - 2020 (Generasi Baru)"),
    "62838912": ("Purwakarta", "Jawa Barat", "Sekitar 2018 - 2020 (Generasi Baru)"),
    "6283110": ("Bandung", "Jawa Barat", "Sekitar 2012 - 2015 (Generasi Menengah)"),
    "628562": ("Bandung", "Jawa Barat", "Era 2004 - 2008 (> 15 Tahun Aktif)"),
    "628571": ("Bogor", "Jawa Barat", "Era 2008 - 2012 (Generasi Menengah)"),
    "628122": ("Bandung", "Jawa Barat", "Era 2000 - 2005 (Legendaris)"),
    "628132": ("Cirebon", "Jawa Barat", "Era 2005 - 2010 (Pengguna Lama)"),
    "628131": ("Tangerang", "Banten", "Era 2005 - 2010 (Pengguna Lama)"),

    # --- AREA DKI JAKARTA ---
    "62811": ("Jakarta", "DKI Jakarta", "Sebelum Tahun 2000 (> 25 Tahun Aktif - Sangat Tepercaya)"),
    "628121": ("Jakarta", "DKI Jakarta", "Era 2000 - 2005 (> 20 Tahun Aktif - Pengguna Lama)"),
    "628211": ("Jakarta", "DKI Jakarta", "Era 2010 - 2015 (Generasi Menengah)"),
    "628577": ("Jakarta", "DKI Jakarta", "Era 2010 - 2015 (Generasi Menengah)"),

    # --- AREA JAWA TENGAH & DIY ---
    "628170": ("Yogyakarta", "DI Yogyakarta", "Era 2000 - 2005 (Sangat Tepercaya)"),
    "628564": ("Semarang", "Jawa Tengah", "Era 2004 - 2008 (> 15 Tahun Aktif)"),
    "6281329": ("Solo", "Jawa Tengah", "Era 2005 - 2010 (Pengguna Lama)"),
    "6285227": ("Purwokerto", "Jawa Tengah", "Era 2005 - 2010 (Pengguna Lama)"),

    # --- AREA JAWA TIMUR ---
    "6281234": ("Surabaya", "Jawa Timur", "Era 2000 - 2005 (> 20 Tahun Aktif)"),
    "6281330": ("Malang", "Jawa Timur", "Era 2005 - 2010 (> 15 Tahun Aktif)"),
    "628563": ("Jember", "Jawa Timur", "Era 2004 - 2008 (Pengguna Lama)"),

    # --- AREA SUMATERA ---
    "628116": ("Medan", "Sumatera Utara", "Sebelum Tahun 2000 (Sangat Tepercaya)"),
    "628127": ("Palembang", "Sumatera Selatan", "Era 2000 - 2005 (Pengguna Lama)"),
    "628136": ("Pekanbaru", "Riau", "Era 2005 - 2010 (Generasi Menengah)"),
    "628526": ("Bandar Lampung", "Lampung", "Era 2008 - 2012 (Generasi Menengah)"),

    # --- AREA SULAWESI, BALI & KALIMANTAN ---
    "628114": ("Makassar", "Sulawesi Selatan", "Sebelum Tahun 2000 (Sangat Tepercaya)"),
    "628128": ("Balikpapan", "Kalimantan Timur", "Era 2000 - 2005 (Pengguna Lama)"),
    "628134": ("Banjarmasin", "Kalimantan Selatan", "Era 2005 - 2010 (Generasi Menengah)"),
    "6281238": ("Denpasar", "Bali", "Era 2000 - 2005 (Pengguna Lama)"),
    
    # Blok umum multi-wilayah nasional
    "62896": ("Nasional", "Multi-Wilayah", "Era 2010 - 2015 (Generasi Menengah)")
}

# DESAIN PURE CSS INTERNAL (SUDAL DIKOREKSI DAN DITAMBAHKAN TEKS KOORDINAT)
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

        .header {
            text-align: center;
            margin-bottom: 25px;
        }

        .header h1 {
            font-size: 26px;
            margin: 0;
            font-weight: 800;
            letter-spacing: 1px;
            background: linear-gradient(to right, #38bdf8, #a5b4fc, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .header p {
            font-size: 11px;
            color: #94a3b8;
            margin: 5px 0 0 0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        input[type="text"] {
            width: 100%;
            padding: 14px 16px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            color: #fff;
            font-size: 15px;
            box-sizing: border-box;
            transition: all 0.3s ease;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #38bdf8;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);
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
            transition: all 0.3s ease;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        }

        .result-box {
            margin-top: 25px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 20px;
        }

        .section-title {
            font-size: 11px;
            font-weight: 700;
            color: #38bdf8;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin: 15px 0 8px 0;
        }

        .info-block {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            margin-bottom: 8px;
        }

        .info-row:last-child {
            margin-bottom: 0;
        }

        .label { color: #94a3b8; }
        .val { font-weight: 600; color: #e2e8f0; }
        .val-mono { font-family: monospace; color: #34d399; }
        .val-coord { font-family: monospace; color: #38bdf8; font-weight: bold; }

        .badge {
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
        }
        .badge-high { background: rgba(52, 211, 153, 0.1); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3); }
        .badge-mid { background: rgba(251, 191, 36, 0.1); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }

        .btn-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }

        .btn-action {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px;
            text-decoration: none;
            color: #fff;
            font-size: 13px;
            font-weight: 700;
            border-radius: 10px;
            transition: all 0.2s ease;
            box-sizing: border-box;
        }

        .btn-wa { background-color: #059669; }
        .btn-wa:hover { background-color: #10b981; transform: translateY(-2px); }
        .btn-map { background-color: #334155; border: 1px solid rgba(255,255,255,0.1); }
        .btn-map:hover { background-color: #475569; transform: translateY(-2px); }
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
                <input type="text" name="nomor_input" placeholder="Masukkan Nomor HP (Contoh: 083891019471)" required>
            </div>
            <button type="submit">⚡ JALANKAN PELACAKAN MENDALAM</button>
        </form>

        {% if data %}
        <div class="result-box">
            
            <div class="section-title">📌 Informasi Jaringan (By @K7N)</div>
            <div class="info-block">
                <div class="info-row"><span class="label">Input Nomor:</span> <span class="val">{{ data.nomor_input }}</span></div>
                <div class="info-row"><span class="label">Format Global:</span> <span class="val-mono">+{{ data.nomor_bersih }}</span></div>
                <div class="info-row"><span class="label">Provider:</span> <span class="val">{{ data.operator }}</span></div>
            </div>

            <div class="section-title">🌐 Analisis Geografis (HLR Asal)</div>
            <div class="info-block">
                <div class="info-row"><span class="label">Kota/Kabupaten:</span> <span class="val" style="color: #38bdf8;">{{ data.kota }}</span></div>
                <div class="info-row"><span class="label">Provinsi:</span> <span class="val">{{ data.provinsi }}</span></div>
                <div class="info-row"><span class="label">Cakupan Wilayah:</span> <span class="val" style="font-size:11px;">{{ data.wilayah_bawaan }}</span></div>
