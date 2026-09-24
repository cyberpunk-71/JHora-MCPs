import swisseph as swe
import datetime
from jhora import utils
from jhora.panchanga import drik
from jhora_helpers import create_date_and_place, RASI_NAMES, PLANET_NAMES

def get_tropical_long(jd, body):
    # Tropical longitude (no ayanamsa)
    res = swe.calc_ut(jd, body, swe.FLG_SWIEPH | swe.FLG_SPEED)
    return res[0][0]

def calculate_natal_tp_params(year, month, day, hour, minute, second, lat, lon, tz):
    dob, tob, place, jd = create_date_and_place(year, month, day, hour, minute, second, lat, lon, tz, "Ahmedabad", "PUSHYA_PAKSHA")
    # Sun and Moon tropical longitudes
    # Julian day in UT
    jd_ut = jd - (tz / 24.0)
    sun_trop = get_tropical_long(jd_ut, swe.SUN)
    moon_trop = get_tropical_long(jd_ut, swe.MOON)
    elongation = (moon_trop - sun_trop) % 360.0
    tithi_num = int(elongation / 12.0) + 1
    fraction_in_tithi = (elongation % 12.0) / 12.0
    sun_trop_sign = int(sun_trop / 30.0)
    
    return {
        'jd_birth': jd,
        'sun_trop': sun_trop,
        'moon_trop': moon_trop,
        'elongation': elongation,
        'tithi_num': tithi_num,
        'fraction_in_tithi': fraction_in_tithi,
        'sun_trop_sign': sun_trop_sign
    }

def find_tp_for_year(natal_params, target_year, lat, lon, tz):
    # Sun returns to same tropical sign around the same month
    # Search around target_year, month 9-10 (September-October)
    target_elongation = natal_params['elongation']
    target_sun_sign = natal_params['sun_trop_sign']
    
    # Start searching around Sept 15 of target_year
    t_start_dob = drik.Date(target_year, 9, 15)
    jd_search_start = utils.julian_day_number(t_start_dob, (0, 0, 0)) - (tz / 24.0)
    
    # Step through 45 days in 1-hour steps to find when elongation crosses target_elongation and Sun is in target_sun_sign
    best_jd = None
    min_diff = 999.0
    
    for step in range(45 * 24 * 6): # every 10 mins
        jd_cur = jd_search_start + (step * (10.0 / (24.0 * 60.0)))
        s_trop = get_tropical_long(jd_cur, swe.SUN)
        if int(s_trop / 30.0) != target_sun_sign:
            continue
        m_trop = get_tropical_long(jd_cur, swe.MOON)
        cur_elong = (m_trop - s_trop) % 360.0
        
        # Check diff
        diff = (cur_elong - target_elongation)
        if diff > 180.0: diff -= 360.0
        if diff < -180.0: diff += 360.0
        
        if abs(diff) < 0.2: # close, refine via bisection
            # Bisection
            jd_a = jd_cur - (10.0 / (24.0 * 60.0))
            jd_b = jd_cur + (10.0 / (24.0 * 60.0))
            for _ in range(30):
                jd_mid = (jd_a + jd_b) / 2.0
                s_m = get_tropical_long(jd_mid, swe.SUN)
                m_m = get_tropical_long(jd_mid, swe.MOON)
                e_m = (m_m - s_m) % 360.0
                d_m = (e_m - target_elongation)
                if d_m > 180.0: d_m -= 360.0
                if d_m < -180.0: d_m += 360.0
                
                s_a = get_tropical_long(jd_a, swe.SUN)
                m_a = get_tropical_long(jd_a, swe.MOON)
                e_a = (m_a - s_a) % 360.0
                d_a = (e_a - target_elongation)
                if d_a > 180.0: d_a -= 360.0
                if d_a < -180.0: d_a += 360.0
                
                if d_a * d_m <= 0:
                    jd_b = jd_mid
                else:
                    jd_a = jd_mid
            best_jd = (jd_a + jd_b) / 2.0
            break
            
    if best_jd is not None:
        # Convert UT JD back to local time
        jd_local = best_jd + (tz / 24.0)
        y, m, d, h_frac = utils.jd_to_gregorian(jd_local)
        hh = int(h_frac)
        mm = int((h_frac - hh) * 60.0)
        ss = round(((h_frac - hh) * 60.0 - mm) * 60.0, 2)
        if ss >= 60.0:
            ss = 0.0
            mm += 1
        if mm >= 60:
            mm = 0
            hh += 1
        return {
            'year': int(y), 'month': int(m), 'day': int(d),
            'hour': hh, 'minute': mm, 'second': ss,
            'jd_local': jd_local,
            'iso_str': f"{int(y):04d}-{int(m):02d}-{int(d):02d} {hh:02d}:{mm:02d}:{ss:05.2f}"
        }
    return None

params = calculate_natal_tp_params(2001, 10, 6, 16, 59, 9, 23.0225, 72.5714, 5.5)
print("Natal TP Params:", params)

for yr in range(2024, 2033):
    tp_res = find_tp_for_year(params, yr, 23.0225, 72.5714, 5.5)
    print(f"Year {yr} (Age {yr-2001}): {tp_res['iso_str']}")
