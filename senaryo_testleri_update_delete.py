# -*- coding: utf-8 -*-
"""SQL UPDATE ve DELETE islemleri icin senaryo testleri modulu.

Bu test dosyasinda 5 temel durum incelenir:
1. Olmayan ID guncellemesi ve rowcount kontrolu.
2. Olmayan ID silme girisimi ve kayit varlik kontrolu.
3. WHERE sarti olmadan yapilan UPDATE isleminin tum tabloya etkisi.
4. Silme isleminin onaysiz birakilmasi ve verinin korunmasi.
5. Hata (Exception) olusturuldugunda rollback'in calismasi.
"""

import sqlite3
from ogrenci_guncelle_sil import ogrenci_guncelle, ogrenci_sil


def gecici_test_veritabani_olustur() -> str:
    """Testler icin temiz bir gecici SQLite veritabani olusturur.

    Returns:
        Olusturulan veritabani dosyasinin adi.
    """
    db_yolu = "senaryo_test.db"
    baglanti = sqlite3.connect(db_yolu)
    imlec = baglanti.cursor()

    imlec.execute("DROP TABLE IF EXISTS ogrenciler;")
    imlec.execute(
        """
        CREATE TABLE ogrenciler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT NOT NULL,
            soyad TEXT NOT NULL,
            email TEXT,
            sinif TEXT DEFAULT 'Belirsiz'
        );
        """
    )

    # Ornek okul ogrenci kayitlari
    ornekler = [
        ("Ali", "Yilmaz", "ali@okul.k12.tr", "9-A"),
        ("Zehra", "Kaya", "zehra@okul.k12.tr", "10-B"),
        ("Yusuf", "Demir", "yusuf@okul.k12.tr", "11-C"),
    ]
    imlec.executemany(
        """
        INSERT INTO ogrenciler (ad, soyad, email, sinif)
        VALUES (?, ?, ?, ?);
        """,
        ornekler,
    )

    baglanti.commit()
    baglanti.close()
    return db_yolu


def test_1_olmayan_id_guncelle(db_yolu: str) -> None:
    """Test 1: Olmayan ID guncellendiginde rowcount degerini test eder."""
    print("\n--- TEST 1: Olmayan ID'yi Guncelleme ---")
    baglanti = sqlite3.connect(db_yolu)
    imlec = baglanti.cursor()

    olmayan_id = 9999
    yeni_sinif = "12-A"

    imlec.execute(
        "UPDATE ogrenciler SET sinif = ? WHERE id = ?;",
        (yeni_sinif, olmayan_id),
    )
    etkilenen_satir = imlec.rowcount
    baglanti.close()

    print(f"Calistirilan sorgu: UPDATE ... WHERE id = {olmayan_id}")
    print(f"Donen imlec.rowcount degeri: {etkilenen_satir}")

    # ogrenci_guncelle fonksiyonunun davranisi
    fonksiyon_sonucu = ogrenci_guncelle(db_yolu, olmayan_id, yeni_sinif)
    print(f"ogrenci_guncelle({olmayan_id}) donus degeri: {fonksiyon_sonucu}")

    assert etkilenen_satir == 0, "Hata: rowcount 0 olmaliydi!"
    assert fonksiyon_sonucu is False, "Hata: Fonksiyon False dondurmeliydi!"
    print("Sonuc 1: Evet, rowcount kesinlikle 0 doner ve hata firlatmaz.")


def test_2_olmayan_id_sil(db_yolu: str) -> None:
    """Test 2: Olmayan ID silinmeye calisildiginda olusan durumu test eder."""
    print("\n--- TEST 2: Olmayan ID'yi Silme Girisimi ---")
    baglanti = sqlite3.connect(db_yolu)
    imlec = baglanti.cursor()

    olmayan_id = 8888
    # Saf SQL ile silmeyi deniyoruz:
    imlec.execute("DELETE FROM ogrenciler WHERE id = ?;", (olmayan_id,))
    saf_sql_rowcount = imlec.rowcount
    baglanti.close()

    print(f"Saf SQL calistirildi. SQL hata vermez, sessizce biter.")
    print(f"Saf SQL imlec.rowcount degeri: {saf_sql_rowcount}")

    # Bizim fonksiyonumuzun guvenli davranisi:
    # Kaydin varligini once kontrol eder ve kullaniciyi uyarir
    print("Bizim ogrenci_sil fonksiyonumuz calistiriliyor:")
    fonksiyon_sonucu = ogrenci_sil(db_yolu, olmayan_id, onay=True)

    assert saf_sql_rowcount == 0, "Saf SQL rowcount 0 olmaliydi!"
    assert fonksiyon_sonucu is False, "Fonksiyon False dondurmeliydi!"
    print(
        "Sonuc 2: Standart SQL sessizce calisip rowcount=0 verir.\n"
        "Yazdigimiz ogrenci_sil ise kayit yoksa acik hata mesaji verir."
    )


def test_3_where_olmadan_update(db_yolu: str) -> None:
    """Test 3: WHERE sarti unutulan UPDATE sorgusunun etkisini test eder."""
    print("\n--- TEST 3: WHERE Sarti Olmadan UPDATE ---")
    baglanti = sqlite3.connect(db_yolu)
    imlec = baglanti.cursor()

    imlec.execute("SELECT COUNT(*) FROM ogrenciler;")
    toplam_kayit = imlec.fetchone()[0]
    print(f"Guncelleme oncesi toplam ogrenci sayisi: {toplam_kayit}")

    # TEHLIKE: WHERE olmadan tum siniflari degistiren sorgu
    tehlikeli_sorgu = "UPDATE ogrenciler SET sinif = ?;"
    imlec.execute(tehlikeli_sorgu, ("TUM_OKUL_MEZUN",))
    etkilenen = imlec.rowcount

    imlec.execute("SELECT DISTINCT sinif FROM ogrenciler;")
    kalan_siniflar = imlec.fetchall()

    baglanti.rollback()  # Tabloyu bozmamak icin geri aliyoruz
    baglanti.close()

    print(f"WHERE unutulunca etkilenen satir sayisi: {etkilenen}")
    print(f"Tablodaki yeni sinif degerleri: {[s[0] for s in kalan_siniflar]}")

    assert etkilenen == toplam_kayit, "Tum satirlar etkilenmeliydi!"
    print(
        "Sonuc 3: Evet! WHERE sarti unutulursa tablodaki TUM kayitlar "
        "ayni yeni degerle ezilir."
    )


def test_4_silme_onay_iptali(db_yolu: str) -> None:
    """Test 4: Onay verilmeyen silme isleminde kaydin durumunu test eder."""
    print("\n--- TEST 4: Silme Onayinin Iptal Edilmesi ---")
    silinecek_id = 1

    # Silme oncesi kayit var mi?
    baglanti = sqlite3.connect(db_yolu)
    imlec = baglanti.cursor()
    imlec.execute("SELECT * FROM ogrenciler WHERE id = ?;", (silinecek_id,))
    kayit_once = imlec.fetchone()
    print(f"Silme oncesi 1 nolu kayit: {kayit_once[1]} {kayit_once[2]}")

    # Kullanici iptal etti (onay=False)
    silme_sonucu = ogrenci_sil(db_yolu, silinecek_id, onay=False)
    print(f"ogrenci_sil calisti, donen sonuc: {silme_sonucu}")

    # Silme sonrasi kayit kontrolu
    imlec.execute("SELECT * FROM ogrenciler WHERE id = ?;", (silinecek_id,))
    kayit_sonra = imlec.fetchone()
    baglanti.close()

    assert silme_sonucu is False, "Silme islemi gerceklesmemeliydi!"
    assert kayit_sonra is not None, "Kayit silinmis, korunmaliydi!"
    print(
        f"Sonuc 4: Kayit silinmedi! Veritabani aynen korundu "
        f"(Hala mevcut: {kayit_sonra[1]})."
    )


def test_5_exception_ve_rollback(db_yolu: str) -> None:
    """Test 5: Islem aninda hata olusursa rollback calismasini test eder."""
    print("\n--- TEST 5: Hata Aninda Rollback Calismasi ---")
    baglanti = sqlite3.connect(db_yolu)
    imlec = baglanti.cursor()

    # 1 nolu ogrencinin guncelleme oncesi sinifini alalim
    imlec.execute("SELECT sinif FROM ogrenciler WHERE id = 1;")
    eski_sinif = imlec.fetchone()[0]
    print(f"Hata oncesi 1 nolu ogrencinin sinifi: {eski_sinif}")

    try:
        # Guncellemeyi yap
        imlec.execute(
            "UPDATE ogrenciler SET sinif = ? WHERE id = 1;",
            ("GECICI_SINIF",),
        )

        # Bilerek bir veritabani hatasi olusturalim (olmayan sutuna yazma)
        imlec.execute("UPDATE ogrenciler SET var_olmayan_sutun = 123;")

        # Hata olusmazsa commit yapilacakti
        baglanti.commit()
    except sqlite3.OperationalError as hata:
        print(f"Beklenen hata yakalandi: {hata}")
        # Hata olustugu icin rollback yapiyoruz
        baglanti.rollback()
        print("baglanti.rollback() cagirildi ve degisiklikler geri alindi.")

    # Rollback sonrasi veritabanini kontrol edelim
    imlec.execute("SELECT sinif FROM ogrenciler WHERE id = 1;")
    mevcut_sinif = imlec.fetchone()[0]
    baglanti.close()

    print(f"Hata ve rollback sonrasi 1 nolu ogrencinin sinifi: {mevcut_sinif}")

    assert mevcut_sinif == eski_sinif, "Rollback basarisiz oldu, sinif degismis!"
    print("Sonuc 5: Evet! Rollback sayesinde yapilan guncelleme tamamen geri alindi.")


def main():
    db_yolu = gecici_test_veritabani_olustur()
    test_1_olmayan_id_guncelle(db_yolu)
    test_2_olmayan_id_sil(db_yolu)
    test_3_where_olmadan_update(db_yolu)
    test_4_silme_onay_iptali(db_yolu)
    test_5_exception_ve_rollback(db_yolu)
    print("\n==========================================")
    print("Tum 5 senaryo basariyla test edildi ve onaylandi.")


if __name__ == "__main__":
    main()
