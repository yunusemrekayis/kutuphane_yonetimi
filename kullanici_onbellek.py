import json
import os
import requests
from requests.exceptions import RequestException


def kullanici_verilerini_getir():
    """'users.json' dosyası varsa dosyadan okur; yoksa API'den çekip

    dosyaya kaydeder ve kullanıcı listesini döndürür.
    """
    dosya_adi = "users.json"
    adres = "https://jsonplaceholder.typicode.com/users"

    # 1. Adım: Dosyanın bilgisayarda olup olmadığını kontrol ediyoruz
    if os.path.exists(dosya_adi):
        print(f"'{dosya_adi}' dosyası bulundu, yerel dosyadan okunuyor...")
        with open(dosya_adi, mode="r", encoding="utf-8") as dosya:
            kullanicilar = json.load(dosya)
        return kullanicilar

    # 2. Adım: Dosya yoksa API'den verileri çekiyoruz
    print(f"'{dosya_adi}' bulunamadı, API üzerinden çekiliyor...")
    try:
        cevap = requests.get(adres, timeout=10)
        cevap.raise_for_status()
        kullanicilar = cevap.json()

        # 3. Adım: Çekilen veriyi yerel JSON dosyasına kaydediyoruz
        with open(dosya_adi, mode="w", encoding="utf-8") as dosya:
            json.dump(kullanicilar, dosya, ensure_ascii=False, indent=4)

        print(
            f"Veriler çekildi ve '{dosya_adi}' dosyasına kaydedildi."
        )
        return kullanicilar

    except RequestException as hata:
        print(f"API bağlantı hatası oluştu: {hata}")
        return []


if __name__ == "__main__":
    kullanici_listesi = kullanici_verilerini_getir()
    print(f"Toplam {len(kullanici_listesi)} kullanıcı yüklendi.")
