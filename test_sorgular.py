# -*- coding: utf-8 -*-
"""SQL sorgu mekanizmalari ve donus tipleri test modulu."""

import sqlite3
from typing import Any, Dict, List, Optional


def test_veritabani_olustur() -> sqlite3.Connection:
    """Bellekte gecici bir veritabani olusturup ornek ogrenciler ekler.

    Returns:
        sqlite3.Connection: Bellek uzerindeki SQLite baglantisi.
    """
    baglanti = sqlite3.connect(":memory:")
    baglanti.row_factory = sqlite3.Row
    imlec = baglanti.cursor()

    imlec.execute(
        """
        CREATE TABLE ogrenciler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT NOT NULL,
            soyad TEXT NOT NULL,
            email TEXT,
            sinif TEXT
        );
        """
    )

    # Bos tablo testleri icin ayri bir bos tablo aciyoruz
    imlec.execute(
        """
        CREATE TABLE bos_tablo (
            id INTEGER PRIMARY KEY,
            ad TEXT
        );
        """
    )

    # Ornek ogrenciler (Bazilarinda email NULL birakildi)
    ogrenciler = [
        ("Ahmet", "Demir", "ahmet@okul.k12.tr", "10-A"),
        ("Ayse", "Celik", None, "10-A"),
        ("Mehmet", "Kaya", "mehmet@okul.k12.tr", "10-B"),
        ("Fatma", "Yildiz", None, "10-B"),
        ("Zeynep", "Aydin", "zeynep@okul.k12.tr", "10-B"),
    ]

    imlec.executemany(
        """
        INSERT INTO ogrenciler (ad, soyad, email, sinif)
        VALUES (?, ?, ?, ?);
        """,
        ogrenciler,
    )
    baglanti.commit()
    return baglanti


def test_1_bos_tablo_fetchall(baglanti: sqlite3.Connection) -> None:
    """Test 1: Bos tablo sorgusunda fetchall() sonucunu inceler.

    Args:
        baglanti: SQLite veritabani baglantisi.
    """
    print("\n--- Test 1: Bos Tablo Sorgusu ve fetchall() ---")
    imlec = baglanti.cursor()
    imlec.execute("SELECT * FROM bos_tablo")
    sonuc = imlec.fetchall()

    print(f"Dönen Deger: {sonuc}")
    print(f"Dönen Tip: {type(sonuc)}")
    print(f"None mi?: {sonuc is None}")
    print(f"Bos liste [] mi?: {sonuc == []}")

    # fetchone() bos tabloda None donerken, fetchall() bos liste [] doner
    assert sonuc == [], "fetchall bos tabloda bos liste dondurmelidir!"
    assert sonuc is not None, "fetchall bos tabloda None dondurmez!"
    print("Sonuc: fetchall() bos tabloda None degil, [] (bos liste) doner.")


def test_2_olmayan_sinif(baglanti: sqlite3.Connection) -> None:
    """Test 2: Olmayan bir sinif WHERE sorgusuyla arandiginda ne doner?

    Args:
        baglanti: SQLite veritabani baglantisi.
    """
    print("\n--- Test 2: Olmayan Sinif Sorgusu (WHERE sinif = ?) ---")
    arana_sinif = "12-C"
    imlec = baglanti.cursor()
    sorgu = "SELECT * FROM ogrenciler WHERE sinif = ?"
    imlec.execute(sorgu, (arana_sinif,))
    sonuc = imlec.fetchall()

    print(f"Aranan Sinif: {arana_sinif}")
    print(f"Dönen Deger: {sonuc}")
    print(f"Bos liste mi?: {sonuc == []}")

    assert sonuc == [], "Olmayan sinif sorgusu bos liste [] donmelidir!"
    print("Sonuc: Olmayan sinif icin fetchall() bos liste [] dondurur.")


def test_3_null_filtreleme(baglanti: sqlite3.Connection) -> None:
    """Test 3: SQL'de NULL degerleri filtreleme (IS NULL / IS NOT NULL).

    SQL'de NULL degerler '=' ile degil 'IS NULL' ile kontrol edilir.

    Args:
        baglanti: SQLite veritabani baglantisi.
    """
    print("\n--- Test 3: WHERE Sorgusuyla NULL Degerleri Filtreleme ---")
    imlec = baglanti.cursor()

    # Dogru yontem: IS NULL
    sorgu_null = "SELECT ad, soyad, email FROM ogrenciler WHERE email IS NULL"
    imlec.execute(sorgu_null)
    null_olanlar = [dict(satir) for satir in imlec.fetchall()]
    print(f"E-postasi olmayanlar (IS NULL sayisi): {len(null_olanlar)}")
    for ogr in null_olanlar:
        print(f"  -> {ogr['ad']} {ogr['soyad']} (E-posta: {ogr['email']})")

    # Hatali yaklasim aciklamasi: WHERE email = NULL hic satir dondurmez
    imlec.execute("SELECT * FROM ogrenciler WHERE email = NULL")
    hatali_sonuc = imlec.fetchall()
    print(f"WHERE email = NULL ile donen satir sayisi: {len(hatali_sonuc)}")

    assert len(null_olanlar) == 2, "E-postasi NULL olan 2 ogrenci olmaliydi!"
    assert len(hatali_sonuc) == 0, "'= NULL' kullanimi 0 sonuc uretmelidir!"
    print("Sonuc: NULL sorgulamasi icin '= NULL' degil 'IS NULL' kullanilir.")


def test_4_order_by_desc(baglanti: sqlite3.Connection) -> None:
    """Test 4: ORDER BY ad DESC ile tersten siralama dogrulamasi.

    Args:
        baglanti: SQLite veritabani baglantisi.
    """
    print("\n--- Test 4: ORDER BY ad DESC (Tersten Siralama) ---")
    imlec = baglanti.cursor()
    sorgu = "SELECT ad FROM ogrenciler ORDER BY ad DESC"
    imlec.execute(sorgu)
    sirali_adlar = [satir["ad"] for satir in imlec.fetchall()]

    print(f"Siralama Sonucu (DESC): {sirali_adlar}")

    beklenen = sorted(sirali_adlar, reverse=True)
    assert sirali_adlar == beklenen, "Siralama Z'den A'ya dogru olmalidir!"
    print(f"Ilk ogrenci: {sirali_adlar[0]} (Zeynep bekleniyordu)")
    print(f"Son ogrenci: {sirali_adlar[-1]} (Ahmet bekleniyordu)")
    print("Sonuc: ORDER BY ad DESC ogrencileri tersten (Z-A) dogru siralar.")


def test_5_group_by_count(baglanti: sqlite3.Connection) -> None:
    """Test 5: GROUP BY sinif ile COUNT(*) sayimlarinin dogrulanmasi.

    Args:
        baglanti: SQLite veritabani baglantisi.
    """
    print("\n--- Test 5: GROUP BY sinif, COUNT(*) Dogrulamasi ---")
    imlec = baglanti.cursor()
    sorgu = (
        "SELECT sinif, COUNT(*) AS ogrenci_sayisi "
        "FROM ogrenciler GROUP BY sinif ORDER BY sinif ASC"
    )
    imlec.execute(sorgu)
    gruplar = [dict(satir) for satir in imlec.fetchall()]

    beklenen_sayilar = {"10-A": 2, "10-B": 3}
    print("Hesaplanan Sinif Ogrenci Sayilari:")
    for satir in gruplar:
        sinif = satir["sinif"]
        sayi = satir["ogrenci_sayisi"]
        print(f"  -> Sinif: {sinif} | Sayi: {sayi}")
        assert sayi == beklenen_sayilar[sinif], f"{sinif} sayisi hatali!"

    print("Sonuc: GROUP BY sinif, COUNT(*) tum sinif sayilarini dogru saydi.")


if __name__ == "__main__":
    vt_baglanti = test_veritabani_olustur()
    try:
        test_1_bos_tablo_fetchall(vt_baglanti)
        test_2_olmayan_sinif(vt_baglanti)
        test_3_null_filtreleme(vt_baglanti)
        test_4_order_by_desc(vt_baglanti)
        test_5_group_by_count(vt_baglanti)
        print("\n>>> Tum testler basariyla tamamlandi. <<<")
    finally:
        vt_baglanti.close()
