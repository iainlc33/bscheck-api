import yt_dlp
import flask
from flask import request, jsonify

app = flask.Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the BSCheck API!"

@app.route('/extract', methods=['POST'])
def extract_audio():
    data = request.get_json()

    # Check if the URL is in the incoming request
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    url = data['url']

    options = {
        'format': 'bestaudio/best',  # Fetch the best audio format
        'quiet': True,  # Suppress unnecessary output
        'verbose': True,  # Show verbose output for debugging
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.50 Safari/537.36'
        }
    }

    ydl = yt_dlp.YoutubeDL(options)

    try:
        info = ydl.extract_info(url, download=False)
        audio_url = info['formats'][0]['url']  # Extracting the direct audio URL
        return jsonify({'audio_url': audio_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
