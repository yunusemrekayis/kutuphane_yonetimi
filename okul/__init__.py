"""Okul paketi ana başlatma dosyası.

Öğrenci ve kitap modüllerindeki temel fonksiyonları dışa aktarır.
"""

from .ogrenci import ortalama, gecti_mi
from .kitap import gecikme_ucreti, uzatilabilir_mi

__all__ = [
    "ortalama",
    "gecti_mi",
    "gecikme_ucreti",
    "uzatilabilir_mi",
]
