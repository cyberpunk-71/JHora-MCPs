#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/opc/mcp_jhora')
from jhora.horoscope.chart import charts
from jhora_helpers import create_date_and_place, RASI_NAMES, PLANET_NAMES

dob, tob, place, jd = create_date_and_place(2001, 10, 6, 16, 59, 9, 23.0225, 72.5714, 5.5, "Ahmedabad", "PUSHYA_PAKSHA")

# Short names for planets
P_SHORT = {
    'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma', 'Mercury': 'Me',
    'Jupiter': 'Ju', 'Venus': 'Ve', 'Saturn': 'Sa', 'Rahu': 'Ra', 'Ketu': 'Ke'
}

def format_chart(chart_factor, title):
    data = charts.divisional_chart(jd, place, divisional_chart_factor=chart_factor, chart_method=1)
    lag_idx = data[0][1][0]
    
    # House map
    h_rasi = {}
    h_planets = {h: [] for h in range(1, 13)}
    
    for h in range(1, 13):
        r_i = (lag_idx + (h - 1)) % 12
        h_rasi[h] = (r_i + 1, RASI_NAMES[r_i])
        
    for item in data[1:10]:
        p_name = PLANET_NAMES[item[0]]
        r_i = item[1][0]
        h_num = ((r_i - lag_idx + 12) % 12) + 1
        h_planets[h_num].append(P_SHORT[p_name])
        
    def h_str(h):
        r_num, r_name = h_rasi[h]
        p_txt = " ".join(h_planets[h])
        return f"{r_num}:{p_txt}" if p_txt else f"{r_num}"

    print(f"\n{'='*71}")
    print(f"  {title.upper()} (NORTH INDIAN DIAMOND FORMAT)")
    print(f"  Lagna: {RASI_NAMES[lag_idx]} (Sign {lag_idx+1}) | Ayanamsa: Pushya-Paksha")
    print(f"{'='*71}")
    
    out = f"""
+-----------------------------------+-----------------------------------+
| \\               / \\               |               / \\               / |
|   \\   H2:      /     \\   H1:      |     H1:      /     \\   H12:    /   |
|     \\ {h_str(2):<7} /         \\ {h_str(1):<7}  |   {h_str(1):<7} /         \\ {h_str(12):<7} /     |
|       \\     /             \\       |       /             \\     /       |
|  H3:    \\ /     House 1     \\ /   |   \\ /     House 1     \\ /    H11: |
|  {h_str(3):<6}  X     (LAGNA)       X     |     X     (LAGNA)       X     {h_str(11):<6}|
|        / \\    {h_str(1):<11}  / \\   |   / \\    {h_str(1):<11}  / \\         |
|       /     \\             /     \\ | /     \\             /     \\       |
|     /         \\         /         |         \\         /         \\     |
|   /   H4:       \\     /   H7:     |     H7:   \\     /   H10:      \\   |
| /     {h_str(4):<8}  \\ /   {h_str(7):<8}|   {h_str(7):<8}\\ /     {h_str(10):<8}  \\ |
+------------------X----------------+----------------X------------------+
| \\     {h_str(4):<8}  / \\   {h_str(7):<8}|   {h_str(7):<8}/ \\     {h_str(10):<8}  / |
|   \\   H4:       /     \\   H7:     |     H7:   /     \\   H10:      /   |
|     \\         /         \\         |         /         \\         /     |
|       \\     /             \\       |       /             \\     /       |
|  H5:    \\ /     House 7     \\ /   |   \\ /     House 7     \\ /    H9:  |
|  {h_str(5):<6}  X                   X     |     X                   X     {h_str(9):<6}|
|        / \\    {h_str(7):<11}  / \\   |   / \\    {h_str(7):<11}  / \\         |
|       /     \\             /     \\ | /     \\             /     \\       |
|     /         \\         /         |         \\         /         \\     |
|   /   H6:       \\     /   H7:     |     H7:   \\     /   H8:       \\   |
| /     {h_str(6):<8}  \\ /   {h_str(7):<8}|   {h_str(7):<8}\\ /     {h_str(8):<8}  \\ |
+-----------------------------------+-----------------------------------+
"""
    print(out)

format_chart(10, "D-10 Dasamsa (Career & Professional Action)")
format_chart(24, "D-24 Siddhamsa (Higher Learning & Academic Intellect)")
format_chart(1, "D-1 Rasi (Natal Birth Chart)")
format_chart(9, "D-9 Navamsa (Dharma & Potential)")
