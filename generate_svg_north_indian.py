#!/usr/bin/env python3
import os
import sys
import math
import svgwrite
sys.path.insert(0, '/home/opc/mcp_jhora')
from jhora.horoscope.chart import charts
from jhora_helpers import create_date_and_place, RASI_NAMES, PLANET_NAMES

dob, tob, place, jd = create_date_and_place(2001, 10, 6, 16, 59, 7, 23.0225, 72.5714, 5.5, "Ahmedabad", "LAHIRI")

# Planet colors & glyphs/names
PLANET_DISPLAY = {
    'Sun': {'abbr': 'Su', 'color': '#c2410c', 'full': 'Sun'},
    'Moon': {'abbr': 'Mo', 'color': '#1d4ed8', 'full': 'Moon'},
    'Mars': {'abbr': 'Ma', 'color': '#b91c1c', 'full': 'Mars'},
    'Mercury': {'abbr': 'Me', 'color': '#047857', 'full': 'Mercury'},
    'Jupiter': {'abbr': 'Ju', 'color': '#b45309', 'full': 'Jupiter'},
    'Venus': {'abbr': 'Ve', 'color': '#be185d', 'full': 'Venus'},
    'Saturn': {'abbr': 'Sa', 'color': '#334155', 'full': 'Saturn'},
    'Rahu': {'abbr': 'Ra', 'color': '#475569', 'full': 'Rahu'},
    'Ketu': {'abbr': 'Ke', 'color': '#78350f', 'full': 'Ketu'},
    'Lagna': {'abbr': 'Asc', 'color': '#6d28d9', 'full': 'Lagna'}
}

def generate_north_indian_svg(chart_factor, title, filename, width=640, height=640):
    m = 3 if chart_factor == 10 else 1
    data = charts.divisional_chart(jd, place, divisional_chart_factor=chart_factor, chart_method=m)
    lag_idx = data[0][1][0]
    lag_deg = data[0][1][1]
    
    # Houses data
    h_rasi = {}
    h_planets = {h: [] for h in range(1, 13)}
    
    for h in range(1, 13):
        r_i = (lag_idx + (h - 1)) % 12
        h_rasi[h] = (r_i + 1, RASI_NAMES[r_i])
        
    for item in data[1:10]:
        p_name = PLANET_NAMES[item[0]]
        r_i = item[1][0]
        deg_in_r = item[1][1]
        h_num = ((r_i - lag_idx + 12) % 12) + 1
        h_planets[h_num].append((p_name, deg_in_r))
        
    dwg = svgwrite.Drawing(filename, size=(f'{width}px', f'{height+100}px'), viewBox=f'0 0 {width} {height+100}')
    
    # Gradients
    bg_grad = svgwrite.gradients.LinearGradient(start=(0, 0), end=(1, 1), id=f"bg_grad_{chart_factor}")
    bg_grad.add_stop_color(0, '#fdfbf7')
    bg_grad.add_stop_color(1, '#f7f2e8')
    dwg.defs.add(bg_grad)
    
    h_grad = svgwrite.gradients.LinearGradient(start=(0, 0), end=(0, 1), id=f"h_grad_{chart_factor}")
    h_grad.add_stop_color(0, '#ffffff')
    h_grad.add_stop_color(1, '#faf6ee')
    dwg.defs.add(h_grad)
    
    # Outer Card Background with drop shadow effect
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height+100), fill=f"url(#bg_grad_{chart_factor})", rx=16, ry=16, stroke="#d6d3d1", stroke_width=1.5))
    
    # Title Header
    dwg.add(dwg.text(title, insert=(width/2, 36), text_anchor="middle", font_size="19px", font_weight="bold", fill="#1e293b", font_family="system-ui, -apple-system, sans-serif"))
    subtitle = f"Native: 2001-10-06 16:59:09 IST | Ahmedabad (23.02°N, 72.57°E) | Pushya-Paksha | Lagna: {RASI_NAMES[lag_idx]} ({lag_deg:.2f}°)"
    dwg.add(dwg.text(subtitle, insert=(width/2, 60), text_anchor="middle", font_size="11.5px", fill="#64748b", font_family="system-ui, -apple-system, sans-serif"))
    
    y_off = 80
    w = width - 40
    h = height - 40
    x_off = 20
    cx, cy = x_off + w/2, y_off + h/2
    
    # Polygons for the 12 houses (North Indian geometry)
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
    
    for house_idx, poly_pts in house_polys.items():
        dwg.add(dwg.polygon(points=poly_pts, fill=f"url(#h_grad_{chart_factor})", stroke="#b45309", stroke_width=1.5))
        
    # Outer frame
    dwg.add(dwg.rect(insert=(x_off, y_off), size=(w, h), fill="none", stroke="#78350f", stroke_width=2.5))
    
    # House sign numbers positioning
    sign_pos = {
        1: (cx, y_off + h/2 - 25),
        2: (cx - w/4 + 22, y_off + 35),
        3: (x_off + 35, y_off + h/4 + 20),
        4: (cx - 30, y_off + h/2),
        5: (x_off + 35, y_off + 3*h/4 - 20),
        6: (cx - w/4 + 22, y_off + h - 25),
        7: (cx, y_off + h/2 + 35),
        8: (cx + w/4 - 22, y_off + h - 25),
        9: (x_off + w - 35, y_off + 3*h/4 - 20),
        10: (cx + 30, y_off + h/2),
        11: (x_off + w - 35, y_off + h/4 + 20),
        12: (cx + w/4 - 22, y_off + 35)
    }
    
    planet_centers = {
        1: (cx, y_off + h/4),
        2: (x_off + w/4, y_off + h/8 + 10),
        3: (x_off + w/8 + 10, y_off + h/4),
        4: (x_off + w/4, y_off + h/2),
        5: (x_off + w/8 + 10, y_off + 3*h/4),
        6: (x_off + w/4, y_off + 7*h/8 - 10),
        7: (cx, y_off + 3*h/4),
        8: (x_off + 3*w/4, y_off + 7*h/8 - 10),
        9: (x_off + 7*w/8 - 10, y_off + 3*h/4),
        10: (x_off + 3*w/4, y_off + h/2),
        11: (x_off + 7*w/8 - 10, y_off + h/4),
        12: (x_off + 3*w/4, y_off + h/8 + 10)
    }
    
    # Draw Sign Numbers
    for h_num, (sign_n, r_name) in h_rasi.items():
        sx, sy = sign_pos[h_num]
        dwg.add(dwg.text(str(sign_n), insert=(sx, sy), text_anchor="middle", font_size="13px", font_weight="bold", fill="#92400e", font_family="system-ui, -apple-system, sans-serif"))
        
    # Draw Planets in Houses
    for h_num, plist in h_planets.items():
        if not plist:
            continue
        pcx, pcy = planet_centers[h_num]
        num_p = len(plist)
        
        if num_p == 1:
            p_name, p_deg = plist[0]
            info = PLANET_DISPLAY[p_name]
            p_txt = f"{info['abbr']} {p_deg:.1f}°"
            dwg.add(dwg.text(p_txt, insert=(pcx, pcy + 4), text_anchor="middle", font_size="13px", font_weight="bold", fill=info['color'], font_family="system-ui, -apple-system, sans-serif"))
        elif num_p == 2:
            for idx, (p_name, p_deg) in enumerate(plist):
                info = PLANET_DISPLAY[p_name]
                offset_y = -9 if idx == 0 else 13
                p_txt = f"{info['abbr']} {p_deg:.1f}°"
                dwg.add(dwg.text(p_txt, insert=(pcx, pcy + offset_y), text_anchor="middle", font_size="12px", font_weight="bold", fill=info['color'], font_family="system-ui, -apple-system, sans-serif"))
        else:
            for idx, (p_name, p_deg) in enumerate(plist):
                info = PLANET_DISPLAY[p_name]
                offset_y = (idx - (num_p - 1)/2.0) * 15
                p_txt = f"{info['abbr']} {p_deg:.1f}°"
                dwg.add(dwg.text(p_txt, insert=(pcx, pcy + offset_y), text_anchor="middle", font_size="11px", font_weight="bold", fill=info['color'], font_family="system-ui, -apple-system, sans-serif"))

    # Footer note
    dwg.add(dwg.text("Generated with PyJHora MCP Suite | Pt. P.V.R. Narasimha Rao Standard", insert=(width/2, height+85), text_anchor="middle", font_size="10px", fill="#94a3b8", font_family="system-ui, -apple-system, sans-serif"))
    
    dwg.save()
    print(f"Saved: {filename}")

os.makedirs("/home/opc/mcp_jhora/output_charts", exist_ok=True)
generate_north_indian_svg(1, "D-1 Rasi Natal Birth Chart (Lagna)", "/home/opc/mcp_jhora/output_charts/D1_Rasi_Chart_North_Indian.svg")
generate_north_indian_svg(10, "D-10 Dasamsa Career & Karma Chart", "/home/opc/mcp_jhora/output_charts/D10_Dasamsa_Chart_North_Indian.svg")
generate_north_indian_svg(9, "D-9 Navamsa Dharma & Partnership Chart", "/home/opc/mcp_jhora/output_charts/D9_Navamsa_Chart_North_Indian.svg")
generate_north_indian_svg(24, "D-24 Siddhamsa Higher Learning & Intellect Chart", "/home/opc/mcp_jhora/output_charts/D24_Siddhamsa_Chart_North_Indian.svg")
