import sys
sys.path.insert(0, '/home/opc/mcp_jhora')
from jhora.horoscope.chart import charts
from jhora_helpers import create_date_and_place, RASI_NAMES, PLANET_NAMES

for ayan in ['PUSHYA_PAKSHA', 'LAHIRI']:
    dob, tob, place, jd = create_date_and_place(2001, 10, 6, 16, 59, 9, 23.0225, 72.5714, 5.5, "Ahmedabad", ayan)
    print(f"\n=======================================================")
    print(f"AYANAMSA: {ayan}")
    print(f"=======================================================")
    
    for cm in [1, 2, 3, 4, 5, 6]:
        d10_data = charts.divisional_chart(jd, place, divisional_chart_factor=10, chart_method=cm)
        lag_rasi = RASI_NAMES[d10_data[0][1][0]]
        lag_deg = d10_data[0][1][1]
        print(f"Method {cm}: Lagna = {lag_rasi:<12} ({lag_deg:.2f}°)")
        # Print planets in D-10
        p_str = []
        for item in d10_data[1:10]:
            p_name = PLANET_NAMES[item[0]]
            r_name = RASI_NAMES[item[1][0]]
            p_str.append(f"{p_name}:{r_name}")
        print("  " + ", ".join(p_str))
