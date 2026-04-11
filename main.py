import sys
import re
import math
import json
import random
import string
import os
from PySide6.QtCore import Qt, Signal, QSize, QTimer, QSettings
from PySide6.QtGui import (
    QColor, QPainter, QPen, QFont, QPainterPath, QPixmap
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTabWidget, QFrame, QLineEdit,
    QSpinBox, QDoubleSpinBox, QComboBox, QFormLayout, QDialog,
    QDialogButtonBox, QTextEdit, QGroupBox, QListWidget,
    QListWidgetItem, QListView, QProgressBar, QTextBrowser,
    QFileDialog, QScrollArea, QSlider, QAbstractItemView, QStackedWidget,
    QCheckBox, QGridLayout, QRadioButton, QMessageBox, QSizePolicy
)

# --- НАСТРОЙКИ ЯЗЫКА (ЛОКАЛИЗАЦИЯ) ---
settings = QSettings("LancerTools", "Terminal")
LANG = settings.value("language", "RU")

LOCALE = {
    "RU": {
        "tab_tracker": "⚔️ Боевой Трекер",
        "tab_enc": "⚖️ Энциклопедия и Баланс",
        "tab_map": "🗺️ Планировщик Ситрепов",
        "btn_import": "⬇ Игрок (COMP/CON)",
        "btn_add_npc": "➕ Добавить НИП",
        "btn_save": "💾 Сохр. Энкаунтер",
        "btn_load": "📂 Загр. Энкаунтер",
        "btn_next": "⏩ Следующий Раунд",
        "timeline": "Таймлайн (Очередь ходов)",
        "btn_flip_stats": "Вернуться к статам 🗘",
        "btn_flip_skills": "Показать доп. системы 🗘",
        "base_sys": "БАЗОВЫЕ АТАКИ И СИСТЕМЫ",
        "opt_sys": "ДОП. СИСТЕМЫ / ТАЛАНТЫ / ШАБЛОНЫ",
        "lang_alert": "Язык изменен! Интерфейс обновится немедленно, но для некоторых карточек может потребоваться перезапуск.",
        "grp_settings": "Настройки группы игроков",
        "grp_encyc": "Энциклопедия Врагов (Клик)",
        "grp_balance": "Анализ Баланса",
        "grp_card": "Карточка Класса",
        "lbl_players": "Кол-во Игроков:",
        "lbl_ll": "Средний Уровень (LL):",
        "btn_load_map": "🗺️ Загрузить карту",
        "btn_export_map": "📸 Выгрузить карту",
        "lbl_sitrep": "Ситреп:",
        "lbl_zoom": "🔍 Масштаб (%):",
        "lbl_hex": "Размер гекса:",
        "lbl_ox": "Сдвиг X:",
        "lbl_oy": "Сдвиг Y:",
    },
    "EN": {
        "tab_tracker": "⚔️ Combat Tracker",
        "tab_enc": "⚖️ Encyclopedia & Balance",
        "tab_map": "🗺️ Sitrep Planner",
        "btn_import": "⬇ Import PC (COMP/CON)",
        "btn_add_npc": "➕ Add NPC",
        "btn_save": "💾 Save Encounter",
        "btn_load": "📂 Load Encounter",
        "btn_next": "⏩ Next Round",
        "timeline": "Timeline (Turn Order)",
        "btn_flip_stats": "Back to Stats 🗘",
        "btn_flip_skills": "Show Abilities 🗘",
        "base_sys": "BASE ATTACKS & SYSTEMS",
        "opt_sys": "OPT. SYSTEMS / TALENTS / TEMPLATES",
        "lang_alert": "Language changed! UI updated. Some existing cards might need a restart to fully translate.",
        "grp_settings": "Party Settings",
        "grp_encyc": "NPC Encyclopedia (Click)",
        "grp_balance": "Balance Analysis",
        "grp_card": "Class Card",
        "lbl_players": "Player Count:",
        "lbl_ll": "Average Level (LL):",
        "btn_load_map": "🗺️ Load Map",
        "btn_export_map": "📸 Export Map",
        "lbl_sitrep": "Sitrep:",
        "lbl_zoom": "🔍 Zoom (%):",
        "lbl_hex": "Hex Size:",
        "lbl_ox": "Offset X:",
        "lbl_oy": "Offset Y:",
    }
}


def TR(key): return LOCALE.get(LANG, LOCALE["RU"]).get(key, key)


# --- ИКОНКИ РОЛЕЙ ---
ROLE_ICONS = {
    "Striker": "⚔️", "Artillery": "🎯", "Defender": "🛡️",
    "Controller": "👁️", "Support": "🔧", "Biological": "🧬", "Player": "👤"
}


# --- ПОДДЕРЖКА ДВУЯЗЫЧНОГО JSON ---
def loc(item, key):
    """Вытягивает ключ с учетом языка (name_ru / name_en). Фолбэк на обычный ключ."""
    if not isinstance(item, dict): return str(item)
    lang_key = f"{key}_{LANG.lower()}"
    if lang_key in item and item[lang_key]: return str(item[lang_key])
    return str(item.get(key, ""))


# --- ФОРМАТТЕР ТЕКСТА ПОД СТИЛЬ LANCER ---
def format_lancer_text(text):
    if not text: return ""
    rg = "Дальность" if LANG == "RU" else "Range"
    th = "Угроза" if LANG == "RU" else "Threat"
    ln = "Линия" if LANG == "RU" else "Line"
    cn = "Конус" if LANG == "RU" else "Cone"
    bl = "Взрыв" if LANG == "RU" else "Blast"
    br = "Разрыв" if LANG == "RU" else "Burst"

    text = re.sub(r'(?i)(Range|Дальность)\s*(\d+)',
                  rf"<span style='background:#222; border:1px solid #4CAF50; color:#4CAF50; padding:1px 4px; border-radius:3px;'>⌖ {rg} \2</span>",
                  text)
    text = re.sub(r'(?i)(Threat|Угроза)\s*(\d+)',
                  rf"<span style='background:#222; border:1px solid #F44336; color:#F44336; padding:1px 4px; border-radius:3px;'>⚔️ {th} \2</span>",
                  text)
    text = re.sub(r'(?i)(Line|Линия)\s*(\d+)',
                  rf"<span style='background:#222; border:1px solid #00E5FF; color:#00E5FF; padding:1px 4px; border-radius:3px;'>➖ {ln} \2</span>",
                  text)
    text = re.sub(r'(?i)(Cone|Конус)\s*(\d+)',
                  rf"<span style='background:#222; border:1px solid #FF9800; color:#FF9800; padding:1px 4px; border-radius:3px;'>📐 {cn} \2</span>",
                  text)
    text = re.sub(r'(?i)(Blast|Взрыв)\s*(\d+)',
                  rf"<span style='background:#222; border:1px solid #FF5722; color:#FF5722; padding:1px 4px; border-radius:3px;'>💥 {bl} \2</span>",
                  text)
    text = re.sub(r'(?i)(Burst|Разрыв)\s*(\d+)',
                  rf"<span style='background:#222; border:1px solid #9C27B0; color:#9C27B0; padding:1px 4px; border-radius:3px;'>🎇 {br} \2</span>",
                  text)

    kin = "Кинетика" if LANG == "RU" else "Kinetic"
    ene = "Энергия" if LANG == "RU" else "Energy"
    exp = "Взрыв" if LANG == "RU" else "Explosive"
    brn = "Горение" if LANG == "RU" else "Burn"
    hea = "Нагрев" if LANG == "RU" else "Heat"

    text = re.sub(r'(\d+d\d+(?:\+\d+)?|\d+)\s*(Кинетического|Кинетический|Kinetic)',
                  rf"<b><span style='color:#B0BEC5;'>\1 ⚙️ {kin}</span></b>", text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+d\d+(?:\+\d+)?|\d+)\s*(Энергетического|Энергетический|Energy)',
                  rf"<b><span style='color:#40C4FF;'>\1 ⚡ {ene}</span></b>", text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+d\d+(?:\+\d+)?|\d+)\s*(Взрывного|Взрывной|Explosive)',
                  rf"<b><span style='color:#FFCA28;'>\1 💣 {exp}</span></b>", text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+d\d+(?:\+\d+)?|\d+)\s*(Горения|Burn)',
                  rf"<b><span style='color:#EF5350;'>\1 🔥 {brn}</span></b>", text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+d\d+(?:\+\d+)?|\d+)\s*(Нагрева|Heat)',
                  rf"<b><span style='color:#FF7043;'>\1 🌡️ {hea}</span></b>", text, flags=re.IGNORECASE)

    text = re.sub(r'\b(ББ|AP)\b', r"<span style='color:#FF3366; font-weight:bold;'>[AP]</span>", text)
    return text


def load_npc_database():
    file_name = "npcs.json"
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


NPC_PRESETS = load_npc_database()


# --- ПАРСЕР COMP/CON ---
def translate_compcon(text):
    if LANG == "EN": return text
    dict_ru = {
        "Auxiliary": "Вспом.", "Main": "Осн.", "Heavy": "Тяж.", "Superheavy": "Сверхтяж.",
        "Melee": "ОББ", "CQB": "ОБД", "Rifle": "Винтовка", "Launcher": "ПУ", "Cannon": "Пушка", "Nexus": "Звено",
        "AP": "ББ", "Accurate": "Точное", "Inaccurate": "Неточное", "Smart": "Умное", "Seeking": "Искатель",
        "Knockback": "Толчок", "Blast": "Взрыв", "Cone": "Конус", "Line": "Линия", "Burst": "Разрыв",
        "Threat": "Угроза", "Range": "Дальность", "Energy": "Энергия", "Kinetic": "Кинетика",
        "Explosive": "Взрывной", "Burn": "Горение", "Heat": "Нагрев", "Loading": "Заряжаемое",
        "Personalizations": "Персонализация", "Custom Paint Job": "Покраска"
    }
    for eng, rus in dict_ru.items():
        text = re.sub(rf'\b{eng}\b', rus, text, flags=re.IGNORECASE)
    return text


def parse_compcon(text, faction="player"):
    text_translated = translate_compcon(text)

    data = {
        "name": "PC", "hp": 10, "evasion": 10, "edef": 10, "speed": 4,
        "sensors": 10, "save": 10, "size": "1", "tier": "PC",
        "role": "Player", "modifier": "Base", "faction": faction,
        "base_features": [], "optional_features": []
    }

    callsign_match = re.search(r'»\s*.*?//\s*(.*?)\s*«', text)
    if callsign_match:
        data["name"] = callsign_match.group(1).strip()
    else:
        name_match = re.search(r'-- (.*?) @', text)
        if name_match: data["name"] = name_match.group(1).strip()

    for stat, key in [('HP', 'hp'), ('EVA', 'evasion'), ('EDEF', 'edef'), ('SPD', 'speed'), ('SENS', 'sensors'),
                      ('SAVE', 'save')]:
        m = re.search(rf'{stat}:\s*(\d+)', text)
        if m: data[key] = int(m.group(1))

    m_size = re.search(r'SIZE:\s*([0-9/.]+)', text)
    if m_size: data["size"] = m_size.group(1)

    m_armor = re.search(r'ARMOR:\s*(\d+)', text)
    if m_armor:
        nm = "Броня" if LANG == "RU" else "Armor"
        data["base_features"].append(
            {"name_ru": nm, "name_en": nm, "type_ru": "Стат", "type_en": "Stat", "desc_ru": f"{m_armor.group(1)}",
             "desc_en": f"{m_armor.group(1)}"})

    def extract_section(header):
        m = re.search(rf'\[ {header} \](.*?)(?=\[|$)', text_translated, re.DOTALL)
        return m.group(1).strip().replace('\n', '<br>') if m else ""

    weapons = extract_section('WEAPONS')
    systems = extract_section('SYSTEMS')
    talents = extract_section('TALENTS')

    if weapons: data["base_features"].append(
        {"name_ru": "Оружие", "name_en": "Weapons", "type_ru": "Снаряжение", "type_en": "Gear", "desc_ru": weapons,
         "desc_en": weapons})
    if systems: data["base_features"].append(
        {"name_ru": "Системы", "name_en": "Systems", "type_ru": "Снаряжение", "type_en": "Gear", "desc_ru": systems,
         "desc_en": systems})
    if talents: data["optional_features"].append(
        {"name_ru": "Таланты", "name_en": "Talents", "type_ru": "Навык", "type_en": "Skill", "desc_ru": talents,
         "desc_en": talents})

    return data


def expand_tier_values(text, tier):
    def replacer(match):
        parts = match.group(1).split('/')
        if len(parts) == 3 and tier in (1, 2, 3):
            return parts[tier - 1]
        return match.group(0)

    return re.sub(r'\b(\d+(?:/\d+)+)\b', replacer, text)


def format_feature_with_stats(feature, tier):
    name = loc(feature, 'name')
    typ = loc(feature, 'type')
    desc = loc(feature, 'desc')
    desc = expand_tier_values(desc, tier)
    desc = format_lancer_text(desc)

    range_str = feature.get('range', '')
    threat_str = feature.get('threat', '')
    stats = []
    if range_str: stats.append(f"⌖ {range_str}")
    if threat_str: stats.append(f"⚔️ {threat_str}")
    stat_line = f"<span style='color:#aaa; font-size:10px;'> {' | '.join(stats)}</span>" if stats else ""

    return f"""
    <div style='margin-bottom: 4px;'>
        <span style='color: #00E5FF; font-weight: bold;'>{name}</span>
        <span style='color: #888; font-style: italic;'>[{typ}]</span>
        {stat_line}<br>
        <span>{desc}</span>
    </div>
    """


# --- КАРТОЧКА ПЕРСОНАЖА ---
class CombatantCard(QFrame):
    hp_changed = Signal(object)
    deleted = Signal(object)
    move_up = Signal(object)
    move_down = Signal(object)

    def __init__(self, data, is_preview=False):
        super().__init__()
        self.data = data
        self.max_hp = data["hp"]
        self.current_hp = data.get("current_hp", self.max_hp)
        self.is_dead = False
        self.has_acted = data.get("has_acted", False)

        self.tier_num = 1
        tier_str = data.get("tier", "Tier 1")
        if "Tier 2" in tier_str:
            self.tier_num = 2
        elif "Tier 3" in tier_str:
            self.tier_num = 3

        self.setFixedSize(250, 390)
        self.setObjectName("CardFrame")

        if data.get("faction") == "player":
            self.color_hex = "#00E5FF"
        elif data.get("faction") == "ally":
            self.color_hex = "#00E676"
        else:
            self.color_hex = "#FF3366"

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self._build_front_page(is_preview)
        self._build_back_page(is_preview)
        self.update_style()

    def _build_front_page(self, is_preview):
        front_widget = QWidget()
        layout = QVBoxLayout(front_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        header = QHBoxLayout()
        header.setSpacing(2)

        self.btn_l = QPushButton("◄")
        self.btn_l.setFixedSize(20, 20)
        self.btn_l.clicked.connect(lambda: self.move_up.emit(self))

        role_icon = ROLE_ICONS.get(self.data.get("role", "Player"), "🤖")
        display_name = self.data.get('display_name', self.data.get('name_ru', self.data.get('name', '???')))

        self.name_lbl = QLabel(f"{role_icon} {display_name}")
        self.name_lbl.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {self.color_hex};")

        self.btn_copy = QPushButton("📋")
        self.btn_copy.setFixedSize(20, 20)
        self.btn_copy.setToolTip("Copy UID")
        self.btn_copy.setStyleSheet("background: transparent; border: none; font-size: 12px;")
        self.btn_copy.clicked.connect(self.copy_uid)

        self.btn_r = QPushButton("►")
        self.btn_r.setFixedSize(20, 20)
        self.btn_r.clicked.connect(lambda: self.move_down.emit(self))

        header.addWidget(self.btn_l)
        header.addWidget(self.name_lbl)
        header.addWidget(self.btn_copy)
        header.addStretch()
        header.addWidget(self.btn_r)
        layout.addLayout(header)

        tier_lbl = QLabel(self.data.get('tier_display', self.data.get('tier', 'PC')))
        tier_lbl.setStyleSheet("color: #aaa; font-size: 10px;")
        layout.addWidget(tier_lbl)

        stats_html = f"""
        <table width='100%' style='color: #ddd; font-family: monospace; font-size: 11px; background: #222; border-radius: 3px; padding: 2px;'>
            <tr>
                <td align='center'>SZ: {self.data.get('size', '1')}</td>
                <td align='center'>SPD: {self.data.get('speed', 4)}</td>
                <td align='center'>SEN: {self.data.get('sensors', 10)}</td>
            </tr>
            <tr>
                <td align='center'>EV: {self.data.get('evasion', 10)}</td>
                <td align='center'>ED: {self.data.get('edef', 10)}</td>
                <td align='center'>SAV: {self.data.get('save', 10)}</td>
            </tr>
        </table>
        """
        layout.addWidget(QLabel(stats_html))

        self.hp_bar = QProgressBar()
        self.hp_bar.setMaximum(self.max_hp)
        self.hp_bar.setValue(self.current_hp)
        self.hp_bar.setTextVisible(True)
        self.hp_bar.setFormat("%v / %m HP")
        self.hp_bar.setStyleSheet(f"""
            QProgressBar {{ border: 1px solid #444; background: #111; border-radius: 3px; color: #fff; text-align: center; font-weight: bold; height: 18px; font-size: 11px;}}
            QProgressBar::chunk {{ background-color: {self.color_hex}; border-radius: 2px;}}
        """)
        layout.addWidget(self.hp_bar)

        hp_ctrl = QHBoxLayout()
        btn_minus = QPushButton("-1 HP")
        btn_plus = QPushButton("+1 HP")
        btn_minus.clicked.connect(self.dec_hp)
        btn_plus.clicked.connect(self.inc_hp)
        hp_ctrl.addWidget(btn_minus)
        hp_ctrl.addWidget(btn_plus)
        layout.addLayout(hp_ctrl)

        abilities_browser = QTextBrowser()
        abilities_browser.setStyleSheet(
            "QTextBrowser { background: #161616; color: #ccc; border: 1px solid #333; border-radius: 4px; padding: 4px; font-size: 11px;}")

        html_content = f"<div style='color:#00E5FF; font-weight:bold; margin-bottom:4px;'>{TR('base_sys')}</div>"
        for feat in self.data.get("base_features", []):
            html_content += format_feature_with_stats(feat, self.tier_num)
        abilities_browser.setHtml(html_content)
        layout.addWidget(abilities_browser)

        btn_flip = QPushButton(TR("btn_flip_skills"))
        btn_flip.setStyleSheet("background-color: #2b2b2b; color: #ccc; border: 1px solid #555; padding: 4px;")
        btn_flip.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        layout.addWidget(btn_flip)

        bottom_ctrl = QHBoxLayout()
        self.btn_act = QPushButton("End Turn" if LANG == "EN" else "Завершить ход")
        self.btn_act.setCheckable(True)
        self.btn_act.setChecked(self.has_acted)
        self.btn_act.clicked.connect(self.toggle_act)

        self.btn_del = QPushButton("✖")
        self.btn_del.setFixedWidth(25)
        self.btn_del.setStyleSheet("background-color: #991111; color: white; font-weight: bold; border-radius: 3px;")
        self.btn_del.clicked.connect(lambda: self.deleted.emit(self))

        bottom_ctrl.addWidget(self.btn_act)
        bottom_ctrl.addWidget(self.btn_del)
        layout.addLayout(bottom_ctrl)

        if is_preview:
            self.btn_l.hide();
            self.btn_r.hide();
            self.btn_copy.hide()
            self.btn_act.hide();
            self.btn_del.hide()
            hp_ctrl.itemAt(0).widget().hide()
            hp_ctrl.itemAt(1).widget().hide()

        self.stack.addWidget(front_widget)

    def _build_back_page(self, is_preview):
        back_widget = QWidget()
        layout = QVBoxLayout(back_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        role_icon = ROLE_ICONS.get(self.data.get("role", "Player"), "🤖")
        display_name = self.data.get('display_name', self.data.get('name_ru', self.data.get('name', '???')))

        name_lbl = QLabel(f"🔄 {role_icon} {display_name}")
        name_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {self.color_hex};")
        layout.addWidget(name_lbl)

        abilities_browser = QTextBrowser()
        abilities_browser.setStyleSheet(
            "QTextBrowser { background: #161616; color: #ccc; border: 1px solid #333; border-radius: 4px; padding: 4px; font-size: 11px;}")

        html_content = ""
        if self.data.get("template_features"):
            html_content += f"<div style='color:#FF3366; font-weight:bold; margin-bottom:4px;'>TEMPLATES</div>"
            for feat in self.data.get("template_features", []):
                html_content += format_feature_with_stats(feat, self.tier_num)
            html_content += "<hr style='border: 0; border-top: 1px dashed #333; margin: 4px 0;'>"

        html_content += f"<div style='color:#00E676; font-weight:bold; margin-bottom:4px;'>{TR('opt_sys')}</div>"
        for feat in self.data.get("optional_features", []):
            html_content += format_feature_with_stats(feat, self.tier_num)

        abilities_browser.setHtml(html_content)
        layout.addWidget(abilities_browser)

        btn_flip = QPushButton(TR("btn_flip_stats"))
        btn_flip.setStyleSheet("background-color: #2b2b2b; color: #ccc; border: 1px solid #555; padding: 4px;")
        btn_flip.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(btn_flip)
        self.stack.addWidget(back_widget)

    def copy_uid(self):
        uid = self.data.get("uid", "")
        if uid:
            QApplication.clipboard().setText(uid)
            self.btn_copy.setText("✔")
            QTimer.singleShot(1000, lambda: self.btn_copy.setText("📋"))

    def dec_hp(self):
        if self.current_hp > 0:
            self.current_hp -= 1
            self.hp_bar.setValue(self.current_hp)
            self.data['current_hp'] = self.current_hp
            self.update_style()

    def inc_hp(self):
        self.current_hp += 1
        self.hp_bar.setValue(self.current_hp)
        self.data['current_hp'] = self.current_hp
        self.update_style()

    def toggle_act(self):
        self.has_acted = self.btn_act.isChecked()
        self.data['has_acted'] = self.has_acted
        self.hp_changed.emit(self)

    def update_style(self):
        self.is_dead = (self.current_hp <= 0)
        border_color = "#333" if self.is_dead else self.color_hex
        bg_color = "#111111" if self.is_dead else "#202020"

        self.setStyleSheet(f"""
            QFrame#CardFrame {{ background-color: {bg_color}; border: 2px solid {border_color}; border-radius: 6px; }}
            QPushButton {{ background-color: #333; color: #fff; border: 1px solid #555; border-radius: 3px; font-size: 12px; }}
            QPushButton:hover {{ background-color: #444; border: 1px solid {self.color_hex};}}
            QPushButton:checked {{ background-color: #222; border: 1px solid {self.color_hex}; color: {self.color_hex}; font-weight: bold; }}
        """)
        if self.is_dead:
            self.name_lbl.setStyleSheet("color: #666; font-weight: bold; text-decoration: line-through;")
        else:
            self.name_lbl.setStyleSheet(f"color: {self.color_hex}; font-weight: bold;")
        self.hp_changed.emit(self)


# --- ДИАЛОГИ ---
class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(TR("btn_import"))
        self.resize(500, 400)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Paste COMP/CON Export Text:"))

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        group = QGroupBox("Faction")
        radio_layout = QHBoxLayout()
        self.radio_player = QRadioButton("Player")
        self.radio_enemy = QRadioButton("Enemy")
        self.radio_ally = QRadioButton("Ally")
        self.radio_player.setChecked(True)
        radio_layout.addWidget(self.radio_player)
        radio_layout.addWidget(self.radio_enemy)
        radio_layout.addWidget(self.radio_ally)
        group.setLayout(radio_layout)
        layout.addWidget(group)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_data(self):
        if self.radio_player.isChecked():
            faction = "player"
        elif self.radio_enemy.isChecked():
            faction = "enemy"
        else:
            faction = "ally"
        return parse_compcon(self.text_edit.toPlainText(), faction=faction)


class AddNpcDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(TR("btn_add_npc"))
        self.resize(450, 450)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.faction_combo = QComboBox()
        self.faction_combo.addItems(["Enemy", "Ally", "Player"])

        self.class_combo = QComboBox()
        for key, preset in sorted(NPC_PRESETS.items()):
            name = loc(preset, "name")
            self.class_combo.addItem(name, userData=key)

        self.name_input = QLineEdit()
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["Tier 1", "Tier 2", "Tier 3"])

        stats_layout = QGridLayout()
        self.hp_input = QSpinBox();
        self.hp_input.setRange(1, 500);
        self.hp_input.setPrefix("HP: ")
        self.eva_input = QSpinBox();
        self.eva_input.setRange(1, 30);
        self.eva_input.setPrefix("EV: ")
        self.edef_input = QSpinBox();
        self.edef_input.setRange(1, 30);
        self.edef_input.setPrefix("ED: ")
        self.spd_input = QSpinBox();
        self.spd_input.setRange(1, 20);
        self.spd_input.setPrefix("SP: ")
        self.sen_input = QSpinBox();
        self.sen_input.setRange(1, 30);
        self.sen_input.setPrefix("SEN: ")
        self.sav_input = QSpinBox();
        self.sav_input.setRange(1, 20);
        self.sav_input.setPrefix("SAV: ")

        stats_layout.addWidget(self.hp_input, 0, 0);
        stats_layout.addWidget(self.eva_input, 0, 1);
        stats_layout.addWidget(self.edef_input, 0, 2)
        stats_layout.addWidget(self.spd_input, 1, 0);
        stats_layout.addWidget(self.sen_input, 1, 1);
        stats_layout.addWidget(self.sav_input, 1, 2)

        self.size_input = QLineEdit("1")

        form.addRow("Faction:", self.faction_combo)
        form.addRow("Class:", self.class_combo)
        form.addRow("Name:", self.name_input)
        form.addRow("Tier:", self.tier_combo)
        form.addRow("Stats:", stats_layout)
        form.addRow("Size:", self.size_input)
        layout.addLayout(form)

        template_box = QGroupBox("Templates")
        grid = QGridLayout(template_box)
        self.chk_grunt = QCheckBox("Grunt" if LANG == "EN" else "Салага")
        self.chk_elite = QCheckBox("Elite" if LANG == "EN" else "Элита")
        self.chk_ultra = QCheckBox("Ultra" if LANG == "EN" else "Ультра")
        self.chk_veteran = QCheckBox("Veteran" if LANG == "EN" else "Ветеран")
        self.chk_commander = QCheckBox("Commander" if LANG == "EN" else "Командир")
        self.chk_exot = QCheckBox("Exot" if LANG == "EN" else "Экзот")
        self.chk_merc = QCheckBox("Mercenary" if LANG == "EN" else "Наемник")
        self.chk_pirate = QCheckBox("Pirate" if LANG == "EN" else "Пират")
        self.chk_ship = QCheckBox("Ship" if LANG == "EN" else "Корабль")
        self.chk_vehicle = QCheckBox("Vehicle" if LANG == "EN" else "Транспорт")

        grid.addWidget(self.chk_grunt, 0, 0);
        grid.addWidget(self.chk_elite, 0, 1)
        grid.addWidget(self.chk_ultra, 0, 2);
        grid.addWidget(self.chk_veteran, 1, 0)
        grid.addWidget(self.chk_commander, 1, 1);
        grid.addWidget(self.chk_exot, 1, 2)
        grid.addWidget(self.chk_merc, 2, 0);
        grid.addWidget(self.chk_pirate, 2, 1)
        grid.addWidget(self.chk_ship, 3, 0);
        grid.addWidget(self.chk_vehicle, 3, 1)

        self.chk_grunt.toggled.connect(
            lambda: [c.setChecked(False) for c in [self.chk_elite, self.chk_ultra, self.chk_veteran, self.chk_commander]
                     if self.chk_grunt.isChecked()])
        self.chk_elite.toggled.connect(
            lambda: [c.setChecked(False) for c in [self.chk_grunt, self.chk_ultra] if self.chk_elite.isChecked()])
        self.chk_ultra.toggled.connect(
            lambda: [c.setChecked(False) for c in [self.chk_grunt, self.chk_elite] if self.chk_ultra.isChecked()])
        self.chk_ship.toggled.connect(lambda: self.chk_vehicle.setChecked(False) if self.chk_ship.isChecked() else None)
        self.chk_vehicle.toggled.connect(
            lambda: self.chk_ship.setChecked(False) if self.chk_vehicle.isChecked() else None)

        for chk in [self.chk_grunt, self.chk_elite, self.chk_ultra, self.chk_ship, self.chk_vehicle]:
            chk.toggled.connect(self.update_stats)

        layout.addWidget(template_box)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self.class_combo.currentIndexChanged.connect(self.update_stats)
        self.tier_combo.currentTextChanged.connect(self.update_stats)
        self.faction_combo.currentTextChanged.connect(self.auto_name)
        self.update_stats()

    def auto_name(self):
        if self.faction_combo.currentIndex() == 2:  # Player
            self.name_input.setText("")
        else:
            self.name_input.setText(self.class_combo.currentText())

    def update_stats(self, _=None):
        key = self.class_combo.currentData()
        preset = NPC_PRESETS.get(key, list(NPC_PRESETS.values())[0])
        tier = self.tier_combo.currentText()
        stats = preset.get("tiers", {}).get(tier, {"hp": 10, "eva": 10, "edef": 10, "spd": 4, "sen": 10, "save": 10})

        base_hp = stats.get("hp", 10)
        size = preset.get("size", "1")

        if self.chk_grunt.isChecked():
            base_hp = 1
        elif self.chk_ultra.isChecked():
            base_hp = int(base_hp * 4)
        elif self.chk_elite.isChecked():
            base_hp = int(base_hp * 2)

        if self.chk_ship.isChecked():
            base_hp += 5
            size = "4"

        self.hp_input.setValue(base_hp)
        self.eva_input.setValue(stats.get("eva", 10))
        self.edef_input.setValue(stats.get("edef", 10))
        self.spd_input.setValue(stats.get("spd", 4))
        self.sen_input.setValue(stats.get("sen", 10))
        self.sav_input.setValue(stats.get("save", 10))
        self.size_input.setText(size)

        if self.faction_combo.currentIndex() != 2:
            current_name = self.name_input.text()
            display_names = [loc(p, "name") for p in NPC_PRESETS.values()]
            if not current_name or current_name in display_names:
                self.name_input.setText(self.class_combo.currentText())

    def get_data(self):
        idx = self.faction_combo.currentIndex()
        fac = "enemy" if idx == 0 else "ally" if idx == 1 else "player"
        key = self.class_combo.currentData()
        preset = NPC_PRESETS.get(key, list(NPC_PRESETS.values())[0])

        templates_applied = []
        t_feats = []

        def add_tpl(chk, n_ru, n_en, d_ru, d_en):
            if chk.isChecked():
                templates_applied.append(n_en if LANG == "EN" else n_ru)
                t_feats.append(
                    {"name_ru": n_ru, "name_en": n_en, "type_ru": "Шаблон", "type_en": "Template", "desc_ru": d_ru,
                     "desc_en": d_en})

        add_tpl(self.chk_grunt, "Салага", "Grunt", "1 ПЗ.", "1 HP.")
        add_tpl(self.chk_elite, "Элита", "Elite", "2 хода за раунд.", "2 turns/round.")
        add_tpl(self.chk_ultra, "Ультра", "Ultra", "Иммунитет к состояниям, босс.", "Boss template.")
        add_tpl(self.chk_veteran, "Ветеран", "Veteran", "Иммунитет к 1 состоянию.", "Immune to 1 cond.")
        add_tpl(self.chk_commander, "Командир", "Commander", "Баффы союзникам.", "Ally buffs.")
        add_tpl(self.chk_exot, "Экзот", "Exot", "Паракаузальные системы.", "Paracausal.")
        add_tpl(self.chk_merc, "Наемник", "Mercenary", "+1 Точность по Вовлеченным.", "+1 Acc vs Engaged.")
        add_tpl(self.chk_pirate, "Пират", "Pirate", "+1d6 крит. урон.", "+1d6 crit damage.")
        add_tpl(self.chk_ship, "Корабль", "Ship", "Летает, иммунитет к Сбиванию.", "Flies, Prone immune.")
        add_tpl(self.chk_vehicle, "Транспорт", "Vehicle", "Едет по прямой.", "Straight movement.")

        tier_display = self.tier_combo.currentText()
        if templates_applied:
            tier_display += f" ({', '.join(templates_applied)})"

        return {
            "name": self.name_input.text() or "Unknown",
            "hp": self.hp_input.value(), "evasion": self.eva_input.value(),
            "edef": self.edef_input.value(), "speed": self.spd_input.value(),
            "sensors": self.sen_input.value(), "save": self.sav_input.value(),
            "faction": fac, "tier": self.tier_combo.currentText(),
            "tier_display": tier_display,
            "size": self.size_input.text(),
            "role": preset.get("role", "Player"),
            "base_features": preset.get("base_features", []),
            "optional_features": preset.get("optional_features", []),
            "template_features": t_feats
        }


# --- ВКЛАДКА 1: БОЕВОЙ ТРЕКЕР ---
class CombatTracker(QWidget):
    roster_changed = Signal()

    def __init__(self):
        super().__init__()
        self.combatants = []
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        btn_import = QPushButton(TR("btn_import"))
        btn_import.setStyleSheet("background-color: #1976D2; color: white; font-weight: bold;")
        btn_import.clicked.connect(self.import_cc)

        btn_add = QPushButton(TR("btn_add_npc"))
        btn_add.clicked.connect(self.add_npc)

        btn_save = QPushButton(TR("btn_save"))
        btn_save.clicked.connect(self.save_encounter)

        btn_load = QPushButton(TR("btn_load"))
        btn_load.clicked.connect(self.load_encounter)

        btn_next = QPushButton(TR("btn_next"))
        btn_next.setStyleSheet("background-color: #00897B; color: white; font-weight: bold; font-size: 14px;")
        btn_next.clicked.connect(self.next_round)

        for btn in [btn_import, btn_add, btn_save, btn_load]:
            toolbar.addWidget(btn)

        toolbar.addStretch()
        toolbar.addWidget(btn_next)
        layout.addLayout(toolbar)

        self.card_list = QListWidget()
        self.card_list.setViewMode(QListView.ViewMode.IconMode)
        self.card_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.card_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.card_list.setSpacing(10)
        self.card_list.setStyleSheet("background-color: transparent; border: none;")
        layout.addWidget(self.card_list)

        init_box = QGroupBox(TR("timeline"))
        self.timeline = QHBoxLayout(init_box)
        self.timeline.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(init_box)

    def generate_uid(self):
        existing_uids = [c['card'].data.get('uid', '') for c in self.combatants]
        while True:
            letters = ''.join(random.choices(string.ascii_uppercase, k=2))
            numbers = ''.join(random.choices(string.digits, k=2))
            uid = f"{letters}{numbers}"
            if uid not in existing_uids:
                return uid

    def move_item(self, card, direction):
        QTimer.singleShot(0, lambda: self._perform_move(card, direction))

    def _perform_move(self, card, direction):
        idx = -1
        for i, c in enumerate(self.combatants):
            if c['card'] == card:
                idx = i
                break

        if idx != -1:
            new_idx = idx + direction
            if 0 <= new_idx < len(self.combatants):
                item_current = self.combatants[idx]['item']
                item_target = self.combatants[new_idx]['item']

                self.card_list.removeItemWidget(item_current)
                self.card_list.removeItemWidget(item_target)

                self.combatants[idx], self.combatants[new_idx] = self.combatants[new_idx], self.combatants[idx]

                self.card_list.setItemWidget(item_current, self.combatants[idx]['card'])
                self.card_list.setItemWidget(item_target, self.combatants[new_idx]['card'])

                self.combatants[idx]['item'] = item_current
                self.combatants[new_idx]['item'] = item_target

                self.update_arrows()
                self.update_timeline()

    def update_arrows(self):
        total = len(self.combatants)
        for idx, c in enumerate(self.combatants):
            c['card'].btn_l.setVisible(idx > 0)
            c['card'].btn_r.setVisible(idx < total - 1)

    def import_cc(self):
        dlg = ImportDialog(self)
        if dlg.exec(): self.add_card(dlg.get_data())

    def add_npc(self):
        dlg = AddNpcDialog(self)
        if dlg.exec(): self.add_card(dlg.get_data())

    def add_card(self, data, is_rebuild=False):
        if not is_rebuild:
            base_name = data["name"].strip()
            highest_num = 0

            for c in self.combatants:
                c_name = c['card'].data.get("name", "")
                m = re.match(rf"^{re.escape(base_name)}(?: (\d+))?$", c_name)
                if m:
                    num = m.group(1)
                    highest_num = max(highest_num, int(num) if num else 1)

            if highest_num > 0:
                data["name"] = f"{base_name} {highest_num + 1}"
                if highest_num == 1:
                    for c in self.combatants:
                        if c['card'].data.get("name") == base_name:
                            c['card'].data["name"] = f"{base_name} 1"
                            c['card'].data['display_name'] = f"{base_name} 1"
                            role_icon = ROLE_ICONS.get(c['card'].data.get("role", "Player"), "🤖")
                            c['card'].name_lbl.setText(f"{role_icon} {c['card'].data['display_name']}")
                            break

            if 'uid' not in data:
                data['uid'] = self.generate_uid()
            data['display_name'] = f"{data['name']}"

        card = CombatantCard(data)
        card.hp_changed.connect(self.update_timeline)
        card.deleted.connect(self.remove_card)
        card.move_up.connect(lambda c: self.move_item(c, -1))
        card.move_down.connect(lambda c: self.move_item(c, 1))

        item = QListWidgetItem(self.card_list)
        item.setSizeHint(QSize(250, 390))
        self.card_list.addItem(item)
        self.card_list.setItemWidget(item, card)

        self.combatants.append({'card': card, 'item': item})

        self.update_arrows()
        self.update_timeline()
        if not is_rebuild:
            self.roster_changed.emit()

    def remove_card(self, card):
        for c in self.combatants:
            if c['card'] == card:
                card.setParent(None)
                row = self.card_list.row(c['item'])
                self.card_list.takeItem(row)
                self.combatants.remove(c)
                break
        self.update_arrows()
        self.update_timeline()
        self.roster_changed.emit()

    def save_encounter(self):
        file_path, _ = QFileDialog.getSaveFileName(self, TR("btn_save"), "", "JSON (*.json)")
        if file_path:
            for c in self.combatants:
                c['card'].data['current_hp'] = c['card'].current_hp
                c['card'].data['has_acted'] = c['card'].has_acted

            encounter_data = [c['card'].data for c in self.combatants]
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(encounter_data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print("Ошибка сохранения:", e)

    def load_encounter(self):
        file_path, _ = QFileDialog.getOpenFileName(self, TR("btn_load"), "", "JSON (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    encounter_data = json.load(f)

                for c in self.combatants: c['card'].setParent(None)
                self.card_list.clear()
                self.combatants.clear()

                for data in encounter_data:
                    self.add_card(data, is_rebuild=True)
            except Exception as e:
                print("Ошибка загрузки:", e)

    def update_timeline(self, _=None):
        for i in reversed(range(self.timeline.count())):
            widget = self.timeline.itemAt(i).widget()
            if widget: widget.setParent(None)

        for c in self.combatants:
            card = c['card']
            if not card.is_dead and not card.has_acted:
                lbl = QLabel(card.data.get("display_name", card.data.get("name", "Unknown")))
                lbl.setStyleSheet(
                    f"background-color: {card.color_hex}; color: #000; padding: 4px 10px; border-radius: 8px; font-weight: bold; font-size: 11px;")
                self.timeline.addWidget(lbl)

    def next_round(self):
        for c in self.combatants:
            if not c['card'].is_dead:
                c['card'].btn_act.setChecked(False)
                c['card'].has_acted = False
                c['card'].data['has_acted'] = False
        self.update_timeline()


# --- АНИМАЦИЯ ДЕТАЛИЗИРОВАННОЙ ДЕВУШКИ ASCII ---
class AsciiGirl(QLabel):
    def __init__(self):
        super().__init__()
        self.state = 0
        self.set_art()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_art(self):
        if self.state == 0:
            # Обычное состояние (Строгий кибер-стиль)
            art = (
                "⠀⠀⠀⠀⠀⠔⠁⣠⠞⠕⠁⢠⣾⢿⣻⣿⡿⠀⠀⣰⢀⠀⠀⠀⠀⠀⠀⠀⠹⢿⣿⣧⡀⠉⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀\n"
                "⠀⠀⠀⠀⠀⠀⠀⠌⢠⡞⢁⠊⠀⣰⠛⠁⢪⢺⣿⡇⠀⠀⣿⠘⣤⡀⠀⠢⣅⠂⢀⠀⠈⢻⣿⡕⡀⠀⠈⡟⢿⡻⣟⠛⣿⣿⣿⣿⣿⡀\n"
                "⠐⠒⠤⠤⠤⢄⠂⡶⢋⠀⠀⢀⠀⡵⠀⢠⡟⠸⣿⢱⡇⢀⣿⣶⣯⡇⠀⢀⡉⣿⣦⣕⣤⡀⢙⣷⡌⣆⠀⠘⣦⠑⡜⣆⢱⡌⣿⣿⠙⣷\n"
                "⠀⠀⠀⠀⠀⠎⡼⢡⣾⠁⠠⢡⡾⠁⢀⣿⣇⠀⣿⣿⣷⢸⣿⣿⡿⢿⣤⣮⡻⣿⣿⣿⣿⣿⣿⣿⣿⣾⣆⡄⠈⢷⡈⢞⡄⠹⡄⢣⠀⣿\n"
                "⠀⠀⠀⠀⣜⣼⣵⣿⡇⡠⣡⡿⠡⠀⣾⣿⣿⠀⢿⣿⣿⡐⢹⣿⣵⠀⠀⠈⠙⠪⡻⣿⣿⣿⣷⣝⠬⠃⠈⠂⠀⠈⢷⣻⣷⡀⢻⡌⡄⣼\n"
                "⠀⠀⠀⢰⠹⣿⣿⣿⣳⣿⣿⠃⠇⢰⣿⢿⡿⣧⢸⣿⣿⣧⡌⣿⣿⡇⠀⠀⠀⠀⠹⣿⣿⣿⣷⡹⡟⢮⡢⡀⠀⠀⠈⣷⣿⣧⠘⣿⣡⣿\n"
                "⠀⠀⠀⣆⣳⡿⢻⣿⡳⣿⡛⢸⠀⣾⡏⠸⣷⢻⣇⣿⢻⣿⡇⢿⣯⣿⡄⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⣧⡉⡻⠤⣀⠀⠘⣿⣿⣇⢿⣿⣿\n"
                "⠀⠀⢰⣿⡿⠁⢸⣿⣿⣿⣇⣤⣠⣿⠃⠀⠹⣧⢻⣿⣏⣿⣷⠸⡿⣾⣿⡄⠀⠀⠀⠀⠈⢚⣿⣿⣿⣿⣷⡸⣄⠠⠙⠆⠘⣿⣿⣼⣿⣿\n"
                "⠀⠀⣸⣿⠁⠀⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠱⡻⣿⣿⣾⣿⣆⢳⠙⢿⣿⣆⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⣽⣦⠡⡘⣦⢚⣿⣇⣿⣿\n"
                "⠄⡀⢻⡇⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣀⣀⡉⠓⠺⢌⣻⣿⣿⣿⣾⣆⠀⠙⢝⠳⣄⠀⠀⠀⠀⢿⣿⡟⡟⣿⣿⡿⣷⡐⠼⣷⣻⣿⢿⣿\n"
                "⠀⠈⠻⡇⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣋⣡⣄⣀⡀⠀⠢⡙⢿⣿⣿⣿⣆⠀⠀⠁⢊⠱⠦⠤⠖⠚⣿⣿⠘⡘⢿⣿⣞⣿⣮⣻⣿⣿⣿⣿\n"
                "⠀⠀⠀⠈⠄⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⡏⠹⡍⢳⢆⠀⠙⢿⣿⣿⣷⡀⠀⠀⠀⢠⢞⣓⣠⣿⣿⣆⣡⣊⢿⣿⣿⣿⣿⣿⣿⣿⣿\n"
                "⠀⠀⠀⠀⠘⣸⣿⣿⢹⣿⣿⣿⣿⣿⣧⠉⠓⠺⠶⠶⠋⠀⠁⠀⠈⢻⣿⡌⠙⠲⣄⠀⠁⡕⠋⢃⠘⠃⡿⠈⣿⠟⢻⣿⣿⣿⣿⣯⢻⣿\n"
                "⠀⠀⠀⠀⠀⢻⣿⣯⢀⢻⣿⣟⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠻⣷⡀⠀⠀⠀⠀⠀⠀⠉⠛⠛⠓⠛⢣⠀⠘⣿⣿⢿⣿⣿⣿⣿\n"
                "⠀⠀⠀⠀⠀⠸⣿⢿⣄⠹⣿⣿⠘⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢳⠳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⣽⣿⣸⣿⣾⢪⡟\n"
                "⠀⠀⠀⠀⠀⠀⣿⠸⣿⣦⡈⢻⡇⠹⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢿⣿⣫⡼⠁⣽⡏\n"
                "⠀⠀⠀⠀⠀⠀⣉⡇⢻⣿⣷⣄⣎⠀⠹⡌⢻⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢺⣿⣿⠜⣠⣾⣿⡇\n"
                "⠀⠀⠀⠀⠀⠀⡎⠁⠈⣿⣹⣿⣿⡄⠀⢳⠀⠙⠧⠀⠀⠀⠀⠀⠀⠂⠀⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠇⠀⢹⣼⣿⣿⣿⣇\n"
                "⠀⠀⠀⠀⠀⠀⡇⠀⠀⠘⣧⣿⣿⣿⡄⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣤⣴⣿⣿⣿⣿⣿⣿\n"
                "⠀⠀⠀⠀⠀⢀⠃⠀⠀⣰⣿⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠀⠠⢤⣤⡤⢤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿\n"
                "⠀⠀⠀⠀⠀⠸⠀⠀⢾⣿⣿⣿⣿⣿⣿⣿⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⢀⡠⠚⣹⣿⣿⣿⣿⣿⣿⣿⣿⣧⠙⢯\n"
                "⠀⠀⠀⠀⢀⠃⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣏⠙⠦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡔⡫⠀⢀⣿⣿⣿⣿⣿⣿⣧⠙⢷⡹⣇⠀\n"
                "⠀⠀⠀⠀⠂⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣓⠤⠌⠲⢤⡀⠀⠀⠀⠀⠀⠀⣠⣤⣾⣯⠞⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣆⠀⠃⠘⠀\n"
                "⠀⠀⡀⠀⠀⠀⠀⣀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠙⠷⣦⣤⣤⣶⣿⡿⠟⠋⠁⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀\n"
                "⣠⣀⣤⣤⣶⣾⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡗⠀⠀⠀⠈⠉⠉⠉⠀⠀⠀⠀⠀⠀⢀⠞⢻⣿⣿⣿⣿⣿⢿⠿⢿⣿⡀\n"
            )
            self.setStyleSheet(
                "font-family: monospace; font-size: 5px; line-height: 1.0; color: #00E5FF; font-weight: bold; background: transparent;")
        else:
            # Состояние "Влюблена" (Розовый/Пурпурный стиль)
            art = (
                "⠀⠀⠀⠀⠀⠔⠁⣠⠞⠕⠁⢠⣾⢿⣻⣿⡿⠀⠀⣰⢀⠀⠀⠀⠀⠀⠀⠀⠹⢿⣿⣧⡀⠉⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀\n"
                "⠀⠀⠀⠀⠀⠀⠀⠌⢠⡞⢁⠊⠀⣰⠛⠁⢪⢺⣿⡇⠀⠀⣿⠘⣤⡀⠀⠢⣅⠂⢀⠀⠈⢻⣿⡕⡀⠀⠈⡟⢿⡻⣟⠛⣿⣿⣿⣿⣿⡀\n"
                "⠐⠒⠤⠤⠤⢄⠂⡶⢋⠀⠀⢀⠀⡵⠀⢠⡟⠸⣿⢱⡇⢀⣿⣶⣯⡇⠀⢀⡉⣿⣦⣕⣤⡀⢙⣷⡌⣆⠀⠘⣦⠑⡜⣆⢱⡌⣿⣿⠙⣷\n"
                "⠀⠀⠀⠀⠀⠎⡼⢡⣾⠁⠠⢡⡾⠁⢀⣿⣇⠀⣿⣿⣷⢸⣿⣿⡿⢿⣤⣮⡻⣿⣿⣿⣿⣿⣿⣿⣿⣾⣆⡄⠈⢷⡈⢞⡄⠹⡄⢣⠀⣿\n"
                "⠀⠀⠀⠀⣜⣼⣵⣿⡇⡠⣡⡿⠡⠀⣾⣿⣿⠀⢿⣿⣿⡐⢹⣿⣵⠀⠀⠈⠙⠪⡻⣿⣿⣿⣷⣝⠬⠃⠈⠂⠀⠈⢷⣻⣷⡀⢻⡌⡄⣼\n"
                "⠀⠀⠀⢰⠹⣿⣿⣿⣳⣿⣿⠃⠇⢰⣿⢿⡿⣧⢸⣿⣿⣧⡌⣿⣿⡇⠀⠀⠀⠀⠹⣿⣿⣿⣷⡹⡟⢮⡢⡀⠀⠀⠈⣷⣿⣧⠘⣿⣡⣿\n"
                "⠀⠀⠀⣆⣳⡿⢻⣿⡳⣿⡛⢸⠀⣾⡏⠸⣷⢻⣇⣿⢻⣿⡇⢿⣯⣿⡄⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⣧⡉⡻⠤⣀⠀⠘⣿⣿⣇⢿⣿⣿\n"
                "⠀⠀⢰⣿⡿⠁⢸⣿⣿⣿⣇⣤⣠⣿⠃⠀⠹⣧⢻⣿⣏⣿⣷⠸⡿⣾⣿⡄⠀⠀⠀⠀⠈⢚⣿⣿⣿⣿⣷⡸⣄⠠⠙⠆⠘⣿⣿⣼⣿⣿\n"
                "⠀⠀⣸⣿⠁⠀⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠱⡻⣿⣿⣾⣿⣆⢳⠙⢿⣿⣆⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⣽⣦⠡⡘⣦⢚⣿⣇⣿⣿\n"
                "⠄⡀⢻⡇⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣀⣀⡉⠓⠺⢌⣻⣿⣿⣿⣾⣆⠀⠙⢝⠳⣄⠀⠀⠀⠀⢿⣿⡟⡟⣿⣿⡿⣷⡐⠼⣷⣻⣿⢿⣿\n"
                "⠀⠈⠻⡇⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣋⣡⣄⣀⡀⠀⠢⡙⢿⣿⣿⣿⣆⠀⠀⠁⢊⠱⠦⠤⠖⠚⣿⣿⠘⡘⢿⣿⣞⣿⣮⣻⣿⣿⣿⣿\n"
                "⠀⠀⠀⠈⠄⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⡏⠹⡍⢳⢆⠀⠙⢿⣿⣿⣷⡀⠀⠀⠀⢠⢞⣓⣠⣿⣿⣆⣡⣊⢿⣿⣿⣿⣿⣿⣿⣿⣿\n"
                "⠀⠀⠀⠀⠘⣸⣿⣿⢹⣿⣿⣿⣿⣿⣧⠉⠓⠺⠶⠶⠋⠀⠁⠀⠈⢻⣿⡌⠙⠲⣄⠀⠁⡕⠋⢃⠘⠃⡿⠈⣿⠟⢻⣿⣿⣿⣿⣯⢻⣿\n"
                "⠀⠀⠀⠀⠀⢻⣿⣯⢀⢻⣿⣟⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠻⣷⡀⠀⠀⠀⠀⠀⠀⠉⠛⠛⠓⠛⢣⠀⠘⣿⣿⢿⣿⣿⣿⣿\n"
                "⠀⠀⠀⠀⠀⠸⣿⢿⣄⠹⣿⣿⠘⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢳⠳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⣽⣿⣸⣿⣾⢪⡟\n"
                "⠀⠀⠀⠀⠀⠀⣿⠸⣿⣦⡈⢻⡇⠹⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢿⣿⣫⡼⠁⣽⡏\n"
                "⠀⠀⠀⠀⠀⠀⣉⡇⢻⣿⣷⣄⣎⠀⠹⡌⢻⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢺⣿⣿⠜⣠⣾⣿⡇\n"
                "⠀⠀⠀⠀⠀⠀⡎⠁⠈⣿⣹⣿⣿⡄⠀⢳⠀⠙⠧⠀⠀⠀⠀⠀⠀⠂⠀⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠇⠀⢹⣼⣿⣿⣿⣇\n"
                "⠀⠀⠀⠀⠀⠀⡇⠀⠀⠘⣧⣿⣿⣿⡄⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣤⣴⣿⣿⣿⣿⣿⣿\n"
                "⠀⠀⠀⠀⠀⢀⠃⠀⠀⣰⣿⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠀⠠⢤⣤⡤⢤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿\n"
                "⠀⠀⠀⠀⠀⠸⠀⠀⢾⣿⣿⣿⣿⣿⣿⣿⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⢀⡠⠚⣹⣿⣿⣿⣿⣿⣿⣿⣿⣧⠙⢯\n"
                "⠀⠀⠀⠀⢀⠃⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣏⠙⠦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡔⡫⠀⢀⣿⣿⣿⣿⣿⣿⣧⠙⢷⡹⣇⠀\n"
                "⠀⠀⠀⠀⠂⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣓⠤⠌⠲⢤⡀⠀⠀⠀⠀⠀⠀⣠⣤⣾⣯⠞⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣆⠀⠃⠘⠀\n"
                "⠀⠀⡀⠀⠀⠀⠀⣀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠙⠷⣦⣤⣤⣶⣿⡿⠟⠋⠁⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀\n"
                "⣠⣀⣤⣤⣶⣾⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡗⠀⠀⠀⠈⠉⠉⠉⠀⠀⠀⠀⠀⠀⢀⠞⢻⣿⣿⣿⣿⣿⢿⠿⢿⣿⡀\n"
            )
            self.setStyleSheet(
                "font-family: monospace; font-size: 5px; line-height: 1.0; color: #FF3366; font-weight: bold; background: transparent;")

        self.setText(art)

    def mousePressEvent(self, event):
        self.state = 1 - self.state
        self.set_art()
        super().mousePressEvent(event)


# --- ВКЛАДКА 2: КАЛЬКУЛЯТОР БАЛАНСА И ЭНЦИКЛОПЕДИЯ ВРАГОВ ---
class EncounterBuilder(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QHBoxLayout(self)

        left_panel = QVBoxLayout()
        settings_box = QGroupBox(TR("grp_settings"))
        s_layout = QFormLayout(settings_box)
        self.players_spin = QSpinBox();
        self.players_spin.setRange(1, 8);
        self.players_spin.setValue(4)
        self.players_spin.valueChanged.connect(self.calculate)
        self.ll_spin = QSpinBox();
        self.ll_spin.setRange(0, 12);
        self.ll_spin.setValue(0)
        self.ll_spin.valueChanged.connect(self.calculate)
        s_layout.addRow(TR("lbl_players"), self.players_spin)
        s_layout.addRow(TR("lbl_ll"), self.ll_spin)
        left_panel.addWidget(settings_box)

        enemy_box = QGroupBox(TR("grp_encyc"))
        e_layout = QVBoxLayout(enemy_box)
        self.enemy_list = QListWidget()
        self.enemy_list.setStyleSheet("background: #1e1e1e; border: 1px solid #444; border-radius: 4px; padding: 5px;")
        self.enemy_list.itemClicked.connect(self.preview_enemy)

        for key, preset in sorted(NPC_PRESETS.items()):
            name = loc(preset, "name")
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.enemy_list.addItem(item)

        e_layout.addWidget(self.enemy_list)
        left_panel.addWidget(enemy_box)
        main_layout.addLayout(left_panel, 1)

        res_box = QGroupBox(TR("grp_balance"))
        r_layout = QVBoxLayout(res_box)
        r_header = QHBoxLayout()
        self.result_browser = QTextBrowser()
        self.result_browser.setStyleSheet("border: none; background: transparent;")
        r_header.addWidget(self.result_browser)
        self.ascii_girl = AsciiGirl()
        r_header.addWidget(self.ascii_girl)
        r_layout.addLayout(r_header)
        main_layout.addWidget(res_box, 2)

        self.preview_box = QGroupBox(TR("grp_card"))
        self.preview_layout = QVBoxLayout(self.preview_box)
        self.preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.preview_box, 1)

        self.calculate()

    def preview_enemy(self, item):
        self.clear_preview()
        key = item.data(Qt.ItemDataRole.UserRole)
        preset = NPC_PRESETS.get(key)
        if preset:
            t1_stats = preset.get("tiers", {}).get("Tier 1",
                                                   {"hp": 10, "eva": 10, "edef": 10, "spd": 4, "sen": 10, "save": 10})
            preview_data = {
                "name": loc(preset, "name"),
                "hp": t1_stats.get("hp", 10),
                "evasion": t1_stats.get("eva", 10),
                "edef": t1_stats.get("edef", 10),
                "speed": t1_stats.get("spd", 4),
                "sensors": t1_stats.get("sen", 10),
                "save": t1_stats.get("save", 10),
                "faction": "enemy",
                "tier": "Tier 1",
                "tier_display": "Tier 1 (Base)",
                "size": preset.get("size", "1"),
                "role": preset.get("role", "Striker"),
                "base_features": preset.get("base_features", []),
                "optional_features": preset.get("optional_features", []),
                "template_features": []
            }
            card_preview = CombatantCard(preview_data, is_preview=True)
            self.preview_layout.addWidget(card_preview)

    def clear_preview(self):
        for i in reversed(range(self.preview_layout.count())):
            w = self.preview_layout.itemAt(i).widget()
            if w: w.setParent(None)

    def calculate(self):
        players = self.players_spin.value()
        ll = self.ll_spin.value()
        tier = 1
        if ll >= 5: tier = 2
        if ll >= 9: tier = 3

        budget = players
        if ll in [3, 4, 7, 8, 11, 12]:
            budget += max(1, players // 2)

        if LANG == "EN":
            html = f"""
            <h2 style='color:#00E5FF; margin-top:0;'>Balance Analysis</h2>
            <ul><li><b>Recommended Tier:</b> Tier {tier}</li><li><b>Budget (Standard NPCs):</b> {budget}</li></ul><hr>
            <h3 style='color:#FF3366;'>1. Skirmish</h3><p><b>{budget} Standard NPCs</b>. Good for resource drain.</p>
            <h3 style='color:#FF3366;'>2. Heavy Assault</h3><p><b>{budget // 2} Elites</b> and <b>{budget % 2} Standard</b>.</p>
            <h3 style='color:#FF3366;'>3. Swarm</h3><p><b>{max(1, budget // 3)} Standards</b> and <b>{(budget - max(1, budget // 3)) * 4} Grunts</b>.</p>
            """
            if budget >= 4: html += f"<h3 style='color:#FF3366;'>4. Boss Fight</h3><p><b>1 Ultra</b> and <b>{budget - 4} Standards</b>.</p>"
            html += """<hr><h3 style='color:#00E676;'>Synergies:</h3>
            <ul><li><b>Anvil:</b> 1x Bastion + 2x Sniper.</li><li><b>Chaos:</b> 1x Hive + 3x Assault.</li><li><b>Deathwall:</b> 1x Barricade + 1x Demolisher + 1x Rainmaker.</li></ul>"""
        else:
            html = f"""
            <h2 style='color:#00E5FF; margin-top:0;'>Анализ Баланса</h2>
            <ul><li><b>Рекомендуемый Тир:</b> Tier {tier}</li><li><b>Бюджет очков:</b> {budget}</li></ul><hr>
            <h3 style='color:#FF3366;'>1. Стычка</h3><p><b>{budget} Стандартных НИП</b>. Истощение ресурсов.</p>
            <h3 style='color:#FF3366;'>2. Элитный отряд</h3><p><b>{budget // 2} Элитных</b> и <b>{budget % 2} Стандартных</b>.</p>
            <h3 style='color:#FF3366;'>3. Рой</h3><p><b>{max(1, budget // 3)} Стандартных</b> и <b>{(budget - max(1, budget // 3)) * 4} Салаг</b>.</p>
            """
            if budget >= 4: html += f"<h3 style='color:#FF3366;'>4. Босс</h3><p><b>1 Ультра</b> и <b>{budget - 4} Стандартных</b>.</p>"
            html += """<hr><h3 style='color:#00E676;'>Связки:</h3>
            <ul><li><b>Наковальня:</b> 1x Бастион + 2x Снайпер.</li><li><b>Хаос:</b> 1x Улей + 3x Штурмовик.</li><li><b>Стена Смерти:</b> 1x Баррикадист + 1x Разрушитель + 1x Градовержец.</li></ul>"""

        self.result_browser.setHtml(html)


# --- ВКЛАДКА 3: ПЛАНИРОВЩИК СИТРЕПОВ С КАРТОЙ ---
class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.hex_size = 25.0
        self.offset_x = 0
        self.offset_y = 0
        self.zoom_factor = 1.0
        self.sitrep = "None"
        self.bg_image = None
        self.setMinimumSize(800, 600)

    def set_background(self, file_path):
        self.bg_image = QPixmap(file_path)
        self.update_dimensions()

    def update_dimensions(self):
        if self.bg_image and not self.bg_image.isNull():
            w = int(self.bg_image.width() * self.zoom_factor)
            h = int(self.bg_image.height() * self.zoom_factor)
            self.setFixedSize(w, h)
        else:
            self.setFixedSize(int(800 * self.zoom_factor), int(600 * self.zoom_factor))
        self.update()

    def set_sitrep(self, sitrep):
        self.sitrep = sitrep
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.scale(self.zoom_factor, self.zoom_factor)

        base_w = self.bg_image.width() if self.bg_image else 800
        base_h = self.bg_image.height() if self.bg_image else 600

        if self.bg_image and not self.bg_image.isNull():
            painter.drawPixmap(0, 0, self.bg_image)
        else:
            painter.fillRect(0, 0, base_w, base_h, QColor(30, 30, 30))

        self.draw_sitrep_zones(painter, base_w, base_h)

        pen = QPen(QColor(200, 200, 200, 80))
        pen.setWidth(1)
        pen.setCosmetic(True)
        painter.setPen(pen)

        dx = self.hex_size * 1.5
        dy = self.hex_size * math.sqrt(3)
        cols = int(base_w / dx) + 4
        rows = int(base_h / dy) + 4

        for col in range(-2, cols):
            for row in range(-2, rows):
                x = self.offset_x + col * dx
                y = self.offset_y + row * dy + ((dy / 2) if col % 2 != 0 else 0)
                self.draw_flat_top_hex(painter, x, y, self.hex_size)

    def draw_flat_top_hex(self, painter, cx, cy, size):
        path = QPainterPath()
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = math.radians(angle_deg)
            x = cx + size * math.cos(angle_rad)
            y = cy + size * math.sin(angle_rad)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()
        painter.drawPath(path)

    def draw_sitrep_zones(self, painter, w, h):
        painter.setPen(Qt.PenStyle.NoPen)
        font = QFont("Arial", int(16 / self.zoom_factor), QFont.Weight.Bold)
        painter.setFont(font)

        if "Control" in self.sitrep:
            painter.setBrush(QColor(255, 150, 0, 100))
            sz = w * 0.15
            zones = [(w * 0.1, h * 0.1), (w * 0.9 - sz, h * 0.1), (w * 0.1, h * 0.9 - sz), (w * 0.9 - sz, h * 0.9 - sz)]
            for zx, zy in zones: painter.drawRect(int(zx), int(zy), int(sz), int(sz))
        elif "Escort" in self.sitrep:
            painter.setBrush(QColor(0, 229, 255, 100))
            painter.drawRect(20, int(h / 2 - 100), 100, 200)
            painter.setBrush(QColor(0, 255, 100, 100))
            painter.drawRect(int(w - 120), int(h / 2 - 100), 100, 200)
            painter.setBrush(QColor(255, 51, 102, 60))
            painter.drawRect(150, 20, int(w - 300), 80)
            painter.drawRect(150, int(h - 100), int(w - 300), 80)
        elif "Extraction" in self.sitrep:
            painter.setBrush(QColor(255, 150, 0, 100))
            painter.drawRect(int(w / 2 - 50), int(h / 2 - 50), 100, 100)
            painter.setBrush(QColor(0, 255, 100, 100))
            painter.drawRect(int(w - 150), int(h - 150), 120, 120)
        elif "Strike" in self.sitrep:
            painter.setBrush(QColor(0, 229, 255, 100))
            painter.drawRect(20, 20, 150, int(h - 40))
            painter.setBrush(QColor(255, 51, 102, 100))
            painter.drawRect(int(w - 200), 20, 180, int(h - 40))
        elif "Holdout" in self.sitrep:
            painter.setBrush(QColor(0, 229, 255, 100))
            painter.drawRect(int(w / 2 - 100), int(h / 2 - 100), 200, 200)
            painter.setBrush(QColor(255, 51, 102, 60))
            painter.drawRect(20, 20, int(w - 40), 60)
            painter.drawRect(20, int(h - 80), int(w - 40), 60)


class SitrepPlanner(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        toolbar1 = QHBoxLayout()
        btn_load_map = QPushButton(TR("btn_load_map"))
        btn_load_map.setStyleSheet("background-color: #2196F3; color: black; font-weight: bold; padding: 8px;")
        btn_load_map.clicked.connect(self.load_map)
        toolbar1.addWidget(btn_load_map)

        btn_export = QPushButton(TR("btn_export_map"))
        btn_export.setStyleSheet("background-color: #4CAF50; color: black; font-weight: bold; padding: 8px;")
        btn_export.clicked.connect(self.export_map)
        toolbar1.addWidget(btn_export)

        toolbar1.addWidget(QLabel(TR("lbl_sitrep")))
        self.sitrep_combo = QComboBox()
        self.sitrep_combo.addItems([
            "None", "Control", "Escort", "Extraction", "Strike", "Holdout", "Recon"
        ])
        self.sitrep_combo.currentTextChanged.connect(self.change_sitrep)
        toolbar1.addWidget(self.sitrep_combo)
        toolbar1.addStretch()
        layout.addLayout(toolbar1)

        toolbar2 = QHBoxLayout()
        toolbar2.addWidget(QLabel(TR("lbl_zoom")))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(150)
        self.zoom_slider.valueChanged.connect(self.change_zoom)
        toolbar2.addWidget(self.zoom_slider)

        toolbar2.addWidget(QLabel(f" | {TR('lbl_hex')}"))
        self.hex_spin = QDoubleSpinBox()
        self.hex_spin.setRange(5.0, 300.0)
        self.hex_spin.setValue(25.0)
        self.hex_spin.setSingleStep(0.5)
        self.hex_spin.valueChanged.connect(self.change_hex)
        toolbar2.addWidget(self.hex_spin)

        toolbar2.addWidget(QLabel(f" | {TR('lbl_ox')}"))
        self.ox_spin = QSpinBox()
        self.ox_spin.setRange(-1000, 1000)
        self.ox_spin.valueChanged.connect(self.change_ox)
        toolbar2.addWidget(self.ox_spin)

        toolbar2.addWidget(QLabel(f" {TR('lbl_oy')}"))
        self.oy_spin = QSpinBox()
        self.oy_spin.setRange(-1000, 1000)
        self.oy_spin.valueChanged.connect(self.change_oy)
        toolbar2.addWidget(self.oy_spin)

        toolbar2.addStretch()
        layout.addLayout(toolbar2)

        self.scroll_area = QScrollArea()
        self.map_widget = MapWidget()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setWidget(self.map_widget)
        self.map_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.scroll_area)

    def load_map(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Map", "", "Images (*.png *.jpg *.jpeg)")
        if file_path: self.map_widget.set_background(file_path)

    def export_map(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export", "sitrep_map.png", "PNG (*.png)")
        if file_path:
            pixmap = QPixmap(self.map_widget.size())
            self.map_widget.render(pixmap)
            pixmap.save(file_path)

    def change_sitrep(self, text):
        self.map_widget.set_sitrep(text)

    def change_zoom(self, val):
        self.map_widget.zoom_factor = val / 100.0
        self.map_widget.update_dimensions()

    def change_hex(self, val):
        self.map_widget.hex_size = val
        self.map_widget.update()

    def change_ox(self, val):
        self.map_widget.offset_x = val
        self.map_widget.update()

    def change_oy(self, val):
        self.map_widget.offset_y = val
        self.map_widget.update()


# --- ГЛАВНОЕ ОКНО ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lancer RPG - Omninet Master Terminal")
        self.resize(1300, 850)
        self.setStyleSheet("""
            QMainWindow, QDialog { background-color: #111; color: #E0E0E0; font-family: 'Segoe UI', sans-serif; }
            QWidget { color: #E0E0E0; }
            QTabWidget::pane { border: 1px solid #333; background: #1a1a1a; }
            QTabBar::tab { background: #222; color: #aaa; padding: 10px 20px; border: 1px solid #333; }
            QTabBar::tab:selected { background: #333; color: #00E5FF; border-bottom: 2px solid #00E5FF; }
            QPushButton { background-color: #333; color: #fff; border: 1px solid #555; padding: 6px; border-radius: 4px; }
            QPushButton:hover { background-color: #444; border: 1px solid #00E5FF; }
            QGroupBox { border: 1px solid #444; border-radius: 5px; margin-top: 15px; font-weight: bold; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; color: #00E5FF; }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { background: #222; color: #fff; border: 1px solid #555; padding: 5px; border-radius: 3px; }
            QCheckBox, QRadioButton { spacing: 5px; }
        """)

        top_toolbar = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["🇷🇺 RU", "🇬🇧 EN"])
        self.lang_combo.setCurrentIndex(0 if LANG == "RU" else 1)
        self.lang_combo.currentTextChanged.connect(self.change_language)

        tabs = QTabWidget()
        tabs.setCornerWidget(self.lang_combo, Qt.Corner.TopRightCorner)

        self.tracker = CombatTracker()
        self.builder = EncounterBuilder()
        self.sitrep = SitrepPlanner()

        tabs.addTab(self.tracker, TR("tab_tracker"))
        tabs.addTab(self.builder, TR("tab_enc"))
        tabs.addTab(self.sitrep, TR("tab_map"))

        self.setCentralWidget(tabs)

    def change_language(self, text):
        global LANG
        new_lang = "RU" if "RU" in text else "EN"
        if LANG != new_lang:
            settings.setValue("language", new_lang)
            QMessageBox.information(self, "Language changed", LOCALE[new_lang]["lang_alert"])
            # Приложение нужно перезапустить для полного применения


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())