"""
01.03 - Ajan-Ortam Döngüsünü Canlı İzlemek (SİMÜLASYON)
Bölüm 1 - Pekiştirmeli Öğrenme Nedir?

Bu dosya öğretmenin simülasyon videosunda ekranda gösterdiği araçtır.
Öğrenciler de indirip kendileri deneyebilir.

Ekranda ne var?
    Solda  : robot süpürgenin gezdiği ızgara dünyası (ORTAM)
    Sağda  : pekiştirmeli öğrenme döngüsünün şeması. Döngünün hangi
             aşamasındaysak o kutu/ok renklenir:
                1. Ajan DURUMU görür
                2. Ajan bir EYLEM seçer
                3. Ortam eylemi uygular
                4. Ortam ÖDÜL / CEZA verir
             Altında son adımların kaydı (günlük) yazar.

Kontroller:
    BOŞLUK : duraklat / devam
    N      : (duraklatılmışken) bir sonraki aşamaya geç
    1      : çok yavaş (her aşama ayrı ayrı gösterilir)
    2      : normal   (her kare bir adım)
    3      : hızlı    (bir karede birçok adım)
    R      : her şeyi sıfırla
    ESC    : çıkış

Not: Ajan rastgele hareket eder. Henüz hiçbir şey öğrenmiyor; bu
simülasyonun amacı sadece döngünün nasıl işlediğini göstermektir.
"""

import random
import pygame

# ---------------------------------------------------------------------------
# AYARLAR
# ---------------------------------------------------------------------------
SATIR_SAYISI = 8
SUTUN_SAYISI = 8
HUCRE = 70
PANEL = 420
GENISLIK = SUTUN_SAYISI * HUCRE + PANEL
YUKSEKLIK = SATIR_SAYISI * HUCRE

BASLANGIC = (0, 0)
SARJ_ISTASYONU = (7, 7)
DUVARLAR = {(1, 2), (2, 2), (3, 2), (5, 4), (5, 5), (5, 6), (2, 5), (3, 5)}

ODUL_HEDEF, ODUL_CARPMA, ODUL_NORMAL = 10, -1, 0
MAKS_ADIM = 200

EYLEMLER = {0: ("YUKARI", -1, 0), 1: ("AŞAĞI", 1, 0), 2: ("SOL", 0, -1), 3: ("SAĞ", 0, 1)}

ASAMALAR = [
    "1. Ajan DURUMU görüyor",
    "2. Ajan bir EYLEM seçiyor",
    "3. Ortam eylemi uyguluyor",
    "4. Ortam ÖDÜL veriyor",
]

ARKA = (245, 247, 250)
CIZGI = (200, 205, 215)
DUVAR = (70, 75, 85)
MAVI = (52, 120, 246)
YESIL = (46, 184, 92)
TURUNCU = (240, 130, 50)
KIRMIZI = (220, 60, 60)
SOLUK = (190, 195, 205)
YAZI = (30, 30, 30)
PANEL_RENK = (232, 236, 242)


class OyunDunyasi:
    """ORTAM"""

    def sifirla(self):
        self.robot = BASLANGIC
        self.adim = 0
        return self.robot

    def adim_at(self, eylem):
        _, ds, dc = EYLEMLER[eylem]
        yeni = (self.robot[0] + ds, self.robot[1] + dc)
        self.adim += 1
        if 0 <= yeni[0] < SATIR_SAYISI and 0 <= yeni[1] < SUTUN_SAYISI and yeni not in DUVARLAR:
            self.robot, odul = yeni, ODUL_NORMAL
        else:
            odul = ODUL_CARPMA
        if self.robot == SARJ_ISTASYONU:
            return self.robot, ODUL_HEDEF, True
        return self.robot, odul, self.adim >= MAKS_ADIM


class RastgeleAjan:
    """AJAN"""

    def eylem_sec(self, durum):
        return random.randint(0, 3)


class Simulasyon:
    def __init__(self):
        self.dunya = OyunDunyasi()
        self.ajan = RastgeleAjan()
        self.sifirla_hepsini()

    def sifirla_hepsini(self):
        self.durum = self.dunya.sifirla()
        self.bolum = 1
        self.toplam_odul = 0
        self.basarili_bolum = 0
        self.asama = 0                # sıradaki yapılacak iş (0-3)
        self.secilen_eylem = None
        self.son_odul = None
        self.yeni_bolum_bekliyor = False
        self.gunluk = []

    def gosterilen_asama(self):
        """Ekranda gösterilecek aşama: az önce TAMAMLANAN aşama (0-3)."""
        return {1: 0, 2: 1, 3: 2, 0: 3}[self.asama]

    def tam_adim(self):
        """Dört aşamayı tek seferde yapar (normal ve hızlı mod için)."""
        while not self.asama_ilerlet():
            pass

    def asama_ilerlet(self):
        """Döngüyü bir aşama ilerletir. Bir adım tamamlandıysa True döner."""
        if self.asama == 0:                       # 1. Ajan durumu görür
            if self.yeni_bolum_bekliyor:          # önceki bölüm bittiyse yenisini başlat
                self.bolum += 1
                self.toplam_odul = 0
                self.durum = self.dunya.sifirla()
                self.yeni_bolum_bekliyor = False
            self.son_odul = None
            self.secilen_eylem = None
            self.asama = 1
        elif self.asama == 1:                     # 2. Ajan eylem seçer
            self.secilen_eylem = self.ajan.eylem_sec(self.durum)
            self.asama = 2
        elif self.asama == 2:                     # 3. Ortam eylemi uygular
            self.onceki_durum = self.durum
            self.durum, self.bekleyen_odul, self.bitti = self.dunya.adim_at(self.secilen_eylem)
            self.asama = 3
        else:                                     # 4. Ortam ödülü verir
            self.son_odul = self.bekleyen_odul
            self.toplam_odul += self.son_odul
            ad = EYLEMLER[self.secilen_eylem][0]
            self.gunluk.append(f"B{self.bolum} A{self.dunya.adim}: {self.onceki_durum} "
                               f"-> {ad:<6} -> ödül {self.son_odul:+d}")
            if self.bitti:
                if self.durum == SARJ_ISTASYONU:
                    self.basarili_bolum += 1
                    self.gunluk.append(f"*** Bölüm {self.bolum}: ŞARJ OLDU! ***")
                else:
                    self.gunluk.append(f"*** Bölüm {self.bolum}: pil bitti ***")
                self.yeni_bolum_bekliyor = True
            self.gunluk = self.gunluk[-8:]
            self.asama = 0
            return True
        return False


class Cizim:
    def __init__(self, pencere):
        self.p = pencere
        self.f = pygame.font.SysFont("segoeui,arial,dejavusans", 19)
        self.fk = pygame.font.SysFont("consolas,dejavusansmono,couriernew", 15)
        self.fb = pygame.font.SysFont("segoeui,arial,dejavusans", 24, bold=True)
        self.fdev = pygame.font.SysFont("segoeui,arial,dejavusans", 40, bold=True)

    def yaz(self, metin, x, y, font=None, renk=YAZI):
        self.p.blit((font or self.f).render(metin, True, renk), (x, y))

    def kare(self, s, c, b=0):
        return pygame.Rect(c * HUCRE + b, s * HUCRE + b, HUCRE - 2 * b, HUCRE - 2 * b)

    def ciz(self, sim, hiz_adi, duraklatildi):
        self.p.fill(ARKA)
        d = sim.dunya
        for s in range(SATIR_SAYISI):
            for c in range(SUTUN_SAYISI):
                k = self.kare(s, c)
                if (s, c) in DUVARLAR:
                    pygame.draw.rect(self.p, DUVAR, k)
                pygame.draw.rect(self.p, CIZGI, k, 1)
        sarj = self.kare(*SARJ_ISTASYONU, 8)
        pygame.draw.rect(self.p, YESIL, sarj, border_radius=10)
        x, y, g = sarj.x, sarj.y, sarj.width
        pygame.draw.polygon(self.p, (255, 230, 80), [
            (x + g * .55, y + g * .12), (x + g * .30, y + g * .55), (x + g * .50, y + g * .55),
            (x + g * .42, y + g * .88), (x + g * .72, y + g * .42), (x + g * .52, y + g * .42)])

        # Aşama 1'de robotun etrafında "görüyor" halkası
        robot = self.kare(*d.robot, 10)
        if sim.asama == 1:
            pygame.draw.rect(self.p, TURUNCU, self.kare(*d.robot, 3), 4, border_radius=16)
        pygame.draw.rect(self.p, MAVI, robot, border_radius=14)
        for gx in (robot.x + robot.width // 3, robot.x + 2 * robot.width // 3):
            pygame.draw.circle(self.p, (255, 255, 255), (gx, robot.y + robot.height // 3), 6)

        # Aşama 2'de seçilen eylemin oku
        if sim.asama == 2 and sim.secilen_eylem is not None:
            _, ds, dc = EYLEMLER[sim.secilen_eylem]
            mx, my = robot.center
            hx, hy = mx + dc * HUCRE * 0.8, my + ds * HUCRE * 0.8
            pygame.draw.line(self.p, TURUNCU, (mx, my), (hx, hy), 6)
            pygame.draw.circle(self.p, TURUNCU, (int(hx), int(hy)), 9)

        # Aşama 4'te ödül balonu
        if sim.asama == 0 and sim.son_odul is not None:
            renk = YESIL if sim.son_odul > 0 else (KIRMIZI if sim.son_odul < 0 else SOLUK)
            balon_y = robot.y - 40 if robot.y > 40 else robot.bottom + 2   # üst satırda ise alta yaz
            self.yaz(f"{sim.son_odul:+d}", robot.x + 4, balon_y, self.fdev, renk)

        self.panel(sim, hiz_adi, duraklatildi)
        pygame.display.flip()

    def kutu(self, rect, metin, aktif, renk):
        pygame.draw.rect(self.p, renk if aktif else SOLUK, rect, border_radius=12)
        yazi = self.fb.render(metin, True, (255, 255, 255))
        self.p.blit(yazi, yazi.get_rect(center=rect.center))

    def panel(self, sim, hiz_adi, duraklatildi):
        px = SUTUN_SAYISI * HUCRE
        pygame.draw.rect(self.p, PANEL_RENK, pygame.Rect(px, 0, PANEL, YUKSEKLIK))
        x = px + 20
        a = sim.gosterilen_asama()     # 0: durum, 1: eylem, 2: ortam uygular, 3: ödül

        # Döngü şeması
        ajan_k = pygame.Rect(x, 40, 150, 60)
        ortam_k = pygame.Rect(x + 230, 40, 150, 60)
        self.kutu(ajan_k, "AJAN", a in (0, 1), MAVI)
        self.kutu(ortam_k, "ORTAM", a in (2, 3), (40, 60, 100))
        ust = TURUNCU if a == 2 else SOLUK          # eylem oku
        alt = YESIL if a in (3, 0) else SOLUK       # durum + ödül oku
        pygame.draw.line(self.p, ust, (ajan_k.right, 55), (ortam_k.left, 55), 5)
        pygame.draw.polygon(self.p, ust, [(ortam_k.left, 55), (ortam_k.left - 12, 48), (ortam_k.left - 12, 62)])
        pygame.draw.line(self.p, alt, (ortam_k.left, 88), (ajan_k.right, 88), 5)
        pygame.draw.polygon(self.p, alt, [(ajan_k.right, 88), (ajan_k.right + 12, 81), (ajan_k.right + 12, 95)])
        self.yaz("eylem", x + 165, 18, self.f, ust)
        self.yaz("durum + ödül", x + 145, 98, self.f, alt)

        self.yaz("Şu anki aşama:", x, 135)
        self.yaz(ASAMALAR[a], x, 160, self.fb, TURUNCU)

        eylem = EYLEMLER[sim.secilen_eylem][0] if (sim.secilen_eylem is not None and a >= 1) else "-"
        odul = f"{sim.son_odul:+d}" if (sim.son_odul is not None and a == 3) else "-"
        self.yaz(f"Durum (robotun konumu): {sim.dunya.robot}", x, 205)
        self.yaz(f"Seçilen eylem: {eylem}     Ödül: {odul}", x, 230)
        self.yaz(f"Bölüm: {sim.bolum}    Adım: {sim.dunya.adim}/{MAKS_ADIM}", x, 255)
        self.yaz(f"Bu bölümün toplam ödülü: {sim.toplam_odul}", x, 280)
        self.yaz(f"Şarj olan bölüm sayısı: {sim.basarili_bolum}", x, 305)

        self.yaz("Günlük (son adımlar):", x, 342)
        y = 366
        for satir in sim.gunluk:
            self.yaz(satir, x, y, self.fk)
            y += 19

        alt_yazi = "DURAKLATILDI - N: sonraki aşama" if duraklatildi else f"Hız: {hiz_adi}  (1/2/3, BOŞLUK)"
        self.yaz(alt_yazi, x, YUKSEKLIK - 28, self.f, KIRMIZI if duraklatildi else YAZI)


def main():
    pygame.init()
    pencere = pygame.display.set_mode((GENISLIK, YUKSEKLIK))
    pygame.display.set_caption("01.03 - Ajan-Ortam Döngüsü Simülasyonu")
    saat = pygame.time.Clock()
    sim = Simulasyon()
    cizim = Cizim(pencere)

    hiz = 1                     # 1: çok yavaş, 2: normal, 3: hızlı
    hiz_adlari = {1: "çok yavaş", 2: "normal", 3: "hızlı"}
    duraklatildi = False
    son_asama_zamani = 0
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
                    sim.asama_ilerlet()
                elif olay.key == pygame.K_r:
                    sim.sifirla_hepsini()
                elif olay.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    hiz = int(pygame.key.name(olay.key))

        if not duraklatildi:
            simdi = pygame.time.get_ticks()
            if hiz == 1:
                if simdi - son_asama_zamani > 800:     # her aşama 0.8 saniye
                    sim.asama_ilerlet()
                    son_asama_zamani = simdi
            elif hiz == 2:
                sim.tam_adim()
            else:
                for _ in range(25):
                    sim.tam_adim()

        cizim.ciz(sim, hiz_adlari[hiz], duraklatildi)
        saat.tick(8 if hiz == 2 else 30)

    pygame.quit()


if __name__ == "__main__":
    main()
