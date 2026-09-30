"""Hesaplayıcı modülü.

Bu modül temel matematiksel işlemleri gerçekleştiren
fonksiyonları içerir.
"""


def topla(sayi_bir: float, sayi_iki: float) -> float:
    """İki sayıyı toplar ve sonucu döndürür.

    Args:
        sayi_bir (float): İlk sayı.
        sayi_iki (float): İkinci sayı.

    Returns:
        float: İki sayının toplamı.
    """
    return sayi_bir + sayi_iki


def cikar(sayi_bir: float, sayi_iki: float) -> float:
    """İlk sayıdan ikinci sayıyı çıkarır ve sonucu döndürür.

    Args:
        sayi_bir (float): Eksilen sayı.
        sayi_iki (float): Çıkan sayı.

    Returns:
        float: Çıkarma işleminin sonucu.
    """
    return sayi_bir - sayi_iki


def carp(sayi_bir: float, sayi_iki: float) -> float:
    """İki sayıyı çarpar ve sonucu döndürür.

    Args:
        sayi_bir (float): İlk sayı.
        sayi_iki (float): İkinci sayı.

    Returns:
        float: İki sayının çarpımı.
    """
    return sayi_bir * sayi_iki
