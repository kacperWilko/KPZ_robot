# KPZ_robot

Projekt realizowany na Raspberry Pi Zero 2 W, którego celem jest zbieranie danych
z czujników środowiskowych oraz obsługa urządzeń peryferyjnych (I2C, kamera).
Aplikacja została napisana w Pythonie i jest przygotowana do uruchamiania bezpośrednio
na Raspberry Pi OS.

Repozytorium zawiera kompletną logikę aplikacji oraz kod zewnętrzny wymagany
do obsługi czujnika ENS160.

---

## Funkcjonalność

- Obsługa czujnika jakości powietrza ENS160 (biblioteka DFRobot)
- Obsługa czujnika środowiskowego BME280
- Pętla pomiarowa realizowana w Pythonie
- Przygotowanie pod pracę z kamerą Raspberry Pi
- Struktura projektu umożliwiająca łatwe uruchomienie i rozwój

---

## System

Projekt uruchamiany jest na następującej konfiguracji sprzętowo-systemowej:

- Płytka: Raspberry Pi Zero 2 W Rev 1.0
- Architektura: aarch64 (64-bit)
- System operacyjny: Debian GNU/Linux 12 (bookworm)
- Kernel: Linux 6.12.x (rpt-rpi-v8)
- Python:
  - systemowy interpreter: Python 3.11.2
  - środowisko wirtualne (venv): Python 3.11.2

Projekt wykorzystuje środowisko wirtualne Pythona w celu izolacji zależności
oraz zapewnienia powtarzalności uruchomienia aplikacji.

---

## Wykorzystane komponenty sprzętowe

- Raspberry Pi Zero 2 W
- Karta microSD z Raspberry Pi OS
- Czujnik jakości powietrza ENS160 (I2C)
- Czujnik BME280 (temperatura, wilgotność, ciśnienie)
- Kamera Raspberry Pi (interfejs CSI)
- Okablowanie

---

## Struktura repozytorium

- `src/robot/` – główny kod aplikacji
- `src/robot/sensors/` – obsługa czujników
- `src/robot/loops/` – pętle i logika cykliczna
- `third_party/DFRobot_ENS160/` – biblioteka do obsługi ENS160

---

## Kamera

Projekt jest przygotowany do pracy z kamerą Raspberry Pi Camera Module v3 podłączoną przez interfejs CSI.

Obsługa kamery realizowana jest z poziomu Pythona przy użyciu biblioteki `picamera2`.

Biblioteka wykorzystywana w projekcie:
- picamera2

---

## Uruchamianie

Przed uruchomieniem aplikacji wymagane jest utworzenie środowiska wirtualnego
oraz instalacja zależności Pythona.

```bash
cd ~/robot
source .venv/bin/activate
PYTHONPATH=src:third_party python3 -m robot.main
```

## Automatyczne uruchamianie aplikacji

Aplikacja jest uruchamiana automatycznie po starcie systemu
oraz po podaniu zasilania na płytkę Raspberry Pi.

Mechanizm autostartu zrealizowany jest przy użyciu usługi `systemd`,
która uruchamia aplikację w środowisku wirtualnym Pythona.







