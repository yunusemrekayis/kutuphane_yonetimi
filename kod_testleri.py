"""Yazilan fonksiyonlar ve islemler icin dogrulama ve test betigi."""


def duzlestir(kullanici):
    """Kullanici sozlügündeki ic ice (nested) alanlari duzlestirir."""
    adres = kullanici.get("address", {})
    sirket = kullanici.get("company", {})

    return {
        "id": kullanici.get("id", "-"),
        "ad": kullanici.get("name", "-"),
        "eposta": kullanici.get("email", "-"),
        "sehir": adres.get("city", "-"),
        "sirket_adi": sirket.get("name", "-"),
    }


def testleri_calistir():
    """Tum test maddelerini sirasiyla kontrol eder ve sonuclari basar."""
    print("=== TESTLER BASLATILIYOR ===\n")

    # Test 1: duzlestir({}) bos sozlukle ne donduruyor?
    sonuc_1 = duzlestir({})
    durum_1 = isinstance(sonuc_1, dict) and sonuc_1["ad"] == "-"
    print(
        f"Test 1 - Bos sozluk testi: {'BASARILI [OK]' if durum_1 else 'BASARISIZ [X]'}"
    )

    # Test 2: .get() eksik alanda default degeri veriyor mu?
    ornek_kullanici = {"id": 1}
    sonuc_2 = ornek_kullanici.get("adres", "-")
    durum_2 = sonuc_2 == "-"
    print(
        f"Test 2 - .get() guvenli varsayilan testi: "
        f"{'BASARILI [OK]' if durum_2 else 'BASARISIZ [X]'}"
    )

    # Test 3: List comprehension 2 elemanli listede calisiyor mu?
    sahte_liste = [{"id": 1, "name": "Ahmet"}, {"id": 2, "name": "Mehmet"}]
    sonuc_3 = [duzlestir(k) for k in sahte_liste]
    durum_3 = len(sonuc_3) == 2 and sonuc_3[0]["ad"] == "Ahmet"
    print(
        f"Test 3 - List comprehension testi: "
        f"{'BASARILI [OK]' if durum_3 else 'BASARISIZ [X]'}"
    )

    # Test 4: Lambda baslik uzunlugunu dogru hesapliyor mu?
    baslik_olcer = lambda g: len(g.get("title", ""))
    durum_4 = baslik_olcer({"title": "Kitap Listesi"}) == 13
    print(
        f"Test 4 - Lambda baslik uzunlugu testi: "
        f"{'BASARILI [OK]' if durum_4 else 'BASARISIZ [X]'}"
    )

    # Test 5: max() dogru sonucu seciyor mu?
    ornek_gonderiler = [
        {"id": 1, "title": "Kisa"},
        {"id": 2, "title": "En Uzun Baslik Burada"},
        {"id": 3, "title": "Orta Baslik"},
    ]
    en_uzun = max(ornek_gonderiler, key=lambda g: len(g.get("title", "")))
    durum_5 = en_uzun["id"] == 2
    print(
        f"Test 5 - max() ile en uzunu bulma testi: "
        f"{'BASARILI [OK]' if durum_5 else 'BASARISIZ [X]'}"
    )

    # Test 6: Sozluk ile sayma islemi dogru calisiyor mu?
    sayilar = {}
    gelen_idler = [1, 2, 1, 1, 3]
    for k_id in gelen_idler:
        sayilar[k_id] = sayilar.get(k_id, 0) + 1
    durum_6 = sayilar[1] == 3 and sayilar[2] == 1 and sayilar[3] == 1
    print(
        f"Test 6 - Sozluk frekans sayma testi: "
        f"{'BASARILI [OK]' if durum_6 else 'BASARISIZ [X]'}"
    )

    print("\n=== POTANSIYEL HATA KONTROLLERI ===")

    # Hata Kontrolü 1: Liste boş gelirse (TypeError onlenmesi)
    bos_liste = []
    if len(bos_liste) > 0:
        _ = max(bos_liste, key=lambda g: len(g.get("title", "")))
    else:
        print("Kontrol 1 - Bos liste kontrolu: Basariyla engellendi [OK]")

    # Hata Kontrolü 2: "title" anahtari yoksa (KeyError onlenmesi)
    eksik_anahtarli_gonderiler = [{"id": 1}, {"id": 2, "title": "Deneme"}]
    try:
        # g.get("title", "") sayesinde KeyError olusmaz
        en_uzun_guvenli = max(
            eksik_anahtarli_gonderiler, key=lambda g: len(g.get("title", ""))
        )
        print("Kontrol 2 - Eksik 'title' anahtari kontrolu: Basarili [OK]")
    except KeyError as hata:
        print(f"Kontrol 2 - Hata yakalandi: {hata} [X]")


if __name__ == "__main__":
    testleri_calistir()
