from flask import Blueprint, request, jsonify
from src.Controllers.voice_controllers import process_audio

voice_bp = Blueprint("voice", __name__)

@voice_bp.route("/upload", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file found"}), 400

    audio_file = request.files["audio"]
    result = process_audio(audio_file)
    return jsonify(result)
