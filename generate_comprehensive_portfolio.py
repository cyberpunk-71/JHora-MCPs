#!/usr/bin/env python3
import os
import sys
import svgwrite
sys.path.insert(0, '/home/opc/mcp_jhora')
from jhora.horoscope.chart import charts
from jhora_helpers import create_date_and_place, RASI_NAMES, PLANET_NAMES

dob, tob, place, jd = create_date_and_place(2001, 10, 6, 16, 59, 7, 23.0225, 72.5714, 5.5, "Ahmedabad", "PUSHYA_PAKSHA")

# Planet colors & glyphs
PLANET_DISPLAY = {
    'Sun': {'abbr': 'Su', 'color': '#c2410c'},
    'Moon': {'abbr': 'Mo', 'color': '#1d4ed8'},
    'Mars': {'abbr': 'Ma', 'color': '#b91c1c'},
    'Mercury': {'abbr': 'Me', 'color': '#047857'},
    'Jupiter': {'abbr': 'Ju', 'color': '#b45309'},
    'Venus': {'abbr': 'Ve', 'color': '#be185d'},
    'Saturn': {'abbr': 'Sa', 'color': '#334155'},
    'Rahu': {'abbr': 'Ra', 'color': '#475569'},
    'Ketu': {'abbr': 'Ke', 'color': '#78350f'},
    'Lagna': {'abbr': 'Asc', 'color': '#6d28d9'}
}

def draw_single_diamond(dwg, chart_factor, title, x_start, y_start, w=420, h=420):
    data = charts.divisional_chart(jd, place, divisional_chart_factor=chart_factor, chart_method=1)
    lag_idx = data[0][1][0]
    lag_deg = data[0][1][1]
    
    h_rasi = {}
    h_planets = {h: [] for h in range(1, 13)}
    
    for h_num in range(1, 13):
        r_i = (lag_idx + (h_num - 1)) % 12
        h_rasi[h_num] = (r_i + 1, RASI_NAMES[r_i])
        
    for item in data[1:10]:
        p_name = PLANET_NAMES[item[0]]
        r_i = item[1][0]
        deg_in_r = item[1][1]
        h_num = ((r_i - lag_idx + 12) % 12) + 1
        h_planets[h_num].append((p_name, deg_in_r))
        
    # Chart background box
    dwg.add(dwg.rect(insert=(x_start, y_start), size=(w, h+55), fill="#faf6ee", rx=12, ry=12, stroke="#d6d3d1", stroke_width=1.5))
    
    # Title
    dwg.add(dwg.text(title, insert=(x_start + w/2, y_start + 24), text_anchor="middle", font_size="15px", font_weight="bold", fill="#1e293b", font_family="system-ui, sans-serif"))
    dwg.add(dwg.text(f"Lagna: {RASI_NAMES[lag_idx]} ({lag_deg:.2f}°)", insert=(x_start + w/2, y_start + 42), text_anchor="middle", font_size="11px", fill="#64748b", font_family="system-ui, sans-serif"))
    
    y_off = y_start + 50
    x_off = x_start
    cx, cy = x_off + w/2, y_off + h/2
    
    # Coordinates
    p_h1 = [(cx, y_off), (cx + w/4, y_off + h/4), (cx, y_off + h/2), (cx - w/4, y_off + h/4)]
    p_h2 = [(x_off, y_off), (cx, y_off), (cx - w/4, y_off + h/4)]
    p_h3 = [(x_off, y_off), (cx - w/4, y_off + h/4), (x_off, y_off + h/2)]
    p_h4 = [(x_off, y_off + h/2), (cx - w/4, y_off + h/4), (cx, y_off + h/2), (cx - w/4, y_off + 3*h/4)]
    p_h5 = [(x_off, y_off + h/2), (cx - w/4, y_off + 3*h/4), (x_off, y_off + h)]
    p_h6 = [(x_off, y_off + h), (cx - w/4, y_off + 3*h/4), (cx, y_off + h)]
    p_h7 = [(cx, y_off + h/2), (cx + w/4, y_off + 3*h/4), (cx, y_off + h), (cx - w/4, y_off + 3*h/4)]
    p_h8 = [(cx, y_off + h), (cx + w/4, y_off + 3*h/4), (x_off + w, y_off + h)]
    p_h9 = [(x_off + w, y_off + h), (cx + w/4, y_off + 3*h/4), (x_off + w, y_off + h/2)]
    p_h10 = [(cx, y_off + h/2), (cx + w/4, y_off + h/4), (x_off + w, y_off + h/2), (cx + w/4, y_off + 3*h/4)]
    p_h11 = [(x_off + w, y_off + h/2), (cx + w/4, y_off + h/4), (x_off + w, y_off)]
    p_h12 = [(x_off + w, y_off), (cx + w/4, y_off + h/4), (cx, y_off)]
    
    house_polys = {
        1: p_h1, 2: p_h2, 3: p_h3, 4: p_h4, 5: p_h5, 6: p_h6,
        7: p_h7, 8: p_h8, 9: p_h9, 10: p_h10, 11: p_h11, 12: p_h12
    }
    
    for h_idx, poly_pts in house_polys.items():
        dwg.add(dwg.polygon(points=poly_pts, fill="#ffffff", stroke="#b45309", stroke_width=1.2))
        
    dwg.add(dwg.rect(insert=(x_off, y_off), size=(w, h), fill="none", stroke="#78350f", stroke_width=2))
    
    # Sign pos
    sign_pos = {
        1: (cx, y_off + h/2 - 18),
        2: (cx - w/4 + 16, y_off + 25),
        3: (x_off + 25, y_off + h/4 + 14),
        4: (cx - 22, y_off + h/2),
        5: (x_off + 25, y_off + 3*h/4 - 14),
        6: (cx - w/4 + 16, y_off + h - 18),
        7: (cx, y_off + h/2 + 25),
        8: (cx + w/4 - 16, y_off + h - 18),
        9: (x_off + w - 25, y_off + 3*h/4 - 14),
        10: (cx + 22, y_off + h/2),
        11: (x_off + w - 25, y_off + h/4 + 14),
        12: (cx + w/4 - 16, y_off + 25)
    }
    
    planet_centers = {
        1: (cx, y_off + h/4),
        2: (x_off + w/4, y_off + h/8 + 8),
        3: (x_off + w/8 + 8, y_off + h/4),
        4: (x_off + w/4, y_off + h/2),
        5: (x_off + w/8 + 8, y_off + 3*h/4),
        6: (x_off + w/4, y_off + 7*h/8 - 8),
        7: (cx, y_off + 3*h/4),
        8: (x_off + 3*w/4, y_off + 7*h/8 - 8),
        9: (x_off + 7*w/8 - 8, y_off + 3*h/4),
        10: (x_off + 3*w/4, y_off + h/2),
        11: (x_off + 7*w/8 - 8, y_off + h/4),
        12: (x_off + 3*w/4, y_off + h/8 + 8)
    }
    
    for h_num, (sign_n, r_name) in h_rasi.items():
        sx, sy = sign_pos[h_num]
        dwg.add(dwg.text(str(sign_n), insert=(sx, sy), text_anchor="middle", font_size="11px", font_weight="bold", fill="#92400e", font_family="system-ui, sans-serif"))
        
    for h_num, plist in h_planets.items():
        if not plist:
            continue
        pcx, pcy = planet_centers[h_num]
        num_p = len(plist)
        if num_p == 1:
            p_name, p_deg = plist[0]
            info = PLANET_DISPLAY[p_name]
            dwg.add(dwg.text(f"{info['abbr']} {p_deg:.1f}°", insert=(pcx, pcy + 4), text_anchor="middle", font_size="11px", font_weight="bold", fill=info['color'], font_family="system-ui, sans-serif"))
        elif num_p == 2:
            for idx, (p_name, p_deg) in enumerate(plist):
                info = PLANET_DISPLAY[p_name]
                offset_y = -7 if idx == 0 else 11
                dwg.add(dwg.text(f"{info['abbr']} {p_deg:.1f}°", insert=(pcx, pcy + offset_y), text_anchor="middle", font_size="10px", font_weight="bold", fill=info['color'], font_family="system-ui, sans-serif"))
        else:
            for idx, (p_name, p_deg) in enumerate(plist):
                info = PLANET_DISPLAY[p_name]
                offset_y = (idx - (num_p - 1)/2.0) * 12
                dwg.add(dwg.text(f"{info['abbr']} {p_deg:.1f}°", insert=(pcx, pcy + offset_y), text_anchor="middle", font_size="9.5px", font_weight="bold", fill=info['color'], font_family="system-ui, sans-serif"))

# Generate Master Portfolio SVG
portfolio_dwg = svgwrite.Drawing("/home/opc/mcp_jhora/output_charts/North_Indian_Charts_Portfolio.svg", size=('920px', '1180px'), viewBox='0 0 920 1180')
bg = svgwrite.gradients.LinearGradient(start=(0, 0), end=(1, 1), id="port_bg")
bg.add_stop_color(0, '#fdfbf7')
bg.add_stop_color(1, '#f5efe6')
portfolio_dwg.defs.add(bg)

portfolio_dwg.add(portfolio_dwg.rect(insert=(0, 0), size=(920, 1180), fill="url(#port_bg)", rx=16, ry=16, stroke="#cbd5e1", stroke_width=2))

# Master Title
portfolio_dwg.add(portfolio_dwg.text("Complete Vedic Astrology Portfolio (North Indian Diamond Style)", insert=(460, 42), text_anchor="middle", font_size="22px", font_weight="bold", fill="#0f172a", font_family="system-ui, sans-serif"))
portfolio_dwg.add(portfolio_dwg.text("Native: Born 2001-10-06 at 16:59:09 IST | Ahmedabad, Gujarat | Pushya-Paksha Ayanamsa (Pt. PVR Narasimha Rao)", insert=(460, 68), text_anchor="middle", font_size="12.5px", fill="#475569", font_family="system-ui, sans-serif"))

# Grid of 4 Charts
# Top Left: D-1 Rasi (x=25, y=95)
draw_single_diamond(portfolio_dwg, 1, "D-1 Rasi Birth Chart (Lagna)", 25, 95, w=420, h=420)
# Top Right: D-10 Dasamsa (x=475, y=95)
draw_single_diamond(portfolio_dwg, 10, "D-10 Dasamsa Career & Karma Chart", 475, 95, w=420, h=420)
# Bottom Left: D-9 Navamsa (x=25, y=600)
draw_single_diamond(portfolio_dwg, 9, "D-9 Navamsa Dharma & Partnership Chart", 25, 600, w=420, h=420)
# Bottom Right: D-24 Siddhamsa (x=475, y=600)
draw_single_diamond(portfolio_dwg, 24, "D-24 Siddhamsa Higher Learning Chart", 475, 600, w=420, h=420)

# Master Footer
portfolio_dwg.add(portfolio_dwg.text("Generated with PyJHora 6-MCP Architecture | Pushya-Paksha Ayanamsa (22°45'08\") | Pt. P. V. R. Narasimha Rao Standard", insert=(460, 1145), text_anchor="middle", font_size="11.5px", fill="#64748b", font_family="system-ui, sans-serif"))

portfolio_dwg.save()
print("Saved Master Portfolio SVG: /home/opc/mcp_jhora/output_charts/North_Indian_Charts_Portfolio.svg")

