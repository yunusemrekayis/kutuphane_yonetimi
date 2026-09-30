"""Kütüphane Yönetim Sistemi Flask ve SQLite Veritabanı Uygulaması."""

import functools
import hashlib
import sqlite3
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

app = Flask(__name__)
app.secret_key = "kutuphane_guvenli_anahtar_2026"
VERITABANI_YOLU = "kutuphane.db"


def veritabani_baglantisi_al():
    """SQLite veritabanı bağlantısı açar ve satır nesnesiyle döndürür."""
    baglanti = sqlite3.connect(VERITABANI_YOLU)
    baglanti.row_factory = sqlite3.Row
    return baglanti


def sifre_ozetle(sifre):
    """Verilen şifreyi standart SHA-256 algoritması ile özetler."""
    if not isinstance(sifre, str):
        sifre = str(sifre)
    return hashlib.sha256(sifre.encode("utf-8")).hexdigest()


def sifre_dogrula(duz_sifre, ozet_sifre):
    """Düz metin şifrenin veritabanındaki özet ile eşleşmesini denetler."""
    if not duz_sifre or not ozet_sifre:
        return False
    return sifre_ozetle(duz_sifre) == ozet_sifre


def veritabani_olustur():
    """Tabloları oluşturur, sütunları günceller ve örnek verileri yükler."""
    baglanti = None
    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()

        # 1. Üye Tablosu
        imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS uyeler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telefon TEXT,
                sifre TEXT NOT NULL,
                rol TEXT DEFAULT 'uye',
                kayit_tarihi TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Mevcut uyeler tablosunda yeni sütunların varlığını kontrol et
        imlec.execute("PRAGMA table_info(uyeler);")
        sutun_bilgileri = imlec.fetchall()
        mevcut_sutunlar = [sutun["name"] for sutun in sutun_bilgileri]

        varsayilan_sifre = sifre_ozetle("ogrenci123")
        if "sifre" not in mevcut_sutunlar:
            imlec.execute(
                f"ALTER TABLE uyeler ADD COLUMN sifre TEXT "
                f"DEFAULT '{varsayilan_sifre}';"
            )
        if "rol" not in mevcut_sutunlar:
            imlec.execute(
                "ALTER TABLE uyeler ADD COLUMN rol TEXT DEFAULT 'uye';"
            )

        # 2. Kitap Tablosu
        imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS kitaplar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                yazar TEXT NOT NULL,
                yil INTEGER,
                kategori TEXT,
                kopya_sayisi INTEGER DEFAULT 1
            );
            """
        )

        # 3. Ödünç Tablosu
        imlec.execute(
            """
            CREATE TABLE IF NOT EXISTS oduncler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uye_id INTEGER NOT NULL,
                kitap_id INTEGER NOT NULL,
                odunc_tarihi TEXT DEFAULT CURRENT_TIMESTAMP,
                son_teslim_tarihi TEXT,
                durum TEXT DEFAULT 'aktif',
                FOREIGN KEY (uye_id) REFERENCES uyeler(id),
                FOREIGN KEY (kitap_id) REFERENCES kitaplar(id)
            );
            """
        )

        # Örnek kitap verilerini kontrol et ve ekle
        imlec.execute("SELECT COUNT(*) AS adet FROM kitaplar;")
        if imlec.fetchone()["adet"] == 0:
            ornek_kitaplar = [
                ("Safahat", "Mehmet Akif Ersoy", 1911, "Şiir", 3),
                ("Kutadgu Bilig", "Yusuf Has Hacib", 1069, "Siyaset", 2),
                ("Divanu Lugati't-Turk", "Kaşgarlı Mahmud", 1074, "Sözlük", 2),
                ("Mesnevi", "Mevlana", 1273, "Tasavvuf", 4),
                ("Seyahatname", "Evliya Çelebi", 1682, "Gezi", 1),
            ]
            imlec.executemany(
                """
                INSERT INTO kitaplar (ad, yazar, yil, kategori, kopya_sayisi)
                VALUES (?, ?, ?, ?, ?);
                """,
                ornek_kitaplar,
            )

        # Admin ve örnek üyeleri kontrol et
        imlec.execute(
            "SELECT COUNT(*) AS adet FROM uyeler WHERE rol = 'admin';"
        )
        if imlec.fetchone()["adet"] == 0:
            admin_sifre = sifre_ozetle("admin123")
            imlec.execute(
                """
                INSERT OR IGNORE INTO uyeler (isim, email, telefon, sifre, rol)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    "Kütüphane Yöneticisi",
                    "admin@kutuphane.k12.tr",
                    "0555 000 00 00",
                    admin_sifre,
                    "admin",
                ),
            )

        imlec.execute(
            "SELECT COUNT(*) AS adet FROM uyeler WHERE email = ?;",
            ("ahmet.yilmaz@okul.k12.tr",),
        )
        if imlec.fetchone()["adet"] == 0:
            ogrenci_sifre = sifre_ozetle("ogrenci123")
            imlec.execute(
                """
                INSERT OR IGNORE INTO uyeler (isim, email, telefon, sifre, rol)
                VALUES (?, ?, ?, ?, ?);
                """,
                (
                    "Ahmet Yılmaz",
                    "ahmet.yilmaz@okul.k12.tr",
                    "0555 111 22 33",
                    ogrenci_sifre,
                    "uye",
                ),
            )

        # Örnek aktif ödünç kaydı kontrolü
        imlec.execute("SELECT COUNT(*) AS adet FROM oduncler;")
        if imlec.fetchone()["adet"] == 0:
            imlec.execute(
                "SELECT id FROM uyeler WHERE email = ?;",
                ("ahmet.yilmaz@okul.k12.tr",),
            )
            ahmet = imlec.fetchone()
            imlec.execute("SELECT id FROM kitaplar LIMIT 1;")
            kitap = imlec.fetchone()
            if ahmet and kitap:
                imlec.execute(
                    """
                    INSERT INTO oduncler (
                        uye_id,
                        kitap_id,
                        odunc_tarihi,
                        son_teslim_tarihi,
                        durum
                    )
                    VALUES (?, ?, '2026-09-20', '2026-10-05', 'aktif');
                    """,
                    (ahmet["id"], kitap["id"]),
                )

        baglanti.commit()
    except sqlite3.Error as hata:
        print(f"Veritabanı oluşturulurken hata: {hata}")
    finally:
        if baglanti:
            baglanti.close()


# İngilizce fonksiyon adı ile çağrılabilsin diye takma ad
create_database = veritabani_olustur


def eposta_dogrula(eposta):
    """E-posta adresinin geçerliliğini '@' ve '.' ile denetler."""
    if not isinstance(eposta, str):
        return False
    eposta_metni = eposta.strip()
    return ("@" in eposta_metni) and ("." in eposta_metni)


def uye_girdisi_dogrula(isim, email):
    """Kullanıcıdan gelen isim ve e-posta verilerini doğrular."""
    if not isinstance(isim, str) or not isim.strip():
        return "İsim alanı zorunludur. Lütfen adınızı giriniz."
    if not isinstance(email, str) or not email.strip():
        return "E-posta alanı zorunludur. Lütfen e-postanızı giriniz."
    if not eposta_dogrula(email):
        return "Geçersiz e-posta adresi! E-posta '@' ve '.' içermelidir."
    return None


def kayit_girdisi_dogrula(isim, email, sifre, sifre_tekrar):
    """Yeni üye kayıt formundaki tüm alanların geçerliliğini denetler."""
    temel_hata = uye_girdisi_dogrula(isim, email)
    if temel_hata:
        return temel_hata
    if not isinstance(sifre, str) or not sifre:
        return "Şifre alanı zorunludur. Lütfen şifrenizi giriniz."
    if len(sifre) < 6:
        return "Şifre en az 6 karakter olmalıdır."
    if sifre != sifre_tekrar:
        return "Girdiğiniz şifreler birbiriyle eşleşmiyor."
    return None


def giris_girdisi_dogrula(email, sifre):
    """Giriş formundaki e-posta ve şifre verilerini denetler."""
    if not isinstance(email, str) or not email.strip():
        return "Lütfen e-posta adresinizi giriniz."
    if not eposta_dogrula(email):
        return "Geçersiz e-posta adresi formatı."
    if not isinstance(sifre, str) or not sifre:
        return "Lütfen şifrenizi giriniz."
    return None


def sifre_degistirme_dogrula(eski_sifre, yeni_sifre, yeni_sifre_tekrar):
    """Şifre değiştirme formundaki alanları ve kuralları doğrular."""
    if not isinstance(eski_sifre, str) or not eski_sifre:
        return "Mevcut şifrenizi girmeniz zorunludur."
    if not isinstance(yeni_sifre, str) or not yeni_sifre:
        return "Yeni şifre alanı boş bırakılamaz."
    if len(yeni_sifre) < 6:
        return "Yeni şifre en az 6 karakter olmalıdır."
    if yeni_sifre != yeni_sifre_tekrar:
        return "Yeni şifre ve şifre tekrarı birbiriyle eşleşmiyor."
    return None


def kitap_girdisi_dogrula(ad, yazar, yil_metni, kopya_metni):
    """Kitap ekleme ve güncelleme form verilerini doğrular."""
    if not isinstance(ad, str) or not ad.strip():
        return "Kitap adı zorunludur. Boş bırakılamaz.", None, None
    if not isinstance(yazar, str) or not yazar.strip():
        return "Yazar adı zorunludur. Boş bırakılamaz.", None, None

    yil_degeri = None
    if yil_metni is not None and str(yil_metni).strip() != "":
        yil_temiz = str(yil_metni).strip()
        if not (yil_temiz.isdigit() and len(yil_temiz) == 4):
            return "Basım yılı 4 haneli bir sayı olmalıdır.", None, None
        yil_degeri = int(yil_temiz)
        if yil_degeri < 1000 or yil_degeri > 2099:
            return "Basım yılı 1000-2099 arasında olmalıdır.", None, None

    kopya_sayisi = 1
    if kopya_metni is not None and str(kopya_metni).strip() != "":
        kopya_temiz = str(kopya_metni).strip()
        if not kopya_temiz.isdigit():
            return "Kopya sayısı pozitif sayı olmalıdır.", None, None
        kopya_sayisi = int(kopya_temiz)
        if kopya_sayisi < 1:
            return "Kopya sayısı en az 1 olmalıdır.", None, None

    return None, yil_degeri, kopya_sayisi


def giris_gerekli(fonksiyon):
    """Giriş yapılmış olmasını zorunlu kılan dekoratör."""
    @functools.wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        if "kullanici_id" not in session:
            return redirect(url_for("giris"))
        return fonksiyon(*args, **kwargs)

    return sarmalayici


# İngilizce dekoratör ismi ile çağrılabilsin diye takma ad
login_required = giris_gerekli


def admin_gerekli(fonksiyon):
    """Yalnızca yönetici (admin) üyelerin girmesine izin veren dekoratör."""
    @functools.wraps(fonksiyon)
    def sarmalayici(*args, **kwargs):
        if "kullanici_id" not in session:
            return redirect(url_for("giris"))
        if session.get("rol") != "admin":
            return (
                "Yetkisiz erişim! Bu sayfayı yalnızca yöneticiler görebilir.",
                403,
            )
        return fonksiyon(*args, **kwargs)

    return sarmalayici


# İngilizce dekoratör ismi ile çağrılabilsin diye takma ad
admin_required = admin_gerekli


@app.route("/")
def ana_sayfa():
    """Kütüphane ana sayfasını ve özet istatistikleri sunar."""
    baglanti = None
    toplam_kitap = 0
    toplam_uye = 0
    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()
        imlec.execute("SELECT COUNT(*) AS adet FROM kitaplar;")
        toplam_kitap = imlec.fetchone()["adet"]
        imlec.execute("SELECT COUNT(*) AS adet FROM uyeler;")
        toplam_uye = imlec.fetchone()["adet"]
    except sqlite3.Error as hata:
        print(f"İstatistik alınırken hata: {hata}")
    finally:
        if baglanti:
            baglanti.close()

    return render_template(
        "ana_sayfa.html",
        kutuphane_adi="Merkez Okul Kütüphanesi",
        acilis_saati="Hafta içi 08:30 - 17:00",
        toplam_kitap=toplam_kitap,
        toplam_uye=toplam_uye,
        aktif_gun="5 Gün (Pzt-Cum)",
    )


@app.route("/kitaplar")
def kitaplar():
    """Kütüphanedeki tüm kitapları 10'arlı sayfalayarak listeler."""
    sayfa_girdisi = request.args.get("sayfa", "1")
    try:
        sayfa = int(sayfa_girdisi)
        if sayfa < 1:
            sayfa = 1
    except ValueError:
        sayfa = 1

    sayfa_boyutu = 10
    baglanti = None
    kitap_listesi = []
    toplam_kitap = 0
    toplam_sayfa = 1

    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()
        imlec.execute("SELECT COUNT(*) AS adet FROM kitaplar;")
        toplam_kitap = imlec.fetchone()["adet"]

        if toplam_kitap > 0:
            toplam_sayfa = (
                toplam_kitap + sayfa_boyutu - 1
            ) // sayfa_boyutu
        else:
            toplam_sayfa = 1

        if sayfa > toplam_sayfa:
            sayfa = toplam_sayfa

        ofset = (sayfa - 1) * sayfa_boyutu
        imlec.execute(
            """
            SELECT id, ad, yazar, yil, kategori, kopya_sayisi
            FROM kitaplar
            ORDER BY id ASC
            LIMIT ? OFFSET ?;
            """,
            (sayfa_boyutu, ofset),
        )
        kitap_listesi = imlec.fetchall()
    except sqlite3.Error as hata:
        print(f"Kitaplar listelenirken hata: {hata}")
    finally:
        if baglanti:
            baglanti.close()

    return render_template(
        "kitaplar.html",
        kitaplar=kitap_listesi,
        sayfa=sayfa,
        toplam_sayfa=toplam_sayfa,
        toplam_kitap=toplam_kitap,
    )


@app.route("/kitap-ekle", methods=["GET", "POST"])
def kitap_ekle():
    """Yeni kitap ekleme sayfasını sunar ve form verilerini kaydeder."""
    if request.method == "POST":
        ad = request.form.get("ad", "").strip()
        yazar = request.form.get("yazar", "").strip()
        yil_metni = request.form.get("yil", "").strip()
        kategori = request.form.get("kategori", "").strip()
        kopya_metni = request.form.get("kopya_sayisi", "1").strip()

        hata, yil, kopya = kitap_girdisi_dogrula(
            ad, yazar, yil_metni, kopya_metni
        )
        if hata:
            return render_template(
                "kitap_ekle.html",
                hata=hata,
                form_verisi={
                    "ad": ad,
                    "yazar": yazar,
                    "yil": yil_metni,
                    "kategori": kategori,
                    "kopya_sayisi": kopya_metni,
                },
            )

        baglanti = None
        try:
            baglanti = veritabani_baglantisi_al()
            imlec = baglanti.cursor()
            imlec.execute(
                """
                INSERT INTO kitaplar (ad, yazar, yil, kategori, kopya_sayisi)
                VALUES (?, ?, ?, ?, ?);
                """,
                (ad, yazar, yil, kategori, kopya),
            )
            baglanti.commit()
            return redirect(url_for("kitaplar"))
        except sqlite3.Error as hata_db:
            return render_template(
                "kitap_ekle.html",
                hata=f"Veritabanı hatası: {hata_db}",
                form_verisi={
                    "ad": ad,
                    "yazar": yazar,
                    "yil": yil_metni,
                    "kategori": kategori,
                    "kopya_sayisi": kopya_metni,
                },
            )
        finally:
            if baglanti:
                baglanti.close()

    return render_template("kitap_ekle.html", hata=None, form_verisi={})


@app.route("/kitap/<int:id>")
def kitap_detay(id):
    """Belirtilen id numaralı kitabın tüm detaylarını gösterir."""
    baglanti = None
    kitap = None
    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()
        imlec.execute(
            """
            SELECT id, ad, yazar, yil, kategori, kopya_sayisi
            FROM kitaplar
            WHERE id = ?;
            """,
            (id,),
        )
        kitap = imlec.fetchone()
        if not kitap:
            return "Hata: Aranan kitap bulunamadı.", 404
    except sqlite3.Error as hata:
        return f"Veritabanı hatası: {hata}", 500
    finally:
        if baglanti:
            baglanti.close()

    return render_template("kitap_detay.html", kitap=kitap)


@app.route("/kitap-guncelle/<int:id>", methods=["GET", "POST"])
def kitap_guncelle(id):
    """Kitap bilgilerini form ile günceller veya formu gösterir."""
    baglanti = None
    kitap = None
    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()
        imlec.execute(
            """
            SELECT id, ad, yazar, yil, kategori, kopya_sayisi
            FROM kitaplar
            WHERE id = ?;
            """,
            (id,),
        )
        kitap = imlec.fetchone()

        if not kitap:
            return "Hata: Güncellenecek kitap bulunamadı.", 404

        if request.method == "POST":
            ad = request.form.get("ad", "").strip()
            yazar = request.form.get("yazar", "").strip()
            yil_metni = request.form.get("yil", "").strip()
            kategori = request.form.get("kategori", "").strip()
            kopya_metni = request.form.get("kopya_sayisi", "1").strip()

            hata, yil, kopya = kitap_girdisi_dogrula(
                ad, yazar, yil_metni, kopya_metni
            )
            if hata:
                return render_template(
                    "kitap_guncelle.html",
                    kitap=kitap,
                    hata=hata,
                    form_verisi={
                        "ad": ad,
                        "yazar": yazar,
                        "yil": yil_metni,
                        "kategori": kategori,
                        "kopya_sayisi": kopya_metni,
                    },
                )

            imlec.execute(
                """
                UPDATE kitaplar
                SET ad = ?, yazar = ?, yil = ?, kategori = ?, kopya_sayisi = ?
                WHERE id = ?;
                """,
                (ad, yazar, yil, kategori, kopya, id),
            )
            baglanti.commit()
            return redirect(url_for("kitap_detay", id=id))
    except sqlite3.Error as hata:
        return f"Veritabanı hatası: {hata}", 500
    finally:
        if baglanti:
            baglanti.close()

    return render_template(
        "kitap_guncelle.html",
        kitap=kitap,
        hata=None,
        form_verisi={},
    )


@app.route("/kitap-sil/<int:id>", methods=["GET", "POST"])
def kitap_sil(id):
    """Kitap silme onay sayfasını gösterir ve silme işlemini yapar."""
    baglanti = None
    kitap = None
    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()
        imlec.execute(
            """
            SELECT id, ad, yazar, yil, kategori, kopya_sayisi
            FROM kitaplar
            WHERE id = ?;
            """,
            (id,),
        )
        kitap = imlec.fetchone()

        if not kitap:
            return "Hata: Silinecek kitap bulunamadı.", 404

        if request.method == "POST":
            imlec.execute("DELETE FROM kitaplar WHERE id = ?;", (id,))
            baglanti.commit()
            return redirect(url_for("kitaplar"))
    except sqlite3.Error as hata:
        return f"Veritabanı hatası: {hata}", 500
    finally:
        if baglanti:
            baglanti.close()

    return render_template("kitap_sil.html", kitap=kitap)


@app.route("/kayit", methods=["GET", "POST"])
def kayit():
    """Yeni üye kaydeder veya kayıt formunu gösterir."""
    if request.method == "POST":
        isim = request.form.get("isim", "").strip()
        email = request.form.get(
            "email", request.form.get("eposta", "")
        ).strip()
        telefon = request.form.get("telefon", "").strip()
        sifre = request.form.get("sifre", "")
        sifre_tekrar = request.form.get("sifre_tekrar", "")

        # Şifre alanı formda bulunuyorsa tam doğrulama yap
        if "sifre" in request.form:
            hata_mesaji = kayit_girdisi_dogrula(
                isim, email, sifre, sifre_tekrar
            )
        else:
            hata_mesaji = uye_girdisi_dogrula(isim, email)
            sifre = "ogrenci123"

        if hata_mesaji:
            return render_template(
                "kayit.html",
                hata=hata_mesaji,
                form_verisi={
                    "isim": isim,
                    "email": email,
                    "telefon": telefon,
                },
            )

        baglanti = None
        try:
            baglanti = veritabani_baglantisi_al()
            imlec = baglanti.cursor()
            sifreli_sifre = sifre_ozetle(sifre)
            imlec.execute(
                """
                INSERT INTO uyeler (isim, email, telefon, sifre, rol)
                VALUES (?, ?, ?, ?, 'uye');
                """,
                (isim, email, telefon, sifreli_sifre),
            )
            baglanti.commit()
            return redirect(url_for("basari"))
        except sqlite3.IntegrityError:
            hata_mesaji = (
                "Bu e-posta adresi ile kayıtlı başka bir üye bulunmaktadır."
            )
            return render_template(
                "kayit.html",
                hata=hata_mesaji,
                form_verisi={
                    "isim": isim,
                    "email": email,
                    "telefon": telefon,
                },
            )
        except sqlite3.Error as hata:
            hata_mesaji = f"Veritabanı hatası oluştu: {hata}"
            return render_template(
                "kayit.html",
                hata=hata_mesaji,
                form_verisi={
                    "isim": isim,
                    "email": email,
                    "telefon": telefon,
                },
            )
        finally:
            if baglanti:
                baglanti.close()

    return render_template("kayit.html", hata=None, form_verisi={})


@app.route("/giris", methods=["GET", "POST"])
def giris():
    """Kullanıcı girişini denetler ve oturum açar."""
    if "kullanici_id" in session:
        return redirect(url_for("dashboard"))

    hata = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        sifre = request.form.get("sifre", "")

        hata = giris_girdisi_dogrula(email, sifre)
        if not hata:
            baglanti = None
            try:
                baglanti = veritabani_baglantisi_al()
                imlec = baglanti.cursor()
                imlec.execute(
                    """
                    SELECT id, isim, email, sifre, rol
                    FROM uyeler
                    WHERE email = ?;
                    """,
                    (email,),
                )
                uye = imlec.fetchone()

                if uye and sifre_dogrula(sifre, uye["sifre"]):
                    session["kullanici_id"] = uye["id"]
                    session["kullanici_adi"] = uye["isim"]
                    session["email"] = uye["email"]
                    session["rol"] = uye["rol"]
                    return redirect(url_for("dashboard"))
                else:
                    hata = "E-posta veya şifre hatalı!"
            except sqlite3.Error as db_hatasi:
                hata = f"Veritabanı hatası: {db_hatasi}"
            finally:
                if baglanti:
                    baglanti.close()

    return render_template("giris.html", hata=hata)


@app.route("/cikis")
def cikis():
    """Kullanıcı oturumunu sonlandırır ve giriş sayfasına yönlendirir."""
    session.clear()
    return redirect(url_for("giris"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Giriş yapmış kullanıcının panelini ve aktif ödünçlerini gösterir."""
    baglanti = None
    uye = None
    aktif_oduncler = []
    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()
        imlec.execute(
            """
            SELECT id, isim, email, telefon, rol, kayit_tarihi
            FROM uyeler
            WHERE id = ?;
            """,
            (session["kullanici_id"],),
        )
        uye = imlec.fetchone()

        imlec.execute(
            """
            SELECT o.id, k.ad AS kitap_adi, k.yazar,
                   o.odunc_tarihi, o.son_teslim_tarihi
            FROM oduncler o
            JOIN kitaplar k ON o.kitap_id = k.id
            WHERE o.uye_id = ? AND o.durum = 'aktif'
            ORDER BY o.id DESC;
            """,
            (session["kullanici_id"],),
        )
        aktif_oduncler = imlec.fetchall()
    except sqlite3.Error as hata:
        print(f"Dashboard verisi çekilirken hata: {hata}")
    finally:
        if baglanti:
            baglanti.close()

    return render_template(
        "dashboard.html",
        uye=uye,
        aktif_oduncler=aktif_oduncler,
    )


@app.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    """Kullanıcının profil bilgilerini gösterir ve güncellemesini sağlar."""
    baglanti = None
    uye = None
    hata = None
    bilgi = None
    kullanici_id = session["kullanici_id"]

    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()

        if request.method == "POST":
            isim = request.form.get("isim", "").strip()
            telefon = request.form.get("telefon", "").strip()

            if not isim:
                hata = "İsim alanı boş bırakılamaz."
            else:
                imlec.execute(
                    """
                    UPDATE uyeler
                    SET isim = ?, telefon = ?
                    WHERE id = ?;
                    """,
                    (isim, telefon, kullanici_id),
                )
                baglanti.commit()
                session["kullanici_adi"] = isim
                bilgi = "Profil bilgileriniz başarıyla güncellendi."

        imlec.execute(
            """
            SELECT id, isim, email, telefon, rol, kayit_tarihi
            FROM uyeler
            WHERE id = ?;
            """,
            (kullanici_id,),
        )
        uye = imlec.fetchone()
    except sqlite3.Error as db_hatasi:
        hata = f"Veritabanı hatası: {db_hatasi}"
    finally:
        if baglanti:
            baglanti.close()

    return render_template(
        "profil.html",
        uye=uye,
        hata=hata,
        bilgi=bilgi,
    )


@app.route("/sifre-degistir", methods=["GET", "POST"])
@login_required
def sifre_degistir():
    """Giriş yapmış kullanıcının şifresini değiştirmesini sağlar."""
    hata = None
    bilgi = None
    if request.method == "POST":
        eski_sifre = request.form.get("eski_sifre", "")
        yeni_sifre = request.form.get("yeni_sifre", "")
        yeni_sifre_tekrar = request.form.get("yeni_sifre_tekrar", "")

        hata = sifre_degistirme_dogrula(
            eski_sifre, yeni_sifre, yeni_sifre_tekrar
        )

        if not hata:
            baglanti = None
            try:
                baglanti = veritabani_baglantisi_al()
                imlec = baglanti.cursor()
                imlec.execute(
                    "SELECT sifre FROM uyeler WHERE id = ?;",
                    (session["kullanici_id"],),
                )
                satir = imlec.fetchone()

                if not satir or not sifre_dogrula(
                    eski_sifre, satir["sifre"]
                ):
                    hata = "Mevcut şifrenizi hatalı girdiniz."
                else:
                    yeni_ozet = sifre_ozetle(yeni_sifre)
                    imlec.execute(
                        "UPDATE uyeler SET sifre = ? WHERE id = ?;",
                        (yeni_ozet, session["kullanici_id"]),
                    )
                    baglanti.commit()
                    bilgi = "Şifreniz başarıyla değiştirildi."
            except sqlite3.Error as db_hatasi:
                hata = f"Veritabanı hatası: {db_hatasi}"
            finally:
                if baglanti:
                    baglanti.close()

    return render_template(
        "sifre_degistir.html",
        hata=hata,
        bilgi=bilgi,
    )


@app.route("/admin")
@admin_required
def admin():
    """Sadece yöneticilerin erişebildiği üye yönetim panelini sunar."""
    baglanti = None
    uye_listesi = []
    toplam_uye = 0
    toplam_admin = 0
    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()
        imlec.execute(
            """
            SELECT id, isim, email, telefon, rol, kayit_tarihi
            FROM uyeler
            ORDER BY id ASC;
            """
        )
        uye_listesi = imlec.fetchall()
        toplam_uye = len(uye_listesi)
        toplam_admin = sum(
            1 for u in uye_listesi if u["rol"] == "admin"
        )
    except sqlite3.Error as db_hatasi:
        print(f"Admin paneli veri hatası: {db_hatasi}")
    finally:
        if baglanti:
            baglanti.close()

    return render_template(
        "admin.html",
        uyeler=uye_listesi,
        toplam_uye=toplam_uye,
        toplam_admin=toplam_admin,
    )


@app.route("/uyeler")
def uyeler():
    """Veritabanındaki tüm üyeleri çeker ve listeler."""
    baglanti = None
    uye_listesi = []
    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()
        imlec.execute(
            """
            SELECT id, isim, email, telefon, kayit_tarihi
            FROM uyeler
            ORDER BY id ASC;
            """
        )
        uye_listesi = imlec.fetchall()
    except sqlite3.Error as hata:
        print(f"Üyeler listelenirken hata: {hata}")
    finally:
        if baglanti:
            baglanti.close()

    return render_template("uyeler.html", uyeler=uye_listesi)


@app.route("/guncelle/<int:id>", methods=["GET", "POST"])
def uye_guncelle(id):
    """Belirtilen id numarasına sahip üye bilgilerini günceller."""
    baglanti = None
    uye = None
    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()
        imlec.execute(
            "SELECT id, isim, email, telefon FROM uyeler WHERE id = ?;",
            (id,),
        )
        uye = imlec.fetchone()

        if not uye:
            return "Hata: Güncellenecek üye bulunamadı.", 404

        if request.method == "POST":
            isim = request.form.get("isim", "").strip()
            email = request.form.get(
                "email", request.form.get("eposta", "")
            ).strip()
            telefon = request.form.get("telefon", "").strip()

            hata_mesaji = uye_girdisi_dogrula(isim, email)
            if hata_mesaji:
                return render_template(
                    "guncelle.html",
                    uye=uye,
                    hata=hata_mesaji,
                    form_verisi={
                        "isim": isim,
                        "email": email,
                        "telefon": telefon,
                    },
                )

            try:
                imlec.execute(
                    """
                    UPDATE uyeler
                    SET isim = ?, email = ?, telefon = ?
                    WHERE id = ?;
                    """,
                    (isim, email, telefon, id),
                )
                baglanti.commit()
                return redirect(url_for("uyeler"))
            except sqlite3.IntegrityError:
                hata_mesaji = (
                    "Bu e-posta adresi başka bir üye tarafından kullanılıyor."
                )
                return render_template(
                    "guncelle.html",
                    uye=uye,
                    hata=hata_mesaji,
                    form_verisi={
                        "isim": isim,
                        "email": email,
                        "telefon": telefon,
                    },
                )
    except sqlite3.Error as hata:
        return f"Veritabanı hatası: {hata}", 500
    finally:
        if baglanti:
            baglanti.close()

    return render_template(
        "guncelle.html",
        uye=uye,
        hata=None,
        form_verisi={},
    )


@app.route("/sil/<int:id>", methods=["GET", "POST"])
def uye_sil(id):
    """Belirtilen id numarasına sahip üyeyi veritabanından siler."""
    baglanti = None
    try:
        baglanti = veritabani_baglantisi_al()
        imlec = baglanti.cursor()
        imlec.execute("DELETE FROM uyeler WHERE id = ?;", (id,))
        baglanti.commit()
    except sqlite3.Error as hata:
        print(f"Üye silinirken hata: {hata}")
    finally:
        if baglanti:
            baglanti.close()

    return redirect(url_for("uyeler"))


@app.route("/basari")
def basari():
    """Kayıt işlemi başarılı olduğunda tebrik mesajını gösterir."""
    return render_template("basari.html")


@app.route("/ayarlar")
def ayarlar():
    """Kütüphanenin iletişim ve yetkili bilgilerini gösterir."""
    kutuphane_bilgisi = {
        "ad": "Merkez Okul Kütüphanesi",
        "acilis_saati": "Hafta içi 08:30 - 17:00",
        "telefon": "0312 123 45 67",
        "eposta": "kutuphane@okul.k12.tr",
        "adres": "Okul Caddesi No:10, Ankara",
        "yetkili": "Kütüphane Sorumlusu Öğretmen",
    }
    return render_template("ayarlar.html", iletisim=kutuphane_bilgisi)


# Uygulama başlatıldığında veritabanı ve tabloların hazır olduğundan emin olalım
veritabani_olustur()


if __name__ == "__main__":
    app.run(debug=True, port=5000)

