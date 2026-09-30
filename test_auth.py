"""Kütüphane Yönetim Sistemi Kimlik Doğrulama Birim Testleri."""

import sqlite3
import unittest
from app import (
    app,
    sifre_dogrula,
    sifre_ozetle,
    veritabani_baglantisi_al,
    veritabani_olustur,
)


class TestKimlikDogrulama(unittest.TestCase):
    """Kayıt, giriş, seans, şifre ve yetkilendirme testlerini yürütür."""

    def setUp(self):
        """Her testten önce veritabanını ve test istemcisini hazırlar."""
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test_gizli_anahtar"
        self.istemci = app.test_client()
        veritabani_olustur()

        # Test veritabanında temizlik yap
        baglanti = None
        try:
            baglanti = veritabani_baglantisi_al()
            imlec = baglanti.cursor()
            imlec.execute(
                "DELETE FROM uyeler WHERE email = ?;",
                ("yeni.ogrenci@okul.k12.tr",),
            )
            imlec.execute(
                "UPDATE uyeler SET sifre = ? WHERE id = 1 OR email = ?;",
                (sifre_ozetle("ogrenci123"), "ahmet.yilmaz@okul.k12.tr"),
            )
            baglanti.commit()
        finally:
            if baglanti:
                baglanti.close()

    def test_sifre_ozetleme_ve_dogrulama(self):
        """Şifrelerin SHA-256 ile özetlenmesini ve doğrulamasını test eder."""
        parola = "gizliSifre123"
        ozet = sifre_ozetle(parola)
        self.assertNotEqual(parola, ozet)
        self.assertTrue(sifre_dogrula(parola, ozet))
        self.assertFalse(sifre_dogrula("yanlisSifre", ozet))

    def test_kayit_sayfasi_gorunumu(self):
        """Kayıt sayfasının şifre alanlarıyla açıldığını kontrol eder."""
        yanit = self.istemci.get("/kayit")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Kütüphane Üye Kayıt Formu", metin)
        self.assertIn("sifre", metin)
        self.assertIn("sifre_tekrar", metin)

    def test_kayit_kisa_sifre_hatasi(self):
        """6 karakterden kısa şifre girildiğinde hata verilmesini denetler."""
        yanit = self.istemci.post(
            "/kayit",
            data={
                "isim": "Fatma Şen",
                "email": "fatma.sen@okul.k12.tr",
                "sifre": "12345",
                "sifre_tekrar": "12345",
            },
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Şifre en az 6 karakter olmalıdır", metin)

    def test_kayit_sifre_uyusmazlik_hatasi(self):
        """Şifre ve tekrarı eşleşmediğinde hata verilmesini denetler."""
        yanit = self.istemci.post(
            "/kayit",
            data={
                "isim": "Fatma Şen",
                "email": "fatma.sen@okul.k12.tr",
                "sifre": "sifre123",
                "sifre_tekrar": "farkliSifre123",
            },
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Girdiğiniz şifreler birbiriyle eşleşmiyor", metin)

    def test_kayit_mukerrer_eposta_hatasi(self):
        """Aynı e-posta ile ikinci kez kayıt olunamayacağını denetler."""
        yanit = self.istemci.post(
            "/kayit",
            data={
                "isim": "Ahmet Tekrar",
                "email": "ahmet.yilmaz@okul.k12.tr",
                "sifre": "ogrenci123",
                "sifre_tekrar": "ogrenci123",
            },
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Bu e-posta adresi ile kayıtlı başka bir üye", metin)

    def test_basarili_kayit(self):
        """Geçerli bilgilerle üye kaydının başarıyla yapılmasını denetler."""
        yanit = self.istemci.post(
            "/kayit",
            data={
                "isim": "Yeni Öğrenci",
                "email": "yeni.ogrenci@okul.k12.tr",
                "telefon": "0555 333 22 11",
                "sifre": "yeniSifre123",
                "sifre_tekrar": "yeniSifre123",
            },
            follow_redirects=False,
        )
        self.assertEqual(yanit.status_code, 302)

        # Veritabanında kontrol et
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()
        imlec.execute(
            "SELECT * FROM uyeler WHERE email = ?;",
            ("yeni.ogrenci@okul.k12.tr",),
        )
        uye = imlec.fetchone()
        baglanti.close()

        self.assertIsNotNone(uye)
        self.assertEqual(uye["isim"], "Yeni Öğrenci")
        self.assertTrue(sifre_dogrula("yeniSifre123", uye["sifre"]))

    def test_giris_sayfasi_gorunumu(self):
        """Giriş sayfasının erişilebilirliğini kontrol eder."""
        yanit = self.istemci.get("/giris")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Üye Girişi", metin)

    def test_giris_hatali_bilgiler(self):
        """Yanlış e-posta veya şifre ile girişte hata verilmesini test eder."""
        yanit = self.istemci.post(
            "/giris",
            data={
                "email": "ahmet.yilmaz@okul.k12.tr",
                "sifre": "yanlisSifre123",
            },
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("E-posta veya şifre hatalı", metin)

    def test_giris_basarili_ve_dashboard_yonlendirme(self):
        """Doğru bilgilerle girişte dashboard'a yönlendirildiğini test eder."""
        yanit = self.istemci.post(
            "/giris",
            data={
                "email": "ahmet.yilmaz@okul.k12.tr",
                "sifre": "ogrenci123",
            },
            follow_redirects=False,
        )
        self.assertEqual(yanit.status_code, 302)
        self.assertIn("/dashboard", yanit.headers["Location"])

    def test_giris_yapilmadan_dashboard_engeli(self):
        """Giriş yapılmadan dashboard'a erişilmek istendiğinde yönlendirir."""
        yanit = self.istemci.get("/dashboard", follow_redirects=False)
        self.assertEqual(yanit.status_code, 302)
        self.assertIn("/giris", yanit.headers["Location"])

    def test_dashboard_gorunumu_ve_aktif_oduncler(self):
        """Giriş yapıldığında dashboard ve aktif ödünçlerin listelenmesi."""
        with self.istemci.session_transaction() as seans:
            seans["kullanici_id"] = 1
            seans["kullanici_adi"] = "Ahmet Yılmaz"
            seans["rol"] = "uye"

        yanit = self.istemci.get("/dashboard")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Hoş Geldiniz", metin)
        self.assertIn("Profil Bilgilerim", metin)
        self.assertIn("Şifre Değiştir", metin)
        self.assertIn("Çıkış Yap", metin)

    def test_profil_goruntule_ve_guncelle(self):
        """Giriş yapan üyenin profil bilgilerini güncellemesini test eder."""
        with self.istemci.session_transaction() as seans:
            seans["kullanici_id"] = 1
            seans["kullanici_adi"] = "Ahmet Yılmaz"
            seans["rol"] = "uye"

        # Profil sayfasını aç
        yanit = self.istemci.get("/profil")
        self.assertEqual(yanit.status_code, 200)

        # Bilgileri güncelle
        yanit = self.istemci.post(
            "/profil",
            data={
                "isim": "Ahmet Guncel",
                "telefon": "0555 999 11 22",
            },
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Profil bilgileriniz başarıyla güncellendi", metin)

    def test_sifre_degistirme(self):
        """Mevcut şifre doğrulanarak yeni şifre atanmasını test eder."""
        with self.istemci.session_transaction() as seans:
            seans["kullanici_id"] = 1
            seans["kullanici_adi"] = "Ahmet Yılmaz"
            seans["rol"] = "uye"

        # Yanlış eski şifre denemesi
        yanit = self.istemci.post(
            "/sifre-degistir",
            data={
                "eski_sifre": "yanlisEskiSifre",
                "yeni_sifre": "yeniParola456",
                "yeni_sifre_tekrar": "yeniParola456",
            },
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Mevcut şifrenizi hatalı girdiniz", metin)

        # Doğru eski şifre ile değişim
        yanit = self.istemci.post(
            "/sifre-degistir",
            data={
                "eski_sifre": "ogrenci123",
                "yeni_sifre": "yeniParola456",
                "yeni_sifre_tekrar": "yeniParola456",
            },
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Şifreniz başarıyla değiştirildi", metin)

    def test_admin_sayfasi_yetkisiz_giris(self):
        """Normal üyenin admin sayfasına erişiminin 403 ile engellenmesi."""
        with self.istemci.session_transaction() as seans:
            seans["kullanici_id"] = 1
            seans["kullanici_adi"] = "Ahmet Yılmaz"
            seans["rol"] = "uye"

        yanit = self.istemci.get("/admin")
        self.assertEqual(yanit.status_code, 403)

    def test_admin_sayfasi_yetkili_giris(self):
        """Admin rolündeki kullanıcının üye listesini görmesini test eder."""
        with self.istemci.session_transaction() as seans:
            seans["kullanici_id"] = 999
            seans["kullanici_adi"] = "Kütüphane Yöneticisi"
            seans["rol"] = "admin"

        yanit = self.istemci.get("/admin")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Yönetici (Admin) Kontrol Paneli", metin)
        self.assertIn("Tüm Sistem Üyeleri", metin)

    def test_cikis_islemi(self):
        """Çıkışta oturumun silinmesini ve yönlendirmeyi test eder."""
        with self.istemci.session_transaction() as seans:
            seans["kullanici_id"] = 1

        yanit = self.istemci.get("/cikis", follow_redirects=False)
        self.assertEqual(yanit.status_code, 302)
        self.assertIn("/giris", yanit.headers["Location"])


if __name__ == "__main__":
    unittest.main()
