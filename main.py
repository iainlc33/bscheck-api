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
        print(f"Downloading audio from: {url}")  # Log the URL being processed
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
            print(f"Audio downloaded to: {file_path}")  # Log the path
            return file_path

    except Exception as e:
        print(f"Error in download_audio: {str(e)}")  # Log the error
        return f"Error downloading audio: {str(e)}"


# Function to upload file to transfer.sh
def upload_file(file_path):
    try:
        print(f"Uploading file to transfer.sh: {file_path}")  # Log the file being uploaded
        with open(file_path, 'rb') as file:
            response = requests.post("https://transfer.sh", files={'file': file})
            if response.status_code == 200:
                print(f"File uploaded successfully: {response.text}")  # Log the success
                return response.text
            else:
                print(f"Error uploading file: {response.status_code} - {response.text}")  # Log error
                return f"Error uploading file: {response.status_code} - {response.text}"

    except Exception as e:
        print(f"Error in upload_file: {str(e)}")  # Log the error
        return f"Error uploading file: {str(e)}"


@app.route('/extract', methods=['POST'])
def extract_audio():
    try:
        print("Received request to extract audio.")  # Log the request receipt
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        print(f"Processing URL: {url}")  # Log the URL

        # Download audio
        file_path = download_audio(url)
        if file_path.startswith('Error'):
            print(f"Error downloading audio: {file_path}")  # Log the error message
            return jsonify({'error': file_path}), 500

        # Upload file to transfer.sh
        file_url = upload_file(file_path)
        if file_url.startswith('Error'):
            print(f"Error uploading file: {file_url}")  # Log the error message
            return jsonify({'error': file_url}), 500

        # Delete the temporary file after upload
        os.remove(file_path)

        print(f"Returning download link: {file_url}")  # Log the response
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
