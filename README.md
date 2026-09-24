# PyJHora 6-MCP Vedic Astrology Server Suite

Model Context Protocol (MCP) suite exposing 100% of mathematical calculations and astrological parameters from [PyJHora](https://github.com/naturalstupid/PyJHora) via JSON-RPC 2.0 stdio interfaces. Compatible with **Claude Desktop**, **Cursor**, **Windsurf**, **Antigravity**, **Gemini CLI**, and any standard MCP client across **Linux**, **macOS**, and **Windows**.

---

## 🏛️ Architecture Overview

```
+----------------------------------------------------------------------------------------------------+
|                                    PyJHora 6-MCP Architecture                                      |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|   +---------------------------------------+            +---------------------------------------+   |
|   |  MCP 1: Panchanga & Ephemeris         |            |  MCP 2: Vargas, Lagnas & Arudhas      |   |
|   |  • 5-Fold Panchanga (Tithi, Vara, etc)|            |  • Shodashavarga (D-1 to D-60)        |   |
|   |  • Auspicious & Inauspicious Muhurthas|            |  • 8 Special Lagnas (Hora, Ghatika)   |   |
|   |  • Vedic Calendar & Eras (Saka/Vikram)|            |  • 11 Upagrahas (Mandi, Gulika)       |   |
|   |  • Swiss Ephemeris Planetary Motion   |            |  • 12 Arudha Padas (AL, UL, A1-A12)   |   |
|   +---------------------------------------+            +---------------------------------------+   |
|                                                                                                    |
|   +---------------------------------------+            +---------------------------------------+   |
|   |  MCP 3: Strengths & Ashtakavarga      |            |  MCP 4: Dasha & Timing Engine         |   |
|   |  • 6-Fold Shadbala Breakdown          |            |  • 120y Vimsottari (Maha/Antar/Prat)  |   |
|   |  • Vimsopaka & Panchavargeeya Bala    |            |  • Graha Dashas (Ashtottari, Yogini)  |   |
|   |  • Bhava Bala (All 12 Houses)         |            |  • Shodasottari, Dwadasottari         |   |
|   |  • BAV & SAV (337 Total Bindus)       |            |  • Narayana & Chara Rasi Dashas       |   |
|   |  • Trikona/Ekadhipatya Shodhaya Pindas|            |  • Kalachakra, Mudda & Patyayini      |   |
|   +---------------------------------------+            +---------------------------------------+   |
|                                                                                                    |
|   +---------------------------------------+            +---------------------------------------+   |
|   |  MCP 5: Yogas, Doshas & Sphutas       |            |  MCP 6: Transits, Tajaka & Match      |   |
|   |  • 120+ Parasara & BV Raman Yogas     |            |  • Tajaka Annual Solar Return Chart   |   |
|   |  • Dharma-Karmadhipati Raja Yogas     |            |  • Lord of Year (Varshapathi), Muntha |   |
|   |  • 8 Doshas (Manglik with cancel, etc)|            |  • 50+ Tajaka Sahams (Punya, Vidya)   |   |
|   |  • 10 Mathematical Vedic Sphutas      |            |  • 16 Tajaka Yogas (Ithasala, etc.)   |   |
|   |    (Bija, Kshetra, Yogi, Prana, Deha) |            |  • Ashta Koota (36 Guna) & Longevity  |   |
|   +---------------------------------------+            +---------------------------------------+   |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

---

## ⚡ Quickstart & Installation (For Any Setup)

### 1. Prerequisites
- **Python 3.9+** (Python 3.9, 3.10, 3.11, 3.12, 3.13 supported)
- `git`
- (Optional on Linux) `gcc` / `python3-devel` for compiling `pyswisseph` if pre-built wheels are not available for your architecture.

### 2. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/cyberpunk-71/JHora-MCPs.git
cd JHora-MCPs

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows (Command Prompt):
venv\Scripts\activate
# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Verify All 6 MCP Servers (32 Tools)

Run the automated test suite to ensure all calculations and ephemeris tables are working correctly on your machine:

```bash
python verify_all_mcps.py
```

Expected output:
```text
================================================================================
  PYJHORA 6-MCP SERVER SUITE: END-TO-END VERIFICATION & BENCHMARK
================================================================================
...
  Passed: 32 / 32 (100.0%)
  Total Test Duration: ~4.40 seconds
================================================================================
```

---

## 🔧 Client Configuration Guide

Configure the MCP servers in your preferred AI assistant or IDE by adding the JSON snippet below. Replace `<ABSOLUTE_PATH_TO_REPO>` and `<ABSOLUTE_PATH_TO_PYTHON>` with your actual paths.

### 1. Claude Desktop (`claude_desktop_config.json`)

**Config file locations:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "jhora-panchanga-ephemeris": {
      "command": "/path/to/JHora-MCPs/venv/bin/python",
      "args": ["/path/to/JHora-MCPs/mcp_panchanga_ephemeris.py"]
    },
    "jhora-vargas-lagnas": {
      "command": "/path/to/JHora-MCPs/venv/bin/python",
      "args": ["/path/to/JHora-MCPs/mcp_vargas_lagnas.py"]
    },
    "jhora-strengths-ashtakavarga": {
      "command": "/path/to/JHora-MCPs/venv/bin/python",
      "args": ["/path/to/JHora-MCPs/mcp_strengths_ashtakavarga.py"]
    },
    "jhora-dasha-engine": {
      "command": "/path/to/JHora-MCPs/venv/bin/python",
      "args": ["/path/to/JHora-MCPs/mcp_dasha_engine.py"]
    },
    "jhora-yogas-doshas": {
      "command": "/path/to/JHora-MCPs/venv/bin/python",
      "args": ["/path/to/JHora-MCPs/mcp_yogas_doshas.py"]
    },
    "jhora-transits-annual-match": {
      "command": "/path/to/JHora-MCPs/venv/bin/python",
      "args": ["/path/to/JHora-MCPs/mcp_transits_annual_match.py"]
    }
  }
}
```

*(Note for Windows: Use `\\` or `/` in paths, e.g., `"C:/JHora-MCPs/venv/Scripts/python.exe"` and `"C:/JHora-MCPs/mcp_panchanga_ephemeris.py"`)*.

---

### 2. Cursor / Windsurf / Roo Code / Antigravity

In your IDE's MCP Server settings, register each server using `command: python` and the script path as the argument.

---

## 📦 Detailed Tool Inventory (32 Tools)

### MCP 1: Panchanga & Ephemeris (`mcp_panchanga_ephemeris.py`)
- `get_panchanga_details`: 5-fold Panchanga (Tithi, Vara, Nakshatra, Yoga, Karana), Moon Rasi, Sun/Moon rise/set times.
- `get_inauspicious_periods`: Rahu Kalam, Yamagandam, Gulika Kalam, Durmuhurtham.
- `get_auspicious_periods`: Abhijit Muhurtha, Brahma Muhurtha windows.
- `get_calendar_details`: Samvatsara, Solar/Lunar months, Ayana, Ritu, Saka/Vikram/Kali eras.
- `get_planetary_ephemeris`: High-precision tropical/sidereal planet coordinates (Sun-Ketu + Lagna).

### MCP 2: Divisional Charts, Special Lagnas & Arudhas (`mcp_vargas_lagnas.py`)
- `get_divisional_chart`: Detailed D-1 to D-60 varga calculation with degrees, signs, and houses from Lagna.
- `get_all_divisional_charts_summary`: 16 Shodashavarga matrix (D-1 to D-60) in a single response.
- `get_special_lagnas`: Bhava, Hora, Ghatika, Vighatika, Varnada, Sree, Indu, Pranapada Lagnas.
- `get_upagrahas`: Mandi, Gulika, Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu, Kaala, Mrityu.
- `get_arudha_padas`: All 12 house arudha padas (AL, UL, A1 to A12).
- `get_argala_virodhargala`: Primary, secondary, tertiary Argala and obstruction analysis.
- `get_planetary_aspects`: Graha Drishti (with exact aspect strengths) and Rasi Drishti.

### MCP 3: Planetary Strengths & Ashtakavarga (`mcp_strengths_ashtakavarga.py`)
- `get_shadbala_breakdown`: Sthana, Dig, Kala, Chesta, Naisargika, Drik Balas, Virupas, Rupas, Relative Ranks.
- `get_vimsopaka_and_vargeeya_bala`: Panchavargeeya, Dwadasavargeeya, Harsha Bala, Ishta/Kashta Phala.
- `get_bhava_bala`: Bhava Adhipati, Dig, and Drishti Balas for all 12 houses with strength ranking.
- `get_ashtakavarga_matrices`: 8 Bhinna Ashtakavarga tables (BAV) + Sarvashtakavarga (SAV 337 sum).
- `get_shodhaya_pindas_and_reductions`: Trikona Shodhana, Ekadhipatya Shodhana, Rasi/Graha/Shodhaya Pindas.

### MCP 4: Dasha & Timing Engine (`mcp_dasha_engine.py`)
- `get_vimsottari_dasha`: 120-year Vimsottari Mahadashas & Antardashas + active running dasha finder.
- `get_nakshatra_dashas`: Ashtottari (108y), Yogini (36y), Shodasottari (116y), Dwadasottari (112y).
- `get_narayana_dasa`: Narayana Rasi Dasa for D-1 and divisional charts (D-9, D-10, etc.).
- `get_chara_dasa`: Jaimini Chara Dasa sign progressions and Antardashas.
- `get_kalachakra_dasa`: Kalachakra Dasa based on Moon's Navamsa Savya/Apasavya progression.
- `get_annual_dashas`: Mudda Dasa (annual Vimsottari) and Patyayini Dasa.

### MCP 5: Vedic Yogas, Doshas & Sphutas (`mcp_yogas_doshas.py`)
- `detect_all_yogas`: 120+ Parasara & BV Raman yogas (Pancha Mahapurusha, Dhana, Nabhasa).
- `detect_raja_yogas`: 9th-10th Dharma-Karmadhipati, Kendra-Trikona, Vipareeta, Neecha Bhanga.
- `detect_doshas`: Manglik (with cancellation rules), Kala Sarpa (12 types), Pitru, Guru Chandal, Shrapit.
- `get_sphutas_and_sensitive_points`: Bija, Kshetra, Santhana, Yogi, Avayogi, Tithi, Prana, Deha, Mrityu Sphutas.

### MCP 6: Transits, Tajaka & Match Engine (`mcp_transits_annual_match.py`)
- `calculate_tajaka_varshaphal`: Annual Solar Return chart, Varshapathi (Lord of Year), Maasa Pati, Muntha.
- `calculate_tajaka_sahams`: 50+ Sahams (Punya, Vidya, Yashas, Mitra, Shatru, Karma, Vivaha, Karyasiddhi).
- `calculate_tajaka_yogas`: 16 Tajaka Yogas (Ithasala, Eesarpha, Kamboola, Nakta, Yamaya).
- `calculate_kundali_match`: Ashta Koota (36 Guna Milan) + South Indian Naalu Porutham (Mahendra, Vedha, Rajju).
- `calculate_longevity_estimates`: Jaimini / Parasara 3-pair longevity brackets (Alpayu, Madhyayu, Deerghayu).

---

## 🌐 Common Parameters & Ayanamsa Options

Most tools accept the following standard input schema:
- `year`, `month`, `day`: Birth date
- `hour`, `minute`, `second`: Birth time in 24h format (default: 12:00:00)
- `latitude`, `longitude`: Decimal coordinates (e.g. `13.0827, 80.2707` for Chennai, `42.3601, -71.0589` for Boston)
- `timezone_offset`: Timezone offset from UTC in hours (e.g. `5.5` for IST, `-4.0` for EDT, `0.0` for UTC)
- `place_name`: City/Location string
- `ayanamsa_mode`: `LAHIRI` (default / Chitrapaksha), `PUSHYA_PAKSHA`, `RAMAN`, `KP`, `YUKTESHWAR`, `JN_BHASIN`, `SAYANA` (Tropical)

---

## 🔬 Research Papers Benchmark & Validation Suite (Pt. P. V. R. Narasimha Rao)

This MCP suite is validated against **60 real-world astrological case studies** published across two research papers by **Pt. P. V. R. Narasimha Rao**:

1. [**"Re-defining Tajaka Varshaphal Charts (Annual Solar Return Charts)"**](./research_papers/Redefining_Tajaka_Varshaphal_Charts_PVR_Narasimha_Rao.pdf) (June 15, 2014) — 30 Case Studies.
2. [**"Re-defining Tithi Pravesha Chart (Annual Soli-lunar Return Chart)"**](./research_papers/Redefining_Tithi_Pravesha_Chart_PVR_Narasimha_Rao.pdf) (June 29, 2014) — 30 Case Studies.

Both PDFs are included in the [`research_papers/`](./research_papers/) directory.

### 📊 Benchmark Verification Results (100.0% Pass Rate)

| Metric | Paper 1 (Tajaka Varshaphal) | Paper 2 (Tithi Pravesha) | Combined Total |
| :--- | :--- | :--- | :--- |
| **Total Case Studies Tested** | 30 Charts | 30 Charts | **60 Charts** |
| **MCP Verification Status** | **30 / 30 (100.0%)** | **30 / 30 (100.0%)** | **60 / 60 (100.0%)** |
| **Mathematical Delta** | `< 0.01°` (Arc-second precision) | `< 0.01°` (Arc-second precision) | **Zero Discrepancy** |
| **Execution Duration** | ~2.1 seconds | ~2.0 seconds | **~4.1 seconds** |

The full case-by-case computational comparison with exact planetary longitudes, divisional chart ascendants, return timestamps, and delta metrics is documented in:
📄 [**`RESEARCH_VERIFICATION_REPORT.md`**](./RESEARCH_VERIFICATION_REPORT.md)

### 🧪 Re-running the Automated Validation Suite

Anyone running this repository can execute the verification suite locally:
```bash
# Run full automated validation on all 60 research charts
python3 validate_pdf_charts.py

# Re-generate the in-depth verification report markdown
python3 generate_in_depth_report.py
```

---

## 📜 License & Credits

- **License:** [MIT License](LICENSE) (2026)
- **Engine Core:** Built on top of [PyJHora](https://github.com/naturalstupid/PyJHora) and [pyswisseph](https://github.com/astronexus/pyswisseph).
- **Astrological Foundation & Research Benchmark:** Based on the foundational teachings and published research of **Pt. P. V. R. Narasimha Rao** (*Jagannatha Hora*, *Vedic Astrology: An Integrated Approach*, and research monographs).
