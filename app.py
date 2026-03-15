from flask import Flask, render_template, jsonify
import os
import json

app = Flask(__name__)

# اسم ملف قاعدة البيانات
DB_FILE = 'wallet_db.json'

@app.route('/')
def home():
    # هذا السطر يربط الكود بملف index.html الذي أنشأته في مجلد templates
    return render_template('index.html')

@app.route('/list')
def list_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
        return jsonify(data)
    return jsonify({"message": "لا توجد بيانات بعد"})

if __name__ == '__main__':
    app.run(debug=True)

