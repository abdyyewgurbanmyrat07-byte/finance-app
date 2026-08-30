from flask import Flask, render_template_string, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ----------------- DATABASE SETUP -----------------
def init_db():
    conn = sqlite3.connect("finance_ultra.db")
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, amount REAL, trans_type TEXT, category TEXT, date TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, target_amount REAL, current_amount REAL)')
    conn.commit()
    conn.close()

init_db()

# ----------------- HTML / JS / CSS (FRONTEND UI) -----------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MEIKA - Finance Tracker ULTRA PRO</title>
    <style>
        :root {
            --bg-color: #0D0E15;
            --card-bg: #161824;
            --border-color: #25283B;
            --cyan: #00F0FF;
            --green: #00FF88;
            --red: #FF2A6D;
            --text: #FFFFFF;
            --muted: #8A8DAB;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 15px;
        }

        h1, h2, h3 { margin: 0; }
        
        .header {
            color: var(--cyan);
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            padding: 10px 0;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 15px;
        }

        .balance-card {
            background: var(--card-bg);
            border: 1px solid var(--cyan);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            text-align: center;
        }

        .balance-val {
            font-size: 28px;
            font-weight: bold;
            color: var(--cyan);
            margin-top: 5px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px;
        }

        .inc-val { color: var(--green); font-size: 18px; font-weight: bold; }
        .exp-val { color: var(--red); font-size: 18px; font-weight: bold; }

        .form-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }

        input, select, button {
            width: 100%;
            padding: 10px;
            margin-top: 8px;
            background: #0D0E15;
            border: 1px solid var(--border-color);
            color: #fff;
            border-radius: 5px;
            box-sizing: border-box;
        }

        .btn-inc { background: var(--green); color: #000; font-weight: bold; cursor: pointer; border: none; }
        .btn-exp { background: var(--red); color: #fff; font-weight: bold; cursor: pointer; border: none; }

        .trans-item {
            background: var(--card-bg);
            border-bottom: 1px solid var(--border-color);
            padding: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 5px;
            margin-bottom: 5px;
        }

        .trans-title { font-weight: bold; font-size: 14px; }
        .trans-cat { color: var(--muted); font-size: 12px; }
        .trans-amount { font-weight: bold; font-size: 16px; }

        .goal-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
        }

        .progress-bar {
            background: #25283B;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }

        .progress-fill {
            background: var(--cyan);
            height: 100%;
            width: 0%;
        }
    </style>
</head>
<body>

    <div class="header">⚡ MEIKA FINANCE ULTRA PRO</div>

    <!-- BALANCE OVERVIEW -->
    <div class="balance-card">
        <div style="color: var(--muted); font-size: 12px;">JEMI BALANS</div>
        <div class="balance-val" id="totalBalance">$0.00</div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div style="color: var(--muted); font-size: 11px;">GIRDEJILER</div>
            <div class="inc-val" id="totalIncome">+$0.00</div>
        </div>
        <div class="stat-card">
            <div style="color: var(--muted); font-size: 11px;">ÇYKDAJYLAR</div>
            <div class="exp-val" id="totalExpense">-$0.00</div>
        </div>
    </div>

    <!-- FORM PANEL -->
    <div class="form-card">
        <input type="text" id="desc" placeholder="Düşündiriş (Meselem: Nahar)">
        <input type="number" id="amount" placeholder="Mukdary ($)">
        <select id="cat">
            <option value="Iýmit">Iýmit</option>
            <option value="Oýun/Programma">Oýun/Programma</option>
            <option value="Söwda">Söwda</option>
            <option value="Transport">Transport</option>
            <option value="Beýleki">Beýleki</option>
        </select>
        <div style="display: flex; gap: 10px; margin-top: 10px;">
            <button class="btn-inc" onclick="addTrans('Girdeji')">➕ Girdeji</button>
            <button class="btn-exp" onclick="addTrans('Çykdajy')">➖ Çykdajy</button>
        </div>
    </div>

    <!-- TRANSACTIONS LIST -->
    <h3 style="color: var(--cyan); margin-bottom: 10px; font-size: 16px;">Geçirimler</h3>
    <div id="transList"></div>

    <script>
        async function fetchFinanceData() {
            const res = await fetch('/api/get_data');
            const data = await res.json();
            
            document.getElementById('totalBalance').innerText = `$${data.balance.toFixed(2)}`;
            document.getElementById('totalIncome').innerText = `+$${data.income.toFixed(2)}`;
            document.getElementById('totalExpense').innerText = `-$${data.expense.toFixed(2)}`;

            const listEl = document.getElementById('transList');
            listEl.innerHTML = '';
            
            data.transactions.forEach(item => {
                const isInc = item.type === 'Girdeji';
                const color = isInc ? 'var(--green)' : 'var(--red)';
                const sign = isInc ? '+' : '-';
                
                listEl.innerHTML += `
                    <div class="trans-item">
                        <div>
                            <div class="trans-title">${item.title}</div>
                            <div class="trans-cat">${item.category} • ${item.date}</div>
                        </div>
                        <div class="trans-amount" style="color: ${color}">
                            ${sign}$${item.amount.toFixed(2)}
                        </div>
                    </div>
                `;
            });
        }

        async function addTrans(type) {
            const title = document.getElementById('desc').value;
            const amount = document.getElementById('amount').value;
            const category = document.getElementById('cat').value;

            if(!title || !amount) return;

            await fetch('/api/add_trans', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, amount: parseFloat(amount), type, category })
            });

            document.getElementById('desc').value = '';
            document.getElementById('amount').value = '';
            fetchFinanceData();
        }

        fetchFinanceData();
    </script>
</body>
</html>
"""

# ----------------- API ENDPOINTS -----------------
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/get_data', methods=['GET'])
def get_data():
    conn = sqlite3.connect("finance_ultra.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, amount, trans_type, category, date FROM transactions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    tot_inc, tot_exp = 0.0, 0.0
    transactions = []

    for r in rows:
        t_id, title, amt, t_type, cat, date = r
        if t_type == "Girdeji":
            tot_inc += amt
        else:
            tot_exp += amt
        
        transactions.append({
            "id": t_id, "title": title, "amount": amt,
            "type": t_type, "category": cat, "date": date
        })

    return jsonify({
        "balance": tot_inc - tot_exp,
        "income": tot_inc,
        "expense": tot_exp,
        "transactions": transactions
    })

@app.route('/api/add_trans', methods=['POST'])
def add_trans():
    data = request.json
    title = data.get('title')
    amount = data.get('amount')
    trans_type = data.get('type')
    category = data.get('category')
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = sqlite3.connect("finance_ultra.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (title, amount, trans_type, category, date) VALUES (?, ?, ?, ?, ?)",
                   (title, amount, trans_type, category, date_str))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
