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
    video_id = None
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Request body gerekli'}), 400
            
        video_input = data.get('video_id') or data.get('url')
        language_code = data.get('language_code', 'en')
        
        if not video_input:
            return jsonify({'error': 'video_id veya url gerekli'}), 400
        
        video_id = extract_video_id(video_input)
        if not video_id:
            return jsonify({'error': 'Geçersiz YouTube URL veya video ID'}), 400
        
        print(f"Fetching transcript for video ID: {video_id}")
        
        # Transcript'i çek
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except Exception as list_error:
            print(f"Error listing transcripts: {str(list_error)}")
            return jsonify({'error': f'Transcript listelenemedi: {str(list_error)}'}), 400
        
        # İstenen dili bulmaya çalış
        transcript = None
        try:
            transcript = transcript_list.find_transcript([language_code])
            print(f"Found transcript in language: {language_code}")
        except Exception as find_error:
            print(f"Language {language_code} not found, trying any available...")
            # Mevcut ilk transcript'i al
            try:
                for t in transcript_list:
                    transcript = t
                    print(f"Using available transcript: {t.language}")
                    break
            except Exception as iter_error:
                print(f"Error iterating transcripts: {str(iter_error)}")
                return jsonify({'error': 'Bu video için hiçbir transcript bulunamadı'}), 404
        
        if not transcript:
            return jsonify({'error': 'Bu video için transcript bulunamadı'}), 404
        
        # Transcript verisini al
        try:
            transcript_data = transcript.fetch()
            print(f"Fetched {len(transcript_data)} transcript segments")
        except Exception as fetch_error:
            print(f"Error fetching transcript data: {str(fetch_error)}")
            return jsonify({'error': f'Transcript verisi alınamadı: {str(fetch_error)}'}), 500
        
        if not transcript_data:
            return jsonify({'error': 'Transcript verisi boş'}), 404
        
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
        
        print(f"Successfully processed transcript for {video_id}")
        return jsonify(result), 200
        
    except TranscriptsDisabled:
        error_msg = f'Bu video için altyazılar devre dışı (Video ID: {video_id})'
        print(f"TranscriptsDisabled: {error_msg}")
        return jsonify({'error': error_msg}), 400
    except NoTranscriptFound:
        error_msg = f'Bu video için transcript bulunamadı (Video ID: {video_id})'
        print(f"NoTranscriptFound: {error_msg}")
        return jsonify({'error': error_msg}), 404
    except Exception as e:
        error_msg = f'Beklenmeyen hata: {str(e)}'
        print(f"Exception: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

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

