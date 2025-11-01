from flask import Flask, request
from flask_cors import CORS
import os
import socket
import random
import json
import logging
import psycopg2
import time
import sys

# -----------------------------
# Logging Setup
# -----------------------------
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# -----------------------------
# Config (from environment)
# -----------------------------
option_a = os.getenv('OPTION_A', "Cats")
option_b = os.getenv('OPTION_B', "Dogs")

db_hostname = os.getenv('PGHOST', 'postgres')
db_database = os.getenv('PGDATABASE', 'postgres')
db_password = os.getenv('PGPASSWORD', 'postgres')
db_user = os.getenv('PGUSER', 'postgres')

hostname = socket.gethostname()

app = Flask(__name__)
CORS(app)

print("🐍 Starting API Service...")
print(f"Connecting to DB at host={db_hostname}, db={db_database}, user={db_user}")

# -----------------------------
# Helper: Wait for DB and init table
# -----------------------------
def init_db(retries=10, delay=3):
    """Wait for Postgres and initialize the votes table."""
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(
                host=db_hostname,
                user=db_user,
                password=db_password,
                dbname=db_database
            )
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS votes (
                    id VARCHAR(255) PRIMARY KEY,
                    vote VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("✅ Database ready (votes table exists)")
            return
        except Exception as e:
            print(f"⚠️ Database not ready yet ({e}) — retrying ({attempt+1}/{retries})...")
            time.sleep(delay)
    print("❌ Could not connect to database after several retries.")
    sys.exit(1)

# Initialize database when app starts
init_db()

# -----------------------------
# Routes
# -----------------------------
@app.route("/health", methods=['GET'])
def health():
    return ("", 200)

@app.route("/api", methods=['GET'])
def hello():
    return ("Hello, I am the API service", 200)

@app.route("/api/vote", methods=['GET'])
def get_votes():
    try:
        conn = psycopg2.connect(host=db_hostname, user=db_user, password=db_password, dbname=db_database)
        cur = conn.cursor()
        cur.execute("SELECT vote, COUNT(id) AS count FROM votes GROUP BY vote;")
        res = cur.fetchall()
        cur.close()
        conn.close()
        return app.response_class(
            response=json.dumps(res),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print("❌ Error fetching votes:", e)
        return app.response_class(response=json.dumps({"error": str(e)}), status=500, mimetype='application/json')

@app.route("/api/vote", methods=['POST'])
def post_vote():
    try:
        voter_id = hex(random.getrandbits(64))[2:-1]
        vote = request.form.get('vote')

        if not vote:
            return app.response_class(
                response=json.dumps({"error": "Missing vote parameter"}),
                status=400,
                mimetype='application/json'
            )

        conn = psycopg2.connect(host=db_hostname, user=db_user, password=db_password, dbname=db_database)
        cur = conn.cursor()
        cur.execute("INSERT INTO votes (id, vote, created_at) VALUES (%s, %s, NOW());", (voter_id, vote))
        conn.commit()
        cur.close()
        conn.close()

        print(f"🗳️ Received vote '{vote}' from voter '{voter_id}'")
        return app.response_class(
            response=json.dumps({'voter_id': voter_id, 'vote': vote}),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        print("❌ Error inserting vote:", e)
        return app.response_class(response=json.dumps({"error": str(e)}), status=500, mimetype='application/json')


# -----------------------------
# Main Entry
# -----------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
