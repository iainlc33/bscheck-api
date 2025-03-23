import os
import yt_dlp as youtube_dl
import ffmpeg
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to extract audio
def extract_audio(url):
    try:
        # Set up youtube-dl options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'verbose': True,
            'compat_opts': set(),
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate'
            }
        }

        # Use yt-dlp to download audio
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)

        # Check if there is any audio extracted
        if result:
            print(f"Audio extraction successful: {result}")
            return f"Audio extracted and saved successfully!"
        else:
            print(f"No audio found for URL: {url}")
            return "Error extracting audio."

    except Exception as e:
        print(f"Error during extraction: {e}")
        return f"Error: {e}"

# API route to handle the audio extraction request
@app.route('/extract', methods=['POST'])
def extract():
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400

    url = data['url']
    print(f"Extracting audio for URL: {url}")
    
    # Call the function to extract audio
    result = extract_audio(url)
    
    return jsonify({"message": result})

# Check if FFmpeg is installed and accessible
@app.route('/check_ffmpeg', methods=['GET'])
def check_ffmpeg():
    try:
        ffmpeg_version = ffmpeg.probe("version")
        return jsonify({"message": "FFmpeg is installed", "output": ffmpeg_version})
    except ffmpeg.Error as e:
        return jsonify({"message": "FFmpeg is not installed", "output": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
