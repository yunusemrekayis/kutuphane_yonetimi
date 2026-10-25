"""Pekiştirmeli Öğrenme Ödül Kuralları ve Ajan Birim Testleri.

Bu dosya odul_kurallari.py dosyasındaki ödül kurallarını, ortamın
sonuc ve adim_at metotlarını, açgözlü ajanı ve indirimli skor
hesaplarını doğrular.
"""

import os
import unittest
from odul_kurallari import (
    AdimCezasi,
    AcgozluAjan,
    BASLANGIC,
    Bolum1Kurali,
    DUVARLAR,
    EYLEMLER,
    GAMA,
    manhattan_mesafe,
    OyunDunyasi,
    RastgeleAjan,
    SadeceHedef,
    SARJ_ISTASYONU,
    Simulasyon,
    YaklasmaOdulu,
)

# Pygame'i arka planda (ekransız) çalıştırmak için sanal sürücü
os.environ["SDL_VIDEODRIVER"] = "dummy"


class TestOdulKurallari(unittest.TestCase):
    """Ödül kuralları sınıflarını test eder."""

    def test_manhattan_mesafesi(self):
        """Manhattan mesafesinin doğru hesaplandığını doğrular."""
        self.assertEqual(manhattan_mesafe((0, 0), (7, 7)), 14)
        self.assertEqual(manhattan_mesafe((2, 3), (2, 5)), 2)
        self.assertEqual(manhattan_mesafe((4, 4), (4, 4)), 0)

    def test_bolum1_kurali(self):
        """Bölüm 1 kuralı ödüllerini test eder."""
        kural = Bolum1Kurali()
        # Şarj: +10
        self.assertEqual(kural.hesapla(1, 0, False, True), 10)
        # Çarpma: -1
        self.assertEqual(kural.hesapla(5, 5, True, False), -1)
        # Normal adım: 0
        self.assertEqual(kural.hesapla(5, 4, False, False), 0)
        self.assertEqual(kural.hesapla(5, 6, False, False), 0)

    def test_sadece_hedef_kurali(self):
        """Sadece hedef kuralı ödüllerini test eder."""
        kural = SadeceHedef()
        # Şarj: +10
        self.assertEqual(kural.hesapla(1, 0, False, True), 10)
        # Çarpma: 0
        self.assertEqual(kural.hesapla(5, 5, True, False), 0)
        # Normal adım: 0
        self.assertEqual(kural.hesapla(5, 4, False, False), 0)

    def test_adim_cezasi_kurali(self):
        """Adım cezası kuralı ödüllerini test eder."""
        kural = AdimCezasi()
        # Şarj: +10
        self.assertEqual(kural.hesapla(1, 0, False, True), 10)
        # Çarpma: -1
        self.assertEqual(kural.hesapla(5, 5, True, False), -1)
        # Normal adım: -1
        self.assertEqual(kural.hesapla(5, 4, False, False), -1)

    def test_yaklasma_odulu_kurali(self):
        """Yaklaşma ödülü kuralı ödüllerini test eder."""
        kural = YaklasmaOdulu()
        # Şarj: +10
        self.assertEqual(kural.hesapla(1, 0, False, True), 10)
        # Yaklaşınca: +1 (eski=5, yeni=4)
        self.assertEqual(kural.hesapla(5, 4, False, False), 1)
        # Uzaklaşınca: -1 (eski=4, yeni=5)
        self.assertEqual(kural.hesapla(4, 5, False, False), -1)
        # Duvara çarpıp aynı mesafede kalınca: -1 (eski=5, yeni=5)
        self.assertEqual(kural.hesapla(5, 5, True, False), -1)


class TestOyunDunyasi(unittest.TestCase):
    """Oyun dünyası ortamını ve sonuc metodunu test eder."""

    def test_sonuc_dunyayi_degistirmez(self):
        """sonuc() metodunun ortam durumunu değiştirmediğini doğrular."""
        dunya = OyunDunyasi(Bolum1Kurali())
        baslangic_konum = dunya.robot
        baslangic_adim = dunya.adim

        # Bir eylemin sonucuna bak
        yeni_konum, odul, hedefte = dunya.sonuc(baslangic_konum, 1)

        # Ortamın değişmediğini doğrula
        self.assertEqual(dunya.robot, baslangic_konum)
        self.assertEqual(dunya.adim, baslangic_adim)
        self.assertEqual(yeni_konum, (1, 0))
        self.assertEqual(odul, 0)
        self.assertFalse(hedefte)

    def test_sonuc_duvar_carpmasi(self):
        """sonuc() metodunun duvar çarpmasını doğru yakaladığını test eder."""
        dunya = OyunDunyasi(Bolum1Kurali())
        # (1, 2) bir duvardır. Robot (1, 1)'de iken
        # SAĞ (3) yaparsa duvara çarpar.
        konum = (1, 1)
        yeni_konum, odul, hedefte = dunya.sonuc(konum, 3)
        self.assertEqual(yeni_konum, (1, 1))  # Konum değişmemeli
        self.assertEqual(odul, -1)           # Bölüm 1 kuralında çarpma -1
        self.assertFalse(hedefte)

    def test_adim_at_kullanimi(self):
        """adim_at metodunun ortam durumunu güncellediğini doğrular."""
        dunya = OyunDunyasi(Bolum1Kurali())
        konum, odul, bitti = dunya.adim_at(1)  # AŞAĞI
        self.assertEqual(konum, (1, 0))
        self.assertEqual(dunya.robot, (1, 0))
        self.assertEqual(dunya.adim, 1)
        self.assertFalse(bitti)


class TestAjanlar(unittest.TestCase):
    """Rastgele ve açgözlü ajanların kararlarını test eder."""

    def test_acgozlu_ajan_hedefe_yonelecektir(self):
        """Açgözlü ajanın şarj istasyonu yanındayken şarjı
        seçeceğini test eder."""
        dunya = OyunDunyasi(Bolum1Kurali())
        ajan = AcgozluAjan(dunya)

        # Robot şarj istasyonunun (7, 7) hemen solunda: (7, 6)
        # Eylem 3 (SAĞ) şarja ulaştırır ve +10 verir.
        eylem = ajan.eylem_sec((7, 6), dunya)
        self.assertEqual(eylem, 3)

    def test_acgozlu_ajan_yaklasma_odulunde_yaklasir(self):
        """Açgözlü ajanın yaklaşma ödülünde yaklaşan adımı
        seçeceğini test eder."""
        dunya = OyunDunyasi(YaklasmaOdulu())
        ajan = AcgozluAjan(dunya)

        # Robot (0, 0)'da iken AŞAĞI (1) veya SAĞ (3) mesafeyi azaltır (+1).
        # YUKARI (0) ve SOL (2) duvara çarpar (-1).
        # Ajan 1 veya 3'ten birini seçmelidir.
        secilenler = {ajan.eylem_sec((0, 0), dunya) for _ in range(20)}
        self.assertTrue(secilenler.issubset({1, 3}))

    def test_acgozlu_ajan_esitlikte_secim_yapar(self):
        """Ödüller eşit olduğunda rastgele geçerli eylemlerden seçer."""
        dunya = OyunDunyasi(SadeceHedef())
        ajan = AcgozluAjan(dunya)

        # (0, 0)'da SadeceHedef kuralında tüm adımlar 0 verir.
        secimler = {ajan.eylem_sec((0, 0), dunya) for _ in range(50)}
        # Birden fazla eylem seçilmiş olmalıdır (eşitler arası seçim)
        self.assertGreater(len(secimler), 1)


class TestSimulasyonVeSkorTablosu(unittest.TestCase):
    """Simülasyon indirimli toplam ve kural geçişlerini test eder."""

    def test_indirimli_toplam_odul_hesabi(self):
        """GAMA = 0.9 indirim katsayısının doğru uygulandığını test eder."""
        sim = Simulasyon()
        # İki adım attırıp indirimli ödülü kontrol edelim
        # 1. adımda odul = r0 -> indirimli = (0.9^0) * r0 = r0
        # 2. adımda odul = r1 -> indirimli = r0 + (0.9^1) * r1 = r0 + 0.9 * r1
        sim.adim_yap()
        ilk_odul = sim.son_odul
        beklenen_indirimli = float(ilk_odul)
        self.assertAlmostEqual(sim.indirimli_toplam, beklenen_indirimli)

        sim.adim_yap()
        ikinci_odul = sim.son_odul
        beklenen_indirimli += (GAMA ** 1) * ikinci_odul
        self.assertAlmostEqual(sim.indirimli_toplam, beklenen_indirimli)

    def test_kural_degisince_skor_tablosu_sifirlanir(self):
        """Kural değiştirildiğinde geçmiş ve skor tablosunun
        sıfırlandığını test eder."""
        sim = Simulasyon()
        # Bölümü bitirene kadar veya birkaç adım çalıştır
        sim.adim_yap()
        sim.bolum_gecmisi.append({"bolum": 1, "adim": 10, "sarj": True,
                                  "toplam": 10, "indirimli": 5.0})
        self.assertEqual(len(sim.bolum_gecmisi), 1)

        # Kural 2'ye geç
        sim.kural_sec(2)
        self.assertEqual(sim.aktif_kural_no, 2)
        self.assertEqual(len(sim.bolum_gecmisi), 0)
        self.assertEqual(sim.bolum, 1)

    def test_ajan_degisince_skor_tablosu_sifirlanir(self):
        """Ajan değiştirildiğinde skor tablosunun sıfırlandığını test eder."""
        sim = Simulasyon()
        sim.bolum_gecmisi.append({"bolum": 1, "adim": 10, "sarj": True,
                                  "toplam": 10, "indirimli": 5.0})
        self.assertIsInstance(sim.ajan, RastgeleAjan)

        # Ajanı değiştir -> AcgozluAjan olmalı
        sim.ajan_degistir()
        self.assertIsInstance(sim.ajan, AcgozluAjan)
        self.assertEqual(len(sim.bolum_gecmisi), 0)
        self.assertEqual(sim.bolum, 1)

        # Tekrar değiştir -> RastgeleAjan olmalı
        sim.ajan_degistir()
        self.assertIsInstance(sim.ajan, RastgeleAjan)


if __name__ == "__main__":
    unittest.main()
