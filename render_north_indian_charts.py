#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/opc/mcp_jhora')
from jhora.horoscope.chart import charts
from jhora_helpers import create_date_and_place, RASI_NAMES, PLANET_NAMES

dob, tob, place, jd = create_date_and_place(2001, 10, 6, 16, 59, 9, 23.0225, 72.5714, 5.5, "Ahmedabad", "PUSHYA_PAKSHA")

# D-1 Rasi
d1_data = charts.divisional_chart(jd, place, divisional_chart_factor=1)
# D-10 Dasamsa (Parasara standard)
d10_data = charts.divisional_chart(jd, place, divisional_chart_factor=10, chart_method=1)
# D-9 Navamsa
d9_data = charts.divisional_chart(jd, place, divisional_chart_factor=9)
# D-24 Siddhamsa
d24_data = charts.divisional_chart(jd, place, divisional_chart_factor=24)

def get_house_map(chart_data):
    lagna_rasi_idx = chart_data[0][1][0]
    house_planets = {h: [] for h in range(1, 13)}
    house_rasi = {}
    for h in range(1, 13):
        r_idx = (lagna_rasi_idx + (h - 1)) % 12
        house_rasi[h] = (r_idx + 1, RASI_NAMES[r_idx])
        
    for item in chart_data[1:10]:
        p_id = item[0]
        p_name = PLANET_NAMES[p_id]
        p_rasi_idx = item[1][0]
        h_num = ((p_rasi_idx - lagna_rasi_idx + 12) % 12) + 1
        house_planets[h_num].append(p_name)
        
    return lagna_rasi_idx, house_rasi, house_planets

def render_north_indian_ascii(title, chart_data):
    lag_idx, h_rasi, h_planets = get_house_map(chart_data)
    
    # Helper to format house contents
    def h_str(h):
        r_num, r_name = h_rasi[h]
        planets = h_planets[h]
        p_txt = ",".join(planets) if planets else "-"
        return f"H{h}({r_num}): {p_txt}"
    
    # Format clean box
    print(f"\n{'='*75}")
    print(f"       {title.upper()} (NORTH INDIAN DIAMOND FORMAT)")
    print(f"       Lagna: {RASI_NAMES[lag_idx]} | Ayanamsa: Pushya-Paksha")
    print(f"{'='*75}")
    
    lines = [
        "+-----------------------------+-----------------------------+",
        f"| \\  House 12: {h_rasi[12][0]:<2}            /   \\  House 2: {h_rasi[2][0]:<2}             / |",
        f"|   \\  {', '.join(h_planets[12]) if h_planets[12] else '-':<18} /     \\  {', '.join(h_planets[2]) if h_planets[2] else '-':<18} /   |",
        f"|     \\               /  House 1  \\               /     |",
        f"|       \\           /  (LAGNA): {h_rasi[1][0]:<2} \\           /       |",
        f"| House 11: {h_rasi[11][0]:<2}   /   {', '.join(h_planets[1]) if h_planets[1] else 'Lagna':<12}  \\   House 3: {h_rasi[3][0]:<2}    |",
        f"| {', '.join(h_planets[11]) if h_planets[11] else '-':<13} /                     \\  {', '.join(h_planets[3]) if h_planets[3] else '-':<13} |",
        f"|           /                         \\           |",
        "+----------+                           +----------+",
        f"|          \\                         /           |",
        f"| House 10: {h_rasi[10][0]:<2}\\                     /   House 4: {h_rasi[4][0]:<2}    |",
        f"| {', '.join(h_planets[10]) if h_planets[10] else '-':<13} \\       House 7: {h_rasi[7][0]:<2}       /   {', '.join(h_planets[4]) if h_planets[4] else '-':<13} |",
        f"|       /   \\    {', '.join(h_planets[7]) if h_planets[7] else '-':<12}    /   \\       |",
        f"|     /       \\                 /       \\     |",
        f"|   /  House 9: {h_rasi[9][0]:<2} \\             /  House 5: {h_rasi[5][0]:<2}   \\   |",
        f"| /   {', '.join(h_planets[9]) if h_planets[9] else '-':<18} \\         /   {', '.join(h_planets[5]) if h_planets[5] else '-':<18} \\ |",
        "+-----------------------------+-----------------------------+",
        f"| \\  House 8: {h_rasi[8][0]:<2}             /   \\  House 6: {h_rasi[6][0]:<2}             / |",
        f"|   \\  {', '.join(h_planets[8]) if h_planets[8] else '-':<18} /     \\  {', '.join(h_planets[6]) if h_planets[6] else '-':<18} /   |",
        "+-----------------------------+-----------------------------+"
    ]
    for l in lines:
        print(l)

render_north_indian_ascii("D-10 Dasamsa (Career & Karma Chart)", d10_data)
render_north_indian_ascii("D-24 Siddhamsa (Higher Learning & Intellect)", d24_data)
render_north_indian_ascii("D-1 Rasi (Natal Birth Chart)", d1_data)
render_north_indian_ascii("D-9 Navamsa (Dharma & Potential)", d9_data)
