# Volební Data CLI

Tento projekt poskytuje CLI nástroj pro zpracování volebních dat z webové stránky a jejich export do CSV. Nástroj umožňuje stahovat data jednotlivých obcí, analyzovat volební výsledky a ukládat je ve strukturovaném formátu.

---

## Funkcionalita

1. **Stahování dat obcí**: Z hlavní stránky stáhne URL jednotlivých obcí a jejich volební data.
2. **Export do CSV**: Uloží zpracovaná data do CSV souboru.
3. **Vypisování seznamu URL obcí**: Vypíše seznam URL jednotlivých obcí na základě zadané stránky.

---

## Instalace

1. Naklonujte tento projekt:
   ```bash
   git clone https://github.com/uzivatel/volebni-data-cli.git
   cd volebni-data-cli
   ```

2. Vytvořte virtuální prostředí a aktivujte jej:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux / macOS
   venv\Scripts\activate     # Windows
   ```

3. Nainstalujte požadované balíčky:
   ```bash
   pip install -r requirements.txt
   ```

---

## Použití

CLI nástroj obsahuje dva hlavní příkazy: `fetch-data` a `list-towns`.

### 1. Stažení a export dat do CSV
Tento příkaz stáhne data obcí a uloží je do zadaného CSV souboru.

```bash
python cli.py fetch-data <URL> <OUTPUT_PATH>
```

**Příklady:**
- Stažení dat a uložení do `output.csv`:
  ```bash
  python cli.py fetch-data "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" "output.csv"
  ```

### 2. Výpis URL jednotlivých obcí
Tento příkaz vypíše seznam URL obcí na základě hlavní stránky.

```bash
python cli.py list-towns <URL>
```

**Příklady:**
- Výpis URL obcí:
  ```bash
  python cli.py list-towns "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"
  ```

---

## Struktura Projektu

```
volebni-data-cli/
│
├── cli.py                     # CLI rozhraní projektu
├── your_module.py             # Logika pro zpracování volebních dat
├── requirements.txt           # Seznam požadovaných knihoven
└── README.md                  # Dokumentace projektu
```

---

## Požadované knihovny

Seznam požadovaných knihoven je uveden v souboru `requirements.txt`. Tento projekt využívá:

- **Click**: Pro tvorbu CLI.
- **Requests**: Pro stahování HTML obsahu.
- **BeautifulSoup4**: Pro analýzu HTML.
- **Loguru**: Pro logování.
- **Pathlib**: Pro manipulaci s cestami.

Nainstalujte knihovny pomocí:
```bash
pip install -r requirements.txt
```

---

## Příklady CSV Výstupu

CSV soubor obsahuje sloupce:
- `town_code`: Kód obce.
- `town_name`: Název obce.
- `registered_voters`: Počet registrovaných voličů.
- `envelopes_count`: Počet odevzdaných obálek.
- `valid_votes`: Počet platných hlasů.
- Každý další sloupec reprezentuje stranu a počet hlasů.

Příklad:
```csv
town_code,town_name,registered_voters,envelopes_count,valid_votes,Party A,Party B
590185,Example Town,1500,1200,1180,600,580
```

---

## Debugging

Pro podrobné logování přidejte volbu `DEBUG` do prostředí:
```bash
export LOGURU_LEVEL=DEBUG  # Linux / macOS
set LOGURU_LEVEL=DEBUG     # Windows
```

---

## Testování

Testy můžete spustit pomocí `pytest`:
1. Nainstalujte `pytest`:
   ```bash
   pip install pytest
   ```

2. Spusťte testy:
   ```bash
   pytest
   ```

---
