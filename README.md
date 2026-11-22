# DXF Label Generator

Jednoduché GUI pro vytvoření jednoho DXF štítku na každý záznam ve vstupní tabulce. Množství zůstává jen informací pro operátora a je uvedeno v názvu souboru.

**Návod pro obsluhu:** [Uživatelská příručka s obrázky](UZIVATELSKA_PRIRUCKA.md).

## Rychlý návod

1. Připravte CSV nebo Excel `.xlsx` se sloupci **ID**, **Označení** a **Množství**. Například:

   ```text
   ID;Označení;Množství
   1;E-12;2
   2;C-45;1
   ```

2. Spusťte aplikaci a vyberte vstupní tabulku. Zkontrolujte počet záznamů a celkový počet kusů.
3. Vyberte složku pro výstup a stiskněte **Vygeneruj**.
4. Po dokončení najdete ve vybrané složce jeden DXF soubor na každý řádek. Množství v názvu souboru je počet kusů pro obsluhu stroje, ne počet kopií DXF.

Konfigurace štítku se načítá automaticky z `config.csv` dodaného s aplikací. Pokud se text při nastavené velikosti nevejde mezi otvory, aplikace upozorní na záznam, který je třeba upravit.

## Spuštění ze zdrojového kódu

Potřebujete Python 3.10 nebo novější. Na macOS otevřete aplikaci **Terminál** a přejděte do složky projektu. Pokud je projekt ve složce Stažené:

```bash
cd ~/Downloads/DXF_lable_generator
```

Pokud je jinde, napište `cd ` (včetně mezery), přetáhněte složku projektu z Finderu do okna Terminálu a stiskněte Enter.

Vytvořte virtuální prostředí (tento krok stačí udělat jednou):

```bash
python3 -m venv .venv
```

Aktivujte ho. Po aktivaci se na začátku příkazového řádku zobrazí `(.venv)`:

```bash
source .venv/bin/activate
```

Nainstalujte potřebné knihovny (stačí po vytvoření prostředí nebo po změně `requirements.txt`):

```bash
python -m pip install -r requirements.txt
```

Spusťte aplikaci:

```bash
python main.py
```

Až skončíte, můžete prostředí deaktivovat:

```bash
deactivate
```

Při příštím spuštění otevřete Terminál, znovu přejděte do složky projektu a proveďte `source .venv/bin/activate` a `python main.py`. Prostředí znovu vytvářet ani knihovny instalovat nemusíte.

#### Když chybí Tkinter

Grafické rozhraní vyžaduje Tkinter. Dostupnost ověříte po aktivaci prostředí příkazem:

```bash
python -m tkinter
```

Pokud se objeví chyba `No module named '_tkinter'`, vaše instalace Pythonu neobsahuje podporu Tk. Virtuální prostředí ji samo nedoplní; je potřeba nainstalovat Python s podporou Tcl/Tk a potom složku `.venv` znovu vytvořit. Na některých linuxových distribucích je potřeba doinstalovat systémový balíček Tkinter (`python3-tk`).

### Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Konfigurace štítku je soubor `config.csv` přímo v kořenové složce projektu, vedle `main.py`. Aplikace ho používá automaticky; v GUI se nemění. Při spuštění ze zdrojového kódu je výchozí výstupní složka `OUTPUTS/`; v hotové aplikaci je ve složce Dokumenty. V obou případech lze v GUI vybrat jinou.

Projektový font používá tučnou variantu `fonts/Stardos_Stencil/StardosStencil-Bold.ttf`; aplikace převádí text na obrysovou geometrii, takže DXF nezávisí na fontech nainstalovaných u operátora. Licence je přiložena vedle fontu.

## Hotová aplikace pro Windows a Linux

Vydané balíčky budou dostupné na stránce **Releases** repozitáře GitHub. Pro Windows 11 stáhněte `DXF_Label_Generator.exe` a spusťte ho. Pro Linux stáhněte `DXF_Label_Generator-linux-x86_64.tar.gz`, rozbalte archiv a spusťte aplikaci `DXF_Label_Generator`. Linuxová aplikace se sestavuje pro x86-64.

Balíčky obsahují aplikaci, nastavení štítku, ukázkový vstup a potřebný font; Python ani pip není třeba instalovat. Výchozí výstupy hotové aplikace se ukládají do `Dokumenty/DXF_Label_Generator/OUTPUTS`, cílovou složku lze změnit v GUI.

Vstup lze dodat jako CSV se středníkem (`ID;označení;množství`, například `1;E-12;5 ks`) nebo jako Excelový sešit `.xlsx`. CSV může být v UTF-8 nebo Windows-1250 (ANSI ze středoevropského Excelu). Excel se čte z aktivního listu, kde první tři sloupce obsahují ID, označení a množství; hlavička je volitelná. Množství může být číslo nebo text jako `5 ks`. Konfigurace štítku zůstává v CSV se středníkem a dvojicemi `parametr;hodnota`.
