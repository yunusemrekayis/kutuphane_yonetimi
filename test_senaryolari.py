# -*- coding: utf-8 -*-
"""Veritabani ekleme islemleri icin 5 farkli senaryo test modulu."""

import sqlite3


def test_veritabani_sifirla(vt_adi: str = "okul.db") -> None:
    """Testler oncesinde ogrenciler tablosunu temizler veya olusturur.

    Args:
        vt_adi: Veritabani dosya adi.
    """
    baglanti = sqlite3.connect(vt_adi)
    imlec = baglanti.cursor()
    imlec.execute(
        """
        CREATE TABLE IF NOT EXISTS ogrenciler (
            id INTEGER PRIMARY KEY,
            ad TEXT NOT NULL,
            soyad TEXT NOT NULL,
            email TEXT,
            sinif TEXT DEFAULT 'Belirsiz'
        );
        """
    )
    baglanti.commit()
    baglanti.close()


def test_1_ayni_ad_ekleme(vt_adi: str = "okul.db") -> None:
    """Test 1: Duplicate (ayni) ad ile iki kayit eklemeyi dener.

    Sonuc: Tabloda ad uzerinde UNIQUE kisiti olmadigi icin basarili olur.
    Otomatik artan id degeri farkli atanir.
    """
    print("\n[TEST 1] Ayni ad ile iki ogrenci ekleme denemesi...")
    baglanti = sqlite3.connect(vt_adi)
    imlec = baglanti.cursor()
    try:
        sorgu = "INSERT INTO ogrenciler (ad, soyad) VALUES (?, ?);"
        imlec.execute(sorgu, ("Ali", "Yilmaz"))
        id_1 = imlec.lastrowid
        imlec.execute(sorgu, ("Ali", "Demir"))
        id_2 = imlec.lastrowid
        baglanti.commit()
        print(f"-> Basarili: Iki 'Ali' kaydi da eklendi. ID'ler: {id_1}, {id_2}")
        print("-> Aciklama: Tabloda UNIQUE kisiti olmadigi icin isimler tekrar edebilir.")
    except sqlite3.Error as hata:
        print(f"-> Hata olustu: {hata}")
    finally:
        baglanti.close()


def test_2_bos_string_ve_null_ad(vt_adi: str = "okul.db") -> None:
    """Test 2: Bos string ('') ve gercek NULL (None) ad ekleme denemesi.

    Sonuc:
    - SQL'de '' (bos string) ile NULL ayni degildir. Bos string NOT NULL'i
      ihlal etmez ve SQLite tarafindan kabul edilir (Python seviyesinde
      engellenmedikce).
    - None (NULL) gonderildiginde ise NOT NULL kisiti devreye girer ve hata verir.
    """
    print("\n[TEST 2] Bos string ('') ve NULL ad ekleme denemesi...")
    baglanti = sqlite3.connect(vt_adi)
    imlec = baglanti.cursor()
    sorgu = "INSERT INTO ogrenciler (ad, soyad) VALUES (?, ?);"

    # 1. Deneme: Bos string
    try:
        imlec.execute(sorgu, ("", "Soyadsiz"))
        baglanti.commit()
        print("-> Bos string ('') eklendi! (SQLite acisindan metindir, NULL degildir)")
    except sqlite3.Error as hata:
        print(f"-> Bos string hatasi: {hata}")

    # 2. Deneme: NULL (None)
    try:
        imlec.execute(sorgu, (None, "Soyadli"))
        baglanti.commit()
        print("-> NULL ad eklendi!")
    except sqlite3.IntegrityError as hata:
        print(f"-> Basarili yakalama: NOT NULL kisiti ihlal edildi! Hata: {hata}")
    finally:
        baglanti.close()


def test_3_null_email_ekleme(vt_adi: str = "okul.db") -> None:
    """Test 3: email sutununa NULL (None) degeri gondermeyi dener.

    Sonuc: email sutununda NOT NULL kisiti bulunmadigi icin NULL basariyla kabul edilir.
    """
    print("\n[TEST 3] NULL email ile kayit ekleme denemesi...")
    baglanti = sqlite3.connect(vt_adi)
    imlec = baglanti.cursor()
    try:
        sorgu = "INSERT INTO ogrenciler (ad, soyad, email) VALUES (?, ?, ?);"
        imlec.execute(sorgu, ("Zeynep", "Aydin", None))
        baglanti.commit()
        print(f"-> Basarili: NULL email ile kayit eklendi. (rowcount: {imlec.rowcount})")
        print("-> Aciklama: Tablo semasinda email sutununda NOT NULL kisiti yoktur.")
    except sqlite3.Error as hata:
        print(f"-> Hata olustu: {hata}")
    finally:
        baglanti.close()


def test_4_cok_fazla_veri_ekleme(vt_adi: str = "okul.db") -> None:
    """Test 4: 100 adet ogrenciyi toplu ekler ve rowcount degerini kontrol eder.

    Sonuc: executemany sonrasi rowcount degeri tam olarak 100 olmalidir.
    """
    print("\n[TEST 4] 100 adet ogrenciyi toplu ekleme ve rowcount testi...")
    baglanti = sqlite3.connect(vt_adi)
    imlec = baglanti.cursor()
    try:
        toplu_liste = [
            (f"Ogrenci_{i}", f"Soyad_{i}", f"ogrenci_{i}@okul.k12.tr", "11-A")
            for i in range(1, 101)
        ]
        sorgu = """
        INSERT INTO ogrenciler (ad, soyad, email, sinif)
        VALUES (?, ?, ?, ?);
        """
        imlec.executemany(sorgu, toplu_liste)
        baglanti.commit()
        print(f"-> Eklenen satir sayisi (rowcount): {imlec.rowcount}")
        if imlec.rowcount == 100:
            print("-> Basarili: rowcount beklendigi gibi tam 100 sonucunu verdi.")
        else:
            print(f"-> Beklenmeyen rowcount degeri: {imlec.rowcount}")
    except sqlite3.Error as hata:
        print(f"-> Toplu ekleme hatasi: {hata}")
    finally:
        baglanti.close()


def test_5_sql_injection_denemesi(vt_adi: str = "okul.db") -> None:
    """Test 5: Parametresiz (f-string) guvensiz sorgu ile SQL injection ornegi.

    Sonuc:
    Kullanici girdisi dogrudan metin birlestirme ile calistirildiginda,
    girdideki tek tirnak (') sorgu mantigini bozabilir veya verileri degistirebilir.
    Parametreli (?) sorguda ise bu girdi yalın metin olarak guvenle algilanir.
    """
    print("\n[TEST 5] Parametresiz sorguda SQL Injection acigi testi...")
    baglanti = sqlite3.connect(vt_adi)
    imlec = baglanti.cursor()

    # Saldirgan ogrenci adi yerine tirnak kapatip baska deger enjekte etmeyi dener
    zararli_girdi = "Hasan', 'Saldirgan'); --"

    # Guvensiz yontem (f-string / metin birlestirme):
    guvensiz_sorgu = (
        f"INSERT INTO ogrenciler (ad, soyad) "
        f"VALUES ('{zararli_girdi}', 'Guvensiz');"
    )
    print("Calistirilacak guvensiz SQL:")
    print(guvensiz_sorgu)

    try:
        # SQLite'in tek execute() fonksiyonu coklu sorgu calistirmaz (enjection kisitli kalir),
        # ancak mevcut sorgunun deger alanlarini degistirebilir.
        imlec.execute(guvensiz_sorgu)
        baglanti.commit()
        print("-> Guvensiz sorgu calisti ve SQL yapisi istismar edildi!")
    except sqlite3.Error as hata:
        print(f"-> Guvensiz sorguda soz dizimi kirildi: {hata}")

    # Guvenli yontem (Parametreli sorgu):
    print("\nAyni zararli girdinin parametreli (?) sorgu ile calistirilmasi:")
    guvenli_sorgu = "INSERT INTO ogrenciler (ad, soyad) VALUES (?, ?);"
    try:
        imlec.execute(guvenli_sorgu, (zararli_girdi, "Guvenli"))
        baglanti.commit()
        print("-> Basarili: Parametreli sorgu enjeksiyonu engelledi.")
        print("-> Girdi oldugu gibi zararsiz bir metin (string) olarak kaydedildi.")
    except sqlite3.Error as hata:
        print(f"-> Guvenli sorgu hatasi: {hata}")
    finally:
        baglanti.close()


if __name__ == "__main__":
    test_veritabani_sifirla()
    test_1_ayni_ad_ekleme()
    test_2_bos_string_ve_null_ad()
    test_3_null_email_ekleme()
    test_4_cok_fazla_veri_ekleme()
    test_5_sql_injection_denemesi()
