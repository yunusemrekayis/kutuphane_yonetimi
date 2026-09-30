import functools
import time
import unittest
from unittest.mock import patch, mock_open

# Test edilecek dekoratorler
def sure_olc(fonksiyon):
    """Fonksiyonun calisma suresini olcer."""
    @functools.wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        baslangic = time.perf_counter()
        try:
            return fonksiyon(*args, **kwargs)
        except Exception as hata:
            raise
        finally:
            bitis = time.perf_counter()
            gecen_sure = bitis - baslangic
            sarmalayici.son_sure = gecen_sure
    sarmalayici.son_sure = 0.0
    return sarmalayici


def kayit_tut(fonksiyon):
    """Cagri ve ciktilari hem ekrana hem de log dosyasina yazar."""
    @functools.wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        bilgi = f"{fonksiyon.__name__} cagrildi: {args}, {kwargs}\n"
        # Dosya yazma islemi ve olasi izin hatasi
        try:
            with open("kayitlar.log", "a", encoding="utf-8") as dosya:
                dosya.write(bilgi)
        except PermissionError as izin_hatasi:
            print(f"[UYARI] Dosya yazma izni yok: {izin_hatasi}")
        except OSError as dosya_hatasi:
            print(f"[UYARI] Dosya islemi basarisiz: {dosya_hatasi}")

        try:
            sonuc = fonksiyon(*args, **kwargs)
            return sonuc
        except Exception as hata:
            raise
    return sarmalayici


def pozitif_olmali(fonksiyon):
    """Sayisal girdilerin pozitif olmasini zorunlu kilar."""
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

        return fonksiyon(*args, **kwargs)
    return sarmalayici


class TestDekoratorler(unittest.TestCase):
    """Dekoratorlerin sinir durumlarini dogrulayan test sinifi."""

    def test_pozitif_olmali_negatif_sayida_hata_firlatir(self):
        """Negatif deger verildiginde ValueError firlatildigini test eder."""
        @pozitif_olmali
        def kermes_gelir(adet, fiyat):
            return adet * fiyat

        with self.assertRaises(ValueError):
            kermes_gelir(-5, 10)

        with self.assertRaises(ValueError):
            kermes_gelir(5, fiyat=-2.5)

    def test_kayit_tut_dosya_yazma_izni_olmadiginda(self):
        """Dosya yazma izni (PermissionError) durumunu test eder."""
        @kayit_tut
        def hatim_oku(cuz_no):
            return f"{cuz_no}. cuz okundu."

        # open fonksiyonunun PermissionError vermesini saglayalim
        with patch("builtins.open", side_effect=PermissionError("Erisim reddedildi")):
            # Fonksiyon hata almadan calismaya devam etmeli
            sonuc = hatim_oku(5)
            self.assertEqual(sonuc, "5. cuz okundu.")

    def test_sure_olc_hata_firlatilsa_bile_sureyi_olcer(self):
        """Hata firlatilsa dahi finally ile surenin dogru olculdugunu test eder."""
        @sure_olc
        def hatali_islem():
            time.sleep(0.05)
            raise RuntimeError("Beklenmeyen kesinti")

        with self.assertRaises(RuntimeError):
            hatali_islem()

        # Sure 0.05 saniyeden buyuk olmali
        self.assertGreaterEqual(hatali_islem.son_sure, 0.04)


if __name__ == "__main__":
    unittest.main()
