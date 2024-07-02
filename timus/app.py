from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    if request.is_json:
        data = request.get_json()
        url = data.get('url', '')
    else:
        url = request.form.get('url', '')

    if not url:
        return jsonify({'error': 'URL parameter missing'}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info_dict)
            mp3_file = file_name.rsplit('.', 1)[0] + '.mp3'

            # Ambil judul dan thumbnail dari info_dict
            title = info_dict.get('title', '')
            thumbnail_url = info_dict.get('thumbnail', '')

    except Exception as e:
        return jsonify({'error': f'Error downloading audio: {str(e)}'}), 500

    return jsonify({
        'title': title,
        'thumbnailUrl': thumbnail_url,
        'audioUrl': f'/static/{os.path.basename(mp3_file)}',  # URL file MP3 yang diunduh
    })

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
