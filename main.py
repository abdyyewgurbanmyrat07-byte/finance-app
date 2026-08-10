import flet as ft
import requests
import json
import os
from datetime import datetime

DATA_FILE = "finance_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"transactions": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main(page: ft.Page):
    page.title = "Maliýe Tracker"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 15

    data = load_data()

    # UI elementler
    crypto_text = ft.Text("🪙 BTC: Ýüklenýär... | 💎 ETH: Ýüklenýär...", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.CYAN)
    balance_text = ft.Text("0.00 TMT", size=26, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400)
    
    desc_input = ft.TextField(label="Düşündiriş (Taksi, Çörek, Aýlyk)", border_radius=10)
    amount_input = ft.TextField(label="Mukdary (TMT)", keyboard_type=ft.KeyboardType.NUMBER, border_radius=10)
    type_dropdown = ft.Dropdown(
        label="Görnüşi",
        options=[
            ft.dropdown.Option("Çykdajy"),
            ft.dropdown.Option("Girdeji"),
        ],
        value="Çykdajy",
        border_radius=10
    )

    transactions_list = ft.Column(spacing=10)

    def fetch_crypto():
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            url_btc = "https://api.bybit.com/v5/market/tickers?category=spot&symbol=BTCUSDT"
            url_eth = "https://api.bybit.com/v5/market/tickers?category=spot&symbol=ETHUSDT"
            
            res_btc = requests.get(url_btc, headers=headers, timeout=5).json()
            res_eth = requests.get(url_eth, headers=headers, timeout=5).json()
            
            btc_price = float(res_btc['result']['list'][0]['lastPrice'])
            eth_price = float(res_eth['result']['list'][0]['lastPrice'])
            
            crypto_text.value = f"🪙 BTC: ${btc_price:,.2f} | 💎 ETH: ${eth_price:,.2f}"
        except:
            crypto_text.value = "⚠️ Bahalara birigip bolmady"
        page.update()

    def update_ui():
        transactions_list.controls.clear()
        total_balance = 0.0

        for item in reversed(data["transactions"]):
            amount = item["amount"]
            is_income = item["type"] == "Girdeji"

            if is_income:
                total_balance += amount
                icon = ft.icons.ARROW_DOWNWARD
                color = ft.colors.GREEN_400
                prefix = "+"
            else:
                total_balance -= amount
                icon = ft.icons.ARROW_UPWARD
                color = ft.colors.RED_400
                prefix = "-"

            card = ft.Card(
                content=ft.Container(
                    padding=10,
                    content=ft.ListTile(
                        leading=ft.Icon(icon, color=color),
                        title=ft.Text(f"{item['desc']}", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(f"{item['date']}"),
                        trailing=ft.Text(f"{prefix}{amount:.2f} TMT", size=16, weight=ft.FontWeight.BOLD, color=color)
                    )
                )
            )
            transactions_list.controls.append(card)

        balance_text.value = f"{total_balance:,.2f} TMT"
        page.update()

    def add_transaction(e):
        desc = desc_input.value.strip() if desc_input.value else ""
        amount_str = amount_input.value.strip() if amount_str else ""
        trans_type = type_dropdown.value

        if not desc or not amount_str:
            return

        try:
            amount = float(amount_str)
        except ValueError:
            return

        now = datetime.now().strftime("%d.%m %H:%M")

        new_item = {
            "desc": desc,
            "amount": amount,
            "type": trans_type,
            "date": now
        }

        data["transactions"].append(new_item)
        save_data(data)

        desc_input.value = ""
        amount_input.value = ""
        update_ui()

    add_btn = ft.ElevatedButton(
        text="➕ Ýatda Sakla",
        on_click=add_transaction,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        width=400,
        height=45
    )

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("🌐 Kripto Bahalary", size=18, weight=ft.FontWeight.BOLD),
                crypto_text
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            border_radius=10,
            bgcolor=ft.colors.SURFACE_VARIANT
        ),
        ft.Divider(),
        ft.Container(
            content=ft.Column([
                ft.Text("Jemi Balansyňyz", size=14, color=ft.colors.GREY_400),
                balance_text
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=15,
            border_radius=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
            alignment=ft.alignment.center
        ),
        ft.Divider(),
        ft.Text("Täze Geçirme Goşmak", size=16, weight=ft.FontWeight.BOLD),
        desc_input,
        amount_input,
        type_dropdown,
        add_btn,
        ft.Divider(),
        ft.Text("📜 Soňky Geçirilmeler", size=16, weight=ft.FontWeight.BOLD),
        transactions_list
    )

    fetch_crypto()
    update_ui()

ft.app(target=main)
