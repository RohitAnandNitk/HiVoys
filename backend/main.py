from flask import Flask
from flask_cors import CORS
from src.Routes.voice_routes import voice_bp

app = Flask(__name__)
CORS(app)

# Register routes
app.register_blueprint(voice_bp, url_prefix="/api/voice")

@app.route("/")
def home():
    return {"message": "HiVoys backend is running!"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
