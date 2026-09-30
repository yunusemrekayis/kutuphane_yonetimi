"""Kütüphane uygulaması sağlık kontrolü (healthcheck) test modülü."""

import unittest
from app import app, veritabani_baglantisi_al, veritabani_olustur


class TestKutuphaneSaglik(unittest.TestCase):
    """Web uygulamasının temel sayfalarını ve yanıtlarını test eder."""

    def setUp(self):
        """Test istemcisini ve veritabanını hazırlar."""
        self.istemci = app.test_client()
        veritabani_olustur()
        # Test kullanıcısını temizle
        baglanti = None
        try:
            baglanti = veritabani_baglantisi_al()
            imlec = baglanti.cursor()
            imlec.execute(
                "DELETE FROM uyeler WHERE email = ?;",
                ("zeynep.kaya@okul.k12.tr",),
            )
            baglanti.commit()
        except Exception as hata:
            print(f"Test hazırlık hatası: {hata}")
        finally:
            if baglanti:
                baglanti.close()

    def test_ana_sayfa(self):
        """Ana sayfa erişimini ve içeriğini kontrol eder."""
        yanit = self.istemci.get("/")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Merkez Okul Kütüphanesi", metin)
        self.assertIn("Hafta içi 08:30 - 17:00", metin)

    def test_kitaplar_sayfasi(self):
        """Kitaplar sayfası erişimini ve tablo içeriğini kontrol eder."""
        yanit = self.istemci.get("/kitaplar")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Safahat", metin)
        self.assertIn("Mehmet Akif Ersoy", metin)
        self.assertIn("Kutadgu Bilig", metin)

    def test_ayarlar_sayfasi(self):
        """Ayarlar sayfası erişimini ve iletişim bilgilerini kontrol eder."""
        yanit = self.istemci.get("/ayarlar")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("kutuphane@okul.k12.tr", metin)
        self.assertIn("0312 123 45 67", metin)

    def test_kayit_sayfasi_gorunumu(self):
        """Kayıt sayfası formunun açıldığını kontrol eder."""
        yanit = self.istemci.get("/kayit")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Kütüphane Üye Kayıt Formu", metin)
        self.assertIn("Kaydol", metin)

    def test_kayit_bos_alan_dogrulamasi(self):
        """Boş isimle form gönderildiğinde uyarı verilmesini kontrol eder."""
        yanit = self.istemci.post(
            "/kayit",
            data={"isim": "", "email": "ornek@okul.k12.tr"},
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("İsim alanı zorunludur", metin)

    def test_kayit_gecersiz_eposta_dogrulamasi(self):
        """Hatalı e-posta gönderildiğinde uyarı verilmesini kontrol eder."""
        yanit = self.istemci.post(
            "/kayit",
            data={"isim": "Ali", "email": "gecersizeposta"},
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Geçersiz e-posta adresi", metin)

    def test_kayit_basarili_yonlendirme(self):
        """Doğru verilerle kayıt sonrası başarı yönlendirmesini denetler."""
        yanit = self.istemci.post(
            "/kayit",
            data={
                "isim": "Zeynep Kaya",
                "email": "zeynep.kaya@okul.k12.tr",
                "telefon": "0555 999 88 77",
            },
            follow_redirects=False,
        )
        self.assertEqual(yanit.status_code, 302)
        self.assertIn("/basari", yanit.headers["Location"])

    def test_basari_sayfasi(self):
        """Başarı sayfasının içeriğini kontrol eder."""
        yanit = self.istemci.get("/basari")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Tebrikler, kaydoldunuz!", metin)

    def test_uyeler_sayfasi(self):
        """Üye listesi sayfasının erişilebilirliğini kontrol eder."""
        yanit = self.istemci.get("/uyeler")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Kayıtlı Kütüphane Üyeleri", metin)

    def test_uye_guncelleme_sayfasi(self):
        """Üye güncelleme sayfasının açıldığını kontrol eder."""
        baglanti = None
        uye_id = 1
        try:
            baglanti = veritabani_baglantisi_al()
            imlec = baglanti.cursor()
            imlec.execute(
                """
                INSERT OR IGNORE INTO uyeler (id, isim, email, telefon)
                VALUES (1, 'Örnek', 'ornek@okul.k12.tr', '05551112233');
                """
            )
            baglanti.commit()
            imlec.execute("SELECT id FROM uyeler LIMIT 1;")
            satir = imlec.fetchone()
            if satir:
                uye_id = satir["id"]
        finally:
            if baglanti:
                baglanti.close()

        yanit = self.istemci.get(f"/guncelle/{uye_id}")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Üye Bilgilerini Güncelle", metin)

    def test_statik_stil(self):
        """CSS dosyasının erişilebilirliğini kontrol eder."""
        yanit = self.istemci.get("/static/stil.css")
        self.assertEqual(yanit.status_code, 200)


if __name__ == "__main__":
    unittest.main()

