from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from flask_cors import CORS
import re
import os

app = Flask(__name__)
CORS(app)

def extract_video_id(url_or_id):
    """YouTube URL'den video ID çıkart veya ID'yi döndür"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return None

@app.route('/')
def home():
    return jsonify({
        'message': 'YouTube Transcript API Service',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'transcript': '/api/transcript (POST)',
            'languages': '/api/transcript/languages (POST)'
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'youtube-transcript-api'}), 200

@app.route('/api/transcript', methods=['POST'])
def get_transcript():
    try:
        data = request.json
        video_input = data.get('video_id') or data.get('url')
        language_code = data.get('language_code', 'en')
        
        if not video_input:
            return jsonify({'error': 'video_id veya url gerekli'}), 400
        
        video_id = extract_video_id(video_input)
        if not video_id:
            return jsonify({'error': 'Geçersiz YouTube URL veya video ID'}), 400
        
        # Transcript'i çek
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # İstenen dili bulmaya çalış
        try:
            transcript = transcript_list.find_transcript([language_code])
        except:
            # Mevcut ilk transcript'i al
            transcript = next(iter(transcript_list))
        
        # Transcript verisini al
        transcript_data = transcript.fetch()
        
        # Yanıtı formatla
        result = {
            'video_id': video_id,
            'language': transcript.language,
            'language_code': transcript.language_code,
            'is_generated': transcript.is_generated,
            'is_translatable': transcript.is_translatable,
            'full_text': ' '.join([item['text'] for item in transcript_data]),
            'snippets': [
                {
                    'text': item['text'],
                    'start': item['start'],
                    'duration': item['duration']
                }
                for item in transcript_data
            ],
            'total_duration': transcript_data[-1]['start'] + transcript_data[-1]['duration'] if transcript_data else 0
        }
        
        return jsonify(result), 200
        
    except TranscriptsDisabled:
        return jsonify({'error': 'Bu video için altyazılar devre dışı'}), 400
    except NoTranscriptFound:
        return jsonify({'error': 'Bu video için transcript bulunamadı'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/transcript/languages', methods=['POST'])
def get_available_languages():
    try:
        data = request.json
        video_input = data.get('video_id') or data.get('url')
        
        if not video_input:
            return jsonify({'error': 'video_id veya url gerekli'}), 400
        
        video_id = extract_video_id(video_input)
        if not video_id:
            return jsonify({'error': 'Geçersiz YouTube URL veya video ID'}), 400
        
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        languages = []
        for transcript in transcript_list:
            languages.append({
                'language': transcript.language,
                'language_code': transcript.language_code,
                'is_generated': transcript.is_generated,
                'is_translatable': transcript.is_translatable
            })
        
        return jsonify({
            'video_id': video_id,
            'languages': languages
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

