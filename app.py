import os
from flask import Flask, render_template, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from ai_module import analyze

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.secret_key = os.getenv('FLASK_SECRET', 'supersecretkey')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/api/predict', methods=['POST'])
def api_predict():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "File tidak ditemukan"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Nama file kosong"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        try:
            top_k = int(request.args.get("top_k", 1))
        except ValueError:
            top_k = 1        
        try:
            result = analyze(save_path, top_k=top_k)
        finally:
            # apapun hasilnya, hapus file upload setelah diproses
            if os.path.exists(save_path):
                os.remove(save_path)
        
        return jsonify({"status": "success", "result": result})
    else:
        return jsonify({"status": "error", "message": "Ekstensi file tidak valid"}), 400


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
