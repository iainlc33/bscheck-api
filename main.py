from flask import Flask, jsonify, request
import subprocess
import yt_dlp as youtube_dl
import os

app = Flask(__name__)

# Path to store the downloaded audio files
DOWNLOAD_PATH = "/tmp/"

@app.route('/test_ffmpeg', methods=['GET'])
def test_ffmpeg():
    try:
        # Check if ffmpeg is installed
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"message": "FFmpeg is installed", "output": result.stdout}), 200
        else:
            return jsonify({"error": "FFmpeg is not properly installed", "output": result.stderr}), 500
    except Exception as e:
        return jsonify({"error": f"Error checking FFmpeg: {str(e)}"}), 500

@app.route('/extract', methods=['POST'])
def extract_audio():
    # Get the video URL from the request body
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    # Options for yt-dlp to download the audio only
    ydl_opts = {
        'format': 'bestaudio/best',  # Get the best audio format
        'extractaudio': True,  # Extract audio only
        'audioquality': 1,  # Best quality
        'outtmpl': os.path.join(DOWNLOAD_PATH, '%(id)s.%(ext)s'),  # Path to save the file
        'quiet': True,  # Don't show download progress
    }

    try:
        # Download the video (but only the audio) using yt-dlp
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            audio_file_path = os.path.join(DOWNLOAD_PATH, f"{info_dict['id']}.mp3")

            if os.path.exists(audio_file_path):
                return jsonify({'message': 'Audio extracted successfully', 'file_path': audio_file_path}), 200
            else:
                return jsonify({'error': 'Audio extraction failed'}), 500
    except Exception as e:
        return jsonify({'error': f'Error extracting audio: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
