# -*- coding: utf-8 -*-
"""SQLite ogrenci guncelleme ve guvenli silme islemleri modulu.

Bu modul, okul veritabaninda ogrencilerin sinif bilgilerini guncelleme
ve guvenli (onay mekanizmali) silme islemlerini gerceklestirir.
"""

import sqlite3
from typing import Any, Dict, Optional


def _metin_temizle(deger: Any) -> Optional[str]:
    """Metin verisinin bosluklarini temizler ve bos ise None dondurur.

    Args:
        deger: Kontrol edilecek metin veya deger.

    Returns:
        Temizlenmis metin ya da gecersizse None.
    """
    if deger is None:
        return None
    if isinstance(deger, str):
        temiz = deger.strip()
        return temiz if temiz else None
    return str(deger).strip() or None


def _pozitif_tam_sayi_mi(deger: Any) -> bool:
    """Degerin pozitif bir tamsayi kimligi olup olmadigini denetler.

    Args:
        deger: Denetlenecek kimlik verisi.

    Returns:
        Gecerli ve sifirdan buyuk tamsayi ise True, degilse False.
    """
    if isinstance(deger, bool):
        return False
    if isinstance(deger, int):
        return deger > 0
    if isinstance(deger, str) and deger.strip().isdigit():
        return int(deger.strip()) > 0
    return False


def ogrenci_bilgisi_getir(
    veritabani_adi: str, ogrenci_id: Any
) -> Optional[Dict[str, Any]]:
    """Verilen kimlige (ID) ait ogrenci kaydini getirir.

    Args:
        veritabani_adi: SQLite veritabani dosya yolu.
        ogrenci_id: Ogrencinin benzersiz kimlik numarasi.

    Returns:
        Ogrenci verilerini iceren sozluk veya bulunamazsa None.
    """
    if not _pozitif_tam_sayi_mi(ogrenci_id):
        return None

    baglanti = None
    try:
        baglanti = sqlite3.connect(veritabani_adi)
        baglanti.row_factory = sqlite3.Row
        imlec = baglanti.cursor()

        sorgu = "SELECT * FROM ogrenciler WHERE id = ?"
        imlec.execute(sorgu, (int(ogrenci_id),))
        satir = imlec.fetchone()

        if satir:
            return dict(satir)
        return None
    except sqlite3.Error as hata:
        print(f"Sorgulama hatasi: {hata}")
        return None
    finally:
        if baglanti:
            baglanti.close()


def ogrenci_guncelle(
    veritabani_adi: str, ogrenci_id: Any, yeni_sinif: Any
) -> bool:
    """Belirli bir ogrencinin sinif bilgisini gunceller (UPDATE).

    Parametreli sorgu ile guvenlik saglanir. Islem sirasinda bir hata
    meydana gelirse degisiklikler geri alinir (rollback).

    Args:
        veritabani_adi: SQLite veritabani dosya yolu.
        ogrenci_id: Guncellenecek ogrencinin numarasi (ID).
        yeni_sinif: Ogrencinin atanacagi yeni sinif.

    Returns:
        Guncelleme basarili ve en az 1 kayit degismisse True, aksi halde False.
    """
    # 1. Girdi dogrulamasi
    if not _pozitif_tam_sayi_mi(ogrenci_id):
        print("Hata: Gecersiz ogrenci numarasi (ID).")
        return False

    temiz_sinif = _metin_temizle(yeni_sinif)
    if not temiz_sinif:
        print("Hata: Yeni sinif bilgisi bos birakilamaz.")
        return False

    sayisal_id = int(ogrenci_id)
    baglanti = None

    try:
        baglanti = sqlite3.connect(veritabani_adi)
        imlec = baglanti.cursor()

        # 2. Parametreli UPDATE sorgusu
        guncelleme_sorgusu = """
            UPDATE ogrenciler
            SET sinif = ?
            WHERE id = ?;
        """
        imlec.execute(guncelleme_sorgusu, (temiz_sinif, sayisal_id))

        # 3. rowcount ile etkilenen satir sayisini kontrol etme
        etkilenen_satir = imlec.rowcount
        if etkilenen_satir > 0:
            baglanti.commit()
            print(
                f"Basarili: {sayisal_id} numarali ogrencinin sinifi "
                f"'{temiz_sinif}' olarak guncellendi. (Satir: {etkilenen_satir})"
            )
            return True
        else:
            print(f"Uyari: {sayisal_id} numarali ogrenci bulunamadi.")
            return False

    except sqlite3.Error as hata:
        # Hata durumunda yapilan islemleri geri al (rollback)
        if baglanti:
            baglanti.rollback()
        print(f"Veritabani hatasi olustu, degisiklikler geri alindi: {hata}")
        return False

    finally:
        if baglanti:
            baglanti.close()


def ogrenci_sil(
    veritabani_adi: str, ogrenci_id: Any, onay: Optional[bool] = None
) -> bool:
    """Belirli bir ogrenci kaydini guvenli sekilde siler (DELETE).

    Silme oncesi ogrencinin varligi dogrulanir ve kullanicidan onay alinir.
    Parametreli sorgu ve rollback yapisi ile veri butunlugu korunur.

    Args:
        veritabani_adi: SQLite veritabani dosya yolu.
        ogrenci_id: Silinecek ogrencinin numarasi (ID).
        onay: Test veya otomatik islemler icin onceden verilen onay degeri.
              None verilirse konsoldan kullaniciya sorulur.

    Returns:
        Silme basarili ise True, silinmediyse veya hata olustuysa False.
    """
    # 1. Girdi dogrulamasi
    if not _pozitif_tam_sayi_mi(ogrenci_id):
        print("Hata: Gecersiz ogrenci numarasi (ID).")
        return False

    sayisal_id = int(ogrenci_id)

    # 2. Silmeden once kaydin varligini dogrulama
    ogrenci = ogrenci_bilgisi_getir(veritabani_adi, sayisal_id)
    if not ogrenci:
        print(f"Hata: {sayisal_id} numarali ogrenci kaydi bulunamadi.")
        return False

    ogrenci_adi = f"{ogrenci.get('ad', '')} {ogrenci.get('soyad', '')}".strip()
    ogrenci_sinif = ogrenci.get("sinif", "Belirsiz")

    # 3. Silme oncesi 'Emin misin?' kontrolu
    if onay is None:
        mesaj = (
            f"DIKKAT: '{ogrenci_adi}' ({ogrenci_sinif}) kaydini silmek "
            f"uzeresiniz.\nEmin misiniz? (E/H): "
        )
        try:
            cevap = input(mesaj).strip().upper()
            onaylanmis = cevap in ("E", "EVET")
        except EOFError:
            onaylanmis = False
    else:
        onaylanmis = bool(onay)

    if not onaylanmis:
        print("Silme islemi kullanici tarafindan iptal edildi.")
        return False

    baglanti = None
    try:
        baglanti = sqlite3.connect(veritabani_adi)
        imlec = baglanti.cursor()

        # 4. Parametreli DELETE sorgusu
        silme_sorgusu = "DELETE FROM ogrenciler WHERE id = ?;"
        imlec.execute(silme_sorgusu, (sayisal_id,))

        # 5. rowcount kontrolu
        etkilenen_satir = imlec.rowcount
        if etkilenen_satir > 0:
            baglanti.commit()
            print(
                f"Basarili: {ogrenci_adi} kaydi sistemden silindi. "
                f"(Silinen kayit sayisi: {etkilenen_satir})"
            )
            return True
        else:
            print(f"Uyari: {sayisal_id} numarali kayit silinemedi.")
            return False

    except sqlite3.Error as hata:
        # Hata aninda geri alma
        if baglanti:
            baglanti.rollback()
        print(f"Silme sirasinda hata olustu, geri alindi: {hata}")
        return False

    finally:
        if baglanti:
            baglanti.close()


if __name__ == "__main__":
    db_yolu = "okul.db"

    print("--- 1. Ogrenci Guncelleme (UPDATE) Testi ---")
    ogrenci_guncelle(db_yolu, 1, "11-A")
    ogrenci_guncelle(db_yolu, 9999, "12-F")

    print("\n--- 2. Guvenli Ogrenci Silme (DELETE) Testi ---")
    ogrenci_sil(db_yolu, 2, onay=False)
    ogrenci_sil(db_yolu, -5, onay=True)
