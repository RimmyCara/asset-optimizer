from flask import Flask, request, jsonify, render_template
import mysql.connector
import heapq
import itertools
import os
import re

app = Flask(__name__)

counter = itertools.count()
asset_queue = []
current_asset = None


# -------------------------
# DATABASE CONNECTION
# -------------------------
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )


# -------------------------
# PRIORITY SYSTEM
# -------------------------
def calculate_priority(status):
    priority_map = {
        "critical": 1,
        "high": 2,
        "standard": 3,
        "low": 4,
        "complete": 5
    }
    return priority_map.get(status.lower(), 0)


def process_asset(asset_name, condition, asset_id=None):
    priority = calculate_priority(condition)

    asset = {
        "name": asset_name,
        "status": condition,
        "priority": priority,
        "id": asset_id
    }

    heapq.heappush(asset_queue, (priority, next(counter), asset))
    return asset


def process_next_asset():
    if asset_queue:
        _, _, asset = heapq.heappop(asset_queue)
        return asset
    return None


# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1")
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return f"MySQL Connected Successfully: {result}"


@app.route("/assets", methods=["GET"])
def get_assets():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM assets")
    assets = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(assets)


@app.route("/add_asset", methods=["POST"])
def add_asset():
    data = request.json
    name = data["name"].strip()
    status = data["status"].strip().lower()

    if not re.match(r'^[a-zA-Z0-9\s]+$', name):
        return jsonify({"error": "Invalid name"}), 400

    if status not in ["critical", "high", "standard", "low", "complete"]:
        return jsonify({"error": "Invalid status"}), 400

    priority = calculate_priority(status)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO assets (name, priority, status) VALUES (%s, %s, %s)",
        (name, priority, status)
    )

    conn.commit()
    asset_id = cursor.lastrowid

    cursor.close()
    conn.close()

    process_asset(name, status, asset_id)

    return jsonify({"message": "Asset added", "id": asset_id})


@app.route("/next_asset", methods=["GET"])
def get_next_asset():
    global current_asset

    if current_asset:
        return jsonify({"message": "Complete current asset first", "asset": current_asset})

    asset = process_next_asset()

    if asset:
        current_asset = asset
        return jsonify(asset)

    return jsonify({"message": "No assets in queue"})


@app.route("/completeAsset/<int:id>", methods=["PUT"])
def complete_asset(id):
    global current_asset

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE assets SET completed = TRUE WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    if current_asset and current_asset.get("id") == id:
        current_asset = None

    global asset_queue
    asset_queue = [item for item in asset_queue if item[2]["id"] != id]
    heapq.heapify(asset_queue)

    return jsonify({"message": "Asset completed"})


# -------------------------
# RENDER ENTRY POINT
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)