"""Öğrenci listesi CSV yazma ve okuma işlemleri."""

import csv


def ogrenci_listesi_olustur(dosya_yolu: str) -> None:
    """Belirtilen CSV dosyasına 3 öğrencinin bilgilerini DictWriter ile yazar."""
    alan_adlari = ["ad", "soyad", "yaş", "sınıf"]

    ogrenciler = [
        {"ad": "Ahmet", "soyad": "Yılmaz", "yaş": "15", "sınıf": "9-A"},
        {"ad": "Ayşe", "soyad": "Kaya", "yaş": "16", "sınıf": "10-B"},
        {"ad": "Mehmet", "soyad": "Demir", "yaş": "15", "sınıf": "9-B"},
    ]

    with open(dosya_yolu, mode="w", newline="", encoding="utf-8") as dosya:
        yazici = csv.DictWriter(dosya, fieldnames=alan_adlari)
        yazici.writeheader()
        yazici.writerows(ogrenciler)


def ogrenci_listesi_oku(dosya_yolu: str) -> None:
    """Belirtilen CSV dosyasını DictReader ile okuyup sözlük olarak yazdırır."""
    try:
        with open(dosya_yolu, mode="r", encoding="utf-8") as dosya:
            okuyucu = csv.DictReader(dosya)
            for satir in okuyucu:
                print(dict(satir))
    except FileNotFoundError:
        print(f"Hata: '{dosya_yolu}' dosyası bulunamadı.")


def main() -> None:
    """Ana çalıştırma fonksiyonu."""
    hedef_dosya = "students.csv"
    ogrenci_listesi_olustur(hedef_dosya)
    ogrenci_listesi_oku(hedef_dosya)


if __name__ == "__main__":
    main()
