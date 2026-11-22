"""Small cross-platform GUI for generating pipe label DXF files."""

from __future__ import annotations

import csv
import io
import math
import re
import sys
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import ezdxf
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parent
FONT_PATH = ROOT / "fonts" / "Stardos_Stencil" / "StardosStencil-Bold.ttf"
CONFIG_PATH = ROOT / "config.csv"
if getattr(sys, "frozen", False):
    DEFAULT_INPUT_PATH = ROOT / "input.example.csv"
    DEFAULT_OUTPUT_PATH = Path.home() / "Documents" / "DXF_Label_Generator" / "OUTPUTS"
else:
    local_input = ROOT / "input.csv"
    DEFAULT_INPUT_PATH = local_input if local_input.exists() else ROOT / "input.example.csv"
    DEFAULT_OUTPUT_PATH = ROOT / "OUTPUTS"


@dataclass
class LabelConfig:
    width: float = 100
    height: float = 40
    radius: float = 5
    hole_diameter: float = 6
    hole_count: int = 4
    font_size: float = 12
    hole_offset: float = 8


@dataclass
class Record:
    item_id: str
    text: str
    amount: int


def number(value: str, unit: str = "") -> float:
    value = value.strip().lower()
    if unit:
        value = re.sub(rf"\s*{re.escape(unit)}\s*$", "", value)
    return float(value.replace(",", "."))


def read_csv_rows(path: Path):
    content = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1250"):
        try:
            decoded = content.decode(encoding)
            return list(csv.reader(io.StringIO(decoded), delimiter=";"))
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Soubor {path.name} musí být uložený jako UTF-8 nebo Windows-1250.")


def read_config(path: Path) -> LabelConfig:
    raw: dict[str, str] = {}
    for row in read_csv_rows(path):
        if len(row) >= 2 and row[0].strip():
            raw[re.sub(r"[^a-z]", "", row[0].lower())] = row[1].strip()

    def get(keys: tuple[str, ...], default: str) -> str:
        return next((raw[key] for key in keys if key in raw), default)

    config = LabelConfig(
        width=number(get(("width",), "100mm"), "mm"),
        height=number(get(("height", "heigth"), "40mm"), "mm"),
        radius=number(get(("radius",), "5mm"), "mm"),
        hole_diameter=number(get(("holediameter", "holediametr"), "6mm"), "mm"),
        hole_count=int(number(get(("holeamount",), "4"), "pc")),
        font_size=number(get(("fontsize",), "12"), "mm"),
    )
    if config.width <= 0 or config.height <= 0 or config.font_size <= 0:
        raise ValueError("Rozměry štítku a velikost písma musí být kladné.")
    if config.radius < 0 or 2 * config.radius > min(config.width, config.height):
        raise ValueError("Poloměr rohů neodpovídá rozměrům štítku.")
    if config.hole_count not in (0, 2, 4) or config.hole_diameter <= 0:
        raise ValueError("Počet děr musí být 0, 2 nebo 4 a průměr kladný.")
    if config.hole_count and config.hole_offset * 2 + config.hole_diameter > min(config.width, config.height):
        raise ValueError("Díry se při zadaných rozměrech nevejdou na štítek.")
    return config


def read_records(path: Path) -> list[Record]:
    if path.suffix.lower() == ".xlsx":
        workbook = load_workbook(path, read_only=True, data_only=True)
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
    elif path.suffix.lower() == ".csv":
        rows = read_csv_rows(path)
    else:
        raise ValueError("Vstupní soubor musí být CSV nebo Excel .xlsx.")

    def cell_text(value) -> str:
        if value is None:
            return ""
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value).strip()

    result: list[Record] = []
    try:
        for line_no, row in enumerate(rows, 1):
            row = [cell_text(cell) for cell in row]
            if not row or not any(cell for cell in row):
                continue
            if len(row) < 3 or not row[0] or not row[1]:
                continue
            try:
                amount = int(number(row[2], "ks"))
            except ValueError:
                if line_no == 1 and row[0].lower() in ("id", "číslo", "cislo"):
                    continue
                raise ValueError(f"Řádek {line_no}: množství musí být celé číslo, například 5 ks.")
            if amount < 1:
                raise ValueError(f"Řádek {line_no}: množství musí být alespoň 1.")
            text = row[1]
            if not re.fullmatch(r"[A-Za-z0-9 -]+", text):
                raise ValueError(f"Řádek {line_no}: označení „{text}“ smí obsahovat písmena, číslice, mezery a spojovník.")
            result.append(Record(row[0], text, amount))
    finally:
        if path.suffix.lower() == ".xlsx":
            workbook.close()
    return result


def safe_part(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip()).strip("._-")
    return value or "label"


class OutlinePen(BasePen):
    """Collect closed glyph contours as sampled straight segments."""

    def __init__(self, glyph_set, scale: float):
        super().__init__(glyph_set)
        self.scale = scale
        self.paths: list[list[tuple[float, float]]] = []
        self.path: list[tuple[float, float]] = []
        self.current = (0.0, 0.0)

    def _pt(self, p):
        return (p[0] * self.scale, p[1] * self.scale)

    def _moveTo(self, p):
        if self.path:
            self.paths.append(self.path)
        self.current = p
        self.path = [self._pt(p)]

    def _lineTo(self, p):
        self.path.append(self._pt(p))
        self.current = p

    def _curveToOne(self, p1, p2, p3):
        p0 = self.current
        for step in range(1, 13):
            t = step / 12
            u = 1 - t
            p = tuple(u**3 * p0[i] + 3*u*u*t*p1[i] + 3*u*t*t*p2[i] + t**3*p3[i] for i in (0, 1))
            self.path.append(self._pt(p))
        self.current = p3

    def _qCurveToOne(self, p1, p2):
        p0 = self.current
        for step in range(1, 13):
            t = step / 12
            u = 1 - t
            p = tuple(u*u*p0[i] + 2*u*t*p1[i] + t*t*p2[i] for i in (0, 1))
            self.path.append(self._pt(p))
        self.current = p2

    def _closePath(self):
        if self.path and self.path[-1] != self.path[0]:
            self.path.append(self.path[0])
        if self.path:
            self.paths.append(self.path)
        self.path = []

    def _endPath(self):
        if self.path:
            self.paths.append(self.path)
        self.path = []


def stencil_outlines(text: str, font_path: Path, size: float):
    font = TTFont(str(font_path))
    cmap = font.getBestCmap() or {}
    glyph_set = font.getGlyphSet()
    metrics = font["hmtx"].metrics
    units = font["head"].unitsPerEm
    scale = size / units
    placed_paths: list[tuple[float, list[tuple[float, float]]]] = []
    cursor_x = 0.0
    for char in text:
        glyph_name = cmap.get(ord(char))
        if glyph_name is None:
            raise ValueError(f"Font Stardos Stencil nepodporuje znak „{char}“.")
        pen = OutlinePen(glyph_set, scale)
        glyph_set[glyph_name].draw(pen)
        if pen.path:
            pen.paths.append(pen.path)
        advance = metrics[glyph_name][0] * scale
        placed_paths.extend((cursor_x, path) for path in pen.paths)
        cursor_x += advance

    outline_points = [(x + px, py) for x, path in placed_paths for px, py in path]
    if not outline_points:
        raise ValueError("Text neobsahuje žádné vykreslitelné znaky.")
    min_x = min(point[0] for point in outline_points)
    max_x = max(point[0] for point in outline_points)
    min_y = min(point[1] for point in outline_points)
    max_y = max(point[1] for point in outline_points)
    bounds = (max_x - min_x, max_y - min_y)
    normalized = [[(x + px - min_x, py - min_y) for px, py in path] for x, path in placed_paths]
    return normalized, bounds


def text_clearance(config: LabelConfig) -> tuple[float, float]:
    if config.hole_count in (2, 4):
        inset = config.hole_offset + config.hole_diameter / 2
        clear_height = config.height if config.hole_count == 2 else config.height - 2 * inset
        return config.width - 2 * inset, clear_height
    return config.width, config.height


def validate_text_fits(config: LabelConfig, text: str) -> tuple[float, float]:
    _, text_size = stencil_outlines(text, FONT_PATH, config.font_size)
    clear_width, clear_height = text_clearance(config)
    if text_size[0] > clear_width or text_size[1] > clear_height:
        raise ValueError(
            f"Označení „{text}“ se při velikosti písma {config.font_size:g} mm nevejde mezi díry. "
            f"Text má {text_size[0]:.1f} × {text_size[1]:.1f} mm, volný prostor je "
            f"{clear_width:.1f} × {clear_height:.1f} mm."
        )
    return text_size


def add_stencil_text(msp, text: str, font_path: Path, size: float, width: float, height: float):
    paths, _ = stencil_outlines(text, font_path, size)
    all_points = [point for path in paths for point in path]
    min_x = min(point[0] for point in all_points)
    max_x = max(point[0] for point in all_points)
    min_y = min(point[1] for point in all_points)
    max_y = max(point[1] for point in all_points)
    shift_x = (width - (max_x - min_x)) / 2 - min_x
    shift_y = (height - (max_y - min_y)) / 2 - min_y

    for path in paths:
        points = [(shift_x + px, shift_y + py) for px, py in path]
        if len(points) >= 4:
            msp.add_lwpolyline(points, close=True, dxfattribs={"layer": "CUT"})


def generate_one(config: LabelConfig, record: Record, destination: Path):
    validate_text_fits(config, record.text)
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.layers.new("CUT", dxfattribs={"color": 7})
    msp = doc.modelspace()
    x0, y0 = 0.0, 0.0
    x1, y1 = config.width, config.height
    r = config.radius
    bulge = math.tan(math.pi / 8)
    vertices = [
        (x0 + r, y0, 0), (x1 - r, y0, bulge),
        (x1, y0 + r, 0), (x1, y1 - r, bulge),
        (x1 - r, y1, 0), (x0 + r, y1, bulge),
        (x0, y1 - r, 0), (x0, y0 + r, bulge),
    ]
    msp.add_lwpolyline(vertices, format="xyb", close=True, dxfattribs={"layer": "CUT"})
    d = config.hole_offset
    centers = []
    if config.hole_count == 4:
        centers = [(d, d), (x1-d, d), (x1-d, y1-d), (d, y1-d)]
    elif config.hole_count == 2:
        centers = [(d, y1 / 2), (x1 - d, y1 / 2)]
    for center in centers:
        msp.add_circle(center, config.hole_diameter / 2, dxfattribs={"layer": "CUT"})
    add_stencil_text(msp, record.text, FONT_PATH, config.font_size, config.width, config.height)
    destination.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(destination)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DXF Label Generator")
        self.resizable(False, False)
        self.input_path = tk.StringVar(value=str(DEFAULT_INPUT_PATH))
        self.output_path = tk.StringVar(value=str(DEFAULT_OUTPUT_PATH))
        self.stats = tk.StringVar(value="Načítám vstupní soubory…")
        self.status = tk.StringVar(value="Připraveno")
        frame = ttk.Frame(self, padding=18)
        frame.grid(sticky="nsew")
        ttk.Label(frame, text="Vstupní tabulka").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.input_path, width=46).grid(row=0, column=1, padx=8)
        ttk.Button(frame, text="Vybrat…", command=self.choose_input).grid(row=0, column=2)
        ttk.Label(frame, text="Výstupní složka").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(frame, textvariable=self.output_path, width=46, state="readonly").grid(row=1, column=1, padx=8, pady=(8, 0))
        self.output_button = ttk.Button(frame, text="Vybrat…", command=self.choose_output)
        self.output_button.grid(row=1, column=2, pady=(8, 0))
        ttk.Label(frame, textvariable=self.stats).grid(row=2, column=0, columnspan=3, sticky="w", pady=14)
        self.progress = ttk.Progressbar(frame, mode="determinate", length=420)
        self.progress.grid(row=3, column=0, columnspan=3, sticky="ew")
        ttk.Label(frame, textvariable=self.status).grid(row=4, column=0, columnspan=2, sticky="w", pady=10)
        self.button = ttk.Button(frame, text="Vygeneruj", command=self.generate)
        self.button.grid(row=4, column=2, sticky="e", pady=10)
        self.reload_stats()

    def choose_input(self):
        chosen = filedialog.askopenfilename(filetypes=[("Tabulka CSV nebo Excel", "*.csv *.xlsx"), ("Všechny soubory", "*.*")])
        if chosen:
            self.input_path.set(chosen)
            self.reload_stats()

    def choose_output(self):
        chosen = filedialog.askdirectory(initialdir=self.output_path.get())
        if chosen:
            self.output_path.set(chosen)

    def reload_stats(self):
        try:
            records = read_records(Path(self.input_path.get()))
            self.stats.set(f"Záznamů: {len(records)}    Celkem kusů: {sum(r.amount for r in records)}")
        except Exception as exc:
            self.stats.set(f"Vstup nelze načíst: {exc}")

    def generate(self):
        try:
            config = read_config(CONFIG_PATH)
            records = read_records(Path(self.input_path.get()))
            if not FONT_PATH.is_file():
                raise FileNotFoundError(f"Chybí font projektu: {FONT_PATH}")
            if not records:
                raise ValueError("Vstupní CSV neobsahuje žádné záznamy.")
            for record in records:
                try:
                    validate_text_fits(config, record.text)
                except ValueError as exc:
                    raise ValueError(f"ID {record.item_id}: {exc}") from exc
        except Exception as exc:
            messagebox.showerror("Nelze spustit generování", str(exc))
            return
        output = Path(self.output_path.get())
        self.button.configure(state="disabled")
        self.output_button.configure(state="disabled")
        self.progress.configure(maximum=len(records), value=0)
        self.status.set("Pracuje")

        def worker():
            try:
                for index, record in enumerate(records, 1):
                    name = f"{safe_part(record.item_id)}_{safe_part(record.text)}_{record.amount}x.dxf"
                    destination = output / name
                    if destination.exists():
                        stem, suffix, version = destination.stem, destination.suffix, 2
                        while (output / f"{stem}_{version}{suffix}").exists():
                            version += 1
                        destination = output / f"{stem}_{version}{suffix}"
                    generate_one(config, record, destination)
                    self.after(0, self.progress.configure, {"value": index})
                self.after(0, self.done, len(records), None)
            except Exception as exc:
                self.after(0, self.done, 0, str(exc))

        threading.Thread(target=worker, daemon=True).start()

    def done(self, count: int, error: str | None):
        self.button.configure(state="normal")
        self.output_button.configure(state="normal")
        if error:
            self.status.set("Generování se nezdařilo")
            messagebox.showerror("Generování se nezdařilo", error)
        else:
            self.status.set(f"Hotovo — vytvořeno {count} DXF souborů v {self.output_path.get()}")


if __name__ == "__main__":
    App().mainloop()
