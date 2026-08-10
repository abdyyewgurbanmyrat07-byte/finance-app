import flet as ft
import urllib.request
import json
import threading
import time

def main(page: ft.Page):
    page.title = "Crypto & Finance Tracker"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # Balanslary saklamak üçin üýtgeýänler
    total_balance = 0.0
    total_income = 0.0
    total_expense = 0.0

    # 1. Kripto Bahalary üçin Tekstler
    btc_text = ft.Text("BTC: Ýüklenýär...", size=16, weight=ft.FontWeight.BOLD, color="white")
    eth_text = ft.Text("ETH: Ýüklenýär...", size=16, weight=ft.FontWeight.BOLD, color="white")

    crypto_card = ft.Card(
        content=ft.Container(
            padding=15,
            bgcolor="#1f2937",
            border_radius=10,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.CURRENCY_BITCOIN, color="orange", size=28),
                        btc_text,
                    ]),
                    ft.Row([
                        ft.Icon(ft.Icons.CURRENCY_EXCHANGE, color="cyan", size=24),
                        eth_text,
                    ]),
                ]
            )
        )
    )

    # 2. Real-Time Crypto Bahalaryny Çekýän Arka Fon Funksiýasy
    def fetch_crypto_prices():
        while True:
            try:
                # BTC Bahasy (Binance API)
                btc_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
                req_btc = urllib.request.urlopen(btc_url, timeout=5)
                data_btc = json.loads(req_btc.read().decode())
                btc_price = float(data_btc["price"])

                # ETH Bahasy (Binance API)
                eth_url = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
                req_eth = urllib.request.urlopen(eth_url, timeout=5)
                data_eth = json.loads(req_eth.read().decode())
                eth_price = float(data_eth["price"])

                # Ekrandaky tekstleri täzelemek
                btc_text.value = f"BTC: ${btc_price:,.2f}"
                eth_text.value = f"ETH: ${eth_price:,.2f}"
            except Exception as err:
                btc_text.value = "BTC: Yalňyşlyk"
                eth_text.value = "ETH: Yalňyşlyk"
            
            page.update()
            time.sleep(10)  # Her 10 sekuntdan täzeleýär

    # Arka fonda bahalary täzeläp durjak potoky (Thread) başlatmak
    threading.Thread(target=fetch_crypto_prices, daemon=True).start()

    # 3. Balans we Hasabat Kartasy
    balance_text = ft.Text("0.00 TMT", size=32, weight=ft.FontWeight.BOLD, color="green")
    income_text = ft.Text("+0.00 TMT", color="green", weight=ft.FontWeight.BOLD)
    expense_text = ft.Text("-0.00 TMT", color="red", weight=ft.FontWeight.BOLD)

    balance_card = ft.Card(
        content=ft.Container(
            padding=20,
            bgcolor="#111827",
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text("Umumy Balans", size=14, color="grey"),
                    balance_text,
                    ft.Divider(color="grey"),
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
                    )
                ]
            )
        )
    )

    # 4. Amalyň görnüşini saýlamak
    type_radio = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="income", label="Girdeji (+)"),
            ft.Radio(value="expense", label="Çykdajy (-)"),
        ]),
        value="income"
    )

    # 5. Giriş Meýdançalary
    amount_input = ft.TextField(
        label="Möçberi (TMT)", 
        width=180, 
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

    # Goşmak funksiýasy
    def add_transaction(e):
        nonlocal total_balance, total_income, total_expense

        try:
            val = float(amount_input.value)
        except (ValueError, TypeError):
            return

        desc = desc_input.value.strip() if desc_input.value else "Amal"
        is_income = type_radio.value == "income"

        if is_income:
            total_income += val
            total_balance += val
            icon = ft.Icons.ARROW_UPWARD
            color = "green"
            sign = "+"
        else:
            total_expense += val
            total_balance -= val
            icon = ft.Icons.ARROW_DOWNWARD
            color = "red"
            sign = "-"

        balance_text.value = f"{total_balance:.2f} TMT"
        balance_text.color = "green" if total_balance >= 0 else "red"
        income_text.value = f"+{total_income:.2f} TMT"
        expense_text.value = f"-{total_expense:.2f} TMT"

        history_list.controls.insert(
            0,
            ft.Container(
                padding=12,
                bgcolor="#1f2937",
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

        amount_input.value = ""
        desc_input.value = ""
        page.update()

    # 6. Goşmak Düwmesi
    add_btn = ft.Button(
        content=ft.Row(
            [ft.Icon(ft.Icons.ADD), ft.Text("Amaly Goş")],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        on_click=add_transaction,
        style=ft.ButtonStyle(
            color="white",
            bgcolor="blue",
            padding=15,
            shape=ft.RoundedRectangleBorder(radius=8)
        )
    )

    # Sahypa elementleri goşmak
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

if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER)
