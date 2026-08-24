import flet as ft
import sqlite3
import csv
import shutil
from datetime import datetime

# ----------------- BAZA LOGIKASY -----------------
def init_db():
    conn = sqlite3.connect("finance_ultra.db")
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, amount REAL, trans_type TEXT, category TEXT, date TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, target_amount REAL, current_amount REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS budgets (category TEXT PRIMARY KEY, limit_amount REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    cursor.execute("INSERT OR IGNORE INTO settings VALUES ('language', 'Türkmen')")
    cursor.execute("INSERT OR IGNORE INTO settings VALUES ('currency', 'USD')")
    conn.commit()
    conn.close()

def get_setting(key):
    conn = sqlite3.connect("finance_ultra.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""

def set_setting(key, value):
    conn = sqlite3.connect("finance_ultra.db")
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

init_db()

# ----------------- DIL WE VALÝUTA -----------------
CURRENCIES = {
    "USD": {"symbol": "$", "rate": 1.0},
    "TMT": {"symbol": "m.", "rate": 3.5},
    "EUR": {"symbol": "€", "rate": 0.92}
}

CATEGORIES = ["Iýmit", "Oýun/Programma", "Söwda", "Transport", "Beýleki"]

# ----------------- MAIN FLET APP -----------------
def main(page: ft.Page):
    page.title = "MEIKA - Finance Tracker ULTRA PRO v2"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    page.window_width = 450
    page.window_height = 800

    curr_currency = get_setting("currency") or "USD"

    def format_money(amount_usd):
        rate = CURRENCIES[curr_currency]["rate"]
        symbol = CURRENCIES[curr_currency]["symbol"]
        return f"{symbol}{(amount_usd * rate):.2f}"

    # UI Elementleri
    lbl_balance = ft.Text("$0.00", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN)
    lbl_income = ft.Text("+$0.00", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN)
    lbl_expense = ft.Text("-$0.00", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.RED)
    lbl_warning = ft.Text("", size=12, color=ft.colors.YELLOW)

    # Input Form
    ent_title = ft.TextField(label="Düşündiriş", expand=True, dense=True)
    ent_amount = ft.TextField(label="Mukdary", width=100, keyboard_type=ft.KeyboardType.NUMBER, dense=True)
    cmb_cat = ft.Dropdown(label="Kategoriýa", value=CATEGORIES[0], options=[ft.dropdown.Option(c) for c in CATEGORIES], width=150, dense=True)

    # Transactions List view
    trans_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    goals_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    # DATA LOAD FUNCTIONS
    def load_finance_data():
        trans_list.controls.clear()
        conn = sqlite3.connect("finance_ultra.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
        rows = cursor.fetchall()

        cursor.execute("SELECT category, limit_amount FROM budgets")
        budgets = dict(cursor.fetchall())
        conn.close()

        tot_inc, tot_exp = 0.0, 0.0
        cat_expenses = {}

        for r in rows:
            t_id, title, amt, t_type, cat, date = r
            if t_type == "Çykdajy":
                tot_exp += amt
                cat_expenses[cat] = cat_expenses.get(cat, 0.0) + amt
                t_color = ft.colors.RED
                txt_amt = f"-{format_money(amt)}"
            else:
                tot_inc += amt
                t_color = ft.colors.GREEN
                txt_amt = f"+{format_money(amt)}"

            def delete_item(e, item_id=t_id):
                c = sqlite3.connect("finance_ultra.db")
                c.cursor().execute("DELETE FROM transactions WHERE id=?", (item_id,))
                c.commit()
                c.close()
                load_finance_data()

            trans_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(title, weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(f"{cat} | {date}", size=11, color=ft.colors.GREY_400)
                        ], expand=True),
                        ft.Text(txt_amt, color=t_color, weight=ft.FontWeight.BOLD, size=14),
                        ft.IconButton(ft.icons.DELETE, icon_color=ft.colors.RED_400, on_click=delete_item)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    border=ft.border.all(1, ft.colors.GREY_800),
                    border_radius=8,
                    bgcolor=ft.colors.SURFACE_VARIANT
                )
            )

        bal = tot_inc - tot_exp
        lbl_balance.value = format_money(bal)
        lbl_balance.color = ft.colors.CYAN if bal >= 0 else ft.colors.RED
        lbl_income.value = f"+{format_money(tot_inc)}"
        lbl_expense.value = f"-{format_money(tot_exp)}"

        # Warnings
        warnings = []
        for cat, limit in budgets.items():
            if limit > 0 and cat_expenses.get(cat, 0.0) > limit:
                over = cat_expenses[cat] - limit
                warnings.append(f"⚠️ {cat}: Limit aşyldy (+{format_money(over)})")
        lbl_warning.value = "\n".join(warnings)

        page.update()

    def add_trans(trans_type):
        if not ent_title.value or not ent_amount.value: return
        try:
            amt = float(ent_amount.value)
            rate = CURRENCIES[curr_currency]["rate"]
            amt_usd = amt / rate
        except: return

        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect("finance_ultra.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (title, amount, trans_type, category, date) VALUES (?, ?, ?, ?, ?)",
                       (ent_title.value.strip(), amt_usd, trans_type, cmb_cat.value, date_str))
        conn.commit()
        conn.close()

        ent_title.value = ""
        ent_amount.value = ""
        load_finance_data()

    # GOALS DATA LOAD
    def load_goals_data():
        goals_list.controls.clear()
        conn = sqlite3.connect("finance_ultra.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goals")
        rows = cursor.fetchall()
        conn.close()

        for g in rows:
            gid, name, target, curr = g
            pct = min(1.0, (curr / target)) if target > 0 else 0

            def add_dep(e, item_id=gid):
                c = sqlite3.connect("finance_ultra.db")
                c.cursor().execute("UPDATE goals SET current_amount = current_amount + 10 WHERE id=?", (item_id,))
                c.commit()
                c.close()
                load_goals_data()

            goals_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"🎯 {name}", weight=ft.FontWeight.BOLD, expand=True),
                            ft.Text(f"{format_money(curr)} / {format_money(target)}")
                        ]),
                        ft.ProgressBar(value=pct, color=ft.colors.CYAN),
                        ft.ElevatedButton("+$10 Goş", on_click=add_dep, style=ft.ButtonStyle(color=ft.colors.GREEN))
                    ]),
                    padding=10,
                    border=ft.border.all(1, ft.colors.GREY_800),
                    border_radius=8
                )
            )
        page.update()

    # Goals Input
    ent_g_name = ft.TextField(label="Maksat ady", expand=True, dense=True)
    ent_g_target = ft.TextField(label="Maksat mukdary", width=120, keyboard_type=ft.KeyboardType.NUMBER, dense=True)

    def add_goal(e):
        if ent_g_name.value and ent_g_target.value:
            conn = sqlite3.connect("finance_ultra.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO goals (title, target_amount, current_amount) VALUES (?, ?, 0)",
                           (ent_g_name.value.strip(), float(ent_g_target.value)))
            conn.commit()
            conn.close()
            ent_g_name.value = ""
            ent_g_target.value = ""
            load_goals_data()

    # VIEWS
    tab_finance = ft.Column([
        ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("JEMI BALANS", size=12, color=ft.colors.GREY_400),
                    lbl_balance,
                    ft.Divider(),
                    ft.Row([
                        ft.Column([ft.Text("Girdeji", size=10), lbl_income]),
                        ft.Column([ft.Text("Çykdajy", size=10), lbl_expense]),
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
                ]), padding=15
            )
        ),
        lbl_warning,
        ft.Row([ent_title, ent_amount]),
        ft.Row([cmb_cat]),
        ft.Row([
            ft.ElevatedButton("➕ Girdeji", on_click=lambda e: add_trans("Girdeji"), bgcolor=ft.colors.GREEN_800, color=ft.colors.WHITE, expand=True),
            ft.ElevatedButton("➖ Çykdajy", on_click=lambda e: add_trans("Çykdajy"), bgcolor=ft.colors.RED_800, color=ft.colors.WHITE, expand=True)
        ]),
        ft.Text("Geçirimler", weight=ft.FontWeight.BOLD, size=16),
        trans_list
    ], expand=True)

    tab_goals = ft.Column([
        ft.Row([ent_g_name, ent_g_target]),
        ft.ElevatedButton("🎯 Täze Maksat Goş", on_click=add_goal, bgcolor=ft.colors.CYAN_700, color=ft.colors.WHITE),
        ft.Divider(),
        goals_list
    ], expand=True)

    # SETTINGS TAB
    def change_currency(e):
        nonlocal curr_currency
        curr_currency = e.control.value
        set_setting("currency", curr_currency)
        load_finance_data()
        load_goals_data()

    cmb_curr_set = ft.Dropdown(
        label="Valýuta",
        value=curr_currency,
        options=[ft.dropdown.Option(k) for k in CURRENCIES.keys()],
        on_change=change_currency
    )

    tab_settings = ft.Column([
        ft.Text("⚙️ Sazlamalar", size=18, weight=ft.FontWeight.BOLD),
        cmb_curr_set,
        ft.Divider(),
        ft.Text("💾 Baza Dolandyryş", weight=ft.FontWeight.BOLD),
        ft.ElevatedButton("🗑️ Bazany Arassala", bgcolor=ft.colors.RED_900, color=ft.colors.WHITE,
                          on_click=lambda e: [sqlite3.connect("finance_ultra.db").cursor().execute("DELETE FROM transactions"), load_finance_data()])
    ], expand=True)

    # Navigation Tabs
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Balans", icon=ft.icons.ACCOUNT_BALANCE_WALLET, content=tab_finance),
            ft.Tab(text="Maksatlar", icon=ft.icons.TRACK_CHANGES, content=tab_goals),
            ft.Tab(text="Sazlamalar", icon=ft.icons.SETTINGS, content=tab_settings),
        ],
        expand=True
    )

    page.add(tabs)
    load_finance_data()
    load_goals_data()

ft.app(target=main)
