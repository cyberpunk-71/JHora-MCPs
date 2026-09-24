#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/opc/mcp_jhora')
import json
import swisseph as swe
from jhora import utils, const
from jhora.panchanga import drik
from jhora.horoscope.chart import charts, house
from jhora.horoscope.transit import tajaka
from jhora.horoscope.dhasa.graha import vimsottari
from jhora_helpers import create_date_and_place, format_longitude, RASI_NAMES, PLANET_NAMES

from mcp_panchanga_ephemeris import server as s1
from mcp_vargas_lagnas import server as s2
from mcp_strengths_ashtakavarga import server as s3
from mcp_dasha_engine import server as s4
from mcp_yogas_doshas import server as s5
from mcp_transits_annual_match import server as s6
from calculate_tp_exact import calculate_natal_tp_params, find_tp_for_year

birth = {
    'year': 2001, 'month': 10, 'day': 6,
    'hour': 16, 'minute': 59, 'second': 9.0,
    'latitude': 23.0225, 'longitude': 72.5714,
    'timezone_offset': 5.5,
    'place_name': 'Ahmedabad',
    'ayanamsa_mode': 'PUSHYA_PAKSHA'
}

print("================================================================================")
print("       COMPREHENSIVE ACADEMIC & CAREER SUCCESS TIMING EVALUATION                ")
print("Native: Born 2001-10-06 at 16:59:09 IST in Ahmedabad, Gujarat, India            ")
print("Framework: Pt. P. V. R. Narasimha Rao's Research & PyJHora MCP Suite             ")
print("================================================================================")

# 1. Ephemeris & D-1, D-9, D-10, D-24 Charts
ephem = s1.call_tool_direct('get_planetary_ephemeris', birth)
d1 = s2.call_tool_direct('get_divisional_chart', {**birth, 'divisional_chart_factor': 1})
d9 = s2.call_tool_direct('get_divisional_chart', {**birth, 'divisional_chart_factor': 9})
d10 = s2.call_tool_direct('get_divisional_chart', {**birth, 'divisional_chart_factor': 10})
d24 = s2.call_tool_direct('get_divisional_chart', {**birth, 'divisional_chart_factor': 24})
arudhas = s2.call_tool_direct('get_arudha_padas', birth)

print("\n" + "="*80)
print("1. NATAL DIVISIONAL CHARTS (D-1 RASI, D-10 DASAMSA, D-24 SIDDHAMSA)")
print("="*80)
print(f"D-1 Rasi Lagna:       {d1['lagna_rasi']} ({d1['placements']['Lagna']['degrees_in_rasi']}) [Aquarius]")
print(f"D-9 Navamsa Lagna:    {d9['lagna_rasi']} ({d9['placements']['Lagna']['degrees_in_rasi']}) [Taurus]")
print(f"D-10 Dasamsa Lagna:   {d10['lagna_rasi']} ({d10['placements']['Lagna']['degrees_in_rasi']}) [Career & Action]")
print(f"D-24 Siddhamsa Lagna: {d24['lagna_rasi']} ({d24['placements']['Lagna']['degrees_in_rasi']}) [Intellect & Education]")

print("\n--- D-10 Dasamsa (Career & Karma) Placements ---")
for p_name, p in d10['placements'].items():
    print(f"  {p_name:<8}: {p['rasi_name']:<12} (House {p['house_from_lagna']:<2}) - {p['degrees_in_rasi']}")

print("\n--- D-24 Siddhamsa (Higher Learning & Intellect) Placements ---")
for p_name, p in d24['placements'].items():
    print(f"  {p_name:<8}: {p['rasi_name']:<12} (House {p['house_from_lagna']:<2}) - {p['degrees_in_rasi']}")

# Jaimini Karakas & Padas
print("\n--- Jaimini Career & Academic Padas ---")
print(f"Arudha Lagna (AL - Public Image):         {arudhas['arudha_padas']['A1 (Arudha Lagna - AL)']['rasi_name']}")
print(f"Karma/Rajya Pada (A10 - Power & Status):   {arudhas['arudha_padas']['A10 (Karma/Rajya Pada)']['rasi_name']}")
print(f"Vidya/Putra Pada (A5 - Intellect & Talent):{arudhas['arudha_padas']['A5 (Mantra/Putra Pada)']['rasi_name']}")
print(f"Bhagya Pada (A9 - Fortune & Higher Study): {arudhas['arudha_padas']['A9 (Bhagya/Dharma Pada)']['rasi_name']}")
print(f"Labha Pada (A11 - Income & Gains):         {arudhas['arudha_padas']['A11 (Labha Pada)']['rasi_name']}")

# 2. Vimshottari Dasa Timeline (Education & Career)
dob, tob, place, jd = create_date_and_place(birth['year'], birth['month'], birth['day'], birth['hour'], birth['minute'], birth['second'], birth['latitude'], birth['longitude'], birth['timezone_offset'], birth['place_name'], birth['ayanamsa_mode'])
res_v = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place)
bhuktis = res_v[1] if isinstance(res_v, tuple) and len(res_v) > 1 else res_v

print("\n" + "="*80)
print("2. VIMSHOTTARI DASA TIMELINE (ACADEMICS: 2015-2024 | CAREER: 2022-2040)")
print("="*80)
for item in bhuktis:
    lords, start_dt, dur_years = item[0], item[1], item[2]
    m_name = PLANET_NAMES[lords[0]]
    a_name = PLANET_NAMES[lords[1]]
    if isinstance(start_dt, (int, float)):
        y, m, d, h = utils.jd_to_gregorian(start_dt)
        s_jd = start_dt
    else:
        y, m, d, h = start_dt[0], start_dt[1], start_dt[2], start_dt[3] if len(start_dt) > 3 else 0
        s_dob = drik.Date(int(y), int(m), int(d))
        s_tob = (int(h), int((h%1)*60), 0)
        s_jd = utils.julian_day_number(s_dob, s_tob)
    e_jd = s_jd + dur_years * 365.25
    ey, em, ed, eh = utils.jd_to_gregorian(e_jd)
    
    if int(ey) >= 2015 and int(y) <= 2040:
        focus = ""
        if int(y) < 2024:
            focus = "[ACADEMIC PHASE: School, Undergrad, Higher Degree]"
        elif 2024 <= int(y) <= 2028:
            focus = "[EARLY CAREER LAUNCH & FOUNDATIONAL BREAKTHROUGH]"
        elif 2028 <= int(y) <= 2035:
            focus = "[MAJOR CAREER EXPANSION, LEADERSHIP & FINANCIAL SURGE]"
        elif int(y) > 2035:
            focus = "[PEAK PROFESSIONAL PROMINENCE & EXECUTIVE AUTHORITY]"
        print(f"  * {m_name:<8} - {a_name:<8} : {int(y):04d}-{int(m):02d}-{int(d):02d} to {int(ey):04d}-{int(em):02d}-{int(ed):02d} ({dur_years:.2f} yrs) {focus}")

# 3. Annual Charts Evaluation: Tithi Pravesha & Tajaka for Career & Academics
natal_tp = calculate_natal_tp_params(2001, 10, 6, 16, 59, 9, 23.0225, 72.5714, 5.5)

print("\n" + "="*80)
print("3. ANNUAL EVALUATION (TITHI PRAVESHA D-10 & TAJAKA RAJYA SAHAM: 2022 - 2035)")
print("="*80)

for target_year in range(2022, 2036):
    age = target_year - 2001
    tp_data = find_tp_for_year(natal_tp, target_year, 23.0225, 72.5714, 5.5)
    
    # TP D-10 Chart
    tp_d10 = s2.call_tool_direct('get_divisional_chart', {
        'year': tp_data['year'], 'month': tp_data['month'], 'day': tp_data['day'],
        'hour': tp_data['hour'], 'minute': tp_data['minute'], 'second': tp_data['second'],
        'latitude': birth['latitude'], 'longitude': birth['longitude'],
        'timezone_offset': birth['timezone_offset'],
        'ayanamsa_mode': 'PUSHYA_PAKSHA',
        'divisional_chart_factor': 10
    })
    
    # TP D-24 Chart
    tp_d24 = s2.call_tool_direct('get_divisional_chart', {
        'year': tp_data['year'], 'month': tp_data['month'], 'day': tp_data['day'],
        'hour': tp_data['hour'], 'minute': tp_data['minute'], 'second': tp_data['second'],
        'latitude': birth['latitude'], 'longitude': birth['longitude'],
        'timezone_offset': birth['timezone_offset'],
        'ayanamsa_mode': 'PUSHYA_PAKSHA',
        'divisional_chart_factor': 24
    })
    
    # Hora Lord
    dob_tp, tob_tp, place_tp, jd_tp = create_date_and_place(
        tp_data['year'], tp_data['month'], tp_data['day'],
        tp_data['hour'], tp_data['minute'], tp_data['second'],
        birth['latitude'], birth['longitude'], birth['timezone_offset']
    )
    sr_str = drik.sunrise(jd_tp, place_tp)[1]
    sr_dms = utils.from_dms_str_to_dms(sr_str)
    sr_hrs = sr_dms[0] + sr_dms[1]/60.0 + sr_dms[2]/3600.0
    tob_hrs = tp_data['hour'] + tp_data['minute']/60.0 + tp_data['second']/3600.0
    if tob_hrs < sr_hrs:
        hrs_since_sr = (tob_hrs + 24.0) - sr_hrs
    else:
        hrs_since_sr = tob_hrs - sr_hrs
    hora_num = int(hrs_since_sr)
    CHALDEAN_ORDER = [0, 5, 3, 1, 6, 4, 2]
    vaara_idx = drik.vaara(jd_tp, place_tp)
    start_idx = CHALDEAN_ORDER.index(vaara_idx)
    tp_hora_lord = PLANET_NAMES[CHALDEAN_ORDER[(start_idx + hora_num) % 7]]
    
    # Tajaka Chart
    taj_res = s6.call_tool_direct('calculate_tajaka_varshaphal', {**birth, 'target_age_years': age})
    sahams = s6.call_tool_direct('calculate_tajaka_sahams', {**birth, 'target_age_years': age})
    
    rajya_saham = sahams.get('sahams', {}).get('Rajya Saham (Power & Authority)', {})
    vidya_saham = sahams.get('sahams', {}).get('Vidya Saham (Education)', {})
    yashas_saham = sahams.get('sahams', {}).get('Yashas Saham (Fame)', {})
    
    muntha_sign = taj_res['muntha_position']['muntha_sign']
    muntha_house = taj_res['muntha_position']['muntha_house_in_annual_chart']
    varshapathi = taj_res['lord_of_the_year_varshapathi']
    taj_lagna = taj_res['annual_chart_positions']['Lagna']['rasi_name']
    
    d10_lag = tp_d10['lagna_rasi']
    d10_10h_rasi = RASI_NAMES[(RASI_NAMES.index(d10_lag) + 9) % 12]
    d10_10h_planets = [p_name for p_name, p in tp_d10['placements'].items() if p_name != 'Lagna' and p['rasi_name'] == d10_10h_rasi]
    d10_1h_planets = [p_name for p_name, p in tp_d10['placements'].items() if p_name != 'Lagna' and p['rasi_name'] == d10_lag]
    
    print(f"\n>> YEAR {target_year} (Age {age}: {target_year-1}-10 to {target_year}-10):")
    print(f"   * TP Return: {tp_data['iso_str']} | TP Hora Lord: {tp_hora_lord}")
    print(f"   * TP D-10 Lagna: {d10_lag:<11} | 10H ({d10_10h_rasi}): {d10_10h_planets} | 1H: {d10_1h_planets}")
    print(f"   * TP D-24 Lagna: {tp_d24['lagna_rasi']:<11}")
    print(f"   * Tajaka Solar Return: Annual Lagna = {taj_lagna}, Muntha = {muntha_sign} (House {muntha_house}), Varshapathi = {varshapathi}")
    if rajya_saham:
        print(f"     - Rajya Saham: {rajya_saham.get('rasi')} in House {rajya_saham.get('house_from_lagna')}")
    if vidya_saham and age <= 25:
        print(f"     - Vidya Saham: {vidya_saham.get('rasi')} in House {vidya_saham.get('house_from_lagna')}")
    if yashas_saham:
        print(f"     - Yashas Saham (Fame): {yashas_saham.get('rasi')} in House {yashas_saham.get('house_from_lagna')}")

