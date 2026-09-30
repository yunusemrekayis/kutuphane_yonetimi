"""Mescit Kitaplığı Araç Kutusu.

Bu modül okul mescidindeki kitapların ödünç takibini,
gecikme gün hesaplamasını, ceza puanı takibini ve öğrenci limitlerini
yönetmek için gerekli fonksiyonları içerir.
"""

from datetime import date, timedelta

ODUNC_SURESI_GUN = 15
MAX_ODUNC_LIMITI = 3
GUNLUK_CEZA_PUANI = 1


def kutuphane_olustur() -> list[dict]:
    """Boş bir kütüphane kitap listesi oluşturur ve döndürür.

    Returns:
        list[dict]: Bellekte tutulacak boş kitap listesi.
    """
    return []


def kitap_ekle(kutuphane: list[dict], baslik: str, yazar: str) -> dict:
    """Kütüphaneye yeni bir kitap ekler.

    Args:
        kutuphane (list[dict]): Kütüphane kitap listesi.
        baslik (str): Kitabın adı/başlığı.
        yazar (str): Kitabın yazarı.

    Returns:
        dict: Eklenen kitaba ait sözlük verisi.
    """
    yeni_id = len(kutuphane) + 1
    kitap = {
        "id": yeni_id,
        "baslik": baslik,
        "yazar": yazar,
        "odunc_alan": None,
        "odunc_tarihi": None,
    }
    kutuphane.append(kitap)
    return kitap


def kisi_odunc_sayisi(kutuphane: list[dict], kisi_adi: str) -> int:
    """Belirtilen kişinin şu anda aktif olarak ödünç aldığı kitap sayısını hesaplar.

    Args:
        kutuphane (list[dict]): Kütüphane kitap listesi.
        kisi_adi (str): Kitap alan kişinin adı.

    Returns:
        int: Kişinin elindeki aktif ödünç kitap sayısı.
    """
    sayac = 0
    for kitap in kutuphane:
        if kitap["odunc_alan"] is not None and kitap["odunc_alan"].lower() == kisi_adi.lower():
            sayac += 1
    return sayac


def odunc_ver(
    kutuphane: list[dict], kitap_id: int, kisi_adi: str, odunc_tarihi: date | None = None
) -> tuple[bool, str]:
    """Kitabı belirtilen kişiye ödünç verir. Öğrencinin maksimum 3 kitap limitini kontrol eder.

    Args:
        kutuphane (list[dict]): Kütüphane kitap listesi.
        kitap_id (int): Ödünç verilecek kitabın kimlik numarası.
        kisi_adi (str): Ödünç alan kişinin adı.
        odunc_tarihi (date | None, optional): Ödünç verme tarihi. Belirtilmezse bugünün tarihi alınır.

    Returns:
        tuple[bool, str]: (İşlem başarılı mı, Açıklama mesajı)
    """
    kitap = next((k for k in kutuphane if k["id"] == kitap_id), None)
    if not kitap:
        return False, f"Hata: ID={kitap_id} olan kitap kutuphanede bulunamadi."

    if kitap["odunc_alan"] is not None:
        return (
            False,
            f"Hata: '{kitap['baslik']}' kitabi zaten {kitap['odunc_alan']} kisisine odunc verilmis.",
        )

    aktif_odunc_sayisi = kisi_odunc_sayisi(kutuphane, kisi_adi)
    if aktif_odunc_sayisi >= MAX_ODUNC_LIMITI:
        return (
            False,
            f"Hata: {kisi_adi} maksimum odunc alma limitine ({MAX_ODUNC_LIMITI} kitap) ulasmis.",
        )

    tarih = odunc_tarihi if odunc_tarihi is not None else date.today()
    kitap["odunc_alan"] = kisi_adi
    kitap["odunc_tarihi"] = tarih
    son_iade_tarihi = tarih + timedelta(days=ODUNC_SURESI_GUN)

    return (
        True,
        f"Basarili: '{kitap['baslik']}' kitabi {kisi_adi} kisisine odunc verildi. (Son iade tarihi: {son_iade_tarihi.strftime('%d.%m.%Y')})",
    )


def gecikme_ve_ceza_hesapla(kitap: dict, bugun: date | None = None) -> tuple[int, int]:
    """Kitabın ödünç süresini (15 gün) aşan gecikme gününü ve ceza puanını hesaplar.

    Args:
        kitap (dict): Hesaplama yapılacak kitap sözlüğü.
        bugun (date | None, optional): Hesaplama yapılacak hedef tarih. Varsayılan bugündür.

    Returns:
        tuple[int, int]: (Gecikilen gün sayısı, Toplam ceza puanı)
    """
    if kitap["odunc_tarihi"] is None:
        return 0, 0

    mevcut_tarih = bugun if bugun is not None else date.today()
    gecen_gun = (mevcut_tarih - kitap["odunc_tarihi"]).days
    gecikme_gun = gecen_gun - ODUNC_SURESI_GUN

    if gecikme_gun <= 0:
        return 0, 0

    ceza_puani = gecikme_gun * GUNLUK_CEZA_PUANI
    return gecikme_gun, ceza_puani


def iade_al(
    kutuphane: list[dict], kitap_id: int, iade_tarihi: date | None = None
) -> tuple[bool, str]:
    """Ödünç verilmiş kitabı kütüphaneye iade alır, gecikme ve ceza bilgisi sunar.

    Args:
        kutuphane (list[dict]): Kütüphane kitap listesi.
        kitap_id (int): İade alınacak kitabın kimlik numarası.
        iade_tarihi (date | None, optional): İade tarihi. Belirtilmezse bugünün tarihi alınır.

    Returns:
        tuple[bool, str]: (İşlem başarılı mı, İade durum ve ceza bilgisi mesajı)
    """
    kitap = next((k for k in kutuphane if k["id"] == kitap_id), None)
    if not kitap:
        return False, f"Hata: ID={kitap_id} olan kitap kutuphanede bulunamadi."

    if kitap["odunc_alan"] is None:
        return False, f"Hata: '{kitap['baslik']}' kitabi zaten rafta (odunc verilmemis)."

    mevcut_tarih = iade_tarihi if iade_tarihi is not None else date.today()
    gecikme_gun, ceza_puani = gecikme_ve_ceza_hesapla(kitap, bugun=mevcut_tarih)
    eski_odunc_alan = kitap["odunc_alan"]

    # Kitap durumunu sıfırla
    kitap["odunc_alan"] = None
    kitap["odunc_tarihi"] = None

    if gecikme_gun > 0:
        mesaj = (
            f"Iade Alindi (GECIKMELI): '{kitap['baslik']}' kitabi {eski_odunc_alan} kisisinden teslim alindi. "
            f"[Gecikme: {gecikme_gun} gun | Ceza Puani: {ceza_puani} puan]"
        )
    else:
        mesaj = f"Iade Alindi (ZAMANINDA): '{kitap['baslik']}' kitabi {eski_odunc_alan} kisisinden zamaninda teslim alindi."

    return True, mesaj


def kitaplari_listele(kutuphane: list[dict], sadece_odunc: bool = False) -> list[dict]:
    """Kütüphanedeki tüm veya sadece ödünçteki kitapların listesini filtreler.

    Args:
        kutuphane (list[dict]): Kütüphane kitap listesi.
        sadece_odunc (bool, optional): True ise sadece ödünç verilmiş kitapları getirir.

    Returns:
        list[dict]: Filtrelenmiş kitap listesi.
    """
    if sadece_odunc:
        return [k for k in kutuphane if k["odunc_alan"] is not None]
    return kutuphane
