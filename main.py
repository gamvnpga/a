from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import time

app = Flask(__name__)

# アップロード用フォルダと許可されるファイル形式
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

# ファイル形式チェック
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ホームページ (機能選択)
@app.route('/')
def home():
    return render_template('home.html')

# アップロードページ
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            return redirect(url_for('select_preset', filename=file.filename))
    return render_template('upload.html')

# プリセット選択ページ
@app.route('/select_preset/<filename>', methods=['GET', 'POST'])
def select_preset(filename):
    if request.method == 'POST':
        preset = request.form['preset']
        return redirect(url_for('customize', filename=filename, preset=preset))
    return render_template('select_preset.html', filename=filename)

# カスタム設定ページ
@app.route('/customize/<filename>/<preset>', methods=['GET', 'POST'])
def customize(filename, preset):
    if request.method == 'POST':
        eq_settings = request.form.get('eq', 'default')
        fade_in = request.form.get('fade_in', '0')
        fade_out = request.form.get('fade_out', '0')
        return redirect(url_for('process', filename=filename, preset=preset, eq=eq_settings, fade_in=fade_in, fade_out=fade_out))
    return render_template('customize.html', filename=filename, preset=preset)

# 処理ページ
@app.route('/process/<filename>/<preset>/<eq>/<fade_in>/<fade_out>', methods=['GET'])
def process(filename, preset, eq, fade_in, fade_out):
    time.sleep(5)  # 処理をシミュレーション
    processed_file = f"processed_{filename}"
    processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], processed_file)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f_in:
        with open(processed_filepath, 'wb') as f_out:
            f_out.write(f_in.read())
    return redirect(url_for('result', filename=processed_file))

# 結果表示・ダウンロードページ
@app.route('/result/<filename>', methods=['GET'])
def result(filename):
    return render_template('result.html', filename=filename)

# ファイルダウンロード
@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    filepath = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    return jsonify({"message": f"File available for download at {filepath}"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
