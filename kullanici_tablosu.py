import requests


def duzlestir(kullanici):
    """Kullanici sozlügündeki ic ice (nested) alanlari duzlestirir.

    Eksik alanlar icin '-' varsayilan degerini dondurur.
    """
    adres = kullanici.get("address", {})
    sirket = kullanici.get("company", {})

    return {
        "id": kullanici.get("id", "-"),
        "ad": kullanici.get("name", "-"),
        "eposta": kullanici.get("email", "-"),
        "sehir": adres.get("city", "-"),
        "sirket_adi": sirket.get("name", "-"),
    }


def tablolari_yazdir():
    """API'den veriyi ceker, duzlestirir ve ilk 3 kaydi ekrana basar."""
    url = "https://jsonplaceholder.typicode.com/users"

    try:
        yanit = requests.get(url, timeout=5)
        yanit.raise_for_status()
        ham_kullanicilar = yanit.json()

        # List comprehension ile tum kullanicilari duzlestiriyoruz
        duz_kullanicilar = [duzlestir(k) for k in ham_kullanicilar]

        # Tablo basligi
        baslik = (
            f"{'ID':<4} | {'Ad':<22} | {'E-posta':<25} | "
            f"{'Şehir':<16} | {'Şirket Adı':<20}"
        )
        print(baslik)
        print("-" * len(baslik))

        # Ilk 3 satiri guzel formatta yazdiriyoruz
        for k in duz_kullanicilar[:3]:
            satir = (
                f"{str(k['id']):<4} | {k['ad']:<22} | {k['eposta']:<25} | "
                f"{k['sehir']:<16} | {k['sirket_adi']:<20}"
            )
            print(satir)

    except requests.exceptions.RequestException as hata:
        print(f"Ağ veya istek hatası oluştu: {hata}")


if __name__ == "__main__":
    tablolari_yazdir()
