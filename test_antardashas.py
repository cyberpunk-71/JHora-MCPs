import sys
sys.path.insert(0, '/home/opc/mcp_jhora')
from jhora.dasa import vimsottari
from jhora import utils
from jhora.panchanga import drik
from jhora_helpers import create_date_and_place, PLANET_NAMES

dob, tob, place, jd = create_date_and_place(2001, 10, 6, 16, 59, 9, 23.0225, 72.5714, 5.5, "Ahmedabad", "PUSHYA_PAKSHA")
res = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place)
bhuktis = res[1] if isinstance(res, tuple) and len(res) > 1 else res

print(f"Total Bhuktis: {len(bhuktis)}")
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
    
    if int(ey) >= 2020 and int(y) <= 2038:
        print(f"  {m_name:<8} - {a_name:<8} : {int(y):04d}-{int(m):02d}-{int(d):02d} to {int(ey):04d}-{int(em):02d}-{int(ed):02d} ({dur_years:.2f} yrs)")
