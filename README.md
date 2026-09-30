# 📚 Okul Kütüphane Yönetim Sistemi

Bu proje, Python Flask ve SQLite kullanılarak geliştirilmiş modern ve modüler bir Kütüphane Yönetim Sistemi web uygulamasıdır.

## 🌟 Özellikler

- **Kullanıcı Yetkilendirme:** Üye ve Yönetici (Admin) rolleriyle güvenli giriş ve kayıt sistemi (SHA-256 şifreleme).
- **Kitap Yönetimi (CRUD):** Kitap ekleme, düzenleme, silme, arama ve filtreleme işlemleri.
- **Ödünç Takip Sistemi:** Kitap alma, teslim etme ve gecikme durumlarını izleme.
- **Dinamik Şablonlar:** Jinja2 ve Bootstrap arayüz tasarımı.
- **Canlı Dağıtım Uyumluluğu:** Gunicorn, Railway ve bulut platformlarına tam uyumlu yapılandırma.

---

## 🚀 Yerel Kurulum (Local)

1. **Depoyu Klonlayın:**
   `ash
   git clone https://github.com/yunusemrekayis/kutuphane_yonetimi.git
   cd kutuphane_yonetimi
   `

2. **Gerekli Paketleri Yükleyin:**
   `ash
   pip install -r requirements.txt
   `

3. **Uygulamayı Çalıştırın:**
   `ash
   python app.py
   `

4. Tarayıcınızda [http://127.0.0.1:5000](http://127.0.0.1:5000) adresine gidin.

---

## ☁️ Railway Üzerinde Canlıya Alma (Deploy)

1. [Railway.app](https://railway.app) adresinde GitHub hesabınızla oturum açın.
2. **New Project** butonuna tıklayın.
3. **Deploy from GitHub repo** seçeneğini seçin.
4. kutuphane_yonetimi deponuzu seçin.
5. Railway otomatik olarak untime.txt, equirements.txt ve Procfile dosyalarını algılayıp projeyi canlıya alacaktır.
6. **Settings -> Generate Domain** adımından uygulamanızın canlı bağlantısını (URL) alabilirsiniz.

---

## 🔑 Varsayılan Giriş Bilgileri

- **Yönetici E-posta:** admin@kutuphane.k12.tr
- **Yönetici Şifre:** admin123

---

## 📁 Proje Dosya Yapısı

- pp.py: Ana Flask web uygulaması ve rota yöneticisi.
- equirements.txt: Python paket bağımlılıkları.
- Procfile: Canlı sunucu başlatma komutu.
- untime.txt: Python sürüm tanımlayıcısı.
- 	emplates/: HTML şablon dosyaları.
- static/: CSS ve görsel statik dosyalar.
