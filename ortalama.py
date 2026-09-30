def ortalama_hesapla(sayi_listesi):
    """Verilen bir sayı listesinin aritmetik ortalamasını hesaplar."""
    if not isinstance(sayi_listesi, list):
        raise TypeError("Girdi bir liste olmalıdır.")

    if len(sayi_listesi) == 0:
        raise ValueError("Liste boş olamaz.")

    for eleman in sayi_listesi:
        if not isinstance(eleman, (int, float)):
            raise TypeError("Listedeki tüm elemanlar sayı olmalıdır.")

    toplam = sum(sayi_listesi)
    eleman_sayisi = len(sayi_listesi)
    return toplam / eleman_sayisi


# Örnek kullanım: Okul sınav notları
sinav_notlari = [85, 90, 78, 92, 100]

try:
    not_ortalamasi = ortalama_hesapla(sinav_notlari)
    print(f"Sınav Notları: {sinav_notlari}")
    print(f"Not Ortalaması: {not_ortalamasi:.2f}")
except (TypeError, ValueError) as hata:
    print(f"Hata oluştu: {hata}")
