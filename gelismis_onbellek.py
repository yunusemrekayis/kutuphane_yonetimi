import json
import os
import time
import requests
from requests.exceptions import RequestException

ONBELLEK_SURESI = 3600  # Saniye cinsinden önbellek süresi (1 saat)


def onbellekli_cek(url, dosya_adi):
    """Belirtilen adresten veriyi önbellek kontrolü yaparak getirir.

    Dosya taze ise dosyadan okur, eskiyse veya yoksa API'den çeker.
    API hatası durumunda varsa eski dosyayı yedek (fallback) olarak kullanır.
    """
    dosya_var_mi = os.path.exists(dosya_adi)

    # 1. Adım: Dosya var mı ve taze mi kontrol ediyoruz
    if dosya_var_mi:
        dosya_zamani = os.path.getmtime(dosya_adi)
        su_an = time.time()
        yas = su_an - dosya_zamani

        # Dosya 1 saatten daha yeniyse dosyadan oku
        if yas < ONBELLEK_SURESI:
            print(
                f"Dosyadan okundu (Önbellek taze: {int(yas)} saniye önce)."
            )
            with open(dosya_adi, mode="r", encoding="utf-8") as dosya:
                return json.load(dosya)

        print(
            f"Önbellek süresi dolmuş ({int(yas)} saniye eski). "
            "API'den güncelleniyor..."
        )

    # 2. Adım: Dosya yoksa veya eskiyse API'den çekiyoruz
    try:
        cevap = requests.get(url, timeout=10)
        cevap.raise_for_status()
        veri = cevap.json()

        # Yeni veriyi dosyaya yazarak önbelleği güncelliyoruz
        with open(dosya_adi, mode="w", encoding="utf-8") as dosya:
            json.dump(veri, dosya, ensure_ascii=False, indent=4)

        print("API'den çekildi ve önbellek dosyası güncellendi.")
        return veri

    except RequestException as hata:
        print(f"API hatası meydana geldi: {hata}")

        # 3. Adım: API başarısızsa ve eski dosya varsa onu kullan (Fallback)
        if dosya_var_mi:
            print(
                "Yedek plan: Eski önbellek dosyasından veriler yükleniyor."
            )
            with open(dosya_adi, mode="r", encoding="utf-8") as dosya:
                return json.load(dosya)

        print("Dosya bulunamadı ve API'ye erişilemedi.")
        return []


if __name__ == "__main__":
    adres = "https://jsonplaceholder.typicode.com/users"
    dosya = "users.json"

    kullanicilar = onbellekli_cek(adres, dosya)
    print(f"Yüklenen toplam kayıt sayısı: {len(kullanicilar)}")
