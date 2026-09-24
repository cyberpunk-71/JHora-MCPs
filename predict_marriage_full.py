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
print("             DEEP-DIVE MARRIAGE TIMING PREDICTION & EVALUATION                  ")
print("Native: Born 2001-10-06 at 16:59:09 IST in Ahmedabad, Gujarat, India            ")
print("Methodology: Pt. P. V. R. Narasimha Rao's Multi-System Astrological Convergence ")
print("================================================================================")

# 1. Ephemeris & D-1 / D-9 Charts
ephem = s1.call_tool_direct('get_planetary_ephemeris', birth)
d1 = s2.call_tool_direct('get_divisional_chart', {**birth, 'divisional_chart_factor': 1})
d9 = s2.call_tool_direct('get_divisional_chart', {**birth, 'divisional_chart_factor': 9})
arudhas = s2.call_tool_direct('get_arudha_padas', birth)

print("\n" + "="*80)
print("1. NATAL FOUNDATION (D-1 RASI & D-9 NAVAMSA)")
print("="*80)
print(f"D-1 Lagna: {d1['lagna_rasi']} ({d1['placements']['Lagna']['degrees_in_rasi']}) [Aquarius]")
print(f"D-9 Lagna: {d9['lagna_rasi']} ({d9['placements']['Lagna']['degrees_in_rasi']}) [Taurus]")
print(f"Upapada Lagna (UL - Marriage/Spouse): {arudhas['arudha_padas']['A12 (Upapada Lagna - UL)']['rasi_name']} ({arudhas['arudha_padas']['A12 (Upapada Lagna - UL)']['degrees_in_rasi']}) [Virgo]")
print(f"Darapada (A7 - Physical Relations/Partnership): {arudhas['arudha_padas']['A7 (Dara Pada - DP)']['rasi_name']} [Libra]")

# 2. Vimshottari Antardashas
dob, tob, place, jd = create_date_and_place(birth['year'], birth['month'], birth['day'], birth['hour'], birth['minute'], birth['second'], birth['latitude'], birth['longitude'], birth['timezone_offset'], birth['place_name'], birth['ayanamsa_mode'])
res_v = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place)
bhuktis = res_v[1] if isinstance(res_v, tuple) and len(res_v) > 1 else res_v

print("\n" + "="*80)
print("2. VIMSHOTTARI NAKSHATRA DASA (ACTIVE TIMELINE 2023 - 2035)")
print("="*80)
print("Current Running Mahadasha: RAHU (2020-11-21 to 2038-11-21)")
print("Rahu occupies 5th House Gemini in D-1 (dispositor Mercury sits with Venus in D-9 7H).")
print("\nActive Antardashas:")
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
    
    if m_name == 'Rahu':
        relevance = ""
        if a_name == 'Jupiter':
            relevance = "[2L Family Lord in 5H, aspects Lagna & 9H]"
        elif a_name == 'Saturn':
            relevance = "[Lagna Lord in 4H conjoined with Exalted Darakaraka Moon! (2026-2028)]"
        elif a_name == 'Mercury':
            relevance = "[Dispositor of Rahu & 5L, conjoined with Lagna Lord Venus in D-9 7H! (2028-2031)]"
        elif a_name == 'Ketu':
            relevance = "[11H of fulfillment of desires (2031-2032)]"
        elif a_name == 'Venus':
            relevance = "[Supreme Kalatrakaraka, AK, Yogakaraka in 7H & Navamsa 7H! (2032-2035)]"
        print(f"  * Rahu - {a_name:<8} : {int(y):04d}-{int(m):02d}-{int(d):02d} to {int(ey):04d}-{int(em):02d}-{int(ed):02d} ({dur_years:.2f} yrs) {relevance}")

# 3. Tithi Pravesha & Tajaka Annual Charts Evaluation (2024 - 2032)
natal_tp = calculate_natal_tp_params(2001, 10, 6, 16, 59, 9, 23.0225, 72.5714, 5.5)

print("\n" + "="*80)
print("3. TITHI PRAVESHA & TAJAKA SOLAR RETURN ANNUAL EVALUATION (2024 - 2032)")
print("="*80)

annual_eval = []

RASI_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

for target_year in range(2024, 2033):
    age = target_year - 2001
    tp_data = find_tp_for_year(natal_tp, target_year, 23.0225, 72.5714, 5.5)
    
    # TP D-9 Chart
    tp_d9 = s2.call_tool_direct('get_divisional_chart', {
        'year': tp_data['year'], 'month': tp_data['month'], 'day': tp_data['day'],
        'hour': tp_data['hour'], 'minute': tp_data['minute'], 'second': tp_data['second'],
        'latitude': birth['latitude'], 'longitude': birth['longitude'],
        'timezone_offset': birth['timezone_offset'],
        'ayanamsa_mode': 'PUSHYA_PAKSHA',
        'divisional_chart_factor': 9
    })
    
    # TP Rasi Chart
    tp_d1 = s2.call_tool_direct('get_divisional_chart', {
        'year': tp_data['year'], 'month': tp_data['month'], 'day': tp_data['day'],
        'hour': tp_data['hour'], 'minute': tp_data['minute'], 'second': tp_data['second'],
        'latitude': birth['latitude'], 'longitude': birth['longitude'],
        'timezone_offset': birth['timezone_offset'],
        'ayanamsa_mode': 'PUSHYA_PAKSHA',
        'divisional_chart_factor': 1
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
    CHALDEAN_ORDER = [0, 5, 3, 1, 6, 4, 2] # Sun, Ven, Mer, Moon, Sat, Jup, Mars
    vaara_idx = drik.vaara(jd_tp, place_tp)
    start_idx = CHALDEAN_ORDER.index(vaara_idx)
    tp_hora_lord = PLANET_NAMES[CHALDEAN_ORDER[(start_idx + hora_num) % 7]]
    
    # Tajaka Chart
    taj_res = s6.call_tool_direct('calculate_tajaka_varshaphal', {**birth, 'target_age_years': age})
    sahams = s6.call_tool_direct('calculate_tajaka_sahams', {**birth, 'target_age_years': age})
    vivaha_saham = sahams.get('sahams', {}).get('Vivaha Saham (Marriage)', {})
    
    d9_lag = tp_d9['lagna_rasi']
    d9_lag_idx = RASI_NAMES.index(d9_lag)
    seventh_rasi = RASI_NAMES[(d9_lag_idx + 6) % 12]
    
    p_in_1h = [p_name for p_name, p in tp_d9['placements'].items() if p_name != 'Lagna' and p['rasi_name'] == d9_lag]
    p_in_7h = [p_name for p_name, p in tp_d9['placements'].items() if p_name != 'Lagna' and p['rasi_name'] == seventh_rasi]
    
    tp_d9_1L = RASI_LORDS[d9_lag]
    tp_d9_7L = RASI_LORDS[seventh_rasi]
    
    tp_1L_place = tp_d9['placements'][tp_d9_1L]['house_from_lagna']
    tp_7L_place = tp_d9['placements'][tp_d9_7L]['house_from_lagna']
    
    muntha_sign = taj_res['muntha_position']['muntha_sign']
    muntha_house = taj_res['muntha_position']['muntha_house_in_annual_chart']
    varshapathi = taj_res['lord_of_the_year_varshapathi']
    taj_lagna = taj_res['annual_chart_positions']['Lagna']['rasi_name']
    
    score = 0
    reasons = []
    
    # TP Hora Lord analysis
    if tp_hora_lord in ['Venus', 'Jupiter', tp_d9_1L, tp_d9_7L]:
        score += 25
        reasons.append(f"TP Hora Lord is {tp_hora_lord} (Vivaha Significator / D-9 Lord)")
    if tp_1L_place in [1, 7, 5, 9] and tp_7L_place in [1, 7, 5, 9]:
        score += 25
        reasons.append(f"TP D-9 1L ({tp_d9_1L} in H{tp_1L_place}) & 7L ({tp_d9_7L} in H{tp_7L_place}) both in Kendra/Trikona")
    if tp_1L_place == 7 or tp_7L_place == 1 or (tp_1L_place == tp_7L_place):
        score += 30
        reasons.append(f"TP D-9 Vivaha Raja Yoga (1L and 7L aspect or conjunction)")
    if 'Venus' in p_in_7h or 'Jupiter' in p_in_7h or 'Moon' in p_in_7h or 'Mercury' in p_in_7h:
        score += 20
        reasons.append(f"Benefic in TP D-9 7H: {p_in_7h}")
        
    # Tajaka features
    if muntha_house in [1, 7, 5, 9, 11]:
        score += 20
        reasons.append(f"Tajaka Muntha in auspicious House {muntha_house} ({muntha_sign})")
    if varshapathi in ['Venus', 'Jupiter']:
        score += 15
        reasons.append(f"Tajaka Varshapathi is {varshapathi}")
    if vivaha_saham.get('house_from_lagna') in [1, 7, 5, 9, 11]:
        score += 15
        reasons.append(f"Vivaha Saham in auspicious House {vivaha_saham.get('house_from_lagna')} ({vivaha_saham.get('rasi')})")
        
    print(f"\n>> SOLAR YEAR {target_year} (Age {age}: {target_year-1}-10 to {target_year}-10) | TOTAL VIVAHA SCORE: {score} pts")
    print(f"   [1] Tithi Pravesha Return: {tp_data['iso_str']}")
    print(f"       * TP Rasi Lagna: {tp_d1['lagna_rasi']} | TP Hora Lord: {tp_hora_lord}")
    print(f"       * TP D-9 Lagna: {d9_lag} | 7th House: {seventh_rasi}")
    print(f"       * TP D-9 1L: {tp_d9_1L} in H{tp_1L_place} | 7L: {tp_d9_7L} in H{tp_7L_place}")
    print(f"       * TP D-9 1H: {p_in_1h} | 7H: {p_in_7h}")
    print(f"   [2] Tajaka Solar Return:")
    print(f"       * Annual Lagna: {taj_lagna} | Varshapathi: {varshapathi}")
    print(f"       * Muntha: {muntha_sign} in House {muntha_house}")
    print(f"       * Vivaha Saham: {vivaha_saham.get('rasi')} in House {vivaha_saham.get('house_from_lagna')}")
    print(f"   [3] Highlights: {'; '.join(reasons)}")

