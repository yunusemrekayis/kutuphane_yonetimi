def tam_sayi_al(mesaj):
    """Kullanıcıdan geçerli bir tam sayı girmesini ister.

    Hatalı bir giriş yapıldığında uyarı verir ve doğru bir değer
    girilene kadar kullanıcıya tekrar sorar.
    """
    while True:
        try:
            deger = int(input(mesaj))
            return deger
        except ValueError:
            print("Geçersiz giriş, tekrar deneyin")


def yas_sor():
    """Kullanıcıdan yaşını girmesini ister ve sonraki yaşını yazdırır.

    Kullanıcının girdiği yaşın sıfırdan büyük olması gerektiğini
    doğrular.
    """
    while True:
        yas = tam_sayi_al("Yaşınızı girin: ")
        if yas > 0:
            break
        print("Yaş sıfırdan büyük olmalıdır, tekrar deneyin.")

    print(f"Seneye {yas + 1} olacaksınız.")


if __name__ == "__main__":
    yas_sor()
