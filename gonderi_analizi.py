import requests


def gonderi_analizi_yap():
    """Gonderileri API'den ceker, en uzun basligi bulur ve
    kullanici basina gonderi sayilarini hesaplar.
    """
    url = "https://jsonplaceholder.typicode.com/posts"

    try:
        yanit = requests.get(url, timeout=5)
        yanit.raise_for_status()
        gonderiler = yanit.json()

        # 1. En uzun basliga sahip gonderiyi lambda ve max() ile bulma
        en_uzun_gonderi = max(
            gonderiler, key=lambda g: len(g.get("title", ""))
        )
        baslik = en_uzun_gonderi.get("title", "")
        print("--- EN UZUN BAŞLIKLI GÖNDERİ ---")
        print(f"Karakter Sayısı : {len(baslik)}")
        print(f"Kullanıcı ID    : {en_uzun_gonderi.get('userId', '-')}")
        print(f"Gönderi ID      : {en_uzun_gonderi.get('id', '-')}")
        print(f"Başlık          : {baslik}\n")

        # 2. userId basina gonderi sayisini sozlük ile hesaplama
        kullanici_gonderi_sayilari = {}
        for gonderi in gonderiler:
            kullanici_id = gonderi.get("userId")
            if kullanici_id is not None:
                # get() ile mevcut degeri alip 1 ekliyoruz
                mevcut_sayi = kullanici_gonderi_sayilari.get(kullanici_id, 0)
                kullanici_gonderi_sayilari[kullanici_id] = mevcut_sayi + 1

        print("--- KULLANICI BAŞINA GÖNDERİ SAYILARI ---")
        for k_id, sayi in kullanici_gonderi_sayilari.items():
            print(f"Kullanıcı {k_id}: {sayi} gönderi")

        # En cok gonderi yapan kullaniciyi bulma
        en_cok_yapan_id = max(
            kullanici_gonderi_sayilari,
            key=lambda k: kullanici_gonderi_sayilari[k],
        )
        en_cok_sayi = kullanici_gonderi_sayilari[en_cok_yapan_id]
        print(
            f"\nEn çok gönderi yapan: Kullanıcı {en_cok_yapan_id} "
            f"({en_cok_sayi} gönderi)"
        )

    except requests.exceptions.RequestException as hata:
        print(f"Ağ veya istek hatası oluştu: {hata}")


if __name__ == "__main__":
    gonderi_analizi_yap()
