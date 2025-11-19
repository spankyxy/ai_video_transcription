# YouTube Transcript API Backend

Flask tabanlı YouTube transcript çekme API'si.

## Özellikler

- ✅ YouTube video transcript'lerini çeker
- ✅ Çoklu dil desteği
- ✅ Video URL veya ID ile çalışır
- ✅ CORS desteği
- ✅ Railway.app'te deploy edilmeye hazır

## Kurulum

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Lokal'de çalıştır
python app.py
```

## API Endpoints

### Health Check
```
GET /api/health
```

### Transcript Çek
```
POST /api/transcript
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "language_code": "en"
}
```

### Mevcut Dilleri Listele
```
POST /api/transcript/languages
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

## Deployment

### Railway.app

1. GitHub'a push yapın
2. Railway.app'te "Deploy from GitHub repo" seçin
3. Repository'nizi seçin
4. Otomatik deploy olur!

## Test

```bash
# Health check
curl http://localhost:5000/api/health

# Transcript çek
curl -X POST http://localhost:5000/api/transcript \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

## License

MIT

# ai_video_transcription
