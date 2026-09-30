"""Dosya İşlemleri Örnek Programı.

Bu program; bir metin dosyası oluşturmayı, dosyayı 'read', 'readlines'
ve 'readline' yöntemleriyle farklı şekillerde okumayı gösterir.
"""


def dosya_olustur(dosya_yolu):
    """Belirtilen ada sahip dosyayı üç satırlık örnek veriyle oluşturur."""
    metin = (
        "1. Kütüphane Kitap Listesi\n"
        "2. Sınıf Nöbet Çizelgesi\n"
        "3. Kermes Görev Dağılımı\n"
    )
    with open(dosya_yolu, "w", encoding="utf-8") as dosya:
        dosya.write(metin)
    print(f"'{dosya_yolu}' dosyası başarıyla oluşturuldu.\n")


def tumunu_oku(dosya_yolu):
    """Dosyanın tüm içeriğini read() ile okuyup tırnak içinde yazdırır."""
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as dosya:
            icerik = dosya.read()
            print("--- 2) read() ile Okuma ---")
            print(f'"{icerik}"')
    except FileNotFoundError:
        print(f"Hata: '{dosya_yolu}' dosyası bulunamadı.")


def satirlari_liste_olarak_oku(dosya_yolu):
    """Dosyayı readlines() ile okuyup liste biçiminde ekrana yazdırır."""
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as dosya:
            satirlar = dosya.readlines()
            print("--- 3) readlines() ile Okuma ---")
            print(satirlar)
            print()
    except FileNotFoundError:
        print(f"Hata: '{dosya_yolu}' dosyası bulunamadı.")


def satir_satir_oku(dosya_yolu):
    """Dosyayı readline() ve while döngüsü kullanarak satır satır okur."""
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as dosya:
            print("--- 4) readline() ile Satır Satır Okuma ---")
            sayac = 1
            while True:
                satir = dosya.readline()
                if not satir:  # Dosya sonu (EOF) kontrolü
                    break
                print(f"Satır {sayac}: {satir.strip()}")
                sayac += 1
            print()
    except FileNotFoundError:
        print(f"Hata: '{dosya_yolu}' dosyası bulunamadı.")


def ana_program():
    """Tüm dosya işlemlerini sırayla çalıştıran ana fonksiyon."""
    dosya_adi = "metin.txt"

    # 1) Dosya oluşturma ve yazma
    dosya_olustur(dosya_adi)

    # 2) read() ile okuma
    tumunu_oku(dosya_adi)

    # 3) readlines() ile liste olarak okuma
    satirlari_liste_olarak_oku(dosya_adi)

    # 4) readline() ile döngüde satır satır okuma
    satir_satir_oku(dosya_adi)


if __name__ == "__main__":
    ana_program()
