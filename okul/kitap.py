"""Okul kütüphanesi kitap takip modülü."""


def gecikme_ucreti(gun):
    """Kütüphaneden alınan kitabın gecikme ücretini hesaplar.

    Gün başına 2 TL gecikme bedeli uygulanır.

    Argümanlar:
        gun (int): Geciken gün sayısı.

    Döndürür:
        int: Toplam gecikme ücreti (TL).
    """
    if not isinstance(gun, int):
        raise TypeError("Gün sayısı tam sayı olmalıdır.")
    if gun < 0:
        raise ValueError("Gün sayısı sıfırdan küçük olamaz.")

    gunluk_ucret = 2
    return gun * gunluk_ucret


def uzatilabilir_mi(uzatma_sayisi):
    """Kitap teslim süresinin uzatılıp uzatılamayacağını kontrol eder.

    Uzatma hakkı en fazla 2 defadır (2'den az ise uzatılabilir).

    Argümanlar:
        uzatma_sayisi (int): Kitabın daha önce kaç kez uzatıldığı.

    Döndürür:
        bool: Uzatma sayısı 2'den az ise True, aksi halde False.
    """
    if not isinstance(uzatma_sayisi, int):
        raise TypeError("Uzatma sayısı tam sayı olmalıdır.")
    if uzatma_sayisi < 0:
        raise ValueError("Uzatma sayısı negatif olamaz.")

    return uzatma_sayisi < 2
