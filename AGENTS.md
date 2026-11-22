# Pokyny pro práci v tomto repozitáři

## Kontext

Jde o projekt generátoru DXF štítků z CSV konfigurace a tabulky položek. Popis záměru, známých vstupů a nevyřešených požadavků je v `PROJECT_CONTENT.md`; před změnou formátu nebo geometrie se s ním seznam.

## Práce se soubory

- Zachovávej `input.csv`, `config.csv` a `lable.dxf`, pokud úkol výslovně nepožaduje jejich úpravu.
- `lable.dxf` považuj za referenční uživatelský soubor. Neformátuj jej, nepřepisuj ani nepoužívej jako výstupní soubor.
- Generované DXF soubory ukládej do uživatelem vybrané složky (ve zdrojovém režimu výchozí `OUTPUTS/`).
- CSV soubory používají středník jako oddělovač a obsahují český text i hodnoty s jednotkami. Při čtení zachovávej UTF-8 a ošetři okolní mezery.
- Konfigurace se načítá pevně z `config.csv` v kořenové složce projektu; vstupní tabulku a výstupní složku vybírá uživatel v GUI.
- Nevymýšlej chybějící výrobní parametry (zejména polohy děr, font nebo geometrii) bez jasných instrukcí.

## Implementace

- Upřednostňuj jednoduché a srozumitelné řešení pro uživatele bez technických znalostí.
- Vstupy validuj před generováním; chyby formuluj česky, konkrétně a s označením problematického souboru/řádku/hodnoty.
- Distribuční balíčky cílí na Windows 11 a Linux; zdrojový kód má zůstat spustitelný i na macOS. Nepřidávej platformově specifické cesty bez důvodu.
- Při tvorbě názvů souborů bezpečně zpracuj diakritiku, mezery a znaky nepovolené operačním systémem. Zabraň nechtěnému přepsání existujících výstupů.
- Názvy DXF tvoř ve formátu `MNOŽSTVÍx_OZNAČENÍ.dxf`; ID položky do názvu nezahrnuj.
- Udržuj dokumentaci v souladu s implementací; požadavky a nejistoty zaznamenávej v `PROJECT_CONTENT.md`.

## Ověřování

- Po změnách ověř relevantní chování a uveď, co bylo ověřeno.
- DXF výstup musí zůstat otevřitelný a zachovat očekávané jednotky, rozměry a geometrii.
- Při kontrole diffu věnuj zvláštní pozornost tomu, že se referenční `lable.dxf` ani vstupní tabulky nezměnily neúmyslně.
