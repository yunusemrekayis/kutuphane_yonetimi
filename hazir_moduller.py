"""Standart kütüphane modülleri tanıtım ve uygulama dosyası.

math, random ve datetime modüllerini okul ve ezber takibi
bağlamında örneklerle açıklar.
"""

import datetime
import math
import random


def matematik_bolumu() -> None:
    """math modülü temel fonksiyonlarını ve masa hesabı örneğini gösterir."""
    # ==========================================
    # 1. BÖLÜM: math MODÜLÜ
    # ==========================================
    print("--- 1. math Modülü ---")

    # pi sayısı ve karekök
    pi_sayisi = math.pi
    karekok_degeri = math.sqrt(144)
    print(f"Pi sayısı: {pi_sayisi:.4f}")
    print(f"144 sayısının karekökü: {karekok_degeri}")

    # Aşağı ve yukarı yuvarlama
    ornek_sayi = 7.3
    asagi_yuvarlama = math.floor(ornek_sayi)
    yukari_yuvarlama = math.ceil(ornek_sayi)
    print(f"{ornek_sayi} için aşağı yuvarlama (floor): {asagi_yuvarlama}")
    print(f"{ornek_sayi} için yukarı yuvarlama (ceil): {yukari_yuvarlama}")

    # 47 öğrenci 6 kişilik masalara: kaç masa gerekir
    ogrenci_sayisi = 47
    masa_kapasitesi = 6
    gereken_masa = math.ceil(ogrenci_sayisi / masa_kapasitesi)
    print(
        f"{ogrenci_sayisi} öğrenci için ({masa_kapasitesi} kişilik masalardan) "
        f"gereken masa sayısı: {gereken_masa}\n"
    )


def rastgelelik_bolumu() -> None:
    """random modülü ile sözlü ve grup kurası seçimlerini gösterir."""
    # ==========================================
    # 2. BÖLÜM: random MODÜLÜ
    # ==========================================
    print("--- 2. random Modülü ---")

    sinif_listesi = [
        "Ahmet",
        "Mehmet",
        "Ali",
        "Ayşe",
        "Fatma",
        "Zeynep",
        "Yusuf",
        "Ömer",
    ]

    # Rastgele bir öğrenci seçimi (sözlü sırası)
    secilen_ogrenci = random.choice(sinif_listesi)
    print(f"Sözlüye kalkacak öğrenci (choice): {secilen_ogrenci}")

    # Listeyi karıştırıp iki eşit gruba ayırma (grup kurası)
    karisik_liste = sinif_listesi.copy()
    random.shuffle(karisik_liste)

    orta_nokta = len(karisik_liste) // 2
    grup_bir = karisik_liste[:orta_nokta]
    grup_iki = karisik_liste[orta_nokta:]

    print(f"1. Çalışma Grubu: {grup_bir}")
    print(f"2. Çalışma Grubu: {grup_iki}\n")


def tarih_zaman_bolumu() -> None:
    """datetime modülü ile tarih işlemlerini ve gün farkını gösterir."""
    # ==========================================
    # 3. BÖLÜM: datetime MODÜLÜ
    # ==========================================
    print("--- 3. datetime Modülü ---")

    # Bugünün tarihi
    bugun = datetime.date.today()
    print(f"Bugünün tarihi: {bugun}")

    # Tarihi gün.ay.yıl biçiminde yazdırma
    bicimli_tarih = bugun.strftime("%d.%m.%Y")
    print(f"Biçimlendirilmiş tarih (gün.ay.yıl): {bicimli_tarih}")

    # Belirli bir tarihe kaç gün kaldığı
    hedef_tarih = datetime.date(bugun.year, 12, 31)
    kalan_zaman = hedef_tarih - bugun
    print(
        f"{hedef_tarih.strftime('%d.%m.%Y')} tarihine kalan gün sayısı: "
        f"{kalan_zaman.days} gün\n"
    )


def birlesik_ezber_ornegi() -> None:
    """math ve datetime kullanarak ezber bitiş tarihini hesaplar."""
    # ==========================================
    # 4. BÖLÜM: BİRLEŞİK ÖRNEK (EZBER TAKİBİ)
    # ==========================================
    print("--- 4. Birleşik Örnek: Ezber Takibi ---")

    toplam_sayfa = 604
    gunluk_ezber_sayfasi = 20

    # Toplam kaç gün süreceği (yukarı yuvarlama gerektirir)
    toplam_gun = math.ceil(toplam_sayfa / gunluk_ezber_sayfasi)

    # Başlangıç ve bitiş tarihi hesabı
    baslangic_tarihi = datetime.date.today()
    bitis_tarihi = baslangic_tarihi + datetime.timedelta(days=toplam_gun)

    print(f"Toplam sayfa: {toplam_sayfa}")
    print(f"Günlük ezber hedefi: {gunluk_ezber_sayfasi} sayfa")
    print(f"Ezberin tamamlanacağı gün sayısı: {toplam_gun} gün")
    print(f"Başlangıç tarihi: {baslangic_tarihi.strftime('%d.%m.%Y')}")
    print(f"Tahmini bitiş tarihi: {bitis_tarihi.strftime('%d.%m.%Y')}\n")


def ana_fonksiyon() -> None:
    """Tüm modül bölümlerini sırasıyla çalıştıran ana fonksiyon."""
    matematik_bolumu()
    rastgelelik_bolumu()
    tarih_zaman_bolumu()
    birlesik_ezber_ornegi()


if __name__ == "__main__":
    ana_fonksiyon()
