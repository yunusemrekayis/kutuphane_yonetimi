import json


def kullanicilari_goster():
    """'users.json' dosyasını okuma modunda açar ve kullanıcıları listeler.

    """
    try:
        # Dosyayı okuma modunda ("r") ve Türkçe karakter desteğiyle açıyoruz
        with open("users.json", mode="r", encoding="utf-8") as dosya:
            # json.load() dosyayı okuyup Python liste/sözlük yapısına çevirir
            kullanicilar = json.load(dosya)

            # Her bir kullanıcının bilgilerini ekrana yazdırıyoruz
            for kullanici in kullanicilar:
                ad = kullanici.get("name", "Bilinmiyor")
                eposta = kullanici.get("email", "Bilinmiyor")
                sehir = (
                    kullanici.get("address", {}).get("city", "Bilinmiyor")
                )
                print(f"Ad: {ad} | E-posta: {eposta} | Şehir: {sehir}")

    except FileNotFoundError:
        print(
            "Hata: 'users.json' dosyası bulunamadı. Lütfen önce dosyayı oluşturun."
        )
    except json.JSONDecodeError:
        print("Hata: Dosya içeriği geçerli bir JSON formatında değil.")


if __name__ == "__main__":
    kullanicilari_goster()
