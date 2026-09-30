"""Öğrenci notları ve lambda işlemleri için test senaryoları."""

import unittest


def notlari_guncelle(not_listesi: list[int]) -> list[int]:
    """Her notu 5 artırır, maksimum 100 ile sınırlar.

    Args:
        not_listesi: İncelenecek tam sayı not listesi.

    Returns:
        Güncellenmiş not listesi.
    """
    if not isinstance(not_listesi, list):
        raise TypeError("Notlar liste biçiminde olmalıdır.")
    for deger in not_listesi:
        if not isinstance(deger, int):
            raise TypeError("Not değerleri tam sayı olmalıdır.")
    return list(map(lambda not_degeri: min(100, not_degeri + 5), not_listesi))


def elli_alti_filtrele(not_listesi: list[int]) -> list[int]:
    """50 altındaki notları eler, 50 ve üzerini döndürür.

    Args:
        not_listesi: İncelenecek tam sayı not listesi.

    Returns:
        50 ve üzeri notların listesi.
    """
    if not isinstance(not_listesi, list):
        raise TypeError("Notlar liste biçiminde olmalıdır.")
    for deger in not_listesi:
        if not isinstance(deger, int):
            raise TypeError("Not değerleri tam sayı olmalıdır.")
    return list(filter(lambda not_degeri: not_degeri >= 50, not_listesi))


def puana_gore_sirala(ogrenci_listesi: list[dict]) -> list[dict]:
    """Öğrencileri puana göre yüksekten düşüğe sıralar.

    Args:
        ogrenci_listesi: Öğrenci sözlükleri listesi.

    Returns:
        Sıralanmış öğrenci listesi.
    """
    if not isinstance(ogrenci_listesi, list):
        raise TypeError("Öğrenci verisi liste biçiminde olmalıdır.")
    return sorted(
        ogrenci_listesi,
        key=lambda ogrenci: ogrenci["puan"],
        reverse=True,
    )


def en_yuksek_puanli_ogrenci(ogrenci_listesi: list[dict]) -> dict:
    """En yüksek puana sahip öğrenciyi bulur.

    Args:
        ogrenci_listesi: Öğrenci sözlükleri listesi.

    Returns:
        En yüksek puanlı öğrenci sözlüğü.
    """
    if not isinstance(ogrenci_listesi, list) or not ogrenci_listesi:
        raise ValueError("Öğrenci listesi boş olamaz.")
    return max(ogrenci_listesi, key=lambda ogrenci: ogrenci["puan"])


def en_uzun_isimli_ogrenci(ogrenci_listesi: list[dict]) -> dict:
    """İsmi en uzun olan öğrenciyi bulur.

    Args:
        ogrenci_listesi: Öğrenci sözlükleri listesi.

    Returns:
        İsmi en uzun olan öğrenci sözlüğü.
    """
    if not isinstance(ogrenci_listesi, list) or not ogrenci_listesi:
        raise ValueError("Öğrenci listesi boş olamaz.")
    return max(ogrenci_listesi, key=lambda ogrenci: len(ogrenci["ad"]))


class TestOgrenciIslemleri(unittest.TestCase):
    """Lambda işlemlerinin doğruluğunu test eden sınıf."""

    def setUp(self) -> None:
        """Her testten önce ortak test verilerini hazırlar."""
        self.notlar = [88, 95, 70, 98, 60, 45]
        self.ogrenciler = [
            {"ad": "Yusuf", "puan": 85},
            {"ad": "Ahmet", "puan": 92},
            {"ad": "Ömer", "puan": 60},
            {"ad": "Bilal", "puan": 98},
            {"ad": "Mustafa", "puan": 70},
        ]

    def test_notlari_guncelle(self) -> None:
        """Map + lambda ile 5 puan ekleme ve tavan 100 sınırını test eder."""
        beklenen = [93, 100, 75, 100, 65, 50]
        sonuc = notlari_guncelle(self.notlar)
        self.assertEqual(sonuc, beklenen)

    def test_elli_alti_filtrele(self) -> None:
        """Filter + lambda ile 50 altı notların elenmesini test eder."""
        beklenen = [88, 95, 70, 98, 60]
        sonuc = elli_alti_filtrele(self.notlar)
        self.assertEqual(sonuc, beklenen)

    def test_puana_gore_sirala(self) -> None:
        """Sorted + key=lambda ile büyükten küçüğe sıralamayı test eder."""
        sonuc = puana_gore_sirala(self.ogrenciler)
        self.assertEqual(sonuc[0]["ad"], "Bilal")
        self.assertEqual(sonuc[0]["puan"], 98)
        self.assertEqual(sonuc[-1]["ad"], "Ömer")
        self.assertEqual(sonuc[-1]["puan"], 60)

    def test_en_yuksek_puanli_ogrenci(self) -> None:
        """Max + key=lambda ile zirvedeki öğrencinin bulunmasını test eder."""
        sonuc = en_yuksek_puanli_ogrenci(self.ogrenciler)
        self.assertEqual(sonuc["ad"], "Bilal")
        self.assertEqual(sonuc["puan"], 98)

    def test_en_uzun_isimli_ogrenci(self) -> None:
        """Max + key=lambda ile en uzun isimli öğrenciyi test eder."""
        sonuc = en_uzun_isimli_ogrenci(self.ogrenciler)
        self.assertEqual(sonuc["ad"], "Mustafa")


if __name__ == "__main__":
    unittest.main(verbosity=2)
