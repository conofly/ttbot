from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive", 200

def keep_alive():
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
