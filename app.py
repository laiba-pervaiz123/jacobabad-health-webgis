"""
app.py - Flask API for the Jacobabad Medical Facilities Web GIS
Run:  python app.py      then open  http://127.0.0.1:5000
"""
import os
import psycopg2
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# ---------- DATABASE SETTINGS ----------
# Local use: create a file local_settings.py containing:  DB_PASSWORD = "your_password"
# (that file is NOT uploaded to GitHub). Online use: set the DATABASE_URL variable.
try:
    from local_settings import DB_PASSWORD as _LOCAL_PW
except ImportError:
    _LOCAL_PW = "YOUR_PASSWORD"

DATABASE_URL = os.getenv("DATABASE_URL")   # used on Render (Neon connection string)

DB = {
    "dbname": os.getenv("DB_NAME", "jacobabad_medical"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", _LOCAL_PW),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}
# --------------------------------------------------------------

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)


def query_one(sql, params=None):
    """Run a SQL query and return the first column of the first row."""
    conn = psycopg2.connect(DATABASE_URL) if DATABASE_URL else psycopg2.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchone()[0]
    finally:
        conn.close()


@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/api/facilities")
def facilities():
    """All facilities as GeoJSON. Optional filter: /api/facilities?category=Hospitals"""
    category = request.args.get("category")
    sql = """
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', COALESCE(json_agg(json_build_object(
                'type', 'Feature',
                'geometry', ST_AsGeoJSON(geom)::json,
                'properties', json_build_object(
                    'id', id,
                    'name', name,
                    'facility_type', facility_type,
                    'category', category,
                    'contact', contact,
                    'address', address,
                    'operating_hours', operating_hours
                )
            ) ORDER BY id), '[]'::json)
        )
        FROM medical_facilities
        WHERE (%s::text IS NULL OR category = %s::text);
    """
    return jsonify(query_one(sql, (category, category)))


@app.route("/api/stats")
def stats():
    """Summary numbers for the website (counts by category)."""
    sql = """
        SELECT json_build_object(
            'total', (SELECT COUNT(*) FROM medical_facilities),
            'open_24h', (SELECT COUNT(*) FROM medical_facilities
                         WHERE operating_hours ILIKE 'open 24%%'),
            'by_category', (SELECT COALESCE(json_agg(t ORDER BY t.count DESC), '[]'::json)
                            FROM (SELECT category, COUNT(*)::int AS count
                                  FROM medical_facilities GROUP BY category) t)
        );
    """
    return jsonify(query_one(sql))


@app.route("/api/nearest")
def nearest():
    """Nearest facilities to a point (PostGIS distance in metres).
    Example: /api/nearest?lat=28.28&lng=68.44&limit=5"""
    try:
        lat = float(request.args["lat"])
        lng = float(request.args["lng"])
        limit = min(int(request.args.get("limit", 5)), 25)
    except (KeyError, ValueError):
        return jsonify({"error": "Use ?lat=..&lng=..&limit=.."}), 400
    sql = """
        SELECT COALESCE(json_agg(t), '[]'::json) FROM (
            SELECT id, name, facility_type, category, contact, address, operating_hours,
                   ST_Y(geom) AS lat, ST_X(geom) AS lng,
                   ROUND(ST_Distance(geom::geography,
                         ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)::numeric) AS distance_m
            FROM medical_facilities
            ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
            LIMIT %s
        ) t;
    """
    return jsonify(query_one(sql, (lng, lat, lng, lat, limit)))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
