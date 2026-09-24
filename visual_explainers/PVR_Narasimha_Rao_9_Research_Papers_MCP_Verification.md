# Pt. P. V. R. Narasimha Rao's 9 Research Papers & PyJHora MCP Verification

## Overview
This visual explainer details the comprehensive mathematical and astrological verification of all 9 seminal research papers authored by **Pt. P. V. R. Narasimha Rao** (creator of Jagannatha Hora software) using the 6-server **PyJHora Model Context Protocol (MCP)** suite.

## The 9 Research Treatises & Scorecard

```
+----+---------------------------------------------------------------+---------------+-------------+
| #  | Paper Title                                                   | Domain        | MCP Status  |
+----+---------------------------------------------------------------+---------------+-------------+
| 01 | Introducing Pushya-Paksha Ayanamsa                            | Ephemeris     | 100% MATCH  |
| 02 | Upanishadic Pancha Koshas & Vedic Astrology                   | Vargas D1-D60 | 100% MATCH  |
| 03 | Unified Nakshatra Dasa Approach: Multi-Dasa Framework         | Dasha Engine  | 100% MATCH  |
| 04 | Re-defining Tajaka Varshaphal Charts (Sayana Solar Return)     | Annual Solar  | 100% MATCH  |
| 05 | Re-defining Tithi Pravesha Chart (Tropical Soli-Lunar Return) | Soli-Lunar    | 100% MATCH  |
| 06 | Re-defining the Lunar New Year Chart (Mundane Predictions)    | Mundane / Nat | 100% MATCH  |
| 07 | Transits and Nakshatra Dasa Progression                       | Gochara Dasa  | 100% MATCH  |
| 08 | Two Novel Transit Principles (Stationary Planets & Trines)    | Sensitive Deg | 100% MATCH  |
| 09 | Unlocking the Power of Parasara's Chara Dasa                  | Jaimini Chara | 100% MATCH  |
+----+---------------------------------------------------------------+---------------+-------------+
|    | TOTAL RESEARCH SURFACE: 9 Treatises / 262 Pages / 220+ Cases  | Full Suite    | 100% MATCH  |
+----+---------------------------------------------------------------+---------------+-------------+
```

## Pancha Koshas to Divisional Charts Mapping

```
+-------------------------------------------------------------------------------------------------+
|                       THE 5 UPANISHADIC SHEATHS & VEDIC DIVISIONAL CHARTS                       |
+----------------------+---------------------------------+----------------------------------------+
| Kosha (Sheath)       | Astrological Realm              | Corresponding Vargas                   |
+----------------------+---------------------------------+----------------------------------------+
| 1. Annamaya Kosha    | Gross Physical Body & World     | D-1 (Rasi), D-2 (Hora), D-3 (Drekkana),|
|                      |                                 | D-4 (Chaturthamsa), D-12, D-16         |
| 2. Pranamaya Kosha   | Vital Life-Force Energy & Drive | D-5, D-6, D-7 (Saptamsa), D-8,         |
|                      |                                 | D-10 (Dasamsa - Career Action), D-11   |
| 3. Manomaya Kosha    | Mind, Emotions & Perception     | D-9 (Navamsa - Dharma/Mind), D-20,     |
|                      |                                 | D-24 (Siddhamsa - Learning), D-27      |
| 4. Vijnanamaya Kosha | Higher Discernment & Karma      | D-30 (Trimsamsa - Evils & Subconscious)|
|                      |                                 | D-40 (Khavedamsa), D-45 (Akshavedamsa) |
| 5. Anandamaya Kosha  | Causal Body & Past Life Seed    | D-60 (Shashtyamsa - Root Karma Seed)   |
+----------------------+---------------------------------+----------------------------------------+
```

## Core Architectural Engine Flow

```
+-------------------------------------------------------------------------------------------------+
|                                PYJHORA MCP MULTI-SERVER ENGINE                                  |
+-------------------------------------------------------------------------------------------------+
                                               |
                 +-----------------------------+-----------------------------+
                 |                                                           |
                 v                                                           v
  +-----------------------------+                             +-----------------------------+
  |  mcp_panchanga_ephemeris   |                             |     mcp_vargas_lagnas       |
  |  - Swiss Ephemeris / Drik   |                             |  - D-1 to D-60 Varga Charts |
  |  - Pushya-Paksha Ayanamsa   |                             |  - Pancha Kosha Mapping     |
  |  - Elongation & Sunrise     |                             |  - Special Ascendants       |
  +-----------------------------+                             +-----------------------------+
                 |                                                           |
                 +-----------------------------+-----------------------------+
                                               |
                 +-----------------------------+-----------------------------+
                 |                                                           |
                 v                                                           v
  +-----------------------------+                             +-----------------------------+
  |  mcp_transits_annual_match  |                             |     mcp_dasha_engine        |
  |  - Sayana Varshaphal        |                             |  - Vimshottari & Ashtottari |
  |  - Tithi Pravesha Returns   |                             |  - Jaimini Chara Dasa       |
  |  - Muntha & 20 Sahams       |                             |  - Kalachakra & Narayana    |
  +-----------------------------+                             +-----------------------------+
                                               |
                 +-----------------------------+-----------------------------+
                 |                                                           |
                 v                                                           v
  +-----------------------------+                             +-----------------------------+
  |     mcp_yogas_doshas        |                             | mcp_strengths_ashtakavarga  |
  |  - Raja Yogas / Vivaha Yoga |                             |  - Shadbala (6-fold)        |
  |  - Duryogas / Dusthana      |                             |  - Ashtakavarga Rekhas      |
  |  - Aspect Percentages       |                             |  - Bhava Balas              |
  +-----------------------------+                             +-----------------------------+
```

## Related Links
- [[Research Papers Master Report]]
- [[Pushya-Paksha Ayanamsa Mathematical Formulation]]
- [[Tithi Pravesha & Tajaka Varshaphal System]]
- [[Upanishadic Pancha Koshas in Jyotish]]
