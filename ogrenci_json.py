"""Öğrenci bilgilerini JSON dosyasına kaydeden ve ortalama hesaplayan modül.
"""

import json


def ogrenci_kaydet(dosya_yolu, ogrenciler):
    """Öğrenci listesini JSON formatında belirtilen dosyaya kaydeder.

    Argümanlar:
        dosya_yolu (str): Kaydedilecek dosyanın yolu.
        ogrenciler (list): Öğrenci sözlüklerini içeren liste.
    """
    if not isinstance(ogrenciler, list):
        raise TypeError("Öğrenci verisi liste tipinde olmalıdır.")

    with open(dosya_yolu, "w", encoding="utf-8") as dosya:
        json.dump(ogrenciler, dosya, ensure_ascii=False, indent=2)


def ogrencileri_oku(dosya_yolu):
    """Belirtilen JSON dosyasından öğrenci verilerini okur.

    Argümanlar:
        dosya_yolu (str): Okunacak dosyanın yolu.

    Döndürür:
        list: Öğrenci bilgilerini içeren liste.
    """
    with open(dosya_yolu, "r", encoding="utf-8") as dosya:
        veri = json.load(dosya)

    if not isinstance(veri, list):
        raise ValueError("Dosyadaki veri öğrenci listesi biçiminde değil.")

    return veri


def ortalama_hesapla(notlar):
    """Verilen not listesinin aritmetik ortalamasını hesaplar.

    Argümanlar:
        notlar (list): Sayısal notlar listesi.

    Döndürür:
        float: Notların aritmetik ortalaması.
    """
    if not isinstance(notlar, list):
        raise TypeError("Notlar liste tipinde olmalıdır.")

    if not notlar:
        return 0.0

    toplam = 0
    for not_degeri in notlar:
        if not isinstance(not_degeri, (int, float)):
            raise ValueError("Notlar sayısal değer olmalıdır.")
        if not_degeri < 0 or not_degeri > 100:
            raise ValueError("Not 0 ile 100 arasında olmalıdır.")
        toplam += not_degeri

    return toplam / len(notlar)


def main():
    """Temel kullanım örneği."""
    ornek_ogrenciler = [
        {"ad": "Ahmet", "soyad": "Yılmaz", "notlar": [85, 90, 78]},
        {"ad": "Ayşe", "soyad": "Kaya", "notlar": [95, 88, 92]},
    ]
    dosya_adi = "ogrenciler.json"
    ogrenci_kaydet(dosya_adi, ornek_ogrenciler)
    okunan = ogrencileri_oku(dosya_adi)

    for ogr in okunan:
        ort = ortalama_hesapla(ogr["notlar"])
        print(f"{ogr['ad']} {ogr['soyad']} -> Ortalama: {ort:.2f}")


if __name__ == "__main__":
    main()
