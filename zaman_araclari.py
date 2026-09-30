"""Zaman ve gün işlemlerini yöneten yardımcı modül."""

GUNLER = [
    "Pazartesi",
    "Salı",
    "Çarşamba",
    "Perşembe",
    "Cuma",
    "Cumartesi",
    "Pazar"
]


def gun_adi(numara):
    """Verilen gün numarasının (0-6) gün adını döndürür."""
    if not isinstance(numara, int):
        raise TypeError("Gün numarası tam sayı olmalıdır.")
    if numara < 0 or numara > 6:
        raise ValueError("Gün numarası 0 ile 6 arasında olmalıdır.")
    return GUNLER[numara]


def hafta_sonu_mu(numara):
    """Verilen gün numarasının hafta sonu olup olmadığını döndürür."""
    if not isinstance(numara, int):
        raise TypeError("Gün numarası tam sayı olmalıdır.")
    if numara < 0 or numara > 6:
        raise ValueError("Gün numarası 0 ile 6 arasında olmalıdır.")
    return numara in (5, 6)
