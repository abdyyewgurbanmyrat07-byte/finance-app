import flet as ft
import urllib.request
import json
import threading
import time
import os

try:
    from flet_core.pie_chart import PieChartSection
except ImportError:
    try:
        from flet.pie_chart import PieChartSection
    except ImportError:
        PieChartSection = getattr(ft, "PieChartSection", None)

DATA_FILE = "finance_data.json"

def main(page: ft.Page):
    page.title = "Crypto & Finance Tracker"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 15
    page.scroll = ft.ScrollMode.AUTO

    transactions_data = []

    # ==================== 1. KRIPTO BALANSLARY WE BAHALARY ====================
    btc_text = ft.Text("BTC: Ýüklenýär...", size=13, weight=ft.FontWeight.BOLD, color="white")
    eth_text = ft.Text("ETH: Ýüklenýär...", size=13, weight=ft.FontWeight.BOLD, color="white")
    bnb_text = ft.Text("BNB: Ýüklenýär...", size=13, weight=ft.FontWeight.BOLD, color="white")
    sol_text = ft.Text("SOL: Ýüklenýär...", size=13, weight=ft.FontWeight.BOLD, color="white")

    crypto_card = ft.Card(
        content=ft.Container(
            padding=15,
            bgcolor="#1f2937",
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text("🪙 Real-Wagt Kripto Bahalary", size=15, weight=ft.FontWeight.BOLD, color="#38bdf8"),
                    ft.Divider(color="#374151"),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row([ft.Icon(ft.Icons.CURRENCY_BITCOIN, color="orange", size=20), btc_text]),
                            ft.Row([ft.Icon(ft.Icons.CURRENCY_EXCHANGE, color="cyan", size=20), eth_text]),
                        ]
                    ),
                    ft.Container(height=5),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row([ft.Icon(ft.Icons.TOKEN, color="yellow", size=20), bnb_text]),
                            ft.Row([ft.Icon(ft.Icons.FLASH_ON, color="purple", size=20), sol_text]),
                        ]
                    )
                ]
            )
        )
    )

    def fetch_crypto_prices():
        coins = [
            ("BTCUSDT", btc_text, "BTC"),
            ("ETHUSDT", eth_text, "ETH"),
            ("BNBUSDT", bnb_text, "BNB"),
            ("SOLUSDT", sol_text, "SOL"),
        ]
        while True:
            for symbol, text_ctrl, label in coins:
                try:
                    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
                    req = urllib.request.urlopen(url, timeout=5)
                    data = json.loads(req.read().decode())
                    price = float(data["price"])
                    text_ctrl.value = f"{label}: ${price:,.2f}"
                except Exception:
                    text_ctrl.value = f"{label}: Ýalňyşlyk"
            page.update()
            time.sleep(10)

    threading.Thread(target=fetch_crypto_prices, daemon=True).start()

    # ==================== 2. BALANS WE TEGELEK GRAFIK ====================
    balance_text = ft.Text("0.00 TMT", size=26, weight=ft.FontWeight.BOLD, color="green")
    income_text = ft.Text("+0.00 TMT", color="green", weight=ft.FontWeight.BOLD)
    expense_text = ft.Text("-0.00 TMT", color="red", weight=ft.FontWeight.BOLD)

    chart_income_section = PieChartSection(
        value=1,
        title="0 TMT",
        color="green",
        radius=40,
        title_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD, color="white"),
    )
    chart_expense_section = PieChartSection(
        value=1,
        title="0 TMT",
        color="red",
        radius=40,
        title_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD, color="white"),
    )

    pie_chart = ft.PieChart(
        sections=[chart_income_section, chart_expense_section],
        sections_space=3,
        center_space_radius=30,
        height=130,
    )

    balance_card = ft.Card(
        content=ft.Container(
            padding=15,
            bgcolor="#1f2937",
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text("Umumy Balans", size=14, color="grey"),
                    balance_text,
                    ft.Divider(color="#374151"),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        controls=[
                            ft.Column([
                                ft.Text("Girdeji (+)", size=12, color="grey"),
                                income_text,
                            ]),
                            ft.Column([
                                ft.Text("Çykdajy (-)", size=12, color="grey"),
                                expense_text,
                            ]),
                        ]
                    ),
                    ft.Container(height=10),
                    ft.Text("Girdeji / Çykdajy Grafigi", size=12, color="grey"),
                    pie_chart,
                ]
            )
        )
    )

    # ==================== 3. AMALLAR WE TARYH ====================
    type_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="income", label="Girdeji (+)"),
            ft.Radio(value="expense", label="Çykdajy (-)"),
        ]),
        value="income"
    )

    amount_input = ft.TextField(
        label="Möçberi (TMT)", 
        width=150, 
        prefix_icon=ft.Icons.ATTACH_MONEY,
        border_radius=8,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    desc_input = ft.TextField(
        label="Düşündiriş", 
        expand=True, 
        prefix_icon=ft.Icons.DESCRIPTION,
        border_radius=8
    )

    history_list = ft.Column(spacing=10)

    def update_ui_and_chart():
        tot_inc = sum(t["val"] for t in transactions_data if t["is_income"])
        tot_exp = sum(t["val"] for t in transactions_data if not t["is_income"])
        tot_bal = tot_inc - tot_exp

        balance_text.value = f"{tot_bal:.2f} TMT"
        balance_text.color = "green" if tot_bal >= 0 else "red"
        income_text.value = f"+{tot_inc:.2f} TMT"
        expense_text.value = f"-{tot_exp:.2f} TMT"

        chart_income_section.value = tot_inc if tot_inc > 0 else 0.001
        chart_income_section.title = f"+{tot_inc:.0f}"
        
        chart_expense_section.value = tot_exp if tot_exp > 0 else 0.001
        chart_expense_section.title = f"-{tot_exp:.0f}"

        page.update()

    def save_data():
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(transactions_data, f, ensure_ascii=False, indent=2)

    def render_item_to_ui(item):
        val = item["val"]
        desc = item["desc"]
        is_income = item["is_income"]

        if is_income:
            icon = ft.Icons.ARROW_UPWARD
            color = "green"
            sign = "+"
        else:
            icon = ft.Icons.ARROW_DOWNWARD
            color = "red"
            sign = "-"

        history_list.controls.insert(
            0,
            ft.Container(
                padding=12,
                bgcolor="#111827",
                border_radius=8,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row([
                            ft.Icon(icon, color=color),
                            ft.Text(desc, weight=ft.FontWeight.BOLD),
                        ]),
                        ft.Text(f"{sign}{val:.2f} TMT", color=color, weight=ft.FontWeight.BOLD)
                    ]
                )
            )
        )

    def load_data():
        nonlocal transactions_data
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    transactions_data = json.load(f)
                
                history_list.controls.clear()
                for item in transactions_data:
                    render_item_to_ui(item)
                
                update_ui_and_chart()
            except Exception as err:
                print("Baza okamakda ýalňyşlyk:", err)

    def add_transaction(e):
        try:
            val = float(amount_input.value)
        except (ValueError, TypeError):
            return

        desc = desc_input.value.strip() if desc_input.value else "Amal"
        is_income = type_radio.value == "income"

        new_item = {
            "val": val,
            "desc": desc,
            "is_income": is_income
        }

        transactions_data.append(new_item)
        render_item_to_ui(new_item)
        save_data()
        update_ui_and_chart()

        amount_input.value = ""
        desc_input.value = ""
        page.update()

    add_btn = ft.Button(
        content=ft.Row(
            [ft.Icon(ft.Icons.ADD), ft.Text("Amaly Goş")],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        on_click=add_transaction,
        style=ft.ButtonStyle(
            color="white",
            bgcolor="#2563eb",
            padding=15,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )

    page.add(
        crypto_card,
        ft.Container(height=10),
        balance_card,
        ft.Container(height=15),
        ft.Text("Amalyň görnüşi:", size=14, weight=ft.FontWeight.BOLD),
        type_radio,
        ft.Container(height=5),
        ft.Row([amount_input, desc_input]),
        ft.Container(height=10),
        add_btn,
        ft.Container(height=20),
        ft.Text("Soňky Amallar", size=18, weight=ft.FontWeight.BOLD),
        history_list
    )

    load_data()

if __name__ == "__main__":
    ft.app(target=main)
