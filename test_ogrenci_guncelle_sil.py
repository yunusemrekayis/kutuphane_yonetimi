# -*- coding: utf-8 -*-
"""ogrenci_guncelle_sil modulu icin birim testleri."""

import sqlite3
from ogrenci_guncelle_sil import ogrenci_guncelle, ogrenci_sil, ogrenci_bilgisi_getir


def test_veritabani_kur(db_yolu: str) -> None:
    baglanti = sqlite3.connect(db_yolu)
    imlec = baglanti.cursor()
    imlec.execute("DROP TABLE IF EXISTS ogrenciler;")
    imlec.execute("""
        CREATE TABLE ogrenciler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT NOT NULL,
            soyad TEXT NOT NULL,
            email TEXT,
            sinif TEXT DEFAULT 'Belirsiz'
        );
    """)
    ornekler = [
        ("Ali", "Yilmaz", "ali@okul.k12.tr", "9-A"),
        ("Zehra", "Kaya", "zehra@okul.k12.tr", "10-B"),
        ("Yusuf", "Demir", "yusuf@okul.k12.tr", "11-C"),
    ]
    imlec.executemany(
        "INSERT INTO ogrenciler (ad, soyad, email, sinif) VALUES (?, ?, ?, ?);",
        ornekler,
    )
    baglanti.commit()
    baglanti.close()


def main():
    test_db = "test_okul.db"
    test_veritabani_kur(test_db)

    print("--- TEST 1: Gecerli ogrenci guncelleme ---")
    sonuc = ogrenci_guncelle(test_db, 1, "9-B")
    assert sonuc is True
    bilgi = ogrenci_bilgisi_getir(test_db, 1)
    assert bilgi["sinif"] == "9-B"
    print("Test 1 basarili!")

    print("\n--- TEST 2: Olmayan ogrenci guncelleme (rowcount = 0) ---")
    sonuc = ogrenci_guncelle(test_db, 999, "12-A")
    assert sonuc is False
    print("Test 2 basarili!")

    print("\n--- TEST 3: Gecersiz girdi ile guncelleme ---")
    assert ogrenci_guncelle(test_db, -1, "10-A") is False
    assert ogrenci_guncelle(test_db, "abc", "10-A") is False
    assert ogrenci_guncelle(test_db, 1, "   ") is False
    print("Test 3 basarili!")

    print("\n--- TEST 4: Guvenli silme - kullanici onayi iptal ---")
    silindi = ogrenci_sil(test_db, 2, onay=False)
    assert silindi is False
    assert ogrenci_bilgisi_getir(test_db, 2) is not None
    print("Test 4 basarili!")

    print("\n--- TEST 5: Guvenli silme - onay verildi ve basariyla silindi ---")
    silindi = ogrenci_sil(test_db, 2, onay=True)
    assert silindi is True
    assert ogrenci_bilgisi_getir(test_db, 2) is None
    print("Test 5 basarili!")

    print("\n--- TEST 6: Olmayan ogrenciyi silmeye calisma ---")
    silindi = ogrenci_sil(test_db, 999, onay=True)
    assert silindi is False
    print("Test 6 basarili!")

    print("\nTum testler basariyla tamamlandi!")


if __name__ == "__main__":
    main()
