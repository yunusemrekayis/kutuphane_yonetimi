# -*- coding: utf-8 -*-
"""SQLite veritabani olusturma ve tablo tasarimi ornegi."""

import os
import sqlite3


def veritabani_hazirla(veritabani_adi: str) -> None:
    """Okul veritabanini ve ogrenciler tablosunu olusturur.

    Args:
        veritabani_adi: Olusturulacak veritabani dosyasinin adi.
    """
    if not isinstance(veritabani_adi, str) or not veritabani_adi.strip():
        print("Hata: Gecersiz veritabani dosya adi.")
        return

    baglanti = None
    try:
        # 1. Adim: Veritabani baglantisini ac (yoksa olusturur)
        baglanti = sqlite3.connect(veritabani_adi)
        imlec = baglanti.cursor()

        # 2 ve 3. Adim: ogrenciler tablosunu olusturan SQL komutu
        tablo_sql = """
        CREATE TABLE IF NOT EXISTS ogrenciler (
            id INTEGER PRIMARY KEY,
            ad TEXT NOT NULL,
            soyad TEXT NOT NULL,
            email TEXT,
            sinif TEXT DEFAULT 'Belirsiz'
        );
        """
        imlec.execute(tablo_sql)

        # 4. Adim: Degisiklikleri onayla (commit)
        baglanti.commit()
        print("Tablo basariyla kontrol edildi veya olusturuldu.")

    except sqlite3.Error as hata:
        print(f"Veritabani hatasi olustu: {hata}")
    finally:
        # Baglantiyi guvenli bir sekilde kapat
        if baglanti:
            baglanti.close()
            print("Veritabani baglantisi kapatildi.")

    # 5. Adim: Veritabani dosyasinin varligini kontrol et
    if os.path.exists(veritabani_adi):
        print(f"Dogrulama: '{veritabani_adi}' dosyasi mevcut.")
    else:
        print(f"Hata: '{veritabani_adi}' dosyasi bulunamadi.")


if __name__ == "__main__":
    dosya_adi = "okul.db"
    veritabani_hazirla(dosya_adi)
