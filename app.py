from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB = "Mydata"

def init_db():
    with sqlite3.connect(DB) as data:
        cursor = data.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                receiver TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tab(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT UNIQUE NOT NULL,
               password TEXT NOT NULL
            )
        ''')

def save_mes(sender,receiver, message):
    with sqlite3.connect(DB) as data:
        cursor = data.cursor()
        cursor.execute('INSERT INTO chat(sender,receiver, message) VALUES (?, ?,?)', (sender,receiver, message))

def get_mes(sender,receiver):
    with sqlite3.connect(DB) as data:
        cursor = data.cursor()
        cursor.execute('SELECT id, sender,receiver,message,timestamp FROM chat  WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY timestamp ASC', (sender,receiver,receiver,sender))
        rows = cursor.fetchall()
    return [{'id': row[0], 'sender': row[1],'receiver':row[2],'message':row[3],'timestamp':row[4]} for row in rows]

def delete_mes(id_mes, username):
    with sqlite3.connect(DB) as data:
        cursor = data.cursor()
        cursor.execute('DELETE FROM chat WHERE id = ? AND sender= ?', (id_mes, username))
        print(f"[DB] Deleted {cursor.rowcount} row(s) | id={id_mes} | user={username}")

# FIXED /delete ROUTE
@app.route('/delete', methods=['POST'])
def dele():
    mes = request.get_json()
    print(f"[FLASK] /delete → {mes}")  # You will see every delete request
    id_mes = mes.get("id")
    username = mes.get("username")
    if id_mes is None or not username:
        return jsonify({"error": "Missing id or username"}), 400
    delete_mes(int(id_mes), username)
    return jsonify({"status": f"Message {id_mes} deleted"}), 200

@app.route('/send', methods=['POST'])
def send():
    data = request.get_json()
    print(f"[FLASK] /send → {data}")
    sender = data.get('username')
    receiver=data.get('receiver')
    message = data.get('message')
    if not sender or not message:
        return jsonify({'error': 'Missing username or message'}), 400
    save_mes(sender,receiver, message)
    return jsonify({'status': 'Message saved successfully'}), 200

@app.route('/resp', methods=['POST'])
def resp():
    data = request.get_json()
    print(f"[FLASK] /resp → {data}")
    sender = data.get('sender')
    receiver=data.get('receiver')
    
    if not sender or not receiver:
        return jsonify({'error': 'Missing username'}), 400
    messages = get_mes(sender,receiver)
    return jsonify(messages), 200

@app.route('/push', methods=['POST'])
def push():
    details = request.get_json()
    print(f"[FLASK] /push → {details}")
    username = details.get('username')
    password = details.get('password')
    try:
        with sqlite3.connect(DB) as data:
            cursor = data.cursor()
            cursor.execute('INSERT INTO tab(username, password) VALUES (?, ?)', (username, password))
        return jsonify({'message': 'New user added successfully'}), 200
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400

@app.route('/pull', methods=['POST'])
def pull():
    serve = request.get_json()
    print(f"[FLASK] /pull → {serve}")
    name = serve.get('username')
    pas = serve.get('password')
    with sqlite3.connect(DB) as data:
        cursor = data.cursor()
        cursor.execute('SELECT username, password FROM tab WHERE username=? AND password=?', (name, pas))
        user = cursor.fetchone()
    if user:
        return jsonify({'username': name, 'password': pas}), 200
    return jsonify({'error': 'Invalid credentials'}), 400

if __name__ == '__main__':
    init_db()
    print("Server starting on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)