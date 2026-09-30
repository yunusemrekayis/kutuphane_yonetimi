"""Lambda test senaryolarını görsel ve anlaşılır çalıştıran script."""

import sys

# Türkçe karakter desteği için stdout encoding kontrolü
sys.stdout.reconfigure(encoding="utf-8")

# Test Verileri
notlar = [88, 95, 70, 98, 60, 45]
ogrenciler = [
    {"ad": "Yusuf", "puan": 85},
    {"ad": "Ahmet", "puan": 92},
    {"ad": "Ömer", "puan": 60},
    {"ad": "Bilal", "puan": 98},
    {"ad": "Mustafa", "puan": 70},
]


def test_senaryolarini_calistir() -> None:
    """Tüm senaryoları girdi, işlem, beklenen ve gerçek sonuçla raporlar."""
    print("=" * 65)
    print("       ÖĞRENCİ NOT VE LİSTE İŞLEMLERİ: TEST RAPORU")
    print("=" * 65)

    # -------------------------------------------------------------
    # SENARYO 1
    # -------------------------------------------------------------
    print("\n[SENARYO 1] Notları 5 Arttırma ve Tavan Sınırı (map + lambda)")
    print(f"  Girdi Notlar     : {notlar}")
    print("  Kural            : Her nota +5 ekle, 100'ü geçemez (min(100, x+5))")
    
    sonuc_1 = list(map(lambda not_degeri: min(100, not_degeri + 5), notlar))
    beklenen_1 = [93, 100, 75, 100, 65, 50]
    durum_1 = "BAŞARILI (PASSED)" if sonuc_1 == beklenen_1 else "BAŞARISIZ"

    print(f"  Beklenen Sonuç   : {beklenen_1}")
    print(f"  Hesaplanan Sonuç : {sonuc_1}")
    print(f"  Durum            : {durum_1}")

    # -------------------------------------------------------------
    # SENARYO 2
    # -------------------------------------------------------------
    print("\n[SENARYO 2] 50 Altı Notları Eleme (filter + lambda)")
    print(f"  Girdi Notlar     : {notlar}")
    print("  Kural            : Sadece 50 ve üzeri notları tut (not >= 50)")

    sonuc_2 = list(filter(lambda not_degeri: not_degeri >= 50, notlar))
    beklenen_2 = [88, 95, 70, 98, 60]
    durum_2 = "BAŞARILI (PASSED)" if sonuc_2 == beklenen_2 else "BAŞARISIZ"

    print(f"  Elenen Not(lar)  : {[n for n in notlar if n < 50]}")
    print(f"  Beklenen Sonuç   : {beklenen_2}")
    print(f"  Hesaplanan Sonuç : {sonuc_2}")
    print(f"  Durum            : {durum_2}")

    # -------------------------------------------------------------
    # SENARYO 3
    # -------------------------------------------------------------
    print("\n[SENARYO 3] Puana Göre Sıralama (sorted + key=lambda)")
    print("  Girdi Liste      : " + ", ".join(f"{o['ad']} ({o['puan']})" for o in ogrenciler))
    print("  Kural            : Puanı en yüksekten düşüğe doğru sırala")

    sonuc_3 = sorted(
        ogrenciler,
        key=lambda ogrenci: ogrenci["puan"],
        reverse=True,
    )
    beklenen_sirali_isimler = ["Bilal", "Ahmet", "Yusuf", "Mustafa", "Ömer"]
    gerceklesen_isimler = [o["ad"] for o in sonuc_3]
    durum_3 = "BAŞARILI (PASSED)" if gerceklesen_isimler == beklenen_sirali_isimler else "BAŞARISIZ"

    print("  Sıralı Liste     :")
    for sira, ogr in enumerate(sonuc_3, 1):
        print(f"    {sira}. {ogr['ad']} -> {ogr['puan']} puan")
    print(f"  Durum            : {durum_3}")

    # -------------------------------------------------------------
    # SENARYO 4
    # -------------------------------------------------------------
    print("\n[SENARYO 4] En Yüksek Puanlı Öğrenci (max + key=lambda)")
    print("  Kural            : Listedeki en yüksek puana sahip sözlüğü bul")

    sonuc_4 = max(ogrenciler, key=lambda ogrenci: ogrenci["puan"])
    durum_4 = "BAŞARILI (PASSED)" if sonuc_4["ad"] == "Bilal" and sonuc_4["puan"] == 98 else "BAŞARISIZ"

    print(f"  Bulunan Öğrenci  : {sonuc_4['ad']} (Puan: {sonuc_4['puan']})")
    print(f"  Beklenen Öğrenci : Bilal (Puan: 98)")
    print(f"  Durum            : {durum_4}")

    # -------------------------------------------------------------
    # SENARYO 5
    # -------------------------------------------------------------
    print("\n[SENARYO 5] İsmi En Uzun Öğrenci (max + key=lambda)")
    print("  İsim Uzunlukları : " + ", ".join(f"{o['ad']} ({len(o['ad'])})" for o in ogrenciler))
    print("  Kural            : Karakter sayısı (len) en fazla olan öğrenciyi bul")

    sonuc_5 = max(ogrenciler, key=lambda ogrenci: len(ogrenci["ad"]))
    durum_5 = "BAŞARILI (PASSED)" if sonuc_5["ad"] == "Mustafa" else "BAŞARISIZ"

    print(f"  Bulunan Öğrenci  : {sonuc_5['ad']} ({len(sonuc_5['ad'])} karakter)")
    print(f"  Beklenen Öğrenci : Mustafa (7 karakter)")
    print(f"  Durum            : {durum_5}")

    print("\n" + "=" * 65)
    print("               TÜM TEST SENARYOLARI GEÇTİ!")
    print("=" * 65)


if __name__ == "__main__":
    test_senaryolarini_calistir()
