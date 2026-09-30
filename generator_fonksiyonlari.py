"""Generator fonksiyonları örnekleri."""

import csv


def sayac(n):
    """1'den n'e kadar olan sayıları sırayla üreten generator.

    Doğrulama: n bir tam sayı olmalı ve 1'den küçük olmamalıdır.
    """
    if not isinstance(n, int):
        raise TypeError("Girilen değer bir tam sayı olmalıdır.")
    if n < 1:
        raise ValueError("Sayı 1 veya daha büyük olmalıdır.")

    for i in range(1, n + 1):
        yield i


def fibonacci(n):
    """Fibonacci serisinin ilk n elemanını sırayla üreten generator.

    Doğrulama: n bir tam sayı olmalı ve pozitif olmalıdır.
    """
    if not isinstance(n, int):
        raise TypeError("Adım sayısı bir tam sayı olmalıdır.")
    if n < 1:
        raise ValueError("Adım sayısı 1 veya daha büyük olmalıdır.")

    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


def dosya_oku(dosya_adi):
    """Belirtilen metin dosyasını satır satır okuyan generator.

    Dosya bulunamazsa FileNotFoundError hatası yakalanır ve bildirilir.
    """
    if not isinstance(dosya_adi, str) or not dosya_adi.strip():
        raise ValueError("Geçerli bir dosya adı girilmelidir.")

    try:
        with open(dosya_adi, "r", encoding="utf-8") as dosya:
            for satir in dosya:
                yield satir.rstrip("\n")
    except FileNotFoundError:
        print(f"Hata: '{dosya_adi}' dosyası bulunamadı.")


def nobet_sirasi(ogrenciler):
    """Öğrenci listesini nöbet sırası için sonsuza kadar döndüren generator.

    Doğrulama: ogrenciler boş olmayan bir liste/dizi olmalıdır.
    """
    if not ogrenciler:
        raise ValueError("Öğrenci listesi boş olamaz.")

    while True:
        for ogrenci in ogrenciler:
            yield ogrenci


def kayit_oku(dosya_adi):
    """CSV dosyasını satır satır sözlük (dict) olarak üreten generator.

    Dosya bulunamazsa FileNotFoundError hatası yakalanır ve bildirilir.
    """
    if not isinstance(dosya_adi, str) or not dosya_adi.strip():
        raise ValueError("Geçerli bir dosya adı girilmelidir.")

    try:
        with open(dosya_adi, "r", encoding="utf-8") as dosya:
            okuyucu = csv.DictReader(dosya)
            for satir in okuyucu:
                yield dict(satir)
    except FileNotFoundError:
        print(f"Hata: '{dosya_adi}' dosyası bulunamadı.")


if __name__ == "__main__":
    print("--- 1. Sayaç Örneği ---")
    for sayi in sayac(5):
        print(f"Sayı: {sayi}")

    print("\n--- 2. Fibonacci Örneği ---")
    for fib in fibonacci(7):
        print(f"Fibonacci: {fib}")

    print("\n--- 3. Dosya Okuma Örneği ---")
    # Mevcut metin.txt dosyasını okuyoruz
    for satir in dosya_oku("metin.txt"):
        print(f"Satır: {satir}")

    print("\n--- 4. Nöbet Sırası Örneği (İlk 6 nöbetçi) ---")
    sinif_listesi = ["Ahmet", "Mehmet", "Zeynep"]
    siradaki = nobet_sirasi(sinif_listesi)
    for gun in range(1, 7):
        print(f"Gün {gun} Nöbetçisi: {next(siradaki)}")

    print("\n--- 5. CSV Kayıt Okuma Örneği ---")
    # Mevcut students.csv dosyasını okuyoruz
    for kayit in kayit_oku("students.csv"):
        print(f"Kayıt: {kayit}")

    print("\n--- Hata Yakalama Testi (Bulunamayan Dosya) ---")
    list(dosya_oku("olmayan_dosya.txt"))
