"""Dosya Açma Modları ve 'with' Bloğu Gösterimi.

Bu program; 'w' modunun içeriği sıfırlayıp yeniden yazmasını,
'a' modunun mevcut içeriğin sonuna ekleme yapmasını ve 'with'
bloğunun hata durumunda bile dosyayı güvenle kapatmasını gösterir.
"""


def dosya_icerigi_oku(dosya_yolu):
    """Belirtilen dosyanın mevcut içeriğini ekrana yazdırır."""
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as dosya:
            print("Dosya İçeriği:\n" + dosya.read().strip())
    except FileNotFoundError:
        print(f"Hata: '{dosya_yolu}' dosyası bulunamadı.")


def w_modu_goster(dosya_yolu):
    """'w' modunda dosyaya 3 kez yazar; her seferinde silindiğini gösterir."""
    print("=== 1) 'w' (Write - Yazma) Modu ===")
    icerikler = [
        "1. Yazım: Kermes görevlileri listesi hazırlandı.",
        "2. Yazım: Kütüphane temizlik ekibi belirlendi.",
        "3. Yazım: Sınıf hatim takibi listesi güncellendi.",
    ]

    for i, metin in enumerate(icerikler, 1):
        try:
            with open(dosya_yolu, "w", encoding="utf-8") as dosya:
                dosya.write(metin + "\n")
            print(f"--- 'w' moduyla {i}. kez yazıldı ---")
            dosya_icerigi_oku(dosya_yolu)
            print()
        except OSError as hata:
            print(f"Dosya yazma hatası oluştu: {hata}")


def a_modu_goster(dosya_yolu):
    """'a' modunda aynı dosyaya ekleme yapar; eski yazılar korunur."""
    print("=== 2) 'a' (Append - Ekleme) Modu ===")
    eklenecekler = [
        "Ek Satır 1: Ezber takibine yeni ayetler eklendi.",
        "Ek Satır 2: Kütüphaneye yeni bağış kitapları kaydedildi.",
    ]

    for metin in eklenecekler:
        try:
            with open(dosya_yolu, "a", encoding="utf-8") as dosya:
                dosya.write(metin + "\n")
            print(f"-> Eklendi: '{metin}'")
        except OSError as hata:
            print(f"Dosya ekleme hatası oluştu: {hata}")

    print("\n'a' Modu Sonrası Güncel Dosya:")
    dosya_icerigi_oku(dosya_yolu)
    print()


def with_avantaji_goster(dosya_yolu):
    """'with' bloğunun hata anında bile dosyayı kapattığını gösterir."""
    print("=== 3) 'with' Bloğunun Avantajı (Hata Durumu) ===")
    dosya_nesnesi = None

    try:
        with open(dosya_yolu, "a", encoding="utf-8") as dosya:
            dosya_nesnesi = dosya
            print("Dosya açıldı. Kapalı mı?:", dosya.closed)
            dosya.write("Yeni nöbet çizelgesi satırı.\n")
            print("Bilinçli olarak sıfıra bölme hatası üretiliyor...")
            _ = 10 / 0  # Hata fırlatılıyor
    except ZeroDivisionError as hata:
        print(f"Hata başarıyla yakalandı: {hata}")
    except OSError as hata:
        print(f"Dosya hatası yakalandı: {hata}")

    if dosya_nesnesi:
        print("Hata sonrası dosya kapalı mı?:", dosya_nesnesi.closed)
        print("'with' bloğu hata oluşsa dahi dosyayı otomatik kapattı.")


def ana_program():
    """Tüm gösterimleri sırayla çalıştıran ana fonksiyon."""
    dosya_adi = "mod_ornek.txt"
    w_modu_goster(dosya_adi)
    a_modu_goster(dosya_adi)
    with_avantaji_goster(dosya_adi)


if __name__ == "__main__":
    ana_program()
