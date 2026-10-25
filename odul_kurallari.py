"""Pekiştirmeli Öğrenme - Ödül Kuralları ve Açgözlü Ajan Simülasyonu.

Bu modül; ortam, ajan ve ödül kurallarını birbirinden bağımsız
yapılar halinde modeller. Farklı ödül mekanizmalarının ve ajan
davranışlarının (rastgele ve açgözlü) sonuçlarını karşılaştırır.
"""

import random
import pygame

# ---------------------------------------------------------------------------
# ORTAM VE EKRAN AYARLARI
# ---------------------------------------------------------------------------
SATIR_SAYISI = 8
SUTUN_SAYISI = 8
HUCRE = 70
PANEL = 460
GENISLIK = SUTUN_SAYISI * HUCRE + PANEL  # 560 + 460 = 1020
YUKSEKLIK = SATIR_SAYISI * HUCRE         # 560

BASLANGIC = (0, 0)
SARJ_ISTASYONU = (7, 7)
DUVARLAR = {
    (1, 2), (2, 2), (3, 2),
    (5, 4), (5, 5), (5, 6),
    (2, 5), (3, 5),
}

GAMA = 0.9
MAKS_ADIM = 200

EYLEMLER = {
    0: ("YUKARI", -1, 0),
    1: ("AŞAĞI", 1, 0),
    2: ("SOL", 0, -1),
    3: ("SAĞ", 0, 1),
}

# Renkler
ARKA = (245, 247, 250)
CIZGI = (205, 210, 220)
DUVAR = (65, 72, 85)
MAVI = (45, 115, 240)
YESIL = (40, 175, 85)
TURUNCU = (235, 125, 40)
KIRMIZI = (215, 55, 55)
SOLUK = (185, 190, 200)
YAZI = (30, 35, 45)
BEYAZ = (255, 255, 255)
PANEL_RENK = (235, 240, 246)
KART_RENK = (255, 255, 255)
KART_KENAR = (215, 222, 232)


def manhattan_mesafe(konum1, konum2):
    """İki hücre arasındaki Manhattan mesafesini hesaplar."""
    return abs(konum1[0] - konum2[0]) + abs(konum1[1] - konum2[1])


# ---------------------------------------------------------------------------
# 1 VE 2: ÖDÜL KURALLARI
# ---------------------------------------------------------------------------
class OdulKurali:
    """Ödül hesaplaması için temel sınıf."""

    adi = "Temel Kural"

    def hesapla(self, eski_mesafe, yeni_mesafe, carpti, hedefte):
        """Ödül miktarını döndürür (Alt sınıflar uygular)."""
        raise NotImplementedError("Alt sınıf bu metodu uygulamalıdır.")


class Bolum1Kurali(OdulKurali):
    """Bölüm 1 Kuralı: Şarj +10, çarpma -1, gerisi 0."""

    adi = "Bölüm 1 Kuralı"

    def hesapla(self, eski_mesafe, yeni_mesafe, carpti, hedefte):
        """Hedefe ulaşınca +10, çarpınca -1, diğer durumlarda 0 verir."""
        if hedefte:
            return 10
        if carpti:
            return -1
        return 0


class SadeceHedef(OdulKurali):
    """Sadece Hedef Kuralı: Şarj +10, gerisi 0."""

    adi = "Sadece Hedef"

    def hesapla(self, eski_mesafe, yeni_mesafe, carpti, hedefte):
        """Yalnızca şarj istasyonuna ulaşınca +10 verir, gerisi 0."""
        if hedefte:
            return 10
        return 0


class AdimCezasi(OdulKurali):
    """Adım Cezası Kuralı: Şarj +10, her adım -1."""

    adi = "Adım Cezası"

    def hesapla(self, eski_mesafe, yeni_mesafe, carpti, hedefte):
        """Şarja +10 verir; geçen her adım için -1 ceza uygular."""
        if hedefte:
            return 10
        return -1


class YaklasmaOdulu(OdulKurali):
    """Yaklaşma Ödülü Kuralı: Şarj +10, yaklaşınca +1, değilse -1."""

    adi = "Yaklaşma Ödülü"

    def hesapla(self, eski_mesafe, yeni_mesafe, carpti, hedefte):
        """Hedefe yaklaşınca +1, uzaklaşınca/çarpınca -1, şarjda +10."""
        if hedefte:
            return 10
        if yeni_mesafe < eski_mesafe:
            return 1
        return -1


# ---------------------------------------------------------------------------
# 3: OYUN DÜNYASI (ORTAM)
# ---------------------------------------------------------------------------
class OyunDunyasi:
    """Robot süpürgenin hareket ettiği ızgara dünyası."""

    def __init__(self, odul_kurali=None):
        """Ortamı başlatır ve ödül kuralını belirler."""
        self.odul_kurali = odul_kurali if odul_kurali else Bolum1Kurali()
        self.robot = BASLANGIC
        self.adim = 0

    def kural_belirle(self, yeni_kural):
        """Ortamın ödül kuralını günceller."""
        self.odul_kurali = yeni_kural

    def sifirla(self):
        """Robotu başlangıca döndürür ve adımı sıfırlar."""
        self.robot = BASLANGIC
        self.adim = 0
        return self.robot

    def sonuc(self, konum, eylem):
        """Dünyayı değiştirmeden olası bir eylemin sonucunu simüle eder."""
        _, ds, dc = EYLEMLER[eylem]
        yeni = (konum[0] + ds, konum[1] + dc)

        sinir_ici = (0 <= yeni[0] < SATIR_SAYISI and
                     0 <= yeni[1] < SUTUN_SAYISI)
        carpti = (not sinir_ici) or (yeni in DUVARLAR)

        yeni_konum = konum if carpti else yeni
        hedefte = (yeni_konum == SARJ_ISTASYONU)

        eski_m = manhattan_mesafe(konum, SARJ_ISTASYONU)
        yeni_m = manhattan_mesafe(yeni_konum, SARJ_ISTASYONU)

        odul = self.odul_kurali.hesapla(eski_m, yeni_m, carpti, hedefte)
        return yeni_konum, odul, hedefte

    def adim_at(self, eylem):
        """Eylemi ortamda uygular ve yeni durumu döndürür."""
        yeni_konum, odul, hedefte = self.sonuc(self.robot, eylem)
        self.robot = yeni_konum
        self.adim += 1
        bitti = hedefte or (self.adim >= MAKS_ADIM)
        return self.robot, odul, bitti


# ---------------------------------------------------------------------------
# 4: AJANLAR
# ---------------------------------------------------------------------------
class RastgeleAjan:
    """Dört yönden birini rastgele seçen ajan."""

    adi = "Rastgele Ajan"

    def eylem_sec(self, durum, dunya=None):
        """Rastgele bir yön belirler."""
        return random.randint(0, 3)


class AcgozluAjan:
    """Her adımda en yüksek ödülü veren eylemi seçen açgözlü ajan."""

    adi = "Açgözlü Ajan"

    def __init__(self, dunya=None):
        """Ajanı bir dünya referansı ile başlatır."""
        self.dunya = dunya

    def eylem_sec(self, durum, dunya=None):
        """Dört eylemi dener; en yüksek ödüllüyü (eşitlikte kurayla) seçer."""
        aktif_dunya = dunya if dunya is not None else self.dunya
        if aktif_dunya is None:
            return random.randint(0, 3)

        adaylar = []
        for eylem in EYLEMLER:
            _, odul, _ = aktif_dunya.sonuc(durum, eylem)
            adaylar.append((odul, eylem))

        en_buyuk_odul = max(aday[0] for aday in adaylar)
        en_iyiler = [e for od, e in adaylar if od == en_buyuk_odul]
        return random.choice(en_iyiler)


# ---------------------------------------------------------------------------
# 5 VE 6: SİMÜLASYON YÖNETİCİSİ
# ---------------------------------------------------------------------------
class Simulasyon:
    """Simülasyon durumunu, skor tablosunu ve ajan döngüsünü yönetir."""

    def __init__(self):
        """Simülasyon bileşenlerini ve skor tablosunu başlatır."""
        self.kurallar = {
            1: Bolum1Kurali(),
            2: SadeceHedef(),
            3: AdimCezasi(),
            4: YaklasmaOdulu(),
        }
        self.aktif_kural_no = 1
        self.dunya = OyunDunyasi(self.kurallar[self.aktif_kural_no])
        self.ajan = RastgeleAjan()

        self.bolum_gecmisi = []
        self.bolum = 1
        self.durum = self.dunya.sifirla()
        self.bolum_adimi = 0
        self.toplam_odul = 0
        self.indirimli_toplam = 0.0
        self.son_odul = None
        self.secilen_eylem = None
        self.bitti = False

    def skor_tablosunu_sifirla(self):
        """Kural veya ajan değiştiğinde skor tablosunu ve bölümü sıfırlar."""
        self.bolum_gecmisi.clear()
        self.bolum = 1
        self.bolum_sifirla()

    def bolum_sifirla(self):
        """Mevcut bölüm değişkenlerini sıfırlayıp robotu başa alır."""
        self.durum = self.dunya.sifirla()
        self.bolum_adimi = 0
        self.toplam_odul = 0
        self.indirimli_toplam = 0.0
        self.son_odul = None
        self.secilen_eylem = None
        self.bitti = False

    def kural_sec(self, kural_no):
        """Ödül kuralını değiştirir ve skor tablosunu sıfırlar."""
        if kural_no in self.kurallar and kural_no != self.aktif_kural_no:
            self.aktif_kural_no = kural_no
            self.dunya.kural_belirle(self.kurallar[kural_no])
            self.skor_tablosunu_sifirla()

    def ajan_degistir(self):
        """Rastgele ve açgözlü ajan arasında geçiş yapar."""
        if isinstance(self.ajan, RastgeleAjan):
            self.ajan = AcgozluAjan(self.dunya)
        else:
            self.ajan = RastgeleAjan()
        self.skor_tablosunu_sifirla()

    def adim_yap(self):
        """Bir simülasyon adımı işletir ve skor tablosunu günceller."""
        if self.bitti:
            self.bolum += 1
            self.bolum_sifirla()

        self.secilen_eylem = self.ajan.eylem_sec(self.durum, self.dunya)
        yeni_konum, odul, bitti = self.dunya.adim_at(self.secilen_eylem)

        # İndirimli ödül hesabı: Gama ** adım_sayısı * ödül
        indirim = GAMA ** self.bolum_adimi
        self.indirimli_toplam += indirim * odul
        self.toplam_odul += odul
        self.son_odul = odul
        self.durum = yeni_konum
        self.bolum_adimi += 1
        self.bitti = bitti

        if self.bitti:
            kayit = {
                "bolum": self.bolum,
                "adim": self.dunya.adim,
                "sarj": (self.durum == SARJ_ISTASYONU),
                "toplam": self.toplam_odul,
                "indirimli": self.indirimli_toplam,
            }
            self.bolum_gecmisi.append(kayit)


# ---------------------------------------------------------------------------
# EKRAN ÇİZİM SINIFI
# ---------------------------------------------------------------------------
class Cizim:
    """Izgara dünyasını ve sağdaki skor/bilgi panelini çizer."""

    def __init__(self, pencere):
        """Yazı tiplerini ve ekran referansını tanımlar."""
        self.p = pencere
        self.f_kucuk = pygame.font.SysFont("consolas,couriernew", 13)
        self.f_normal = pygame.font.SysFont("segoeui,arial", 15)
        self.f_kalin = pygame.font.SysFont("segoeui,arial", 15, bold=True)
        self.f_baslik = pygame.font.SysFont("segoeui,arial", 17, bold=True)
        self.f_buyuk = pygame.font.SysFont("segoeui,arial", 32, bold=True)

    def yaz(self, metin, x, y, font=None, renk=YAZI):
        """Ekrana belirtilen yazı tipi ve renkle metin basar."""
        fnt = font or self.f_normal
        yazi = fnt.render(metin, True, renk)
        self.p.blit(yazi, (x, y))

    def hucre_rect(self, satir, sutun, pay=0):
        """Verilen satır ve sütuna denk gelen dikdörtgeni döndürür."""
        return pygame.Rect(
            sutun * HUCRE + pay,
            satir * HUCRE + pay,
            HUCRE - 2 * pay,
            HUCRE - 2 * pay,
        )

    def kart_ciz(self, rect, baslik=None):
        """Panelde modern görünümlü bir bilgi kartı çizer."""
        pygame.draw.rect(self.p, KART_RENK, rect, border_radius=8)
        pygame.draw.rect(self.p, KART_KENAR, rect, 1, border_radius=8)
        if baslik:
            self.yaz(baslik, rect.x + 12, rect.y + 8, self.f_kalin, TURUNCU)

    def ciz(self, sim, hiz_adi, duraklatildi):
        """Tüm sahneyi (ızgara ve panel) çizer ve tazeler."""
        self.p.fill(ARKA)
        self.izgara_ciz(sim)
        self.panel_ciz(sim, hiz_adi, duraklatildi)
        pygame.display.flip()

    def izgara_ciz(self, sim):
        """Izgara hücrelerini, duvarları, robotu ve hedefi çizer."""
        for s in range(SATIR_SAYISI):
            for c in range(SUTUN_SAYISI):
                kutu = self.hucre_rect(s, c)
                if (s, c) in DUVARLAR:
                    pygame.draw.rect(self.p, DUVAR, kutu)
                pygame.draw.rect(self.p, CIZGI, kutu, 1)

        # Şarj İstasyonu
        sarj = self.hucre_rect(*SARJ_ISTASYONU, 8)
        pygame.draw.rect(self.p, YESIL, sarj, border_radius=10)
        sx, sy, sg = sarj.x, sarj.y, sarj.width
        pygame.draw.polygon(self.p, (255, 230, 80), [
            (sx + sg * 0.55, sy + sg * 0.12),
            (sx + sg * 0.30, sy + sg * 0.55),
            (sx + sg * 0.50, sy + sg * 0.55),
            (sx + sg * 0.42, sy + sg * 0.88),
            (sx + sg * 0.72, sy + sg * 0.42),
            (sx + sg * 0.52, sy + sg * 0.42),
        ])

        # Robot
        robot = self.hucre_rect(*sim.durum, 10)
        pygame.draw.rect(self.p, MAVI, robot, border_radius=14)
        for goz_x in (robot.x + robot.width // 3,
                      robot.x + 2 * robot.width // 3):
            pygame.draw.circle(
                self.p, BEYAZ, (goz_x, robot.y + robot.height // 3), 5
            )

        # Seçilen Eylem Oku
        if sim.secilen_eylem is not None:
            _, ds, dc = EYLEMLER[sim.secilen_eylem]
            mx, my = robot.center
            hx, hy = mx + dc * HUCRE * 0.75, my + ds * HUCRE * 0.75
            pygame.draw.line(self.p, TURUNCU, (mx, my), (hx, hy), 5)
            pygame.draw.circle(self.p, TURUNCU, (int(hx), int(hy)), 7)

        # Son Ödül Balonu
        if sim.son_odul is not None:
            renk = YESIL if sim.son_odul > 0 else (
                KIRMIZI if sim.son_odul < 0 else SOLUK
            )
            balon_y = robot.y - 32 if robot.y > 35 else robot.bottom + 2
            self.yaz(f"{sim.son_odul:+d}", robot.x + 10, balon_y,
                     self.f_buyuk, renk)

    def panel_ciz(self, sim, hiz_adi, duraklatildi):
        """Sağ taraftaki bilgi, skor tablosu ve geçmiş panelini çizer."""
        px = SUTUN_SAYISI * HUCRE
        pygame.draw.rect(
            self.p, PANEL_RENK, pygame.Rect(px, 0, PANEL, YUKSEKLIK)
        )
        x = px + 15

        # Başlık
        self.yaz("PEKİŞTİRMELİ ÖĞRENME: ÖDÜL KURALLARI",
                 x, 10, self.f_baslik, YAZI)

        # Kart 1: Aktif Yapılandırma ve Anlık Durum
        k1 = pygame.Rect(x, 36, PANEL - 30, 116)
        self.kart_ciz(k1, "AKTİF AYARLAR VE ANLIK BÖLÜM")
        k_adi = f"{sim.aktif_kural_no}. {sim.dunya.odul_kurali.adi}"
        self.yaz(f"Kural [1-4] : {k_adi}", x + 12, 60, self.f_kalin, MAVI)
        self.yaz(f"Ajan  [A]   : {sim.ajan.adi}",
                 x + 12, 80, self.f_kalin, YAZI)

        son_o = f"{sim.son_odul:+d}" if sim.son_odul is not None else "-"
        self.yaz(f"Bölüm: {sim.bolum}   Adım: {sim.dunya.adim}/{MAKS_ADIM}   "
                 f"Son Ödül: {son_o}", x + 12, 103, self.f_normal, YAZI)
        self.yaz(f"Toplam Ödül: {sim.toplam_odul:+d}   "
                 f"İndirimli (γ=0.9): {sim.indirimli_toplam:+.2f}",
                 x + 12, 124, self.f_kalin, TURUNCU)

        # Kart 2: Skor Tablosu (Özet)
        k2 = pygame.Rect(x, 160, PANEL - 30, 94)
        self.kart_ciz(k2, "SKOR TABLOSU (ÖZET)")
        toplam_b = len(sim.bolum_gecmisi)
        basarili_b = sum(1 for k in sim.bolum_gecmisi if k["sarj"])
        oran = (basarili_b / toplam_b * 100) if toplam_b > 0 else 0.0
        ort_top = (sum(k["toplam"] for k in sim.bolum_gecmisi) /
                   toplam_b) if toplam_b > 0 else 0.0
        ort_ind = (sum(k["indirimli"] for k in sim.bolum_gecmisi) /
                   toplam_b) if toplam_b > 0 else 0.0

        self.yaz(f"Tamamlanan: {toplam_b}   |   Şarj Olan: {basarili_b} "
                 f"(%{oran:.1f})", x + 12, 186, self.f_normal, YAZI)
        self.yaz(f"Ort. Toplam Ödül    : {ort_top:+.2f}",
                 x + 12, 208, self.f_normal, YAZI)
        self.yaz(f"Ort. İndirimli Ödül : {ort_ind:+.2f}",
                 x + 12, 228, self.f_normal, YAZI)

        # Kart 3: Son 5 Bölüm Geçmişi
        k3 = pygame.Rect(x, 262, PANEL - 30, 150)
        self.kart_ciz(k3, "SON 5 BÖLÜM")
        self.yaz("Bölüm    Adım    Sonuç       Toplam    İndirimli",
                 x + 12, 286, self.f_kucuk, SOLUK)

        son_bes = sim.bolum_gecmisi[-5:]
        if not son_bes:
            self.yaz("(Henüz tamamlanan bölüm yok)",
                     x + 12, 314, self.f_normal, SOLUK)
        else:
            y_satir = 308
            for kayit in reversed(son_bes):
                b_str = f"B.{kayit['bolum']:<5}"
                a_str = f"{kayit['adim']:<6}"
                d_str = "ŞARJ OLDU " if kayit["sarj"] else "PİL BİTTİ "
                t_str = f"{kayit['toplam']:>+6d}    "
                i_str = f"{kayit['indirimli']:>+7.2f}"
                satir_renk = YESIL if kayit["sarj"] else KIRMIZI
                self.yaz(f"{b_str}  {a_str}  {d_str} {t_str} {i_str}",
                         x + 12, y_satir, self.f_kucuk, satir_renk)
                y_satir += 20

        # Kart 4: Kontrol Kılavuzu ve Durum
        k4 = pygame.Rect(x, 420, PANEL - 30, 128)
        self.kart_ciz(k4, "KONTROLLER")
        self.yaz("1-4: Kural Seç  |  A: Ajan Değiştir  |  R: Sıfırla",
                 x + 12, 444, self.f_normal, YAZI)
        self.yaz("Q: Yavaş   |   W: Normal   |   E: Hızlı",
                 x + 12, 466, self.f_normal, YAZI)
        self.yaz("BOŞLUK: Duraklat / Devam   |   N: Tek Adım",
                 x + 12, 488, self.f_normal, YAZI)

        durum_metin = ("DURAKLATILDI (N ile adım at)" if duraklatildi
                       else f"ÇALIŞIYOR (Hız: {hiz_adi})")
        durum_renk = KIRMIZI if duraklatildi else YESIL
        self.yaz(f"Durum: {durum_metin}",
                 x + 12, 514, self.f_kalin, durum_renk)


# ---------------------------------------------------------------------------
# ANA DÖNGÜ
# ---------------------------------------------------------------------------
def main():
    """Pygame penceresini başlatır ve simülasyon döngüsünü yürütür."""
    pygame.init()
    pencere = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
    pygame.display.set_caption("Pekiştirmeli Öğrenme: Ödül Kuralları")
    saat = pygame.time.Clock()

    sim = Simulasyon()
    cizim = Cizim(pencere)

    hiz_kodu = 2  # 1: yavaş, 2: normal, 3: hızlı
    hiz_adlari = {1: "Yavaş", 2: "Normal", 3: "Hızlı"}
    duraklatildi = False
    son_adim_zamani = 0
    calisiyor = True

    while calisiyor:
        for olay in pygame.event.get():
            if olay.type == pygame.QUIT:
                calisiyor = False
            elif olay.type == pygame.KEYDOWN:
                if olay.key == pygame.K_ESCAPE:
                    calisiyor = False
                elif olay.key == pygame.K_SPACE:
                    duraklatildi = not duraklatildi
                elif olay.key == pygame.K_n and duraklatildi:
                    sim.adim_yap()
                elif olay.key == pygame.K_r:
                    sim.skor_tablosunu_sifirla()
                elif olay.key in (pygame.K_1, pygame.K_KP1):
                    sim.kural_sec(1)
                elif olay.key in (pygame.K_2, pygame.K_KP2):
                    sim.kural_sec(2)
                elif olay.key in (pygame.K_3, pygame.K_KP3):
                    sim.kural_sec(3)
                elif olay.key in (pygame.K_4, pygame.K_KP4):
                    sim.kural_sec(4)
                elif olay.key == pygame.K_a:
                    sim.ajan_degistir()
                elif olay.key == pygame.K_q:
                    hiz_kodu = 1
                elif olay.key == pygame.K_w:
                    hiz_kodu = 2
                elif olay.key == pygame.K_e:
                    hiz_kodu = 3

        if not duraklatildi:
            simdi = pygame.time.get_ticks()
            if hiz_kodu == 1:
                if simdi - son_adim_zamani > 180:
                    sim.adim_yap()
                    son_adim_zamani = simdi
            elif hiz_kodu == 2:
                sim.adim_yap()
            else:
                for _ in range(15):
                    sim.adim_yap()

        cizim.ciz(sim, hiz_adlari[hiz_kodu], duraklatildi)
        saat.tick(12 if hiz_kodu == 2 else 30)

    pygame.quit()


if __name__ == "__main__":
    main()
