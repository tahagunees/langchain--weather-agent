# 🔆 Hava Durumu Kıyafet Öneri Ajanı

Yapay Zeka destekli hava durumu kıyafet öneri ajani, günlük kıyafet seçimi için hava durumuna dayalı öneriler sunar.

![Demo GIF](assets/demo.gif)

## 🚀 Özellikler

- **Gerçek Zamanlı Hava Durumu**: WeatherAPI.com API kullanarak güncel hava durumu bilgilerini alır
- **AI Asistanlık**: Google Gemini API ile akıllı kıyafet önerileri
- **Modern Arayüz**: Kullanıcı dostu, responsive web arayüzü
- **LangChain Entegrasyonu**: Özelleştirilmiş ajan yapısı

## 🛠️ Teknolojiler

- Python, Flask
- LangChain
- Google Gemini API
- WeatherAPI.com
- JavaScript, HTML5, CSS3
- Font Awesome

## 📋 Gereksinimler

- Python 3.8+
- API anahtarları:
  - Google Gemini API
  - WeatherAPI.com

## 🔧 Kurulum

1. Repoyu klonlayın:
```
git clone https://github.com/KULLANICI_ADI/WeatherAgent.git
cd WeatherAgent
```

2. Gereksinimleri yükleyin:
```
pip install -r requirements.txt
```

3. `.env` dosyası oluşturun ve API anahtarlarınızı ekleyin:
```
GOOGLE_API_KEY=your_google_api_key_here
WEATHERAPI_KEY=your_weatherapi_key_here
```

## 🚀 Kullanım

1. Uygulamayı çalıştırın:
```
python app.py
```

2. Tarayıcınızda `http://127.0.0.1:5000/` adresine gidin

3. Şehir adı (örn. "Istanbul") girin ve kıyafet önerilerini alın

## 📸 Ekran Görüntüleri

### Ana Sayfa
![Ana Sayfa](assets/home.png)

### Sonuçlar
![Sonuçlar](assets/results.png)

## 🤝 Katkıda Bulunma

Pull request'lerinizi bekliyoruz! Büyük değişiklikler için, lütfen önce bir konu açın.

## 📝 Lisans

[MIT](LICENSE)

## 👏 Teşekkürler

- LangChain ekibine
- Google Gemini API ekibine
- WeatherAPI.com ekibine 