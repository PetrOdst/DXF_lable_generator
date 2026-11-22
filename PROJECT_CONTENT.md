# DXF Label Generator — obsah projektu

## Cíl

Vytvořit jednoduchý generátor DXF štítků pro vstupní tabulku. Uživatel vybere seznam položek a cílovou složku, spustí generování a dostane DXF soubory. Aplikace má být srozumitelná i kolegům bez IT znalostí. Distribuční balíčky jsou určené pro Windows 11 a Linux; zdrojový kód lze spouštět i na macOS.

## Vstupní soubory v repozitáři

- `config.csv` — obecné parametry štítku. Aktuálně používá oddělovač `;` a dvojice klíč/hodnota, například `Width;100mm`, `Heigth;40mm`, `Radius;5mm`, průměr a počet děr, velikost písma a zarovnání.
- `input.example.csv` — anonymní ukázkový vstup se sloupci `ID;Text;Počet`. Pro vlastní práci může uživatel zvolit `input.csv` nebo `.xlsx`; první tři sloupce aktivního listu obsahují ID, text a množství, hlavička je volitelná.
- `lable.dxf` — místní referenční soubor, který se nepřibaluje do veřejného repozitáře ani aplikace.

## Zamýšlený výstup

- Pro každý platný řádek vstupní tabulky vytvořit právě jeden DXF štítek a uložit jej do uživatelem vybrané složky; ve zdrojovém režimu je výchozí `OUTPUTS/`.
- Název souboru má vycházet z ID, textu a množství, například `01_Vstup_2x.dxf`.
- Množství v názvu je instrukce pro operátora stroje, kolikrát má štítek vyrobit/zadat. Neznamená počet DXF souborů ani násobení výstupu.
- Při tvorbě názvů ošetřit znaky nepovolené v názvech souborů a kolize názvů.

## Požadované parametry štítku

Konfigurace má pokrýt rozměr X/Y, poloměr rohů, písmo a jeho velikost, zarovnání textu, počet instalačních otvorů a jejich průměr.

- Požadované umístění otvorů: jejich středy jsou 8 mm od příslušných hran. U čtyř otvorů jsou v rozích obdélníku, 8 mm od každé hrany. U dvou otvorů jsou na protilehlých stranách, 8 mm od levého/pravého okraje a ve vertikálním středu štítku.
- Text bude vypalován/prořezáván skrz materiál. Písmo proto musí být šablonové (stencil), aby vnitřní části znaků zůstaly spojené s okolním materiálem a nevypadly.
- Font má být součástí projektu/aplikace, aby generování nezáviselo na tom, jaká písma má nainstalovaná stanice operátora. Text se převádí na geometrii DXF, čímž zůstávají šablonové můstky zachované.
- Zvolený font: **Stardos Stencil Bold**. Přibal jeho soubor(y) fontu k projektu a generuj text jako geometrii DXF (kontury), aby výstup nezávisel na instalaci fontu u operátora.
- Text štítků tvoří označení potrubí ve formátu jako `E-12` nebo `C-45`; podpora českých znaků není potřeba.
- Ověř čitelnost a šablonové můstky fontu pro používané znaky (písmena, číslice a spojovník). Pokud se objeví nepodporovaný znak, jeho zpracování musí být předvídatelné a nesmí tiše použít náhradní font.
- Před zahájením generování ověř podle skutečných obrysů fontu, že se text vejde do volného prostoru mezi instalačními dírami při zadané velikosti písma. Při neúspěchu uveď ID/text a potřebný i dostupný rozměr.

## Uživatelské rozhraní a distribuce

GUI má mít malý rozsah a zobrazovat:

- počet záznamů nalezených ve vstupní tabulce;
- celkový počet kusů, vypočtený jako součet množství ze všech záznamů;
- výběr vstupní tabulky a výstupní složky; konfigurace se načítá pevně z `config.csv` v kořenové složce projektu a uživatel ji v GUI nevybírá;
- tlačítko **Vygeneruj**;
- průběhový indikátor generování;
- jednoduchý stav **Pracuje** během generování a **Hotovo** po dokončení; závěrečné shrnutí uvede počet vytvořených DXF souborů. Samostatný stav „Chyba“ ani chybové souhrny nejsou v této chvíli požadované. Pokud generování nelze dokončit, zobrazí se chybové okno, aby obsluha věděla, proč soubory nevznikly.

Primárním cílem je jednoduché ovládání. Automatické balíčky pro Windows 11 a Linux se publikují v GitHub Releases. Zdrojový kód zůstává spustitelný i na macOS.

## Dohody pro implementaci

- Zachovej kompatibilitu se stávajícími CSV soubory, případně přidávej validaci a srozumitelné chyby.
- Lokální vstupy, referenční `lable.dxf` a generované výstupy nepublikuj; ve veřejném repozitáři je pouze anonymní `input.example.csv`.
- Při parsování toleruj mezery, české znaky a běžné varianty jednotek (`mm`, `ks`); uvnitř programu pracuj s číselnými hodnotami a jednotky jasně validuj.
- Zachovávej `lable.dxf` jako místní referenční soubor. Výstupy ukládej do uživatelem vybrané složky.
- Nezměňuj výrobní geometrii, měřítko, vrstvy ani textové parametry bez opory v konfiguraci, referenčním DXF nebo potvrzeném zadání.
- Aktualizuj dokumentaci, pokud se změní formát vstupů, výstupní názvy nebo způsob spuštění.

## Otevřené otázky

- Zatím nebyly doplněny další požadavky.

