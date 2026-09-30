# -*- coding: utf-8 -*-
"""Parametreli sorgularla tekil ve toplu ogrenci ekleme modulu."""

import sqlite3
from typing import List, Optional, Tuple


def _metin_temizle(deger: Optional[str]) -> Optional[str]:
    """Metin verisini dogrular ve bosluklari temizler.

    Args:
        deger: Dogrulanacak metin veya None.

    Returns:
        Temizlenmis metin ya da bos/None ise None.
    """
    if deger is None:
        return None
    if isinstance(deger, str):
        temiz = deger.strip()
        return temiz if temiz else None
    return str(deger).strip() or None


def ogrenci_ekle(
    veritabani_adi: str,
    ad: Optional[str],
    soyad: Optional[str],
    email: Optional[str],
    sinif: Optional[str] = "Belirsiz",
) -> bool:
    """Parametreli INSERT sorgusu ile tek bir ogrenci kaydeder.

    Args:
        veritabani_adi: SQLite veritabani dosya yolu.
        ad: Ogrencinin adi (zorunlu).
        soyad: Ogrencinin soyadi (zorunlu).
        email: Ogrencinin e-posta adresi (opsiyonel).
        sinif: Ogrencinin sinifi (varsayilan: 'Belirsiz').

    Returns:
        Ekleme islemi basarili ise True, aksi halde False.
    """
    # Bos veri ve tip dogrulamasi
    temiz_ad = _metin_temizle(ad)
    temiz_soyad = _metin_temizle(soyad)
    temiz_email = _metin_temizle(email)
    temiz_sinif = _metin_temizle(sinif) or "Belirsiz"

    if not temiz_ad or not temiz_soyad:
        print("Hata: Ogrenci adi ve soyadi bos birakilamaz!")
        return False

    baglanti = None
    try:
        baglanti = sqlite3.connect(veritabani_adi)
        imlec = baglanti.cursor()

        # SQL Injection onlemek icin parametreli (?) INSERT kullanimi
        ekleme_sorgusu = """
        INSERT INTO ogrenciler (ad, soyad, email, sinif)
        VALUES (?, ?, ?, ?);
        """
        parametreler = (temiz_ad, temiz_soyad, temiz_email, temiz_sinif)
        imlec.execute(ekleme_sorgusu, parametreler)

        # rowcount ile eklenen satir sayisini kontrol et
        if imlec.rowcount > 0:
            baglanti.commit()
            print(
                f"Basarili: {temiz_ad} {temiz_soyad} eklendi. "
                f"(Etkilenen satir: {imlec.rowcount})"
            )
            return True
        else:
            print("Uyari: Hicbir satir eklenemedi.")
            return False

    except sqlite3.Error as hata:
        print(f"Veritabani hatasi olustu: {hata}")
        return False
    finally:
        if baglanti:
            baglanti.close()


def ogrenci_listesi_ekle(
    veritabani_adi: str,
    ogrenciler_listesi: List[Tuple[Optional[str], ...]],
) -> int:
    """executemany kullanarak toplu ogrenci ekleme islemi yapar.

    Args:
        veritabani_adi: SQLite veritabani dosya yolu.
        ogrenciler_listesi: (ad, soyad, email, sinif) seklinde demet listesi.

    Returns:
        Eklenen toplam basarili kayit sayisi.
    """
    if not isinstance(ogrenciler_listesi, list) or not ogrenciler_listesi:
        print("Hata: Gecerli ve dolu bir ogrenci listesi verilmeli.")
        return 0

    # Liste icerisindeki ogrencileri filtrele ve dogrula
    gecerli_ogrenciler = []
    for sira, kayit in enumerate(ogrenciler_listesi, start=1):
        if not isinstance(kayit, (tuple, list)) or len(kayit) < 2:
            print(f"Uyari: {sira}. kayit eksik veri iceriyor, atlandi.")
            continue

        ad = _metin_temizle(kayit[0])
        soyad = _metin_temizle(kayit[1])
        email = _metin_temizle(kayit[2]) if len(kayit) > 2 else None
        sinif = (
            _metin_temizle(kayit[3]) if len(kayit) > 3 else None
        ) or "Belirsiz"

        if not ad or not soyad:
            print(f"Uyari: {sira}. kayitta ad veya soyad bos, atlandi.")
            continue

        gecerli_ogrenciler.append((ad, soyad, email, sinif))

    if not gecerli_ogrenciler:
        print("Hata: Eklenecek gecerli ogrenci bulunamadi.")
        return 0

    baglanti = None
    try:
        baglanti = sqlite3.connect(veritabani_adi)
        imlec = baglanti.cursor()

        toplu_sorgu = """
        INSERT INTO ogrenciler (ad, soyad, email, sinif)
        VALUES (?, ?, ?, ?);
        """
        # Toplu veri ekleme icin executemany kullanimi
        imlec.executemany(toplu_sorgu, gecerli_ogrenciler)

        etkilenen = imlec.rowcount
        if etkilenen > 0:
            baglanti.commit()
            print(
                f"Toplu ekleme tamamlandi. "
                f"Eklenen toplam ogrenci sayisi: {etkilenen}"
            )
            return etkilenen
        else:
            print("Uyari: Toplu ekleme sirasinda satir etkilenmedi.")
            return 0

    except sqlite3.Error as hata:
        print(f"Toplu ekleme sirasinda veritabani hatasi olustu: {hata}")
        return 0
    finally:
        if baglanti:
            baglanti.close()


if __name__ == "__main__":
    veritabani = "okul.db"

    print("--- 1. Tek Ogrenci Ekleme Testi ---")
    ogrenci_ekle(veritabani, "Ahmet", "Demir", "ahmet@okul.k12.tr", "10-A")

    print("\n--- 2. Bos/Gecersiz Veri Testi ---")
    ogrenci_ekle(veritabani, "   ", "Yilmaz", None, "10-B")

    print("\n--- 3. Toplu Ogrenci Ekleme Testi ---")
    yeni_ogrenciler = [
        ("Mehmet", "Kaya", "mehmet@okul.k12.tr", "10-B"),
        ("Ayse", "Celik", None, "10-A"),
        ("", "Sahin", "gecersiz@okul.k12.tr", "10-C"),  # Bos ad, atlanmali
        ("Fatma", "Yildiz", "fatma@okul.k12.tr", "10-C"),
    ]
    ogrenci_listesi_ekle(veritabani, yeni_ogrenciler)
