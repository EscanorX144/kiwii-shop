import os
import random
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "1234"
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
ADMIN_ID = "7089720301"

# --- DATABASE SETUP ---
def get_db_connection():
    conn = sqlite3.connect('orders.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS orders 
                     (id TEXT PRIMARY KEY, uid TEXT, zone TEXT, pkg TEXT, amt TEXT, status TEXT, note TEXT)''')
        conn.commit()

init_db()

# Product List
packages = [
    {"d": "Weekly Pass", "p": "5,800"}, {"d": "Twilight Pass", "p": "32,000"},
    {"d": "86", "p": "4,800"}, {"d": "172", "p": "9,600"},
    {"d": "257", "p": "14,400"}, {"d": "343", "p": "19,200"},
    {"d": "429", "p": "24,000"}, {"d": "514", "p": "28,800"},
    {"d": "600", "p": "33,600"}, {"d": "706", "p": "38,400"}
]

@app.route('/order', methods=['POST'])
def order():
    try:
        uid = request.form.get('u'); zone = request.form.get('z')
        pkg_name = request.form.get('p'); amt = request.form.get('a')
        pay = request.form.get('pay'); photo = request.files.get('photo')
        
        if not pkg_name: return "Package ရွေးပေးပါဦးဗျ။", 400
        
        oid = os.urandom(2).hex().upper()
        
        # Save to SQLite Database
        with get_db_connection() as conn:
            conn.execute("INSERT INTO orders (id, uid, zone, pkg, amt, status, note) VALUES (?,?,?,?,?,?,?)",
                         (oid, uid, zone, pkg_name, amt, 'Pending ⏳', ''))
            conn.commit()
        
        admin_link = f"https://kiwiigameshop.onrender.com/admin?pw={ADMIN_PASSWORD}"
        caption_msg = (f"🔔 *NEW ORDER: #{oid}*\n🆔 *ID:* `{uid}` (`{zone}`)\n💎 *Item:* {pkg_name}\n💰 *Price:* {amt} Ks\n💵 *Pay:* {pay}\n\n🔗 [Open Admin Panel]({admin_link})")

        if photo:
            photo.seek(0)
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                          data={'chat_id': ADMIN_ID, 'caption': caption_msg, 'parse_mode': 'Markdown'}, 
                          files={'photo': photo}, timeout=20)
                          
        return render_template_string('<html><body style="background:#0f172a;color:white;text-align:center;padding-top:100px;font-family:sans-serif;"><h2>Order Success! ✅</h2><p>Order ID: #{{oid}}</p><p>Status ကို "Check Status" မှာ ပြန်စစ်ပေးပါဗျ။</p><a href="/" style="color:#fbbf24;text-decoration:none;">Back to Shop</a></body></html>', oid=oid)
    except Exception as e:
        return "Error", 500

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD: return "Unauthorized", 401
    
    order_rows = ""
    with get_db_connection() as conn:
        orders = conn.execute('SELECT * FROM orders ORDER BY rowid DESC').fetchall()
        for v in orders:
            order_rows += f'''
            <div style="border:1px solid #334155; margin-bottom:10px; padding:15px; background:#1e293b; border-radius:12px;">
                <b>#{v['id']}</b>: {v['uid']} ({v['zone']}) - {v['pkg']} <br> Status: <b style="color:#fbbf24">{v['status']}</b> {f'({v["note"]})' if v['note'] else ''}<br><br>
                {f'<a href="/done/{v["id"]}?pw={ADMIN_PASSWORD}" style="background:#22c55e; color:white; padding:8px 16px; border-radius:8px; text-decoration:none;">DONE</a>' if 'Pending' in v['status'] else ''}
                {f'<form action="/reject/{v["id"]}" style="display:inline;margin-left:10px;"><input name="pw" type="hidden" value="{ADMIN_PASSWORD}"><input name="msg" placeholder="ငွေမပြည့်ပါ / ID မှား" style="padding:8px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:white;"><button type="submit" style="background:#ef4444; color:white; border:none; padding:8px 16px; border-radius:8px; margin-left:5px;">REJECT</button></form>' if 'Pending' in v['status'] else ''}
            </div>'''
    return f"<html><body style='background:#0f172a;color:white;padding:20px;font-family:sans-serif;'><h2>Admin Control</h2>{order_rows or 'No orders'}</body></html>"

@app.route('/done/<oid>')
def done(oid):
    pw = request.args.get('pw')
    if pw == ADMIN_PASSWORD:
        with get_db_connection() as conn:
            conn.execute("UPDATE orders SET status = 'Success ✅' WHERE id = ?", (oid,))
            conn.commit()
    return redirect(url_for('admin', pw=ADMIN_PASSWORD))

@app.route('/reject/<oid>', methods=['POST'])
def reject(oid):
    pw = request.form.get('pw'); msg = request.form.get('msg') or "Payment Incorrect"
    if pw == ADMIN_PASSWORD:
        with get_db_connection() as conn:
            conn.execute("UPDATE orders SET status = 'Rejected ❌', note = ? WHERE id = ?", (msg, oid))
            conn.commit()
    return redirect(url_for('admin', pw=ADMIN_PASSWORD))

@app.route('/check', methods=['GET', 'POST'])
def check():
    res = ""
    if request.method == 'POST':
        oid = request.form.get('oid', '').strip().upper().replace("#", "")
        with get_db_connection() as conn:
            o = conn.execute('SELECT * FROM orders WHERE id = ?', (oid,)).fetchone()
            if o:
                color = "#fbbf24" if "Pending" in o['status'] else "#22c55e" if "Success" in o['status'] else "#ef4444"
                res = f"<div style='background:#1e293b;padding:20px;border-radius:15px;border:1px solid {color};margin-top:20px;'>Status: <b style='color:{color};'>{o['status']}</b><br><small>မှတ်ချက် - {o['note'] or 'မရှိပါ'}</small></div>"
            else: res = "<p style='color:#ef4444;margin-top:15px;'>ID မမှန်ပါဗျ။</p>"
    return render_template_string('<html><body style="background:#0f172a;color:white;text-align:center;padding:50px 20px;font-family:sans-serif;"><h3>Check Status</h3><form method="post"><input name="oid" placeholder="Order ID" style="padding:14px;border-radius:10px;width:100%;max-width:300px;"><br><button type="submit" style="padding:12px 30px;background:#fbbf24;border:none;border-radius:10px;margin-top:15px;">CHECK</button></form>{{res|safe}}<br><a href="/" style="color:#94a3b8;text-decoration:none;">← Back</a></body></html>', res=res)

@app.route('/')
def index():
    pkg_items = "".join([f'<div class="pkg-card" onclick="sel(this,\'{p["d"]}\',\'{p["p"]}\')"><span>{p["d"]}</span><br><b style="color:#fbbf24">{p["p"]} Ks</b></div>' for p in packages])
    return render_template_string('''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; padding:15px; max-width:450px; margin:auto; }
    .grid { display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:20px; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; cursor:pointer; text-align:center; }
    .selected { border-color: #fbbf24 !important; background: #334155 !important; }
    .form-box { background:#1e293b; padding:20px; border-radius:20px; border:1px solid #334155; }
    input, select { width:100%; padding:14px; margin:8px 0; border-radius:12px; border:1px solid #334155; background:#0f172a; color:white; box-sizing:border-box; outline:none; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; cursor:pointer; color:#0f172a; font-size:16px; margin-top:10px; }
</style></head>
<body>
    <h2 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h2>
    <div class="grid">{{pkg_items | safe}}</div>
    <div class="form-box">
        <form action="/order" method="post" enctype="multipart/form-data">
            <input name="u" placeholder="User ID" required>
            <input name="z" placeholder="Zone ID" required>
            <input id="p_val" name="p" type="hidden"><input id="a_val" name="a" type="hidden">
            <select name="pay"><option>KBZPay</option><option>WaveMoney</option></select>
            <input type="file" name="photo" required accept="image/*">
            <button type="submit" class="buy-btn">PLACE ORDER NOW</button>
        </form>
        <a href="/check" style="display:block; text-align:center; color:#94a3b8; margin-top:20px; text-decoration:none;">🔍 CHECK STATUS</a>
    </div>
    <script>function sel(el,d,p){var cards=document.getElementsByClassName('pkg-card');for(var i=0;i<cards.length;i++){cards[i].classList.remove('selected');}el.classList.add('selected');document.getElementById('p_val').value=d;document.getElementById('a_val').value=p;}</script>
</body></html>''', pkg_items=pkg_items)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
