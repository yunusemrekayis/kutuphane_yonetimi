"""Kitap CRUD işlemleri ve sayfalama için birim testleri."""

import unittest
from app import app, veritabani_baglantisi_al, veritabani_olustur


class TestKitapCrud(unittest.TestCase):
    """Kitap CRUD işlemlerini ve doğrulama kurallarını test eder."""

    def setUp(self):
        """Her testten önce veritabanını hazırlar ve test istemcisi kurar."""
        self.istemci = app.test_client()
        veritabani_olustur()

    def test_kitap_ekle_sayfasi_gorunumu(self):
        """Kitap ekleme formunun başarılı şekilde açıldığını kontrol eder."""
        yanit = self.istemci.get("/kitap-ekle")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Yeni Kitap Ekle", metin)
        self.assertIn("Kitap Adı", metin)

    def test_kitap_ekle_bos_alan_dogrulamasi(self):
        """Kitap adı veya yazar boş girildiğinde hata vermesini denetler."""
        yanit = self.istemci.post(
            "/kitap-ekle",
            data={
                "ad": "",
                "yazar": "Test Yazar",
                "yil": "2020",
                "kategori": "Tarih",
                "kopya_sayisi": "1",
            },
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Kitap adı zorunludur", metin)

    def test_kitap_ekle_gecersiz_yil_dogrulamasi(self):
        """Yıl 4 haneli olmadığında formun hata vermesini denetler."""
        yanit = self.istemci.post(
            "/kitap-ekle",
            data={
                "ad": "Deneme Kitabı",
                "yazar": "Yazar",
                "yil": "99",
                "kategori": "Genel",
                "kopya_sayisi": "1",
            },
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Basım yılı 4 haneli bir sayı olmalıdır", metin)

    def test_kitap_ekle_ve_detay_goster(self):
        """Yeni bir kitap ekler ve detay sayfasından kontrol eder."""
        yanit = self.istemci.post(
            "/kitap-ekle",
            data={
                "ad": "Ahilik Teşkilatı ve Meslek Ahlakı",
                "yazar": "Ahmet Hamdi",
                "yil": "2018",
                "kategori": "Tarih",
                "kopya_sayisi": "5",
            },
            follow_redirects=True,
        )
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Ahilik Teşkilatı", metin)

        # Eklenen kitabın id'sini bulalım
        baglanti = None
        kitap_id = None
        try:
            baglanti = veritabani_baglantisi_al()
            imlec = baglanti.cursor()
            imlec.execute(
                "SELECT id FROM kitaplar WHERE ad = ?;",
                ("Ahilik Teşkilatı ve Meslek Ahlakı",),
            )
            satir = imlec.fetchone()
            kitap_id = satir["id"]
        finally:
            if baglanti:
                baglanti.close()

        detay_yaniti = self.istemci.get(f"/kitap/{kitap_id}")
        self.assertEqual(detay_yaniti.status_code, 200)
        detay_metni = detay_yaniti.data.decode("utf-8")
        self.assertIn("Ahilik Teşkilatı ve Meslek Ahlakı", detay_metni)
        self.assertIn("Ahmet Hamdi", detay_metni)
        self.assertIn("2018", detay_metni)

    def test_kitap_guncelle(self):
        """Kitap bilgilerini güncellemeyi test eder."""
        baglanti = None
        kitap_id = None
        try:
            baglanti = veritabani_baglantisi_al()
            imlec = baglanti.cursor()
            imlec.execute(
                """
                INSERT INTO kitaplar (ad, yazar, yil, kategori, kopya_sayisi)
                VALUES (?, ?, ?, ?, ?);
                """,
                ("Eski Ad", "Eski Yazar", 2000, "Roman", 1),
            )
            baglanti.commit()
            kitap_id = imlec.lastrowid
        finally:
            if baglanti:
                baglanti.close()

        # Güncelleme formu GET kontrolü
        form_yanit = self.istemci.get(f"/kitap-guncelle/{kitap_id}")
        self.assertEqual(form_yanit.status_code, 200)
        self.assertIn("Eski Ad", form_yanit.data.decode("utf-8"))

        # POST ile güncelleme
        guncel_yanit = self.istemci.post(
            f"/kitap-guncelle/{kitap_id}",
            data={
                "ad": "Yeni Kitap Adı",
                "yazar": "Yeni Yazar",
                "yil": "2022",
                "kategori": "Eğitim",
                "kopya_sayisi": "3",
            },
            follow_redirects=True,
        )
        self.assertEqual(guncel_yanit.status_code, 200)
        guncel_metin = guncel_yanit.data.decode("utf-8")
        self.assertIn("Yeni Kitap Adı", guncel_metin)

    def test_kitap_silme_onayi_ve_silme(self):
        """Kitap silme onay sayfasını ve silme işlemini test eder."""
        baglanti = None
        kitap_id = None
        try:
            baglanti = veritabani_baglantisi_al()
            imlec = baglanti.cursor()
            imlec.execute(
                """
                INSERT INTO kitaplar (ad, yazar, yil, kategori, kopya_sayisi)
                VALUES (?, ?, ?, ?, ?);
                """,
                ("Silinecek Kitap", "Sil Yazar", 2010, "Deneme", 1),
            )
            baglanti.commit()
            kitap_id = imlec.lastrowid
        finally:
            if baglanti:
                baglanti.close()

        # Onay sayfası GET
        onay_yaniti = self.istemci.get(f"/kitap-sil/{kitap_id}")
        self.assertEqual(onay_yaniti.status_code, 200)
        self.assertIn("Silinecek Kitap", onay_yaniti.data.decode("utf-8"))

        # Silme işlemi POST
        sil_yaniti = self.istemci.post(
            f"/kitap-sil/{kitap_id}",
            follow_redirects=True,
        )
        self.assertEqual(sil_yaniti.status_code, 200)

        # Tekrar detay sayfası 404 dönmeli
        kontrol_yaniti = self.istemci.get(f"/kitap/{kitap_id}")
        self.assertEqual(kontrol_yaniti.status_code, 404)

    def test_sayfalama_ve_navigasyon(self):
        """Kitap listesi sayfalama yapısını test eder."""
        yanit = self.istemci.get("/kitaplar?sayfa=1")
        self.assertEqual(yanit.status_code, 200)
        metin = yanit.data.decode("utf-8")
        self.assertIn("Kitap Koleksiyonu", metin)
        self.assertIn("Sayfa 1", metin)


if __name__ == "__main__":
    unittest.main()
