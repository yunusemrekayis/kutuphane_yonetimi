"""API isteklerinde hata yönetimi ve yeniden deneme mantığı modülü."""

import os
import time
from typing import Any, Dict, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")

# API Anahtarının varlığını kontrol et
if not API_KEY:
    raise ValueError("API_KEY .env dosyasında tanımlı değil!")


def hava_bilgisi_cek(
    sehir: str, max_deneme: int = 3
) -> Optional[Dict[str, Any]]:
    """API'den hava durumunu çeker, hata durumunda tekrar dener."""
    if not isinstance(sehir, str) or not sehir.strip():
        print("Hata: Geçersiz şehir adı girildi.")
        return None

    if not isinstance(max_deneme, int) or max_deneme < 1:
        print("Hata: Maksimum deneme sayısı pozitif tam sayı olmalıdır.")
        return None

    parametreler = {
        "q": sehir.strip(),
        "appid": API_KEY,
        "units": "metric",
        "lang": "tr",
    }
    denemeler = 0

    while denemeler < max_deneme:
        try:
            print(f"[Deneme {denemeler + 1}] {sehir} için istek atılıyor...")
            yanit = requests.get(API_URL, params=parametreler, timeout=5)

            # 429: Hızlı istek / Kota aşımı (Rate limit)
            if yanit.status_code == 429:
                bekleme_suresi = int(yanit.headers.get("Retry-After", 60))
                print(
                    f"[UYARI] Rate limit aşıldı! "
                    f"{bekleme_suresi} sn bekleniyor..."
                )
                time.sleep(bekleme_suresi)
                denemeler += 1
                continue

            # Diğer HTTP durum hataları
            if yanit.status_code != 200:
                print(f"[HATA] Durum Kodu: {yanit.status_code}")
                print(f"       Mesaj: {yanit.text}")
                return None

            # Başarılı yanıt
            print("[BASARILI] Yanıt alındı (HTTP 200)")
            return yanit.json()

        except requests.exceptions.Timeout:
            print("[ZAMAN ASIMI] Sunucu belirlenen sürede yanıt vermedi.")
            denemeler += 1
            if denemeler < max_deneme:
                print("              5 saniye sonra tekrar deneniyor...")
                time.sleep(5)

        except requests.exceptions.ConnectionError:
            print("[BAGLANTI HATASI] İnternet bağlantınızı kontrol edin.")
            return None

        except requests.exceptions.RequestException as hata:
            print(f"[API HATASI] İstek başarısız oldu: {hata}")
            return None

    print(f"[HATA] {max_deneme} deneme başarısız oldu. Sonra tekrar deneyin.")
    return None


if __name__ == "__main__":
    aranan_sehir = "Istanbul"
    hava_verisi = hava_bilgisi_cek(aranan_sehir)

    if hava_verisi:
        print("\n=== Hava Bilgisi ===")
        print(f"Şehir: {hava_verisi.get('name')}")
        sicaklik = hava_verisi.get("main", {}).get("temp")
        durum = hava_verisi.get("weather", [{}])[0].get("description")
        print(f"Sıcaklık: {sicaklik}°C")
        print(f"Durum: {durum}")
