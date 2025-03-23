from flask import Flask, request, jsonify
import youtube_dl
import os
import tempfile
import ffmpeg

app = Flask(__name__)

# Directory to save downloaded audio files
DOWNLOAD_PATH = tempfile.mkdtemp()

@app.route('/')
def home():
    return jsonify({'message': 'Server is running!'})

@app.route('/extract', methods=['POST'])
def extract_audio():
    # Get the URL from the request
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({'error': 'No URL provided'}), 400

    # Log the received URL
    print(f"Received URL: {video_url}")

    # Configure youtube-dl options for extracting audio
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioquality': 1,
        'outtmpl': os.path.join(DOWNLOAD_PATH, '%(id)s.%(ext)s'),
        'quiet': True,
    }

    try:
        # Download the audio using youtube-dl
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            audio_file_path = os.path.join(DOWNLOAD_PATH, f"{info_dict['id']}.mp3")

            # Check if the audio file is created successfully
            if os.path.exists(audio_file_path):
                return jsonify({'message': 'Audio extracted successfully', 'file_path': audio_file_path}), 200
            else:
                return jsonify({'error': 'Audio extraction failed'}), 500
    except Exception as e:
        # Return error if the extraction fails
        return jsonify({'error': f'Error extracting audio: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
