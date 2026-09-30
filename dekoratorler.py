import functools
import time


def sure_olc(fonksiyon):
    """Fonksiyonun calisma suresini olcer ve ekrana yazdirir."""
    @functools.wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        baslangic = time.perf_counter()
        try:
            sonuc = fonksiyon(*args, **kwargs)
            return sonuc
        except Exception as hata:
            print(f"Hata olustu: {hata}")
            raise
        finally:
            bitis = time.perf_counter()
            gecen_sure = bitis - baslangic
            print(f"[{fonksiyon.__name__}] Calisma suresi: "
                  f"{gecen_sure:.6f} saniye")
    return sarmalayici


def kayit_tut(fonksiyon):
    """Fonksiyon cagrisini, girdilerini ve ciktisini kaydeder."""
    @functools.wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        print(f"[CAGRI] {fonksiyon.__name__} calistiriliyor...")
        print(f"[GIRDI] args: {args}, kwargs: {kwargs}")
        try:
            sonuc = fonksiyon(*args, **kwargs)
            print(f"[CIKTI] Sonuc: {sonuc}")
            return sonuc
        except Exception as hata:
            print(f"[HATA] {fonksiyon.__name__} sirasinda hata: {hata}")
            raise
    return sarmalayici


def pozitif_olmali(fonksiyon):
    """Sayisal girdilerin pozitif olup olmadigini denetler."""
    @functools.wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        for sira, deger in enumerate(args, start=1):
            if isinstance(deger, (int, float)) and deger <= 0:
                raise ValueError(
                    f"{sira}. parametre pozitif bir sayi olmali: {deger}"
                )

        for anahtar, deger in kwargs.items():
            if isinstance(deger, (int, float)) and deger <= 0:
                raise ValueError(
                    f"'{anahtar}' degeri pozitif bir sayi olmali: {deger}"
                )

        try:
            return fonksiyon(*args, **kwargs)
        except Exception as hata:
            print(f"[HATA] Islem basarisiz: {hata}")
            raise
    return sarmalayici


# --- Sinif / Kermes Baglaminda Ornek Kullanimlar ---

@sure_olc
@kayit_tut
@pozitif_olmali
def kermes_kitap_geliri_ekle(kitap_adedi, birim_fiyat):
    """Kermeste satilan kitaplarin toplam gelirini hesaplar."""
    toplam = kitap_adedi * birim_fiyat
    return toplam


@kayit_tut
@pozitif_olmali
def hatim_sayfa_kaydet(ogrenci_adi, okunan_sayfa):
    """Ogrencinin okudugu sayfa sayisini dogrulayip ekler."""
    if not isinstance(ogrenci_adi, str) or not ogrenci_adi.strip():
        raise ValueError("Ogrenci adi bos birakilamaz.")
    return f"{ogrenci_adi} icin {okunan_sayfa} sayfa kaydedildi."


if __name__ == "__main__":
    print("--- 1. Basarili Senaryo: Kermes Kitap Geliri ---")
    kermes_kitap_geliri_ekle(15, 20.5)

    print("\n--- 2. Basarili Senaryo: Hatim Sayfa Takibi ---")
    hatim_sayfa_kaydet("Ahmet", okunan_sayfa=20)

    print("\n--- 3. Hatali Senaryo: Negatif Girdi Kontrolu ---")
    try:
        kermes_kitap_geliri_ekle(-5, 10)
    except ValueError as e:
        print(f"Beklenen hata yakalandi: {e}")
