
import sys
import json
import shutil
import os
import pathlib
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QTextEdit, QFileDialog, QListView, QSplitter,
    QComboBox, QMessageBox, QAbstractItemView, QFrame, QStyledItemDelegate,
    QStyleOptionViewItem, QTabWidget
)
from PySide6.QtGui import Qt, QDragEnterEvent, QDropEvent, QDesktopServices, QColor, QFont, QFontMetrics, QPalette, QBrush, QIcon
from PySide6.QtCore import QUrl

RESOURCE_DIR = pathlib.Path(getattr(sys, "_MEIPASS", pathlib.Path(__file__).parent))

def _get_appdata_dir():
    # prefer Windows APPDATA, then XDG_CONFIG_HOME / LOCALAPPDATA, fall back to home
    appdata = os.environ.get("APPDATA") or os.environ.get("XDG_CONFIG_HOME") or os.environ.get("LOCALAPPDATA")
    if appdata:
        return pathlib.Path(appdata)
    return pathlib.Path.home()

# Always use AppData (or fallback) as the persistent storage location
BASE_DIR = _get_appdata_dir() / "MaturitaApp"

# Ensure directory exists; if creation fails, fall back to user home
try:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    BASE_DIR = pathlib.Path.home() / "MaturitaApp"
    BASE_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = BASE_DIR / "maturita_data.json"
ATTACH_DIR = BASE_DIR / "attachments"
ATTACH_DIR.mkdir(parents=True, exist_ok=True)

# Keep APP_DIR pointing to the resource dir so icon loading still works
APP_DIR = RESOURCE_DIR

# keep any existing flag you use
AUTO_SAVE = True

COLOR_BG = "#2b2b2b"
COLOR_TEXT = "#ffffff"
COLOR_ALTERNATE = "#333333"
COLOR_ALTERNATE2 = "#2f2f2f"
COLOR_COMPLETED = "#7CFC00"
COLOR_LIST_SEL = "#3a3a3a"
COLOR_RIGHT_BG = "#252525"
COLOR_SEPARATOR = "#444444"
COLOR_OK = "#7CFC00"
COLOR_BAD = "#ff4d4d"

# (BOOKS + ORIGINAL_20 + RULES remain the same as v předchozím souboru)
# Kopíruju sem pro úplnost — uprav si podle potřeby.

BOOKS = [
    {"author": "Dante Alighieri", "title": "Božská komedie", "genre": "Poezie", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "Giovanni Boccaccio", "title": "Dekameron", "genre": "Próza", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "Jan Amos Komenský", "title": "Labyrint světa a ráj srdce", "genre": "Próza", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "William Shakespeare", "title": "Hamlet", "genre": "Drama", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "Molière", "title": "Lakomec", "genre": "Drama", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "William Shakespeare", "title": "Othello", "genre": "Drama", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "Daniel Defoe", "title": "Robinson Crusoe", "genre": "Próza", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "William Shakespeare", "title": "Romeo a Julie", "genre": "Drama", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "Carlo Goldoni", "title": "Sluha dvou pánů", "genre": "Drama", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "Johann Wolfgang Goethe", "title": "Utrpení mladého Werthera", "genre": "Próza", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "Molière", "title": "Zdravý nemocný", "genre": "Drama", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "William Shakespeare", "title": "Zkrocení zlé ženy", "genre": "Drama", "section": "Světová a česká literatura do konce 18. stol."},

    {"author": "Božena Němcová", "title": "Babička", "genre": "Próza", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Božena Němcová", "title": "Divá Bára", "genre": "Próza", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Viktor Hugo", "title": "Chrám Matky Boží v Paříži", "genre": "Próza", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Karel Havlíček Borovský", "title": "Král Lávra", "genre": "Poezie", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Karel Jaromír Erben", "title": "Kytice", "genre": "Poezie", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Karel Hynek Mácha", "title": "Máj", "genre": "Poezie", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Jaroslav Vrchlický", "title": "Noc na Karlštejně", "genre": "Drama", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Svatopluk Čech", "title": "Pán Brouček - výlet", "genre": "Próza", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Gustave Flaubert", "title": "Paní Bovaryová", "genre": "Próza", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Jan Neruda", "title": "Povídky malostranské", "genre": "Próza", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Nikolaj Vasiljevič Gogol", "title": "Revizor", "genre": "Drama", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Josef Kajetán Tyl", "title": "Strakonický dudák", "genre": "Drama", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Karel Havlíček Borovský", "title": "Tyrolské elegie", "genre": "Poezie", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Edgar Allan Poe", "title": "Vraždy v ulici Morgue", "genre": "Próza", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Božena Němcová", "title": "V zámku a v podzámčí", "genre": "Próza", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Fjodor Michajlovič Dostojevskij", "title": "Zločin a trest", "genre": "Próza", "section": "Světová a česká literatura do konce 19. stol."},

    {"author": "Erich Maria Remarque", "title": "Cesta zpátky", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Mika Waltari", "title": "Egypťan Sinuhet", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "George Orwell", "title": "Farma zvířat", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Joseph Heller", "title": "Hlava XXII", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Alberto Moravia", "title": "Horalka", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Umberto Eco", "title": "Jméno růže", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Gabriel García Márquez", "title": "Kronika ohlášené smrti", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Vladimir Nabokov", "title": "Lolita", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Ray Bradbury", "title": "Marťanská kronika", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Jack Kerouac", "title": "Na cestě", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Erich Maria Remarque", "title": "Na západní frontě klid", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Romain Rolland", "title": "Petr a Lucie", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Ernest Hemingway", "title": "Sbohem, armádo", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Ernest Hemingway", "title": "Stařec a moře", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "William Styron", "title": "Sophiina volba", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Erich Maria Remarque", "title": "Tři kamarádi", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Francis Scott Fitzgerald", "title": "Veliký Gatsby", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},

    {"author": "Michal Viewegh", "title": "Báječná léta pod psa", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Karel Čapek", "title": "Bílá nemoc", "genre": "Drama", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Karel Poláček", "title": "Bylo nás pět", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Zdeněk Svěrák a Ladislav Smoljak", "title": "České nebe", "genre": "Drama", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Ota Pavel", "title": "Jak jsem potkal ryby", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Květa Legátová", "title": "Jozova Hanule", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Pavel Kohout", "title": "Katyně", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Viktor Dyk", "title": "Krysař", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Vítězslav Nezval", "title": "Manon Lescaut", "genre": "Drama", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Vladislav Vančura", "title": "Markéta Lazarová", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Radek John", "title": "Memento", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Arnošt Lustig", "title": "Modlitba pro Kateřinu Horovitzovou", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Rudolf Křesťan", "title": "Myš v 11. patře", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Ivan Olbracht", "title": "Nikola Šuhaj loupežník", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Bohumil Hrabal", "title": "Obsluhoval jsem anglického krále", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Bohumil Hrabal", "title": "Ostře sledované vlaky", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Jaroslav Hašek", "title": "Osudy dobrého vojáka Švejka za světové války", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Karel Čapek", "title": "Povídky z jedné a druhé kapsy", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Franz Kafka", "title": "Proměna", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Jan Otčenášek", "title": "Romeo, Julie a tma", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Karel Čapek", "title": "R.U.R.", "genre": "Drama", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Petr Bezruč", "title": "Slezské písně", "genre": "Poezie", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Ota Pavel", "title": "Smrt krásných srnců", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Ladislav Fuks", "title": "Spalovač mrtvol", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Michal Viewegh", "title": "Švédské stoly aneb Jací jsme", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Karel Čapek", "title": "Trapné povídky", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Michal Viewegh", "title": "Účastníci zájezdu", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Karel Čapek", "title": "Válka s Mloky", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Karel Čapek", "title": "Výlet do Španěl", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Josef Škvorecký", "title": "Zbabělci", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Viktor Dyk", "title": "Zmoudření Dona Quijota", "genre": "Drama", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Milan Kundera", "title": "Žert", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
]

ORIGINAL_20 = [
    {"author": "Molière", "title": "Lakomec", "genre": "Drama", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "Carlo Goldoni", "title": "Sluha dvou pánů", "genre": "Drama", "section": "Světová a česká literatura do konce 18. stol."},
    {"author": "Božena Němcová", "title": "Babička", "genre": "Próza", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Karel Havlíček Borovský", "title": "Král Lávra", "genre": "Poezie", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Karel Jaromír Erben", "title": "Kytice", "genre": "Poezie", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Nikolaj Vasiljevič Gogol", "title": "Revizor", "genre": "Drama", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Karel Havlíček Borovský", "title": "Tyrolské elegie", "genre": "Poezie", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Edgar Allan Poe", "title": "Vraždy v ulici Morgue", "genre": "Próza", "section": "Světová a česká literatura do konce 19. stol."},
    {"author": "Erich Maria Remarque", "title": "Cesta zpátky", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Erich Maria Remarque", "title": "Na západní frontě klid", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Romain Rolland", "title": "Petr a Lucie", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Francis Scott Fitzgerald", "title": "Veliký Gatsby", "genre": "Próza", "section": "Světová literatura 20. a 21. stol."},
    {"author": "Zdeněk Svěrák a Ladislav Smoljak", "title": "České nebe", "genre": "Drama", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Ota Pavel", "title": "Jak jsem potkal ryby", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Bohumil Hrabal", "title": "Obsluhoval jsem anglického krále", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Bohumil Hrabal", "title": "Ostře sledované vlaky", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Jaroslav Hašek", "title": "Osudy dobrého vojáka Švejka za světové války", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Franz Kafka", "title": "Proměna", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Karel Čapek", "title": "R.U.R.", "genre": "Drama", "section": "Česká literatura 20. a 21. stol."},
    {"author": "Ota Pavel", "title": "Smrt krásných srnců", "genre": "Próza", "section": "Česká literatura 20. a 21. stol."},
]

RULES = {
    "total": 20,
    "section_counts": {
        "Světová a česká literatura do konce 18. stol.": 2,
        "Světová a česká literatura do konce 19. stol.": 3,
        "Světová literatura 20. a 21. stol.": 4,
        "Česká literatura 20. a 21. stol.": 5,
    },
    "genre_min_each": 2,
    "max_per_author": 2,
}

# ---------- persistence helpers (upraveno) ----------
def make_id(item: Dict):
    key = f"{item['author']}|{item['title']}"
    return quote(key, safe='')

def load_state() -> Tuple[Dict[str, dict], Optional[List[str]]]:
    """
    Vrací (entries, custom_selection).
    - entries: mapping id -> {completed, notes, attachments}
    - custom_selection: seznam id nebo None
    Tento formát je tolerantní i k dřívějšímu souboru (pokud byl uložen pouze dict entries).
    """
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict) and "entries" in raw:
                entries = raw.get("entries", {})
                custom = raw.get("custom_selection")
                return entries, custom
            else:
                # starý formát: celý file je entries dict
                return raw, None
        except Exception:
            return {}, None
    return {}, None

def save_state(entries: Dict[str, dict], custom_selection: Optional[List[str]] = None):
    """
    Uloží do DATA_FILE objekt { entries: {...}, custom_selection: [...] }
    """
    data = {"entries": entries}
    if custom_selection is not None:
        data["custom_selection"] = custom_selection
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# (ostatní utility: copy_attachment, NotesEdit, KeepColorDelegate - beze změny)
def copy_attachment(src_path: str) -> str:
    src = pathlib.Path(src_path)
    if not src.exists():
        raise FileNotFoundError(src_path)
    dest = ATTACH_DIR / src.name
    base = dest.stem
    ext = dest.suffix
    i = 1
    while dest.exists():
        dest = ATTACH_DIR / f"{base}_{i}{ext}"
        i += 1
    shutil.copy2(src, dest)
    return dest.name

class NotesEdit(QTextEdit):
    def __init__(self, parent=None, on_files_dropped=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.on_files_dropped = on_files_dropped

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        paths = [u.toLocalFile() for u in urls if u.isLocalFile()]
        if paths and self.on_files_dropped:
            self.on_files_dropped(paths)
        event.acceptProposedAction()

class KeepColorDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        fg = index.data(Qt.ForegroundRole)
        color = None
        if isinstance(fg, QBrush):
            color = fg.color()
        elif isinstance(fg, QColor):
            color = fg
        elif isinstance(fg, str):
            color = QColor(fg)
        if color:
            opt.palette.setColor(QPalette.Text, color)
            opt.palette.setColor(QPalette.HighlightedText, color)
        super().paint(painter, opt, index)

# ---------------------------
# MainWindow (hlavní změny: načítání/ukládání custom_selection)
# ---------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maturita")
        ico = APP_DIR / "icon.ico"
        if ico.exists():
            self.setWindowIcon(QIcon(str(ico)))

        entries, custom = load_state()
        self.state = entries or {}
        self.custom_selection = custom  # bude buď seznam id nebo None

        # ensure state entries for all BOOKS + ORIGINAL_20
        for b in BOOKS + ORIGINAL_20:
            bid = make_id(b)
            if bid not in self.state:
                self.state[bid] = {"completed": False, "notes": "", "attachments": []}

        self.current_id = None

        self.build_ui()
        self.apply_styles()

        # pokud existuje uložený custom_selection a lze ho sestavit, použij ho; jinak ORIGINAL_20
        if self.custom_selection:
            selected_books = []
            for bid in self.custom_selection:
                # najdeme odpovídající objekt v BOOKS / ORIGINAL_20
                for b in BOOKS + ORIGINAL_20:
                    if make_id(b) == bid:
                        selected_books.append(b)
                        break
            if len(selected_books) == RULES['total']:
                self.populate_list(selected_books)
            else:
                # nevalidní uložený seznam -> fallback
                self.custom_selection = None
                self.populate_list(ORIGINAL_20)
        else:
            self.populate_list(ORIGINAL_20)

    # (zbytek MainWindow je stejný jako předtím, jen všechny volání save_state(...) změněny tak,
    # aby posílaly self.custom_selection jako druhý argument)

    # ... (pro přehlednost vkládám zbytek beze změn, ale s aktualizovanými save_state voláními) ...

    def build_ui(self):
        root = QVBoxLayout(self)
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        # --- hlavní tab ---
        tab_main = QWidget()
        tlay = QVBoxLayout(tab_main)
        top = QHBoxLayout()
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["-- Řadit podle --", "Autor", "Název", "Žánr", "Oddíl"])
        self.sort_combo.currentIndexChanged.connect(self.on_sort_changed)
        top.addWidget(self.sort_combo)
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Vše", "Dokončené", "Nedokončené"])
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        top.addWidget(self.filter_combo)
        top.addStretch()
        tlay.addLayout(top)

        splitter = QSplitter(Qt.Horizontal)
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list.itemClicked.connect(self.on_list_select)
        self.list.setUniformItemSizes(True)
        self.list.setViewMode(QListView.ListMode)
        self.list.setSpacing(2)
        self.list.setItemDelegate(KeepColorDelegate(self.list))
        splitter.addWidget(self.list)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)
        sep.setStyleSheet(f"color: {COLOR_SEPARATOR}; background: {COLOR_SEPARATOR};")
        splitter.addWidget(sep)

        detail_widget = QWidget()
        dlay = QVBoxLayout(detail_widget)
        self.lbl_title = QLabel("Vyber dílo vlevo")
        self.lbl_title.setWordWrap(True)
        self.lbl_title.setStyleSheet("font-weight: bold; font-size: 15pt; color: " + COLOR_TEXT)
        dlay.addWidget(self.lbl_title)

        btn_row = QHBoxLayout()
        self.btn_completed = QPushButton("Označit jako dokončené")
        self.btn_completed.clicked.connect(self.toggle_completed)
        btn_row.addWidget(self.btn_completed)
        self.btn_attach_add = QPushButton("Přidat soubor")
        self.btn_attach_add.clicked.connect(self.add_attachment_via_dialog)
        btn_row.addWidget(self.btn_attach_add)
        btn_row.addStretch()
        dlay.addLayout(btn_row)

        self.notes = NotesEdit(on_files_dropped=self.handle_files_dropped)
        self.notes.setPlaceholderText("Poznámky k dílu... (sem lze také přetahovat soubory)")
        self.notes.textChanged.connect(self.on_notes_changed)
        dlay.addWidget(self.notes, 1)

        dlay.addWidget(QLabel("Přílohy:"))
        from PySide6.QtWidgets import QListWidget as QLW
        self.attach_list = QLW()
        self.attach_list.itemDoubleClicked.connect(self.open_attachment)
        dlay.addWidget(self.attach_list, 1)

        self.status = QLabel("")
        dlay.addWidget(self.status)

        splitter.addWidget(detail_widget)
        splitter.setSizes([520, 10, 480])
        tlay.addWidget(splitter)
        tab_main.setLayout(tlay)
        self.tabs.addTab(tab_main, "Seznam")

        # --- DIY tab ---
        tab_diy = QWidget()
        dlay_root = QHBoxLayout(tab_diy)
        left = QWidget()
        left_v = QVBoxLayout(left)
        left_v.addWidget(QLabel("Vyberte položky (zaškrtněte) - seznam se bude live validovat:"))
        self.diy_list = QListWidget()
        self.diy_list.setSelectionMode(QAbstractItemView.NoSelection)
        self.diy_list.itemChanged.connect(self.on_diy_item_changed)
        left_v.addWidget(self.diy_list, 1)
        btns_left = QHBoxLayout()
        self.btn_select_all = QPushButton("Vybrat vše")
        self.btn_select_all.clicked.connect(self.diy_select_all)
        btns_left.addWidget(self.btn_select_all)
        self.btn_clear_all = QPushButton("Zrušit výběr")
        self.btn_clear_all.clicked.connect(self.diy_clear_all)
        btns_left.addWidget(self.btn_clear_all)
        left_v.addLayout(btns_left)
        dlay_root.addWidget(left, 1)

        right = QWidget()
        r_v = QVBoxLayout(right)
        r_v.addWidget(QLabel("Kontrola pravidel (živě):"))
        self.rule_labels = {}
        self.rule_labels['total'] = QLabel("")
        r_v.addWidget(self.rule_labels['total'])
        for sec in RULES['section_counts'].keys():
            self.rule_labels[sec] = QLabel("")
            r_v.addWidget(self.rule_labels[sec])
        self.rule_labels['genre'] = QLabel("")
        r_v.addWidget(self.rule_labels['genre'])
        self.rule_labels['author'] = QLabel("")
        r_v.addWidget(self.rule_labels['author'])

        r_v.addWidget(QLabel("Náhled vybraného seznamu:"))
        self.preview = QListWidget()
        r_v.addWidget(self.preview, 1)

        actions = QHBoxLayout()
        self.btn_save_list = QPushButton("Uložit seznam (přepsat hlavní seznam)")
        self.btn_save_list.clicked.connect(self.save_custom_list)
        self.btn_save_list.setEnabled(False)
        actions.addWidget(self.btn_save_list)
        self.btn_reset_main = QPushButton("Obnovit původních 20")
        self.btn_reset_main.clicked.connect(self.reset_to_full_list)
        actions.addWidget(self.btn_reset_main)
        r_v.addLayout(actions)

        dlay_root.addWidget(right, 1)
        tab_diy.setLayout(dlay_root)
        self.tabs.addTab(tab_diy, "Vytvořit vlastní seznam (DIY)")

        self.setLayout(root)
        self.list.setItemDelegate(KeepColorDelegate(self.list))
        self.populate_diy_list()

    def apply_styles(self):
        style = f"""
            QWidget {{ background: {COLOR_BG}; color: {COLOR_TEXT}; }}
            QListWidget {{ background: {COLOR_BG}; border: none; outline: none; }}
            QListWidget::item {{ padding: 8px; outline: none; }}
            QListWidget::item:selected {{ background: {COLOR_LIST_SEL}; }}
            QTextEdit {{ background: {COLOR_RIGHT_BG}; color: {COLOR_TEXT}; border: 1px solid {COLOR_SEPARATOR}; }}
            QPushButton {{ background: #3a3a3a; color: {COLOR_TEXT}; border-radius: 4px; padding: 6px; }}
            QLabel {{ color: {COLOR_TEXT}; }}
            QWidget:focus {{ outline: none; }}
            QPushButton:focus {{ outline: none; }}
            QListWidget::item:focus {{ outline: none; }}
        """
        self.setStyleSheet(style)

    def auto_size_to_list(self):
        app = QApplication.instance()
        screen = app.primaryScreen()
        screen_geom = screen.availableGeometry()
        screen_h = screen_geom.height()
        total_items = len(BOOKS)
        if self.list.count() > 0:
            item_height = self.list.sizeHintForRow(0) + self.list.spacing()
            if item_height <= 0:
                fm = QFontMetrics(self.list.font())
                item_height = fm.height() + 14
        else:
            fm = QFontMetrics(self.list.font())
            item_height = fm.height() + 14
        desired_list_height = total_items * item_height + 40
        chrome = 140
        desired_total = desired_list_height + chrome
        max_allowed = int(screen_h * 0.90)
        final_height = min(desired_total, max_allowed)
        final_width = 1100
        self.resize(final_width, max(480, int(final_height)))

    def showEvent(self, event):
        super().showEvent(event)

        # ensure size is computed first
        self.auto_size_to_list()

        # get available geometry of the primary screen (taskbar excluded)
        screen = QApplication.instance().primaryScreen()
        avail = screen.availableGeometry()

        # if window is larger than available area, shrink it to fit
        new_w = min(self.width(), avail.width())
        new_h = min(self.height(), avail.height())
        if new_w != self.width() or new_h != self.height():
            self.resize(new_w, new_h)

        # center within available geometry
        x = avail.x() + (avail.width() - new_w) // 2
        y = avail.y() + (avail.height() - new_h) // 2

        # clamp so window doesn't go off-screen
        x = max(avail.x(), min(x, avail.x() + avail.width() - new_w))
        y = max(avail.y(), min(y, avail.y() + avail.height() - new_h))

        self.move(x, y)

    def populate_list(self, books_order: List[Dict]=None):
        self.list.clear()
        self.current_list_books = []
        if books_order is None:
            books_iter = ORIGINAL_20
        else:
            books_iter = []
            for el in books_order:
                if isinstance(el, dict):
                    books_iter.append(el)
                else:
                    for b in BOOKS + ORIGINAL_20:
                        if make_id(b) == el:
                            books_iter.append(b)
                            break
        for idx, b in enumerate(books_iter):
            display = f"{b['author']} — {b['title']}"
            item = QListWidgetItem(display)
            item.setToolTip(f"{b['genre']} — {b['section']}")
            item.setData(Qt.UserRole, make_id(b))
            completed = self.state.get(make_id(b), {}).get("completed", False)
            item.setForeground(QColor(COLOR_COMPLETED if completed else COLOR_TEXT))
            bg = QColor(COLOR_ALTERNATE if (idx % 2 == 0) else COLOR_ALTERNATE2)
            item.setBackground(bg)
            f = QFont()
            f.setPointSize(10)
            item.setFont(f)
            self.list.addItem(item)
            self.current_list_books.append(b)
        self.list.setItemDelegate(KeepColorDelegate(self.list))

    def refresh_list_colors(self):
        for i in range(self.list.count()):
            item = self.list.item(i)
            bid = item.data(Qt.UserRole)
            completed = self.state.get(bid, {}).get("completed", False)
            item.setForeground(QColor(COLOR_COMPLETED if completed else COLOR_TEXT))

    def on_list_select(self, item: QListWidgetItem):
        bid = item.data(Qt.UserRole)
        book = None
        for b in BOOKS + ORIGINAL_20:
            if make_id(b) == bid:
                book = b
                break
        if not book:
            return
        self.current_id = bid
        self.lbl_title.setText(f"{book['author']} — {book['title']}\n{book['genre']} — {book['section']}")
        completed = self.state.get(bid, {}).get("completed", False)
        self.update_completed_button_text(completed)
        notes_text = self.state.get(bid, {}).get("notes", "")
        attachments = self.state.get(bid, {}).get("attachments", [])
        self.notes.blockSignals(True)
        self.notes.setPlainText(notes_text)
        self.notes.blockSignals(False)
        self.reload_attachments(attachments)
        self.refresh_list_colors()

    def update_completed_button_text(self, completed):
        if completed:
            self.btn_completed.setText("Označit jako nedokončené")
        else:
            self.btn_completed.setText("Označit jako dokončené")

    def toggle_completed(self):
        if not self.current_id:
            return
        entry = self.state.setdefault(self.current_id, {"completed": False, "notes": "", "attachments": []})
        entry["completed"] = not entry.get("completed", False)
        self.update_completed_button_text(entry["completed"])
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item.data(Qt.UserRole) == self.current_id:
                item.setForeground(QColor(COLOR_COMPLETED if entry["completed"] else COLOR_TEXT))
                break
        self.status.setText("Změněno: dokončené" if entry["completed"] else "Změněno: nedokončené")
        if AUTO_SAVE:
            save_state(self.state, self.custom_selection)
        self.refresh_list_colors()

    def on_notes_changed(self):
        if not self.current_id:
            return
        self.state.setdefault(self.current_id, {"completed": False, "notes": "", "attachments": []})
        self.state[self.current_id]["notes"] = self.notes.toPlainText()
        self.status.setText("Poznámky změněny")
        if AUTO_SAVE:
            save_state(self.state, self.custom_selection)

    def reload_attachments(self, attachments: List[str]):
        self.attach_list.clear()
        for fn in attachments:
            it = QListWidgetItem(fn)
            it.setToolTip(str(ATTACH_DIR / fn))
            self.attach_list.addItem(it)

    def add_attachment_via_dialog(self):
        if not self.current_id:
            QMessageBox.warning(self, "Chyba", "Nejprve vyber dílo.")
            return
        paths, _ = QFileDialog.getOpenFileNames(self, "Vyber soubor(y) k přidání")
        if not paths:
            return
        self.handle_files_dropped(paths)

    def handle_files_dropped(self, paths: List[str]):
        if not self.current_id:
            QMessageBox.warning(self, "Chyba", "Nejprve vyber dílo.")
            return
        entry = self.state.setdefault(self.current_id, {"completed": False, "notes": "", "attachments": []})
        added = []
        for p in paths:
            try:
                newname = copy_attachment(p)
                entry["attachments"].append(newname)
                added.append(newname)
            except Exception as e:
                QMessageBox.warning(self, "Chyba kopírování", f"Nelze zkopírovat {p}:\n{e}")
        self.reload_attachments(entry["attachments"])
        self.status.setText(f"Přidáno {len(added)} souborů")
        if AUTO_SAVE:
            save_state(self.state, self.custom_selection)

    def open_attachment(self, item: QListWidgetItem):
        fn = item.text()
        full = ATTACH_DIR / fn
        if full.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(full)))
        else:
            QMessageBox.warning(self, "Soubor nenalezen", f"Připojený soubor nenalezen:\n{full}")

    def on_sort_changed(self, idx):
        option = self.sort_combo.currentText()
        if option == "-- Řadit podle --":
            ordered = ORIGINAL_20 if self.custom_selection is None else self.current_list_books
        else:
            key_map = {"Autor": "author", "Název": "title", "Žánr": "genre", "Oddíl": "section"}
            key = key_map.get(option, None)
            if not key:
                ordered = ORIGINAL_20
            else:
                ordered = sorted(self.current_list_books if self.current_list_books else ORIGINAL_20, key=lambda b: b[key].lower())

        filt = self.filter_combo.currentText()
        if filt == "Dokončené":
            ordered = [b for b in ordered if self.state.get(make_id(b), {}).get("completed", False)]
        elif filt == "Nedokončené":
            ordered = [b for b in ordered if not self.state.get(make_id(b), {}).get("completed", False)]

        self.populate_list(ordered)

    def on_filter_changed(self, idx):
        self.on_sort_changed(self.sort_combo.currentIndex())

    def populate_diy_list(self):
        self.diy_list.clear()
        for b in BOOKS:
            it = QListWidgetItem(f"{b['author']} — {b['title']} ({b['genre']})")
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Unchecked)
            it.setData(Qt.UserRole, make_id(b))
            it.setToolTip(f"{b['section']}")
            self.diy_list.addItem(it)
        # pokud jsme načetli custom_selection, předvyplníme checkboxy
        if self.custom_selection:
            ids = set(self.custom_selection)
            for i in range(self.diy_list.count()):
                it = self.diy_list.item(i)
                if it.data(Qt.UserRole) in ids:
                    it.setCheckState(Qt.Checked)
        self.update_diy_validation()

    def diy_select_all(self):
        for i in range(self.diy_list.count()):
            it = self.diy_list.item(i)
            it.setCheckState(Qt.Checked)

    def diy_clear_all(self):
        for i in range(self.diy_list.count()):
            it = self.diy_list.item(i)
            it.setCheckState(Qt.Unchecked)

    def on_diy_item_changed(self, item: QListWidgetItem):
        self.update_diy_validation()

    def get_selected_ids_from_diy(self) -> List[str]:
        sel = []
        for i in range(self.diy_list.count()):
            it = self.diy_list.item(i)
            if it.checkState() == Qt.Checked:
                sel.append(it.data(Qt.UserRole))
        return sel

    def update_diy_validation(self):
        sel_ids = self.get_selected_ids_from_diy()
        sel_books = [b for b in BOOKS if make_id(b) in sel_ids]

        total_ok = len(sel_books) == RULES['total']
        total_text = f"Celkem vybráno: {len(sel_books)} / {RULES['total']}"
        self.rule_labels['total'].setText(total_text)
        self.rule_labels['total'].setStyleSheet("color: "+ (COLOR_OK if total_ok else COLOR_BAD))

        for sec, needed in RULES['section_counts'].items():
            have = sum(1 for b in sel_books if b['section'] == sec)
            ok = have >= needed
            self.rule_labels[sec].setText(f"{sec}: {have} (min {needed})")
            self.rule_labels[sec].setStyleSheet("color: "+ (COLOR_OK if ok else COLOR_BAD))

        genres_required = RULES['genre_min_each']
        genre_counts = {}
        for b in sel_books:
            g = b['genre'].capitalize()
            genre_counts[g] = genre_counts.get(g, 0) + 1
        for g in ["Próza", "Poezie", "Drama"]:
            if g not in genre_counts:
                genre_counts[g] = 0
        genre_ok = all(genre_counts[g] >= genres_required for g in ["Próza", "Poezie", "Drama"])
        self.rule_labels['genre'].setText(f"Žánry: Próza {genre_counts['Próza']}, Poezie {genre_counts['Poezie']}, Drama {genre_counts['Drama']} (min {genres_required} každá)")
        self.rule_labels['genre'].setStyleSheet("color: "+ (COLOR_OK if genre_ok else COLOR_BAD))

        author_counts = {}
        for b in sel_books:
            a = b['author']
            author_counts[a] = author_counts.get(a, 0) + 1
        author_ok = all(count <= RULES['max_per_author'] for count in author_counts.values())
        bad_authors = [f"{a} ({c})" for a,c in author_counts.items() if c > RULES['max_per_author']]
        if author_ok:
            self.rule_labels['author'].setText(f"Autoři: max {RULES['max_per_author']} od jednoho autora (OK)")
            self.rule_labels['author'].setStyleSheet("color: "+COLOR_OK)
        else:
            self.rule_labels['author'].setText("Překročení max. děl od autora: " + ", ".join(bad_authors))
            self.rule_labels['author'].setStyleSheet("color: "+COLOR_BAD)

        sections_ok = all((sum(1 for b in sel_books if b['section']==sec) >= need) for sec, need in RULES['section_counts'].items())

        all_ok = total_ok and genre_ok and author_ok and sections_ok
        self.btn_save_list.setEnabled(all_ok)

        self.preview.clear()
        for b in sel_books:
            it = QListWidgetItem(f"{b['author']} — {b['title']} ({b['genre']})")
            self.preview.addItem(it)

    def save_custom_list(self):
        sel_ids = self.get_selected_ids_from_diy()
        if len(sel_ids) != RULES['total']:
            QMessageBox.warning(self, "Chyba", f"Musíte vybrat přesně {RULES['total']} děl.")
            return
        self.custom_selection = sel_ids.copy()
        selected_books_in_order = []
        for i in range(self.diy_list.count()):
            it = self.diy_list.item(i)
            if it.checkState() == Qt.Checked:
                bid = it.data(Qt.UserRole)
                for b in BOOKS:
                    if make_id(b) == bid:
                        selected_books_in_order.append(b)
                        break
        # přepíš hlavní a ulož custom_selection trvale
        self.populate_list(selected_books_in_order)
        save_state(self.state, self.custom_selection)
        QMessageBox.information(self, "Hotovo", "Vlastní seznam byl uložen a hlavní seznam byl přepnuto a uloženo.")
        self.tabs.setCurrentIndex(0)

    def reset_to_full_list(self):
        self.custom_selection = None
        self.populate_list(ORIGINAL_20)
        save_state(self.state, None)
        QMessageBox.information(self, "Obnovení", "Hlavní seznam byl obnoven na původních 20 děl.")

# ---------------------------
def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
