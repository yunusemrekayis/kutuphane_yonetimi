# -*- coding: utf-8 -*-
"""SQLite ogrenci sorgulama modulu.

Bu modul, okul veritabaninda ogrencileri cesitli SQL sorgulari ile
filtreleme, siralama ve gruplama islemlerini gerceklestirir.
"""

import sqlite3
from typing import Any, Dict, List, Optional


def baglanti_al(veritabani_yolu: str) -> Optional[sqlite3.Connection]:
    """Verilen dosya yolu icin sozluk erisimli SQLite baglantisi acar.

    Args:
        veritabani_yolu: Veritabani dosyasinin tam veya bagil yolu.

    Returns:
        sqlite3.Connection veya hata durumunda None.
    """
    if not isinstance(veritabani_yolu, str) or not veritabani_yolu.strip():
        print("Hata: Gecersiz veritabani yolu belirtildi.")
        return None

    try:
        baglanti = sqlite3.connect(veritabani_yolu.strip())
        # Sonuc sutunlarina isimle erisebilmek icin row_factory ayarlanir
        baglanti.row_factory = sqlite3.Row
        return baglanti
    except sqlite3.Error as hata:
        print(f"Baglanti hatasi olustu: {hata}")
        return None


def tum_ogrencileri_getir(veritabani_yolu: str) -> List[Dict[str, Any]]:
    """Tum ogrenci kayitlarini ceker ve sozluk listesi olarak dondurur.

    Sorgu: SELECT * FROM ogrenciler

    Args:
        veritabani_yolu: SQLite veritabani dosya yolu.

    Returns:
        Ogrenci sozluklerinden olusan liste.
    """
    baglanti = baglanti_al(veritabani_yolu)
    if baglanti is None:
        return []

    sonuclar: List[Dict[str, Any]] = []
    try:
        imlec = baglanti.cursor()
        sorgu = "SELECT * FROM ogrenciler"
        imlec.execute(sorgu)

        satirlar = imlec.fetchall()
        if not satirlar:
            print("Bilgi: Tabloda hic ogrenci kaydi bulunamadi.")
            return []

        for satir in satirlar:
            sonuclar.append(dict(satir))

        return sonuclar
    except sqlite3.Error as hata:
        print(f"Sorgu hatasi (tum ogrenciler): {hata}")
        return []
    finally:
        baglanti.close()


def sinifa_gore_ogrencileri_getir(
    veritabani_yolu: str, sinif_adi: Optional[str]
) -> List[Dict[str, Any]]:
    """Belirli bir siniftaki ogrencileri parametreli sorguyla ceker.

    Sorgu: SELECT * FROM ogrenciler WHERE sinif = ?

    Args:
        veritabani_yolu: SQLite veritabani dosya yolu.
        sinif_adi: Filtrelenecek sinif bilgisi (orn. '10-A').

    Returns:
        Siniftaki ogrencilerin sozluk listesi.
    """
    if not isinstance(sinif_adi, str) or not sinif_adi.strip():
        print("Hata: Sinif adi bos birakilamaz.")
        return []

    baglanti = baglanti_al(veritabani_yolu)
    if baglanti is None:
        return []

    temiz_sinif = sinif_adi.strip()
    sonuclar: List[Dict[str, Any]] = []

    try:
        imlec = baglanti.cursor()
        sorgu = "SELECT * FROM ogrenciler WHERE sinif = ?"
        # SQL Injection acigini engellemek icin parametreli sorgu kullanilir
        imlec.execute(sorgu, (temiz_sinif,))

        satirlar = imlec.fetchall()
        if not satirlar:
            print(f"Bilgi: '{temiz_sinif}' sinifinda ogrenci bulunamadi.")
            return []

        for satir in satirlar:
            sonuclar.append(dict(satir))

        return sonuclar
    except sqlite3.Error as hata:
        print(f"Sorgu hatasi (sinif filtreleme): {hata}")
        return []
    finally:
        baglanti.close()


def ada_gore_sirali_ogrenciler(veritabani_yolu: str) -> List[Dict[str, Any]]:
    """Ogrencileri ada gore alfabetik (A-Z) olarak siralar.

    Sorgu: SELECT * FROM ogrenciler ORDER BY ad ASC

    Args:
        veritabani_yolu: SQLite veritabani dosya yolu.

    Returns:
        Ada gore siralanmis ogrenci listesi.
    """
    baglanti = baglanti_al(veritabani_yolu)
    if baglanti is None:
        return []

    sonuclar: List[Dict[str, Any]] = []
    try:
        imlec = baglanti.cursor()
        sorgu = "SELECT * FROM ogrenciler ORDER BY ad ASC"
        imlec.execute(sorgu)

        satirlar = imlec.fetchall()
        if not satirlar:
            print("Bilgi: Siralanacak ogrenci kaydi bulunamadi.")
            return []

        for satir in satirlar:
            sonuclar.append(dict(satir))

        return sonuclar
    except sqlite3.Error as hata:
        print(f"Sorgu hatasi (ada gore siralama): {hata}")
        return []
    finally:
        baglanti.close()


def sinif_ogrenci_sayilari(veritabani_yolu: str) -> List[Dict[str, Any]]:
    """Her sinifta kac ogrenci oldugunu sayar.

    Sorgu: SELECT sinif, COUNT(*) AS ogrenci_sayisi
           FROM ogrenciler GROUP BY sinif

    Args:
        veritabani_yolu: SQLite veritabani dosya yolu.

    Returns:
        Sinif ve ogrenci sayisi bilgilerini iceren sozluk listesi.
    """
    baglanti = baglanti_al(veritabani_yolu)
    if baglanti is None:
        return []

    sonuclar: List[Dict[str, Any]] = []
    try:
        imlec = baglanti.cursor()
        sorgu = (
            "SELECT sinif, COUNT(*) AS ogrenci_sayisi "
            "FROM ogrenciler GROUP BY sinif"
        )
        imlec.execute(sorgu)

        satirlar = imlec.fetchall()
        if not satirlar:
            print("Bilgi: Sayim yapilacak ogrenci kaydi bulunamadi.")
            return []

        for satir in satirlar:
            sonuclar.append(dict(satir))

        return sonuclar
    except sqlite3.Error as hata:
        print(f"Sorgu hatasi (sinif sayilari): {hata}")
        return []
    finally:
        baglanti.close()


def fetch_farklarini_goster(veritabani_yolu: str) -> None:
    """fetchone, fetchmany ve fetchall metotlarinin calisma farkini gosterir.

    Args:
        veritabani_yolu: SQLite veritabani dosya yolu.
    """
    baglanti = baglanti_al(veritabani_yolu)
    if baglanti is None:
        return

    try:
        imlec = baglanti.cursor()
        imlec.execute("SELECT id, ad, soyad, sinif FROM ogrenciler")

        print("\n--- fetch Yontemlerinin Farklari ---")

        # 1. fetchone(): Tek bir satir ceker ve imleci bir ileri kaydirir
        ilk_kayit = imlec.fetchone()
        if ilk_kayit:
            print(
                f"[fetchone] Ilk ogrenci: {ilk_kayit['ad']} "
                f"{ilk_kayit['soyad']} ({ilk_kayit['sinif']})"
            )
        else:
            print("[fetchone] Kayit bulunamadi.")
            return

        # 2. fetchmany(n): Belirtilen sayi kadar satiri liste olarak alir
        sonraki_iki = imlec.fetchmany(2)
        print(f"[fetchmany(2)] Cekilen satir sayisi: {len(sonraki_iki)}")
        for kayit in sonraki_iki:
            print(f"  -> {kayit['ad']} {kayit['soyad']}")

        # 3. fetchall(): Imlecin yerinden itibaren kalan tum satirlari alir
        kalan_kayitlar = imlec.fetchall()
        print(f"[fetchall] Kalan satir sayisi: {len(kalan_kayitlar)}")
        for kayit in kalan_kayitlar:
            print(f"  -> {kayit['ad']} {kayit['soyad']}")

    except sqlite3.Error as hata:
        print(f"fetch islemi sirasinda hata olustu: {hata}")
    finally:
        baglanti.close()


if __name__ == "__main__":
    db_yolu = "okul.db"

    print("=== 1. Tum Ogrenciler (SELECT *) ===")
    tum_liste = tum_ogrencileri_getir(db_yolu)
    for ogr in tum_liste:
        print(f"- {ogr['ad']} {ogr['soyad']} | Sinif: {ogr['sinif']}")

    print("\n=== 2. Sinifa Gore Ogrenciler (WHERE sinif = ?) ===")
    sinif_10a = sinifa_gore_ogrencileri_getir(db_yolu, "10-A")
    for ogr in sinif_10a:
        print(f"- {ogr['ad']} {ogr['soyad']} | E-posta: {ogr['email']}")

    print("\n=== 3. Ada Gore Sirali Ogrenciler (ORDER BY ad ASC) ===")
    sirali_liste = ada_gore_sirali_ogrenciler(db_yolu)
    for ogr in sirali_liste:
        print(f"- {ogr['ad']} {ogr['soyad']}")

    print("\n=== 4. Sinif Ogrenci Sayilari (GROUP BY sinif) ===")
    sinif_dagilimi = sinif_ogrenci_sayilari(db_yolu)
    for kayit in sinif_dagilimi:
        print(
            f"- Sinif: {kayit['sinif']} -> "
            f"{kayit['ogrenci_sayisi']} ogrenci"
        )

    print("\n=== 5. fetch Metotlarinin Karsilastirilmasi ===")
    fetch_farklarini_goster(db_yolu)
