# PyJHora 6-MCP Vedic Astrology Server Suite

A high-performance, enterprise-grade Model Context Protocol (MCP) suite exposing 100% of mathematical calculations and astrological parameters from [PyJHora](https://github.com/naturalstupid/PyJHora) via JSON-RPC 2.0 stdio interfaces.

---

## 🏛️ Architecture Overview

```
+--------------------------------------------------------------------------------------------------+
|                                    PyJHora 6-MCP Architecture                                    |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   +---------------------------------------+          +---------------------------------------+   |
|   |  MCP 1: Panchanga & Ephemeris         |          |  MCP 2: Vargas, Lagnas & Arudhas      |   |
|   |  - Tithi, Vara, Nakshatra, Yoga, Karan|          |  - Shodashavarga (D-1 to D-60)        |   |
|   |  - Auspicious/Inauspicious Muhurthas  |          |  - Special Lagnas (Hora, Ghatika, etc)|   |
|   |  - Calendar, Ayana, Ritu, Samvatsara  |          |  - Upagrahas (Mandi, Gulika, Dhuma)   |   |
|   |  - High-Precision Planetary Ephemeris |          |  - Arudha Padas (A1-A12, AL, UL)      |   |
|   |  - Sunrise/Sunset, Moonrise/Moonset   |          |  - Argala/Virodha, Graha/Rasi Drishti |   |
|   +---------------------------------------+          +---------------------------------------+   |
|                                                                                                  |
|   +---------------------------------------+          +---------------------------------------+   |
|   |  MCP 3: Strengths & Ashtakavarga      |          |  MCP 4: Dasha & Timing Engine         |   |
|   |  - 6-Fold Shadbala Breakdown          |          |  - Vimsottari (Maha/Antar/Pratyantar) |   |
|   |  - Vimsopaka & Panchavargeeya Bala    |          |  - Graha Dashas (Ashtottari, Yogini)  |   |
|   |  - Bhava Bala (All 12 Houses)         |          |  - Shodasottari, Dwadasottari         |   |
|   |  - Ashtakavarga (BAV, SAV 337 points) |          |  - Narayana & Chara Rasi Dashas       |   |
|   |  - Trikona/Ekadhipatya Shodhaya Pinda |          |  - Kalachakra, Mudda & Patyayini      |   |
|   +---------------------------------------+          +---------------------------------------+   |
|                                                                                                  |
|   +---------------------------------------+          +---------------------------------------+   |
|   |  MCP 5: Yogas, Doshas & Sphutas       |          |  MCP 6: Transits, Tajaka & Match      |   |
|   |  - Classical Yogas (Pancha Mahapurusha|          |  - Tajaka Varshaphal (Annual Solar)   |   |
|   |  - Raja Yogas (Dharma-Karmadhipati)   |          |  - Lord of Year (Varshapathi), Muntha |   |
|   |  - 8 Doshas (Manglik, Kalasarpa, etc) |          |  - 50+ Tajaka Sahams (Punya, Vidya)   |   |
|   |  - Sensitive Sphutas (Bija, Kshetra,  |          |  - 16 Tajaka Yogas (Ithasala, Eesarpha|   |
|   |    Yogi, Tithi, Prana, Deha, Mrityu)  |          |  - Ashta Koota (36 Guna) & Longevity  |   |
|   +---------------------------------------+          +---------------------------------------+   |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
```

---

## 📦 MCP Server Inventory & Tool Directory (32 Tools)

### 1. `mcp_panchanga_ephemeris.py` (MCP 1)
- `get_panchanga_details`: 5-fold Panchanga (Tithi, Vara, Nakshatra, Yoga, Karana), rise/set times.
- `get_inauspicious_periods`: Rahu Kalam, Yamagandam, Gulika Kalam, Durmuhurtham.
- `get_auspicious_periods`: Abhijit Muhurtha, Brahma Muhurtha windows.
- `get_calendar_details`: Samvatsara, Solar/Lunar months, Ayana, Ritu, Saka/Vikram/Kali eras.
- `get_planetary_ephemeris`: High-precision tropical/sidereal planet coordinates (Sun-Ketu + Lagna).

### 2. `mcp_vargas_lagnas.py` (MCP 2)
- `get_divisional_chart`: Detailed D-1 to D-60 varga calculation with degrees, signs, houses from Lagna.
- `get_all_divisional_charts_summary`: High-level 16 Shodashavarga matrix in a single call.
- `get_special_lagnas`: Bhava, Hora, Ghatika, Vighatika, Varnada, Sree, Indu, Pranapada Lagnas.
- `get_upagrahas`: Mandi, Gulika, Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu, Kaala, Mrityu.
- `get_arudha_padas`: All 12 house arudhas (AL, UL, A1 to A12).
- `get_argala_virodhargala`: Primary, secondary, tertiary Argala and obstruction analysis.
- `get_planetary_aspects`: Graha Drishti (with visual strength) and Rasi Drishti.

### 3. `mcp_strengths_ashtakavarga.py` (MCP 3)
- `get_shadbala_breakdown`: Sthana, Dig, Kala, Chesta, Naisargika, Drik Balas, Virupas, Rupas, Ranks.
- `get_vimsopaka_and_vargeeya_bala`: Panchavargeeya, Dwadasavargeeya, Harsha Bala, Ishta/Kashta Phala.
- `get_bhava_bala`: Bhava Adhipati, Dig, Drishti Balas for all 12 houses.
- `get_ashtakavarga_matrices`: 8 Bhinna Ashtakavarga tables (BAV) + Sarvashtakavarga (SAV 337 total).
- `get_shodhaya_pindas_and_reductions`: Trikona Shodhana, Ekadhipatya Shodhana, Rasi/Graha/Shodhaya Pindas.

### 4. `mcp_dasha_engine.py` (MCP 4)
- `get_vimsottari_dasha`: 120-year Vimsottari Mahadashas & Antardashas + active dasha at target date.
- `get_nakshatra_dashas`: Ashtottari (108y), Yogini (36y), Shodasottari (116y), Dwadasottari (112y).
- `get_narayana_dasa`: Narayana Rasi Dasa for D-1 and divisional charts (D-9, D-10, etc.).
- `get_chara_dasa`: Jaimini Chara Dasa sign progressions with Antardashas.
- `get_kalachakra_dasa`: Kalachakra Dasa based on Moon's Navamsa Savya/Apasavya movement.
- `get_annual_dashas`: Mudda Dasa (annual Vimsottari) and Patyayini Dasa.

### 5. `mcp_yogas_doshas.py` (MCP 5)
- `detect_all_yogas`: Scans 120+ classical Parasara & BV Raman yogas (Pancha Mahapurusha, Dhana, Nabhasa).
- `detect_raja_yogas`: 9th-10th Dharma-Karmadhipati, Kendra-Trikona lord yogas, Vipareeta, Neecha Bhanga.
- `detect_doshas`: Manglik (with exceptions), Kala Sarpa (12 types), Pitru, Guru Chandal, Shrapit.
- `get_sphutas_and_sensitive_points`: Bija, Kshetra, Santhana, Yogi, Avayogi, Tithi, Prana, Deha, Mrityu Sphutas.

### 6. `mcp_transits_annual_match.py` (MCP 6)
- `calculate_tajaka_varshaphal`: Annual Solar Return chart, Varshapathi, Maasa Pati, Muntha sign/house.
- `calculate_tajaka_sahams`: Punya, Vidya, Yashas, Mitra, Shatru, Karma, Vivaha, Karyasiddhi Sahams.
- `calculate_tajaka_yogas`: 16 Tajaka Yogas (Ithasala, Eesarpha, Kamboola, Nakta, Yamaya).
- `calculate_kundali_match`: Ashta Koota 36 Gunas + South Indian Naalu Porutham (Mahendra, Vedha, Rajju).
- `calculate_longevity_estimates`: Jaimini / Parasara 3-pair longevity brackets (Alpayu, Madhyayu, Deerghayu).

---

## 🔧 Client Configuration Snippet (`claude_desktop_config.json` / Antigravity)

```json
{
  "mcpServers": {
    "jhora-panchanga-ephemeris": {
      "command": "python3",
      "args": ["/home/opc/mcp_jhora/mcp_panchanga_ephemeris.py"]
    },
    "jhora-vargas-lagnas": {
      "command": "python3",
      "args": ["/home/opc/mcp_jhora/mcp_vargas_lagnas.py"]
    },
    "jhora-strengths-ashtakavarga": {
      "command": "python3",
      "args": ["/home/opc/mcp_jhora/mcp_strengths_ashtakavarga.py"]
    },
    "jhora-dasha-engine": {
      "command": "python3",
      "args": ["/home/opc/mcp_jhora/mcp_dasha_engine.py"]
    },
    "jhora-yogas-doshas": {
      "command": "python3",
      "args": ["/home/opc/mcp_jhora/mcp_yogas_doshas.py"]
    },
    "jhora-transits-annual-match": {
      "command": "python3",
      "args": ["/home/opc/mcp_jhora/mcp_transits_annual_match.py"]
    }
  }
}
```

---

## 🧪 Verification & Benchmark

Run the master test suite:
```bash
python3 /home/opc/mcp_jhora/verify_all_mcps.py
```
**Results:** 32/32 Tools Tested, 100.0% Pass Rate, Execution Time: ~4.40s.
