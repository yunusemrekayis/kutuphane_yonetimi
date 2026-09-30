def ilerleme_yuzdesi(okunan_sayfa: int) -> float:
    """
    Öğrencinin okuduğu sayfa sayısına göre hatim tamamlama yüzdesini hesaplar.

    Parametreler:
        okunan_sayfa (int): Öğrencinin şimdiye kadar okuduğu sayfa sayısı (0 - 604).

    Döndürür:
        float: Bir ondalık basamağa yuvarlanmış ilerleme yüzdesi (örn. 50.0).

    Hatalar:
        ValueError: Sayfa sayısı 0 ile 604 arasında değilse fırlatılır.
    """
    toplam_sayfa = 604
    if not (0 <= okunan_sayfa <= toplam_sayfa):
        raise ValueError(f"Geçersiz sayfa sayısı: {okunan_sayfa}. Sayfa sayısı 0 ile {toplam_sayfa} arasında olmalıdır.")

    yuzde = (okunan_sayfa / toplam_sayfa) * 100
    return round(yuzde, 1)


if __name__ == "__main__":
    # Testler / Kabul Kriterleri
    print(ilerleme_yuzdesi(302))  # Beklenen: 50.0
    print(ilerleme_yuzdesi(0))    # Beklenen: 0.0
    print(ilerleme_yuzdesi(604))  # Beklenen: 100.0
