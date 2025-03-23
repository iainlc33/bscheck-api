import os
import yt_dlp
import requests
import traceback
from flask import Flask, jsonify, request

app = Flask(__name__)

# Temporary file storage directory
TEMP_DIR = '/tmp/'

# Function to download TikTok audio
def download_audio(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': os.path.join(TEMP_DIR, '%(id)s.%(ext)s'),  # Save file in temp directory
            'postprocessors': [{
                'key': 'FFmpegAudioConvertor',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_id = info_dict.get('id', '')
            file_name = f"{video_id}.mp3"
            file_path = os.path.join(TEMP_DIR, file_name)
            return file_path

    except Exception as e:
        return f"Error downloading audio: {str(e)}"


# Function to upload file to transfer.sh
def upload_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            response = requests.post("https://transfer.sh", files={'file': file})
            if response.status_code == 200:
                return response.text
            else:
                return f"Error uploading file: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Error uploading file: {str(e)}"


@app.route('/extract', methods=['POST'])
def extract_audio():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        print(f"Received URL: {url}")

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
        # Log the error with detailed traceback
        error_message = str(e)
        traceback_message = traceback.format_exc()
        print(f"Error: {error_message}")
        print(f"Traceback: {traceback_message}")
        return jsonify({'error': error_message}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
