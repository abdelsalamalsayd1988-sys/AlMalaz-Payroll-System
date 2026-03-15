from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'almalaz_secure_payroll_key'

# 1. إعداد قاعدة البيانات وكلمة السر
DB_FILE = 'wallet_db.json'
DELETE_PASSWORD = 'AlMalaz@2026'

# 2. دالة تحميل البيانات
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

# 3. دالة حفظ البيانات
def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 4. الصفحة الرئيسية مع ميزة البحث
@app.route('/')
def home():
    search_query = request.args.get('search', '')
    all_data = load_data()
    
    # محرك البحث (يؤدي لفلترة البيانات بالاسم)
    if search_query:
        filtered_data = [item for item in all_data if search_query.lower() in item['name'].lower()]
    else:
        filtered_data = all_data
        
    return render_template('index.html', data=filtered_data, search_query=search_query)

# 5. إضافة معاملة جديدة (إيداع/سحب)
@app.route('/add', methods=['POST'])
def add_transaction():
    name = request.form.get('name')
    amount_str = request.form.get('amount')
    trans_type = request.form.get('type')
    
    if name and amount_str:
        new_entry = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'name': name,
            'amount': float(amount_str),
            'type': trans_type
        }
        data = load_data()
        data.append(new_entry)
        save_data(data)
        flash('تمت إضافة المعاملة بنجاح!')
    return redirect(url_for('home'))

# 6. حذف معاملة (محمي بكلمة سر AlMalaz@2026)
@app.route('/delete/<id>', methods=['POST'])
def delete_entry(id):
    password = request.form.get('password')
    if password == DELETE_PASSWORD:
        data = load_data()
        data = [item for item in data if item['id'] != id]
        save_data(data)
        flash('تم حذف السجل بنجاح.')
    else:
        flash('خطأ: كلمة سر المسح غير صحيحة!')
    return redirect(url_for('home'))

if __name__ == '__main__':
    # التشغيل على بورت 8080 ليتوافق مع Google Cloud
    app.run(host='0.0.0.0', port=8080, debug=True)
