# SHEERID VERIFICATION TOOL
### PLATINUM EDITION — RELEASE 2.0

> **Automated stealth verification system with TLS fingerprinting and University rotation logic.**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-Bot_API-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Security](https://img.shields.io/badge/Bypass-Deep_Stealth-FF4B4B?style=for-the-badge&logo=tor-browser&logoColor=white)
![Status](https://img.shields.io/badge/System-ONLINE-brightgreen?style=for-the-badge)

---

## ⚙️ SYSTEM ARCHITECTURE (LOGIC FLOW)

```mermaid
graph TD
    User([USER]) -->|1. Submit Link| Bot[Telegram Bot Engine]
    Bot -->|2. Extract ID| Validator{Valid ID?}
    
    Validator -->|No| Red[Error: Invalid Link]
    Validator -->|Yes| Bypass[Deep Bypass Protocol]
    
    subgraph "CORE ENGINE"
    Bypass -->|3. Force New Session| Warmer["Session Warming\n(Human Behavior Sim)"]
    Warmer -->|4. Rotate Identity| Gen["Identity Generator\n(Univ Rotation)"]
    Gen -->|5. Inject Payload| API["SheerID API\n(TLS Spoofing)"]
    end
    
    API -->|Response| Check{Status?}
    Check -->|Success| Green([VERIFIED\nGet Reward Code])
    Check -->|SSO| Skip[SSO Bypass Module]
    Skip --> API
    Check -->|Fail| Red
```

---

## CORE CAPABILITIES

### STEALTH AND ANTI DETECT
Sistem ini tidak menggunakan Selenium atau browser automation yang mudah terdeteksi.

*   **TLS Spoofing** - Menggunakan `curl_cffi` untuk meniru fingerprint kriptografi Chrome 131 secara identik.
*   **Header Rotation** - Rotasi User-Agent dan Header Order dinamis untuk menghindari tracking statis.
*   **IP Masking** - Integrasi proxy residential untuk menyamarkan lokasi asli.

### REALISTIC DOCUMENT FORGERY
Generator dokumen cerdas yang dirancang untuk mengelabui sistem verifikasi visual.

*   **JPEG Artifacts** - Output gambar memiliki kompresi natural layaknya foto kamera HP.
*   **Organic Imperfections** - Menambahkan efek rotasi, noise bintik film, dan pencahayaan tidak merata.
*   **Silhouette Injection** - Kartu identitas dilengkapi siluet manusia realistis.

### TELEGRAM BOT INTERFACE
Kontrol full sistem verifikasi dari aplikasi Telegram.

*   **One Click Verify** - Kirim link dan bot memproses di background.
*   **Real time Status** - Notifikasi langsung saat verifikasi sukses atau butuh tindakan manual.

---

## DEPLOYMENT GUIDE

### PREREQUISITES
Pastikan Python 3.10+ sudah terinstall.

```bash
# Clone Repository & Setup Environment
git clone https://github.com/privatesector/sheerid-platinum.git
python -m venv .venv
source .venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

### CONFIGURATION
Buat file `.env` untuk menyimpan akses kunci.

```ini
PROXY_URL=http://user:pass@residential-proxy.com:port
TELEGRAM_BOT_TOKEN=123456789:ABCDefGHIjkLmnOPqrstUVwxyz
TELEGRAM_API_ID=12345
TELEGRAM_API_HASH=abcdef12345
```

---

## OPERATION MODES

| MODE | COMMAND | FUNGSI |
| :--- | :--- | :--- |
| **BOT AUTO** | `python telegram_bot.py` | Menjalankan server bot Telegram. |
| **CLI MANUAL** | `python main_v2.py "URL"` | Memproses satu link secara manual. |
| **DIAGNOSTIC** | `python verify_readiness.py` | Self check sistem sebelum eksekusi. |

---

## DISCLAIMERS
> *Tool ini dikembangkan semata-mata untuk keperluan riset keamanan dan pengujian sistem. Pengembang tidak bertanggung jawab atas penyalahgunaan fitur yang ada di dalamnya.*

**COPYRIGHT 2026 PLATINUM DEV TEAM**
