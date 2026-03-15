from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'almalaz_secret_key'

# إعداد ملف قاعدة البيانات
DB_FILE = 'wallet_db.json'
DELETE_PASSWORD = 'AlMalaz@2026'

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def home():
    search_query = request.args.get('search', '')
    all_data = load_data()
    
    # ميزة البحث
    if search_query:
        filtered_data = [item for item in all_data if search_query.lower() in item['name'].lower()]
    else:
        filtered_data = all_data
        
    return render_template('index.html', data=filtered_data, search_query=search_query)

@app.route('/add', methods=['POST'])
def add_transaction():
    name = request.form.get('name')
    amount = float(request.form.get('amount'))
    type = request.form.get('type') # 'إيداع' أو 'سحب'
    
    new_entry = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'name': name,
        'amount': amount,
        'type': type
    }
    
    data = load_data()
    data.append(new_entry)
    save_data(data)
    flash('تمت العملية بنجاح!')
    return redirect(url_for('home'))

@app.route('/delete/<id>', methods=['POST'])
def delete_entry(id):
    password = request.form.get('password')
    if password == DELETE_PASSWORD:
        data = load_data()
        data = [item for item in data if item['id'] != id]
        save_data(data)
        flash('تم المسح بنجاح.')
    else:
        flash('كلمة سر المسح خاطئة!')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
