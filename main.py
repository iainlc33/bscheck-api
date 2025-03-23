import yt_dlp as youtube_dl
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def extract_audio_from_video(url):
    # Set up yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Explicitly use FFmpegExtractAudio to ensure no issues with FFmpegAudioPP
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'extractaudio': True,
        'audioquality': 1,  # Highest audio quality
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Save the file to a specific directory
    }

    # Force an update of yt-dlp to the latest version
    try:
        ydl_opts['postprocessors'][0]['key'] = 'FFmpegExtractAudio'
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            # Extract the audio from the video URL
            info_dict = ydl.extract_info(url, download=True)
            audio_file_path = f"downloads/{info_dict['id']}.mp3"
            return audio_file_path
    except Exception as e:
        return str(e)

@app.route('/extract', methods=['POST'])
def extract_audio():
    try:
        data = request.json
        video_url = data.get('url')
        audio_file_path = extract_audio_from_video(video_url)
        
        # Send a response with the audio file path or URL
        return jsonify({'audio_file_path': audio_file_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)
