from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify(status="ok", version=os.getenv("APP_VERSION", "dev"))


@app.get("/")
def hello():
    return jsonify(message="Hello from sample-app!")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
