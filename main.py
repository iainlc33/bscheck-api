from flask import Flask, request, jsonify
import yt_dlp  # Updated to use yt-dlp
import ffmpeg

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the TikTok audio extractor!"

@app.route('/extract', methods=['POST'])
def extract_audio():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    url = data['url']

    try:
        # Set up options for yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,  # Set to False for verbose logging
            'verbose': True  # Detailed logs for debugging
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)

        # Return the extracted information
        if 'url' in result:
            return jsonify({'audio_url': result['url']}), 200
        else:
            return jsonify({'error': 'Failed to extract audio'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
