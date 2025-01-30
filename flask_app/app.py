import os
import uuid
import zipfile

from flask import Flask, jsonify, request

app = Flask(__name__)
UPLOAD_FOLDER = "/data/uploads"
API_KEY = os.getenv("UPLOAD_KEY")
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB limit

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def extract_zip(file_path, extract_to):
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


@app.route("/upload", methods=["POST"])
def upload_file():
    api_key = request.headers.get("API-Key")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    folder_id = str(uuid.uuid4())
    folder_path = os.path.join(app.config["UPLOAD_FOLDER"], folder_id)
    os.makedirs(folder_path)

    file_path = os.path.join(folder_path, file.filename)
    file.save(file_path)

    # Assuming the uploaded file is a zip file containing the directory structure
    extract_zip(file_path, folder_path)
    os.remove(file_path)

    return jsonify({"url": f"/uploads/{folder_id}/"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
