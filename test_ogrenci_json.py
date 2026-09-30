"""Öğrenci JSON ve ortalama hesaplama işlemleri için test senaryoları.
"""

import os
from ogrenci_json import (
    ogrenci_kaydet,
    ogrencileri_oku,
    ortalama_hesapla,
)


def senaryo_normal_akis():
    """İki öğrencili geçerli verinin kaydedilip okunmasını test eder."""
    print("[Senaryo 1: Normal Akış - Kaydetme ve Okuma]")
    test_dosyasi = "test_ogrenciler.json"
    ogrenciler = [
        {"ad": "Ömer", "soyad": "Demir", "notlar": [80, 85, 90]},
        {"ad": "Zeynep", "soyad": "Çelik", "notlar": [100, 95, 90]},
    ]

    try:
        ogrenci_kaydet(test_dosyasi, ogrenciler)
        print("  - Dosyaya yazma işlemi başarılı.")

        okunanlar = ogrencileri_oku(test_dosyasi)
        print(f"  - Dosyadan {len(okunanlar)} öğrenci okundu.")

        for ogr in okunanlar:
            ort = ortalama_hesapla(ogr["notlar"])
            print(f"  * {ogr['ad']} {ogr['soyad']}: Ortalama = {ort:.2f}")

    finally:
        if os.path.exists(test_dosyasi):
            os.remove(test_dosyasi)
            print("  - Geçici test dosyası temizlendi.\n")


def senaryo_bos_not_listesi():
    """Not listesi boş olan öğrenci durumunu test eder."""
    print("[Senaryo 2: Boş Not Listesi]")
    notlar = []
    ort = ortalama_hesapla(notlar)
    print(f"  - Notlar: {notlar}")
    print(f"  - Hesaplanan Ortalama: {ort:.2f}\n")


def senaryo_gecersiz_veri_kontrolu():
    """Hatalı not değerlerinde doğrulamanın çalıştığını test eder."""
    print("[Senaryo 3: Hatalı Veri Doğrulama]")

    # 1. 100'den büyük not girilmesi
    try:
        ortalama_hesapla([70, 105])
    except ValueError as hata:
        print(f"  - Aralık dışı not hatası yakalandı: {hata}")

    # 2. Sayısal olmayan değer girilmesi
    try:
        ortalama_hesapla([85, "geçersiz_not"])
    except ValueError as hata:
        print(f"  - Tür uyumsuzluğu hatası yakalandı: {hata}")

    # 3. Liste dışı parametre verilmesi
    try:
        ortalama_hesapla("90")
    except TypeError as hata:
        print(f"  - Tip hatası yakalandı: {hata}")


def main():
    """Tüm test senaryolarını sırayla çalıştırır."""
    print("=== ÖĞRENCİ JSON İŞLEMLERİ TEST BAŞLANGICI ===\n")
    senaryo_normal_akis()
    senaryo_bos_not_listesi()
    senaryo_gecersiz_veri_kontrolu()
    print("\n=== TÜM TESTLER TAMAMLANDI ===")


if __name__ == "__main__":
    main()
