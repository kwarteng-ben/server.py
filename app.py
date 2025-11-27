from flask import Flask, request, jsonify
from threading import Lock

app = Flask(__name__)

# === In-memory storage ===
users = {}         # {"username": "password"}
messages = []      # list of {"id": 1, "sender": "user1", "receiver": "user2", "message": "Hello"}
msg_id_counter = 1
lock = Lock()

@app.route("/")
def home():
    return "Server is running! Use /send, /resp, /push, /pull, /delete endpoints."

# === Sign up ===
@app.route("/push", methods=["POST"])
def push():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    with lock:
        if username in users:
            return jsonify({"error": "Username already exists"}), 400
        users[username] = password
    return jsonify({"status": "Account created"})

# === Login ===
@app.route("/pull", methods=["POST"])
def pull():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    stored_password = users.get(username)
    if stored_password and stored_password == password:
        return jsonify({"username": username, "password": stored_password})
    return jsonify({"error": "Invalid username or password"}), 400

# === Send message ===
@app.route("/send", methods=["POST"])
def send():
    global msg_id_counter
    data = request.get_json()
    sender = data.get("sender")
    receiver = data.get("receiver")
    message = data.get("message")
    if not sender or not receiver or not message:
        return jsonify({"error": "Missing fields"}), 400
    with lock:
        messages.append({"id": msg_id_counter, "sender": sender, "receiver": receiver, "message": message})
        msg_id_counter += 1
    return jsonify({"status": "Message sent"})

# === Retrieve messages ===
@app.route("/resp", methods=["POST"])
def resp():
    data = request.get_json()
    sender = data.get("sender")
    receiver = data.get("receiver")
    if not sender or not receiver:
        return jsonify({"error": "Missing fields"}), 400
    relevant = [m for m in messages if (m["sender"] == sender and m["receiver"] == receiver) or
                                     (m["sender"] == receiver and m["receiver"] == sender)]
    return jsonify(relevant)

# === Delete message ===
@app.route("/delete", methods=["POST"])
def delete():
    data = request.get_json()
    mes_id = data.get("id")
    username = data.get("username")
    if mes_id is None or username is None:
        return jsonify({"error": "Missing id or username"}), 400
    with lock:
        global messages
        messages = [m for m in messages if m["id"] != mes_id]
    return jsonify({"status": "Deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)