from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"
socketio = SocketIO(app, cors_allowed_origins="*")

waiting_users = []

@app.route("/")
def index():
    return render_template_string(open("index.html").read())

@socketio.on("find")
def find_partner(data):
    global waiting_users
    sid = request.sid
    age = data["age"]
    gender = data["gender"]

    for user in waiting_users:
        if user["gender"] == gender and abs(user["age"] - age) <= 5:
            emit("matched", room=sid)
            emit("matched", room=user["sid"])
            waiting_users.remove(user)
            return

    waiting_users.append({"sid": sid, "age": age, "gender": gender})

@socketio.on("signal")
def signal(data):
    emit("signal", data, broadcast=True)

if name == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    
