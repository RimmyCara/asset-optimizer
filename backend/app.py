from flask import Flask, request, jsonify, render_template
import mysql.connector
import heapq
import itertools
import os
import re

counter = itertools.count()
app = Flask(__name__,)

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
        port = 3306
    )
    
asset_queue = []
current_asset = None

def process_asset(asset_name, condition, asset_id=None):
    priority = calculate_priority(condition)

    asset = {
        "name": asset_name,
        "status": condition,
        "priority": priority,
        "id": asset_id
    }

    heapq.heappush(asset_queue, (priority, next(counter), asset))  # 1 is highest priority, so lowest numeric value wins

    return asset

def calculate_priority(status):
    # 1 = most important, 5 = least
    priority_map = {
        "critical": 1,      
        "high": 2,
        "standard": 3,
        "low": 4,
        "complete": 5       
    }
    return priority_map.get(status.lower(), 0)  # Default to 0 if unknown


def process_next_asset():
    if asset_queue:
        _, _, asset = heapq.heappop(asset_queue)
        return asset
    else:
        return None

cursor = get_db_connection().cursor(dictionary=True)


@app.route("/")
def home():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1")  # simple test query
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return f"MySQL Connected Successfully: {result}"


@app.route("/assets", methods=["GET"])
def get_assets():
    cursor.execute("SELECT * FROM assets")
    assets = cursor.fetchall()
    return jsonify(assets)

@app.route("/completed_assets", methods=["GET"])
def get_completed_assets():
    cursor.execute("SELECT id, name, status, priority, date_returned FROM assets WHERE completed = TRUE ORDER BY id DESC LIMIT 5")
    assets = cursor.fetchall()
    return jsonify(assets)

@app.route("/add_asset", methods=["POST"])
def add_asset():
    data = request.json
    name = data["name"].strip()
    status = data["status"].strip().lower()
    
    if not re.match(r'^[a-zA-Z0-9\s]+$', name):
        return jsonify({"error": "Add Asset can only contain letters, numbers, and spaces"}), 400
    
    if not name or len(name) > 50:
        return jsonify({"error": "Asset name must be between 1-50 characters"}), 400
    
    # Validate status
    valid_statuses = ["critical", "high", "standard", "low", "complete"]
    if status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400
    
    priority = calculate_priority(status)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "INSERT INTO assets (name, priority, status) VALUES (%s, %s, %s)"
    values = (name, priority, status)
    cursor.execute(sql, values)
    conn.commit()
    
    asset_id = cursor.lastrowid

    cursor.close()
    conn.close()

    process_asset(name, status, asset_id)

    return jsonify({"message": "Asset added successfully!", "id": asset_id})

@app.route("/next_asset", methods=["GET"])
def get_next_asset():
    global current_asset

    if current_asset is not None:
        return jsonify({"message": "Complete the current asset first", "asset": current_asset})

    asset = process_next_asset()
    if asset:
        current_asset = asset
        return jsonify(asset)

    return jsonify({"message": "No assets in queue"})
    
@app.route('/completeAsset/<int:id>', methods=['PUT'])
def complete_asset(id):
    global current_asset

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "UPDATE assets SET completed = TRUE WHERE id = %s"
    cursor.execute(query, (id,))
    
    conn.commit()
    cursor.close()
    conn.close()

    # Reset current asset if it was the same
    if current_asset and current_asset.get('id') == id:
        current_asset = None

    # Remove from queue
    global asset_queue
    asset_queue = [item for item in asset_queue if item[2]['id'] != id]
    heapq.heapify(asset_queue)

    return jsonify({"message": "Asset completed"})

if __name__ == "__main__":
    # Clear the queue first
    asset_queue.clear()

    # load all DB assets into queue
    cursor.execute("SELECT id, name, status FROM assets WHERE completed = FALSE")
    for row in cursor.fetchall():
        process_asset(row["name"], row["status"], row["id"])
    
    app.run(debug=True)