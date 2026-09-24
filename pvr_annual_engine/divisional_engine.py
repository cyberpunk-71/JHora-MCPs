"""
PVR Divisional Chart (Varga) Engine
===================================
Implements P.V.R. Narasimha Rao's exact mathematical rules for divisional charts:
  - D-10: Method 3 (Parasara with Even Sign Reversal)
  - D-24: Method 2 (Parasara Corrected: Odd from Leo direct, Even from Cancer reverse)
  - D-60: Method 3 (Parivritti alternate with reverse from Aries in even signs)
  - All standard Parasara Vargas under Pushya-Paksha Ayanamsa
"""

from typing import Dict, Any, List, Tuple
from pvr_annual_engine.config import RASI_NAMES

def get_divisional_sign_and_deg(rasi_idx: int, deg_in_rasi: float, varga_factor: int) -> Tuple[int, float]:
    """
    Computes (varga_sign_index, varga_degree_in_sign) for any division factor.
    """
    span = 30.0 / float(varga_factor)
    k = int(deg_in_rasi // span)
    if k >= varga_factor:
        k = varga_factor - 1
    deg_in_varga = (deg_in_rasi - (k * span)) * float(varga_factor)

    if varga_factor == 1:
        v_sign = rasi_idx
    elif varga_factor == 2:  # Hora
        if rasi_idx % 2 == 0:  # Odd sign: 0-15 Sun (Leo=4), 15-30 Moon (Cancer=3)
            v_sign = 4 if k == 0 else 3
        else:  # Even sign: 0-15 Moon (Cancer=3), 15-30 Sun (Leo=4)
            v_sign = 3 if k == 0 else 4
    elif varga_factor == 3:  # Drekkana
        v_sign = (rasi_idx + 4 * k) % 12
    elif varga_factor == 4:  # Chaturthamsa
        v_sign = (rasi_idx + 3 * k) % 12
    elif varga_factor == 7:  # Saptamsa
        if rasi_idx % 2 == 0:  # Odd sign
            v_sign = (rasi_idx + k) % 12
        else:  # Even sign (counts direct from 7th)
            v_sign = (rasi_idx + 6 + k) % 12
    elif varga_factor == 9:  # Navamsa
        elem = rasi_idx % 4
        if elem == 0: start = 0    # Fiery -> Aries
        elif elem == 1: start = 9  # Earthy -> Capricorn
        elif elem == 2: start = 6  # Airy -> Libra
        else: start = 3            # Watery -> Cancer
        v_sign = (start + k) % 12
    elif varga_factor == 10:  # Dasamsa (PVR Method 3: Even Sign Reversal)
        if rasi_idx % 2 == 0:  # Odd sign: direct from sign
            v_sign = (rasi_idx + k) % 12
        else:  # Even sign: reverse from 9th from it
            v_sign = ((rasi_idx + 8) - k) % 12
    elif varga_factor == 12:  # Dwadasamsa
        v_sign = (rasi_idx + k) % 12
    elif varga_factor == 16:  # Shodasamsa (Method 2: Even Sign Reversal)
        m = rasi_idx % 3
        start = 0 if m == 0 else (4 if m == 1 else 8)
        if rasi_idx % 2 == 0:
            v_sign = (start + k) % 12
        else:
            v_sign = (start + 15 - k) % 12
    elif varga_factor == 20:  # Vimsamsa
        m = rasi_idx % 3
        start = 0 if m == 0 else (8 if m == 1 else 4)
        v_sign = (start + k) % 12
    elif varga_factor == 24:  # Siddhamsa (PVR Method 2: Odd Leo direct, Even Cancer reverse)
        if rasi_idx % 2 == 0:  # Odd sign -> direct from Leo (4)
            v_sign = (4 + k) % 12
        else:  # Even sign -> reverse from Cancer (3)
            v_sign = (3 - k) % 12
    elif varga_factor == 27:  # Nakshatramsa / Bhamsa
        elem = rasi_idx % 4
        start = 0 if elem == 0 else (3 if elem == 1 else (6 if elem == 2 else 9))
        v_sign = (start + k) % 12
    elif varga_factor == 30:  # Trimsamsa
        if rasi_idx % 2 == 0:  # Odd: Mars(5), Sat(5), Jup(8), Merc(7), Ven(5)
            if deg_in_rasi < 5.0: v_sign = 0      # Aries
            elif deg_in_rasi < 10.0: v_sign = 10  # Aquarius
            elif deg_in_rasi < 18.0: v_sign = 8   # Sagittarius
            elif deg_in_rasi < 25.0: v_sign = 2   # Gemini
            else: v_sign = 6                      # Libra
        else:  # Even: Ven(5), Merc(7), Jup(8), Sat(5), Mars(5)
            if deg_in_rasi < 5.0: v_sign = 1      # Taurus
            elif deg_in_rasi < 12.0: v_sign = 5   # Virgo
            elif deg_in_rasi < 20.0: v_sign = 11  # Pisces
            elif deg_in_rasi < 25.0: v_sign = 9   # Capricorn
            else: v_sign = 7                      # Scorpio
    elif varga_factor == 40:  # Khavedamsa
        start = 0 if rasi_idx % 2 == 0 else 6
        v_sign = (start + k) % 12
    elif varga_factor == 45:  # Akshavedamsa
        m = rasi_idx % 3
        start = 0 if m == 0 else (4 if m == 1 else 8)
        v_sign = (start + k) % 12
    elif varga_factor == 60:  # Shashtiamsa (PVR Method 3)
        if rasi_idx % 2 == 0:
            v_sign = (rasi_idx + k) % 12
        else:
            v_sign = ((rasi_idx + 6) - k) % 12
    else:
        v_sign = (rasi_idx + k) % 12

    return v_sign % 12, deg_in_varga

def build_varga_chart(d1_lagna_deg: float, planets_d1: Dict[str, Tuple[float, bool]], varga_factor: int) -> Dict[str, Any]:
    """
    Builds a complete divisional chart dictionary from D-1 positions.
    """
    lagna_rasi = int(d1_lagna_deg // 30.0)
    lagna_deg = d1_lagna_deg % 30.0
    v_lagna_sign, v_lagna_deg = get_divisional_sign_and_deg(lagna_rasi, lagna_deg, varga_factor)

    v_planets = {}
    for p_name, (tot_deg, is_retro) in planets_d1.items():
        p_rasi = int(tot_deg // 30.0)
        p_deg = tot_deg % 30.0
        v_sign, v_p_deg = get_divisional_sign_and_deg(p_rasi, p_deg, varga_factor)
        v_planets[p_name] = {
            "rasi_idx": v_sign,
            "rasi_name": RASI_NAMES[v_sign],
            "deg_in_rasi": round(v_p_deg, 2),
            "is_retrograde": is_retro
        }

    return {
        "varga_factor": varga_factor,
        "varga_name": f"D-{varga_factor}",
        "lagna": {
            "rasi_idx": v_lagna_sign,
            "rasi_name": RASI_NAMES[v_lagna_sign],
            "deg_in_rasi": round(v_lagna_deg, 2)
        },
        "planets": v_planets
    }
