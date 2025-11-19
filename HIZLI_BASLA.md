# 🚀 HIZLI BAŞLANGIÇ - 5 ADIMDA DEPLOY

## 📋 Ön Gereksinimler

- Git kurulu olmalı
- GitHub hesabı
- Terminal/Command Prompt

## 🎯 5 Adım Deploy

### 1️⃣ Terminal'i Açın

Bu klasörde terminal açın:
```bash
cd youtube-transcript-backend
```

### 2️⃣ Git Başlatın

```bash
git init
git add .
git commit -m "Initial commit: YouTube Transcript API"
```

### 3️⃣ GitHub'a Yükleyin

1. **GitHub'da yeni repo oluşturun:** https://github.com/new
   - Repository name: `youtube-transcript-backend`
   - Private veya Public seçin
   - README eklemeyin!

2. **Terminal'de çalıştırın** (YOUR_USERNAME yerine kendi kullanıcı adınızı yazın):

```bash
git remote add origin https://github.com/YOUR_USERNAME/youtube-transcript-backend.git
git branch -M main
git push -u origin main
```

### 4️⃣ Railway.app'te Deploy Edin

1. **https://railway.app/** adresine gidin
2. **"Login with GitHub"** ile giriş yapın
3. **"New Project"** → **"Deploy from GitHub repo"** seçin
4. **youtube-transcript-backend** repository'nizi seçin
5. **Bekleyin** → Otomatik deploy olacak! ⏳ (2-3 dakika)

### 5️⃣ Public URL Alın

1. Deploy edilen projeye tıklayın
2. **"Settings"** → **"Networking"** → **"Generate Domain"** butonuna tıklayın
3. URL'nizi kopyalayın: `https://your-app.up.railway.app`

## ✅ Test Edin

Tarayıcıda açın:
```
https://your-app.up.railway.app/
```

JSON yanıt görmelisiniz! 🎉

## 📱 Android App'te Kullanın

Backend URL'nizi Android app'inizde kullanın:

```kotlin
private const val YOUTUBE_TRANSCRIPT_BASE_URL = "https://your-app.up.railway.app/"
```

---

## 🐛 Sorun mu Var?

### Build başarısız oldu?
- Railway logs'u kontrol edin
- Tüm dosyaların olduğundan emin olun (app.py, requirements.txt, Procfile, runtime.txt)

### URL çalışmıyor?
- Domain generate ettiniz mi?
- Birkaç dakika bekleyin (ilk deploy biraz uzun sürebilir)

### GitHub push hatası?
- Git kurulu mu: `git --version`
- Remote doğru eklendi mi: `git remote -v`
- GitHub şifreniz/token'ınız doğru mu?

---

## 💡 İPUÇLARI

✅ **Ücretsiz**: Railway $5/ay kredi verir (500 saat çalışma)
✅ **Otomatik Deploy**: Git push → Otomatik deploy!
✅ **Logs**: Railway dashboard'da real-time logs görebilirsiniz
✅ **Monitoring**: CPU, memory, request sayısı izlenebilir

---

## 🎉 Tamamlandı!

Backend'iniz hazır! Artık Android app'inizden YouTube transcript'lerini çekebilirsiniz.

**Sonraki adım:** Android app'te API entegrasyonunu yapın!

