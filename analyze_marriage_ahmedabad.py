#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/opc/mcp_jhora')
import json
from jhora import utils, const
from jhora.panchanga import drik
from jhora_helpers import create_date_and_place, format_longitude, RASI_NAMES, PLANET_NAMES

from mcp_panchanga_ephemeris import server as s1
from mcp_vargas_lagnas import server as s2
from mcp_strengths_ashtakavarga import server as s3
from mcp_dasha_engine import server as s4
from mcp_yogas_doshas import server as s5
from mcp_transits_annual_match import server as s6

birth = {
    'year': 2001, 'month': 10, 'day': 6,
    'hour': 16, 'minute': 59, 'second': 9.0,
    'latitude': 23.0225, 'longitude': 72.5714,
    'timezone_offset': 5.5,
    'place_name': 'Ahmedabad',
    'ayanamsa_mode': 'PUSHYA_PAKSHA'
}

print("================================================================================")
print("             COMPREHENSIVE ASTROLOGICAL MARRIAGE ANALYSIS REPORT                ")
print("Native: Born on 2001-10-06 at 16:59:09 IST in Ahmedabad, Gujarat, India        ")
print("Ayanamsa: Pushya-Paksha (Pt. PVR Narasimha Rao Standard)                        ")
print("================================================================================")

# 1. Panchanga
panchanga = s1.call_tool_direct('get_panchanga_details', birth)
print("\n--- 1. PANCHANGA AT BIRTH ---")
print(f"Tithi:     {panchanga['panchanga']['tithi']}")
print(f"Vara:      {panchanga['panchanga']['vara']}")
print(f"Nakshatra: {panchanga['panchanga']['nakshatra']} (Moon in {panchanga['panchanga']['moon_rasi']})")
print(f"Yoga:      {panchanga['panchanga']['yoga']}")
print(f"Karana:    {panchanga['panchanga']['karana']}")

# 2. Ephemeris & D-1 Chart
ephem = s1.call_tool_direct('get_planetary_ephemeris', birth)
print("\n--- 2. PLANETARY LONGITUDES & PLACEMENTS (Pushya-Paksha Ayanamsa) ---")
for p_name, p in ephem['planets'].items():
    print(f"  {p_name:<8}: {p['rasi_name']:<12} {p['degrees_in_rasi']:<14} (Nakshatra: {p['nakshatra_name']} Pada {p['pada']})")

# 3. D-1 Rasi Chart & D-9 Navamsa Chart
d1 = s2.call_tool_direct('get_divisional_chart', {**birth, 'divisional_chart_factor': 1})
d9 = s2.call_tool_direct('get_divisional_chart', {**birth, 'divisional_chart_factor': 9})

print("\n--- 3. D-1 RASI & D-9 NAVAMSA CHARTS ---")
print(f"D-1 Rasi Lagna:    {d1['lagna_rasi']} ({d1['placements']['Lagna']['degrees_in_rasi']})")
print(f"D-9 Navamsa Lagna: {d9['lagna_rasi']} ({d9['placements']['Lagna']['degrees_in_rasi']})")

print("\nD-1 Rasi Placements (from Aquarius Lagna):")
for p_name, p in d1['placements'].items():
    print(f"  {p_name:<8}: {p['rasi_name']:<12} (House {p['house_from_lagna']:<2}) - {p['degrees_in_rasi']}")

print(f"\nD-9 Navamsa Placements (from {d9['lagna_rasi']} Navamsa Lagna):")
for p_name, p in d9['placements'].items():
    print(f"  {p_name:<8}: {p['rasi_name']:<12} (House {p['house_from_lagna']:<2}) - {p['degrees_in_rasi']}")

# 4. Arudha Padas & Jaimini Karakas
arudha_res = s2.call_tool_direct('get_arudha_padas', birth)
padas = arudha_res.get('arudha_padas', {})
print("\n--- 4. ARUDHA PADAS & JAIMINI KARAKAS ---")
for k, v in padas.items():
    print(f"  {k:<26}: {v['rasi_name']} ({v['degrees_in_rasi']})")

planet_degrees = []
for p_name in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
    p = ephem['planets'][p_name]
    deg_str = p['degrees_in_rasi']
    parts = deg_str.replace('"', '').replace("'", '').split('°')
    d_val = float(parts[0]) + float(parts[1].split()[0])/60.0 + float(parts[1].split()[1])/3600.0
    planet_degrees.append((p_name, d_val, p['rasi_name']))

planet_degrees.sort(key=lambda x: x[1], reverse=True)
karaka_names = ['Atmakaraka (AK)', 'Amatyakaraka (AmK)', 'Bhratrikaraka (BK)', 'Matrikaraka (MK)', 'Putrakaraka (PK)', 'Gnatikaraka (GK)', 'Darakaraka (DK)']
print("\nJaimini Chara Karakas (7-Karaka Scheme):")
for i, k in enumerate(karaka_names):
    p_name, deg, r_name = planet_degrees[i]
    print(f"  {k:<22}: {p_name:<8} in {r_name:<12} at {deg:.2f}°")

# 5. Vimshottari Dasa Engine
vims = s4.call_tool_direct('get_vimsottari_dasha', birth)
print("\n--- 5. VIMSHOTTARI DASA TIMELINE (2020 - 2038) ---")
for ad in vims.get('vimsottari_antardashas', []):
    m_lord = ad['mahadasha_lord']
    a_lord = ad['antardasha_lord']
    s_date = ad['start_date']
    e_date = ad['end_date']
    if int(e_date[:4]) >= 2023 and int(s_date[:4]) <= 2035:
        print(f"  * {m_lord}-{a_lord:<7} : {s_date} to {e_date} (Duration: {ad['duration_years']} yrs)")

# 6. Jaimini Chara Dasa Engine
chara = s4.call_tool_direct('get_chara_dasa', birth)
print("\n--- 6. JAIMINI CHARA DASA TIMELINE (2022 - 2036) ---")
for cd in chara.get('chara_dasa', {}).get('periods', []):
    m_sign = cd['mahadasha_sign']
    a_sign = cd['antardasha_sign']
    st = cd['start_date']
    dur = cd['duration_years']
    # compute end
    y = int(st[:4])
    m = int(st[5:7])
    d = int(st[8:10])
    if 2022 <= y <= 2035:
        print(f"  * Chara Dasa {m_sign}-{a_sign:<11} : Start {st} (Duration: {dur:.2f} yrs)")

# 7. Tithi Pravesha Annual Charts for Ages 23 to 31 (2024 to 2032)
print("\n--- 7. TITHI PRAVESHA ANNUAL RETURNS (Ages 23 to 31 / 2024 to 2032) ---")
for target_year in range(2024, 2033):
    age = target_year - 2001
    tp_res = s6.call_tool_direct('calculate_tithi_pravesha', {**birth, 'target_year': target_year})
    if tp_res.get('status') == 'success':
        tp_ret = tp_res['tithi_pravesha']
        tp_date_str = tp_ret['exact_time']
        
        y = int(tp_date_str[:4])
        m = int(tp_date_str[5:7])
        d = int(tp_date_str[8:10])
        hh = int(tp_date_str[11:13])
        mm = int(tp_date_str[14:16])
        ss = float(tp_date_str[17:19]) if len(tp_date_str) > 17 else 0.0
        
        tp_d9 = s2.call_tool_direct('get_divisional_chart', {
            'year': y, 'month': m, 'day': d,
            'hour': hh, 'minute': mm, 'second': ss,
            'latitude': birth['latitude'], 'longitude': birth['longitude'],
            'timezone_offset': birth['timezone_offset'],
            'ayanamsa_mode': 'PUSHYA_PAKSHA',
            'divisional_chart_factor': 9
        })
        
        # Chaldean hora
        dob_tp, tob_tp, place_tp, jd_tp = create_date_and_place(y, m, d, hh, mm, ss, birth['latitude'], birth['longitude'], birth['timezone_offset'])
        sr_str = drik.sunrise(jd_tp, place_tp)[1]
        sr_dms = utils.from_dms_str_to_dms(sr_str)
        sr_hrs = sr_dms[0] + sr_dms[1]/60.0 + sr_dms[2]/3600.0
        tob_hrs = hh + mm/60.0 + ss/3600.0
        if tob_hrs < sr_hrs:
            hrs_since_sr = (tob_hrs + 24.0) - sr_hrs
        else:
            hrs_since_sr = tob_hrs - sr_hrs
        hora_num = int(hrs_since_sr)
        CHALDEAN_ORDER = [0, 5, 3, 1, 6, 4, 2] # Sun, Ven, Mer, Moon, Sat, Jup, Mars
        vaara_idx = drik.vaara(jd_tp, place_tp)
        start_idx = CHALDEAN_ORDER.index(vaara_idx)
        hora_lord = PLANET_NAMES[CHALDEAN_ORDER[(start_idx + hora_num) % 7]]
        
        d9_lagna = tp_d9['lagna_rasi']
        d9_lagna_idx = RASI_NAMES.index(d9_lagna)
        seventh_rasi = RASI_NAMES[(d9_lagna_idx + 6) % 12]
        
        p_in_1h = [p_name for p_name, p in tp_d9['placements'].items() if p_name != 'Lagna' and p['rasi_name'] == d9_lagna]
        p_in_7h = [p_name for p_name, p in tp_d9['placements'].items() if p_name != 'Lagna' and p['rasi_name'] == seventh_rasi]
        
        print(f"\n>> Age {age} (Solar Year {target_year}) - TP Return: {tp_date_str}")
        print(f"   TP Rasi Lagna: {tp_ret['annual_lagna_rasi']} | TP Hora Lord: {hora_lord}")
        print(f"   TP D-9 Navamsa Lagna: {d9_lagna} | 7th House: {seventh_rasi}")
        print(f"   TP D-9 1H Planets: {p_in_1h} | 7H Planets: {p_in_7h}")

# 8. Tajaka Varshaphal for Ages 23 to 31
print("\n--- 8. TAJAKA VARSHAPHAL (SAYANA SOLAR RETURN) FOR AGES 23 to 31 ---")
for target_age in range(23, 32):
    taj_res = s6.call_tool_direct('calculate_tajaka_varshaphal', {
        **birth, 'target_age_years': target_age
    })
    if taj_res.get('status') == 'success':
        t_data = taj_res['tajaka_annual_chart']
        sahams = s6.call_tool_direct('calculate_tajaka_sahams', {
            **birth, 'target_age_years': target_age
        })
        vivaha_saham = sahams.get('sahams', {}).get('Vivaha Saham (Marriage)', {})
        print(f"\n>> Age {target_age} (Year {2001+target_age}): Varsha Pravesha = {t_data['exact_varsha_pravesha']}")
        print(f"   Annual Lagna: {t_data['annual_lagna_rasi']} | Muntha: {t_data['muntha_sign']} (House {t_data['muntha_house']}) | Varshapathi: {t_data['lord_of_the_year']}")
        if vivaha_saham:
            print(f"   Vivaha Saham: {vivaha_saham.get('rasi')} {vivaha_saham.get('degrees_in_rasi')} (House {vivaha_saham.get('house_from_lagna')})")

