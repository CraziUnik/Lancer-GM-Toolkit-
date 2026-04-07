# Omninet Master Terminal (Lancer RPG Toolkit)

🇬🇧 [English](#english) | 🇷🇺 [Русский](#русский)

## 🇬🇧 English

### About the Project
I created this program to comfortably play **Lancer RPG** with my friends anywhere—whether we are using COMP/CON, playing on Owlbear, TTS, or similar virtual tabletop simulators, or just using a computer during an in-person game. 
I was constantly frustrated by having to hunt for basic NPC files and stats in COMP/CON while running a game. To solve this, I built this desktop companion application so that a GM has everything right at their fingertips!

### Key Features
* **⚔️ Combat Tracker:** Import Player Characters directly from COMP/CON export text. Easily add NPCs from a built-in database without searching for files. Track HP, Turn Order (Timeline), and view abilities on digital "cards".
* **⚖️ Encyclopedia & Encounter Balance:** Calculate encounter difficulty based on Party Size and License Level (LL). Browse a full encyclopedia of basic NPCs, their tiers, and templates (Elite, Grunt, Ultra, etc.).
* **🗺️ Sitrep Planner:** Load custom map images, configure hex grid overlays, and plan out standard Lancer Sitreps (Control, Escort, Extraction, etc.) visually.
* **🌍 Bilingual UI:** Fully supports English and Russian languages (can be switched in the app).

### How to Install and Run
Ensure you have **Python 3.9+** installed on your system.

1. Clone or download this repository.
2. Open your terminal/command prompt in the downloaded folder.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```
   (Note: Ensure `npcs.json` is located in the same directory as `main.py`!)

### How to Add Custom NPCs
You can easily add your own homebrew or missing NPCs without touching the Python code! Everything is stored in the `npcs.json` file.

1. Open `npcs.json` in any text editor (Notepad, VS Code, Notepad++, etc.).
2. Copy an existing NPC block (from the opening `{` to the closing `}`) and paste it at the end of the file. Make sure to place a comma `,` between NPC blocks!
3. Change the data to fit your new enemy.

Here is a basic template structure:
```json
"YourNewNPC": {
     "name_ru": "Снайпер", "name_en": "Sniper",
     "role": "Artillery", "size": "1",
     "tiers": {
         "Tier 1": {"hp": 10, "eva": 10, "edef": 8, "spd": 4, "sen": 15, "save": 11},
         "Tier 2": {"hp": 12, "eva": 13, "edef": 9, "spd": 4, "sen": 15, "save": 13},
         "Tier 3": {"hp": 14, "eva": 16, "edef": 10, "spd": 4, "sen": 15, "save": 15}
     },
     "base_features": [
         {
             "name_ru": "Название Оружия", "name_en": "Weapon Name",
             "type_ru": "Винтовка", "type_en": "Main Rifle",
             "desc_ru": "Описание оружия", "desc_en": "Weapon description",
             "range": "10", "threat": "1"
         }
     ],
     "optional_features": []
}
```
> **Tip:** The `range` and `threat` fields are optional for systems/traits – use them only for weapons. If you need to add damage, just write it in `desc_ru` / `desc_en`. The text will be automatically colored in the app.

4. Save the file and restart the program.

> **Troubleshooting:** If the program stops showing NPCs, you probably missed a comma or a quote in the JSON file. Use any free online JSON Validator to check your file.

### License
This project is open-source. If you modify or distribute it, it must remain free and open-source. (See `LICENSE` file for details).



## 🇷🇺 Русский

### О проекте
Я создал эту программу, чтобы удобно играть в **Lancer RPG** с друзьями где угодно — неважно, используем мы COMP/CON, или виртуальные столы вроде Owlbear или TTS, или просто компьютер в живой игре за реальным столом.
Мне надоело постоянно искать файлы с базовыми NPC в COMP/CON во время сессий, поэтому я написал это приложение, чтобы у мастера (GM) всё необходимое всегда было под рукой!

### Основные возможности
* **⚔️ Боевой Трекер:** Импорт игроков (PC) напрямую через текст экспорта из COMP/CON. Добавление врагов (NPC) в пару кликов из встроенной базы без поиска файлов. Отслеживание HP, очереди ходов (Таймлайн) и просмотр способностей на цифровых "карточках".
* **⚖️ Энциклопедия и Баланс:** Расчет сложности энкаунтера на основе количества игроков и их Уровня (LL). Полная энциклопедия базовых NPC, их тиров и шаблонов (Элита, Салага, Ультра и т.д.).
* **🗺️ Планировщик Ситрепов:** Загрузка своих карт, наложение гексагональной сетки и визуальное планирование стандартных ситрепов (Контроль, Эскорт, Эвакуация и т.д.).
* **🌍 Двуязычный интерфейс:** Полная поддержка русского и английского языков (переключается прямо в программе).

### Как установить и запустить
Для работы программы на вашем ПК должен быть установлен **Python 3.9+**.

1. Скачайте этот репозиторий (кнопка Code -> Download ZIP).
2. Распакуйте архив и откройте консоль (терминал) в папке с файлами.
3. Установите необходимые библиотеки:
   ```bash
   pip install -r requirements.txt
   ```
4. Запустите программу:
   ```bash
   python main.py
   ```
   (Важно: файл `npcs.json` должен находиться в той же папке, что и `main.py`!)

### Как добавить своих (кастомных) NPC
Вы можете легко добавить своих собственных врагов в программу, не залезая в код! Все враги хранятся в файле `npcs.json`.

1. Откройте файл `npcs.json` в любом удобном текстовом редакторе (Блокнот, VS Code, Notepad++).
2. Скопируйте блок любого существующего врага (от открывающей `{` до закрывающей `}`) и вставьте его. Обязательно убедитесь, что между блоками врагов стоит запятая `,`!
3. Замените данные на параметры вашего нового врага.

Структура выглядит так:

```json
"ИмяВашегоНПС": {
     "name_ru": "Ваш Враг", "name_en": "Your Enemy",
     "role": "Striker", "size": "1",
     "tiers": {
         "Tier 1": {"hp": 10, "eva": 10, "edef": 8, "spd": 4, "sen": 15, "save": 11},
         "Tier 2": {"hp": 12, "eva": 13, "edef": 9, "spd": 4, "sen": 15, "save": 13},
         "Tier 3": {"hp": 14, "eva": 16, "edef": 10, "spd": 4, "sen": 15, "save": 15}
     },
     "base_features": [
         {
             "name_ru": "Название Оружия", "name_en": "Weapon Name",
             "type_ru": "Винтовка", "type_en": "Main Rifle",
             "desc_ru": "Описание оружия", "desc_en": "Weapon description",
             "range": "10", "threat": "1"
         }
     ],
     "optional_features": []
}
```

> **Примечание:** Поля `range` (дальность) и `threat` (угроза) необязательны для систем и трейтов, используйте их только для оружия. Если нужно добавить урон, просто напишите это в `desc_ru` / `desc_en`. Текст автоматически раскрасится в программе.

4. Сохраните файл и перезапустите программу.

> **Совет:** Если программа перестала показывать список NPC, скорее всего вы забыли где-то запятую или кавычку. Проверьте ваш файл через любой онлайн JSON валидатор.

### Лицензия
Этот проект является **Open Source** (открытое программное обеспечение). Если вы берете этот код, изменяете его или публикуете где-то еще — он должен оставаться абсолютно бесплатным для всех. Смотрите файл `LICENSE` для подробностей.
