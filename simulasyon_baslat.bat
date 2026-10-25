@echo off
chcp 65001 > nul
title Pekistirmeli Ogrenme - Odul Kurallari Simulasyonu
echo ========================================================
echo   Pekistirmeli Ogrenme Simulasyonu Baslatiliyor...
echo ========================================================
echo.
python odul_kurallari.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Simulasyon calisirken bir hata olustu.
    pause
)
