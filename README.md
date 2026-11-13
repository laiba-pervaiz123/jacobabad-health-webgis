# Jacobabad Health GIS - Dynamic 3D Web GIS (PostgreSQL/PostGIS)

Midterm project - Web GIS Applications (MET418), BS Remote Sensing & GIS, COMSATS University Islamabad.
Student: Laiba Pervaiz (FA23-BRG-031)

Shows 25 medical facilities of Jacobabad, Sindh on an interactive 3D map.

**Flow:** PostgreSQL/PostGIS -> Flask API (GeoJSON) -> MapLibre GL website

## Files
| File | Purpose |
|---|---|
| `schema.sql` | Enables PostGIS and creates the table |
| `insert_data.sql` | 25 facility records |
| `prepare_data.py` | Reads the Excel file and creates `insert_data.sql` |
| `app.py` | Flask API (`/api/facilities`, `/api/stats`, `/api/nearest`) |
| `static/index.html` | The website |

## Run locally
1. Create database `jacobabad_medical`, run `schema.sql` then `insert_data.sql` in pgAdmin.
2. `pip install -r requirements.txt`
3. Create `local_settings.py` with `DB_PASSWORD = "your_password"` (see `local_settings.py.example`).
4. `python app.py` and open http://127.0.0.1:5000

## Live demo
(add link here)
