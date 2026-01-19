# Autoclicker (Windows)

Ein einfacher Autoclicker für Windows, geschrieben in Python (ohne externe Abhängigkeiten).

## Voraussetzungen

- Windows 10/11
- Python 3.9+

## Nutzung

```bash
python autoclicker.py --interval 0.1 --count 100 --button left --delay 3
```

### Als ausführbare Datei (Windows)

Du kannst das Script über die Batch-Datei starten:

```bash
run_autoclicker.bat --gui
```

Die Batch-Datei leitet alle Argumente an das Python-Skript weiter.

### Overlay (GUI)

```bash
python autoclicker.py --gui
```

Im Overlay kannst du einstellen:

- Anzahl der Klicks (0 = unendlich)
- Abstand in Millisekunden
- Taste (left/right)

**Optionen**

- `--interval`: Sekunden zwischen Klicks (Standard: `0.1`)
- `--count`: Anzahl der Klicks (`0` = unendlich)
- `--button`: `left` oder `right`
- `--delay`: Startverzögerung in Sekunden (Standard: `3.0`)
- `--gui`: Overlay öffnen, um Klicks interaktiv zu konfigurieren

Stoppen mit `Strg + C`.
