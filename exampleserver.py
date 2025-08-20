from flask import Flask
from siderequest import siderequest
import json
import os
app = Flask(__name__)
DATA_FILE = "money_data.json"
# internal helper to read/write persistent data
def load_db():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_db(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@app.route("/get_money.png")
@siderequest
def get_money(data):
    username = data.get("username", "")
    if not username:
        return {"error": "missing username"}
    db = load_db()
    money = db.get(username, 0)
    return {"username": username, "money": money}

@app.route("/set_money.png")
@siderequest
def set_money(data):
    username = data.get("username", "")
    if not username:
        return {"error": "missing username"}

    amount = int(data.get("amount", 0))

    db = load_db()
    db[username] = amount
    save_db(db)

    return {"username": username, "money": amount}

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)