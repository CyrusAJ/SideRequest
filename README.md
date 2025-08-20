# SideRequest – Client-side HTTP Requests for Pavlov VR Mods

SideRequest lets your Pavlov VR mod communicate clientside with an external Python server using JSON data. Behind the scenes the system uses `.png` image downloads as the backbone: the server encodes JSON into pixel data and the client decodes it back into json. The client sends data to the python server using the url params

## How it works

- Example request from the client:  
  http://example.com:5000/example_endpoint.png?d={"username":"Bob"}&s=16
- `d` is the json payload the client sends to the python server
- `s` is the **image resolution** of the response and determines the maximum response payload capacity: `s × s × 3` bytes (RGB).  
  For `s=16`, max capacity = `16 × 16 × 3 = 768` bytes.
- Endpoints must:  
  • end in `.png`  
  • be decorated with `@siderequest`
- Your Flask function **receives JSON** as a Python `dict` and must **return JSON** (also a `dict`). SideRequest handles all image packaging/unpackaging.

## Potential use cases

- Cloud-saved money, XP, and levels  
- Loadout/inventory syncing across sessions  
- Kills, deaths, and match-stat tracking

## Requirements

```bash
pip install flask pillow
```

## Minimal example endpoint

```python
from flask import Flask
from siderequest import siderequest

app = Flask(__name__)

@app.route("/hello.png")
@siderequest
def hello(data):
    username = data.get("username", "unknown")
    return {"message": f"Hello {username} from the server!"}

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
```

## Persistent money example

```python
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
```

## Pavlov setup

To use SideRequest in Pavlov VR, install the Source Mod:  
https://mod.io/g/pavlov/m/siderequest-clientside-http-requests
