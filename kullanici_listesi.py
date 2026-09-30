import requests


def kullanicilari_yazdir():
    """Kullanici verilerini API'den ceker ve kimlik, isim, sehir
    bilgilerini ekrana yazdirir.
    """
    url = "https://jsonplaceholder.typicode.com/users"

    try:
        yanit = requests.get(url, timeout=5)
        yanit.raise_for_status()
        kullanici_listesi = yanit.json()

        for kullanici in kullanici_listesi:
            kullanici_id = kullanici.get("id", "-")
            ad = kullanici.get("name", "-")

            # address anahtari yoksa hata almamak icin bos sozluk donduruyoruz
            adres = kullanici.get("address", {})

            # city anahtari yoksa "-" donduruyoruz
            sehir = adres.get("city", "-")

            print(f"ID: {kullanici_id} | Ad: {ad} | Şehir: {sehir}")

    except requests.exceptions.RequestException as hata:
        print(f"Ağ veya istek hatası oluştu: {hata}")


if __name__ == "__main__":
    kullanicilari_yazdir()
