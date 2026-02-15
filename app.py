import pandas as pd
import json
import os
from flask import Flask, render_template_string, request

app = Flask(__name__)

# --- 1. Database & Persistence ---
DB_FILE = 'wallet_db.json'

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"balance": 47000.0, "history": ["System Initialized - V13.5"]}

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

wallet = load_data()

# --- 2. Payroll Data Reader (Staff Statements) ---
def get_staff_statement():
    try:
        df = pd.read_csv('تقرير_مرتبات_الملاذ_7406_فبراير.xlsx - Sheet1.csv')
        # Selecting key columns for the statement
        statement = df[['الاسم', 'الراتب المستحق (EGP)', 'رقم المحفظة المستلمة']].copy()
        statement.columns = ['Name', 'Salary', 'Wallet ID']
        return statement.to_dict(orient='records'), df['الراتب المستحق (EGP)'].sum()
    except:
        return [], 0

# --- 3. Clean Professional English UI ---
html_layout = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AL-MALAZ Fintech Solution</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: #010409; color: #e6edf3; text-align: center; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: #0d1117; border: 1px solid #30363d; border-radius: 12px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); }
        .balance-label { color: #8b949e; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
        .balance-amount { font-size: 52px; color: #3fb950; font-weight: 800; margin: 10px 0; }
        .input-box { width: 90%; padding: 12px; margin: 15px 0; border-radius: 6px; border: 1px solid #30363d; background: #010409; color: white; font-size: 18px; text-align: center; }
        .btn { width: 100%; padding: 14px; margin: 8px 0; border-radius: 6px; border: none; font-weight: bold; cursor: pointer; font-size: 16px; transition: 0.2s; }
        .btn-deposit { background: #238636; color: white; }
        .btn-withdraw { background: #da3633; color: white; }
        .btn-payroll { background: #1f6feb; color: white; margin-top: 15px; }
        .statement-table { width: 100%; border-collapse: collapse; margin-top: 25px; font-size: 14px; text-align: left; }
        .statement-table th, .statement-table td { padding: 12px; border-bottom: 1px solid #30363d; }
        .history { background: #010409; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: left; font-size: 13px; max-height: 120px; overflow-y: auto; color: #8b949e; }
    </style>
</head>
<body>
    <div class="container">
        <div class="balance-label">Total Wallet Balance</div>
        <div class="balance-amount">{{ "{:,.2f}".format(wallet.balance) }} EGP</div>

        <form action="/action" method="post">
            <input type="number" step="0.01" name="amount" class="input-box" placeholder="Enter Amount...">
            <button name="type" value="deposit" class="btn btn-deposit">DEPOSIT FUNDS</button>
            <button name="type" value="withdraw" class="btn btn-withdraw">WITHDRAW FUNDS</button>
        </form>

        <form action="/process_payroll" method="post">
            <button class="btn btn-payroll">PROCESS STAFF PAYROLL</button>
        </form>

        <table class="statement-table">
            <thead>
                <tr><th>Staff Name</th><th>Salary</th><th>Status</th></tr>
            </thead>
            <tbody>
                {% for staff in staff_list %}
                <tr>
                    <td>{{ staff.Name }}</td>
                    <td>{{ "{:,.0f}".format(staff.Salary) }}</td>
                    <td style="color:#3fb950">● Ready</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="history">
            <strong>Activity Log:</strong>
            {% for log in wallet.history %}
                <div style="margin-top:5px; border-bottom: 1px solid #21262d;">{{ log }}</div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    staff_list, _ = get_staff_statement()
    return render_template_string(html_layout, wallet=wallet, staff_list=staff_list)

@app.route('/action', methods=['POST'])
def action():
    try:
        amt = float(request.form.get('amount', 0))
        atype = request.form.get('type')
        if atype == 'deposit' and amt > 0:
            wallet["balance"] += amt
            wallet["history"].insert(0, f"Deposit: +{amt:,.2f} EGP")
        elif atype == 'withdraw' and 0 < amt <= wallet["balance"]:
            wallet["balance"] -= amt
            wallet["history"].insert(0, f"Withdraw: -{amt:,.2f} EGP")
        save_data(wallet)
    except: pass
    return index()

@app.route('/process_payroll', methods=['POST'])
def process_payroll():
    _, total_salaries = get_staff_statement()
    if total_salaries > 0 and wallet["balance"] >= total_salaries:
        wallet["balance"] -= total_salaries
        wallet["history"].insert(0, f"Payroll: -{total_salaries:,.2f} EGP (Processed)")
        save_data(wallet)
    return index()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
