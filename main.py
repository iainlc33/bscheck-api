from flask import Flask, request, jsonify
import yt_dlp
import os
import requests

app = Flask(__name__)

# Temporary directory to store files
TEMP_DIR = './temp'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def download_audio(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(TEMP_DIR, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegAudioConvertor',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_id = info_dict['id']
            file_path = os.path.join(TEMP_DIR, f'{video_id}.mp3')
            return file_path
    except Exception as e:
        return str(e)

def upload_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            response = requests.put(
                'https://transfer.sh/' + os.path.basename(file_path),
                files={'file': f}
            )
            return response.text
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    return "TikTok Audio Extractor API"

@app.route('/extract', methods=['POST'])
def extract_audio():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Download audio
        file_path = download_audio(url)
        if file_path.startswith('Error'):
            return jsonify({'error': file_path}), 500

        # Upload file to transfer.sh
        file_url = upload_file(file_path)
        if file_url.startswith('Error'):
            return jsonify({'error': file_url}), 500

        # Delete the temporary file after upload
        os.remove(file_path)

        return jsonify({'download_link': file_url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
