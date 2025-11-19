from flask import Flask, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from flask_cors import CORS
import re
import os

app = Flask(__name__)
CORS(app)

# Initialize YouTube Transcript API (new API)
ytt_api = YouTubeTranscriptApi()

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
        
        # YENİ API: Transcript'i direkt çek (daha basit!)
        try:
            # fetch() metodu direkt FetchedTranscript objesi döndürür
            fetched_transcript = ytt_api.fetch(video_id, languages=[language_code])
            print(f"Successfully fetched transcript in language: {language_code}")
        except Exception as fetch_error:
            print(f"Failed to fetch in {language_code}, trying English...")
            try:
                # Fallback to English
                fetched_transcript = ytt_api.fetch(video_id, languages=['en'])
                print(f"Successfully fetched English transcript")
            except Exception as en_error:
                print(f"Failed to fetch English transcript, trying any available...")
                try:
                    # Try any available language
                    fetched_transcript = ytt_api.fetch(video_id)
                    print(f"Successfully fetched transcript in default language")
                except Exception as any_error:
                    print(f"No transcript available: {str(any_error)}")
                    return jsonify({'error': f'Bu video için transcript bulunamadı: {str(any_error)}'}), 404
        
        # FetchedTranscript objesi direkt kullanılabilir
        # to_raw_data() ile list[dict] formatına çevirebiliriz
        transcript_data = fetched_transcript.to_raw_data()
        
        if not transcript_data:
            return jsonify({'error': 'Transcript verisi boş'}), 404
        
        print(f"Fetched {len(transcript_data)} transcript segments")
        
        # Yanıtı formatla
        result = {
            'video_id': fetched_transcript.video_id,
            'language': fetched_transcript.language,
            'language_code': fetched_transcript.language_code,
            'is_generated': fetched_transcript.is_generated,
            'is_translatable': False,  # FetchedTranscript'te bu property yok
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
        
        # YENİ API: list() metodu kullan
        transcript_list = ytt_api.list(video_id)
        
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
        print(f"Error listing languages: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

