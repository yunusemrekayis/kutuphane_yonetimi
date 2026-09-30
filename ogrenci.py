"""Öğrenci değerlendirme modülü.

Bu modül öğrenci not ortalamasını hesaplar ve başarı
durumunu belirler.
"""


def not_ortalamasi(notlar: list[float]) -> float:
    """Verilen not listesinin aritmetik ortalamasını hesaplar.

    Args:
        notlar (list[float]): Öğrencinin aldığı notların listesi.

    Returns:
        float: Notların aritmetik ortalaması.

    Raises:
        ValueError: Not listesi boş olduğunda veya geçersiz not girildiğinde.
    """
    if not notlar:
        raise ValueError("Not listesi boş olamaz.")

    toplam = 0.0
    for puan in notlar:
        if not (0 <= puan <= 100):
            raise ValueError(f"Geçersiz not: {puan}. Not 0-100 arasında olmalı.")
        toplam += puan

    return toplam / len(notlar)


def durum(ortalama: float) -> str:
    """Öğrencinin ortalamasına göre başarı durumunu belirler.

    Ortalama 50 ve üzerinde ise 'Geçti', altında ise 'Kaldı'
    metnini döndürür.

    Args:
        ortalama (float): Öğrencinin dönem sonu not ortalaması.

    Returns:
        str: 'Geçti' veya 'Kaldı' bilgisi.

    Raises:
        ValueError: Ortalama 0 ile 100 arasında değilse.
    """
    if not (0 <= ortalama <= 100):
        raise ValueError("Ortalama 0 ile 100 arasında olmalıdır.")

    if ortalama >= 50:
        return "Geçti"
    return "Kaldı"
