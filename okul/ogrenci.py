"""Öğrenci başarı ve not işlemleri modülü."""


def ortalama(notlar):
    """Verilen not listesinin aritmetik ortalamasını hesaplar.

    Argümanlar:
        notlar (list): Öğrencinin aldığı puanların listesi.

    Döndürür:
        float: Notların aritmetik ortalaması.
    """
    if not isinstance(notlar, list):
        raise TypeError("Notlar bir liste olmalıdır.")
    if not notlar:
        return 0.0

    for not_bilgisi in notlar:
        if not isinstance(not_bilgisi, (int, float)):
            raise TypeError("Not değerleri sayısal olmalıdır.")
        if not_bilgisi < 0 or not_bilgisi > 100:
            raise ValueError("Notlar 0 ile 100 arasında olmalıdır.")

    toplam = sum(notlar)
    return toplam / len(notlar)


def gecti_mi(ortalama_puani):
    """Öğrencinin ortalamaya göre geçip geçmediğini belirler.

    Argümanlar:
        ortalama_puani (float/int): Öğrencinin dönem sonu not ortalaması.

    Döndürür:
        bool: Ortalama 50 veya üzerindeyse True, aksi halde False.
    """
    if not isinstance(ortalama_puani, (int, float)):
        raise TypeError("Ortalama puanı sayısal olmalıdır.")
    if ortalama_puani < 0 or ortalama_puani > 100:
        raise ValueError("Ortalama 0 ile 100 arasında olmalıdır.")

    return ortalama_puani >= 50
