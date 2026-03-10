import os
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "1234"
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
ADMIN_ID = "7089720301"
TELEGRAM_USERNAME = "Bby_kiwii7"
BASE_URL = "https://kiwiigameshop.onrender.com" 

packages = [
    {"d": "Weekly Pass", "p": "5,800"}, {"d": "Twilight Pass", "p": "32,000"},
    {"d": "86", "p": "4,800"}, {"d": "172", "p": "9,600"},
    {"d": "257", "p": "14,400"}, {"d": "343", "p": "19,200"},
    {"d": "429", "p": "24,000"}, {"d": "514", "p": "28,800"},
    {"d": "600", "p": "33,600"}, {"d": "706", "p": "38,400"},
    {"d": "878", "p": "48,000"}, {"d": "963", "p": "52,800"},
    {"d": "1049", "p": "57,600"}, {"d": "1135", "p": "62,400"},
    {"d": "1220", "p": "67,200"}, {"d": "1412", "p": "76,800"},
    {"d": "1667", "p": "91,200"}, {"d": "1841", "p": "100,800"},
    {"d": "2195", "p": "115,000"}, {"d": "3688", "p": "192,000"},
    {"d": "4390", "p": "230,000"}, {"d": "5532", "p": "288,000"},
    {"d": "7376", "p": "384,000"}, {"d": "9288", "p": "480,000"}
]

db = {}

@app.route('/order', methods=['POST'])
def order():
    try:
        uid = request.form.get('u'); zone = request.form.get('z')
        pkg = request.form.get('p'); amt = request.form.get('a')
        pay = request.form.get('pay'); photo = request.files.get('photo')
        oid = os.urandom(2).hex().upper()
        db[oid] = {'u': uid, 'z': zone, 'p': pkg, 'a': amt, 'status': 'Pending ⏳'}
        
        # Telegram ဆီသို့ စာနဲ့ပုံ တစ်ခါတည်းတွဲပို့ခြင်း
        admin_link = f"{BASE_URL}/admin?pw={ADMIN_PASSWORD}"
        caption_msg = (f"🔔 *NEW ORDER: #{oid}*\n🆔 *User ID:* {uid}\n🌐 *Zone ID:* {zone}\n💎 *Item:* {pkg}\n💰 *Price:* {amt} Ks\n💵 *Payment:* {pay}\n\n🔗 [Admin Panel]({admin_link})")
        
        if photo:
            photo.seek(0)
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data={'chat_id': ADMIN_ID, 'caption': caption_msg, 'parse_mode': 'Markdown'}, files={'photo': photo})
        else:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={'chat_id': ADMIN_ID, 'text': caption_msg, 'parse_mode': 'Markdown'})
            
        return render_template_string('''
        <html><body style="background:#0f172a;color:white;text-align:center;padding:100px 20px;font-family:sans-serif;">
            <div style="background:#1e293b;padding:30px;border-radius:20px;display:inline-block;border:1px solid #fbbf24;">
                <h2 style="color:#fbbf24;margin-top:0;">Order Successful!</h2>
                <p>Order ID: <b style="font-size:24px;color:#fbbf24;">#{{oid}}</b></p>
                <div style="margin-top:20px;">
                    <a href="/" style="color:white;text-decoration:none;background:#334155;padding:10px 20px;border-radius:10px;margin-right:10px;">Home</a>
                    <a href="/check" style="color:#0f172a;text-decoration:none;background:#fbbf24;padding:10px 20px;border-radius:10px;font-weight:bold;">Check Status</a>
                </div>
            </div>
        </body></html>''', oid=oid)
    except: return "Error", 500

@app.route('/check', methods=['GET', 'POST'])
def check():
    res = ""
    if request.method == 'POST':
        oid = request.form.get('oid', '').strip().upper().replace("#", "")
        if oid in db:
            o = db[oid]
            res = f"<div style='background:#1e293b;padding:15px;border-radius:12px;border:1px solid #fbbf24;margin-top:20px;text-align:left;'>" \
                  f"<b>Order:</b> #{oid}<br><b>Status:</b> <span style='color:#fbbf24'>{o['status']}</span><br>" \
                  f"<b>Item:</b> {o['p']}<br><b>Account:</b> {o['u']} ({o['z']})</div>"
        else: res = "<p style='color:#ef4444;margin-top:15px;'>Order Not Found!</p>"
    return render_template_string('''
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#0f172a;color:white;text-align:center;padding:50px 20px;font-family:sans-serif;">
        <h3 style="color:#fbbf24;">Track Your Order</h3>
        <form method="post" style="max-width:400px;margin:auto;">
            <input name="oid" placeholder="Order ID (e.g. 4A99)" style="width:100%;padding:12px;border-radius:10px;border:1px solid #334155;background:#1e293b;color:white;" required>
            <button type="submit" style="width:100%;margin-top:15px;padding:12px;background:#fbbf24;border:none;border-radius:10px;font-weight:bold;cursor:pointer;">SEARCH</button>
        </form>{{res | safe}}
        <br><a href="/" style="color:#94a3b8;text-decoration:none;">← Back to Shop</a>
    </body></html>''', res=res)

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD: return "Unauthorized", 401
    orders = "".join([f"<div style='border:1px solid #334155;margin-bottom:10px;padding:15px;background:#1e293b;border-radius:10px;'><b>#{k}</b>: {v['u']} - {v['p']} [{v['status']}]</div>" for k, v in db.items()])
    return f"<html><body style='background:#0f172a;color:white;padding:20px;font-family:sans-serif;'><h2>Admin</h2>{orders or 'Empty'}</body></html>"

@app.route('/')
def index():
    pkg_items = "".join([f'<div onclick="sel(this,\'{p["d"]}\',\'{p["p"]}\')" style="background:#1e293b;border:1px solid #334155;padding:15px;border-radius:12px;cursor:pointer;text-align:center;"><span style="font-size:13px;display:block;margin-bottom:5px;">{p["d"]}</span><b style="color:#fbbf24">{p["p"]} Ks</b></div>' for p in packages])
    return render_template_string('''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; padding:15px; max-width:450px; margin:auto; }
    .header { text-align:center; margin-bottom:20px; }
    .grid { display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:25px; }
    .selected { border-color: #fbbf24 !important; box-shadow: 0 0 8px #fbbf24; }
    .form-box { background:#1e293b; padding:20px; border-radius:20px; border:1px solid #334155; margin-bottom:20px; }
    input, select { width:100%; padding:14px; margin:8px 0; border-radius:12px; border:1px solid #334155; background:#0f172a; color:white; box-sizing:border-box; outline:none; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; margin-top:10px; cursor:pointer; color:#0f172a; font-size:16px; }
    .action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
    .action-btn { padding: 12px; border-radius: 12px; text-decoration: none; text-align: center; font-size: 13px; font-weight: bold; border: 1px solid #334155; }
</style></head>
<body>
    <div class="header"><h2 style="color:#fbbf24;margin-bottom:5px;">KIWII GAME SHOP</h2><p style="font-size:12px;color:#94a3b8;margin-top:0;">Fast & Trusted Top-Up Service</p></div>
    
    <div class="grid">{{pkg_items | safe}}</div>
    
    <div class="form-box">
        <form action="/order" method="post" enctype="multipart/form-data">
            <input name="u" placeholder="User ID" required>
            <input name="z" placeholder="Zone ID" required>
            <input id="p_val" name="p" type="hidden"><input id="a_val" name="a" type="hidden">
            <select name="pay"><option>KBZPay</option><option>WaveMoney</option></select>
            <p style="font-size:11px; color:#94a3b8; margin:10px 0 5px 5px;">Upload Payment Screenshot</p>
            <input type="file" name="photo" required accept="image/*">
            <button type="submit" class="buy-btn">PLACE ORDER NOW</button>
        </form>

        <div class="action-grid">
            <a href="/check" class="action-btn" style="background:#0f172a; color:#fbbf24;">🔍 CHECK ORDER</a>
            <a href="https://t.me/{{tu}}" class="action-btn" style="background:#2563eb; color:white; border:none;">💬 CONTACT CS</a>
        </div>
    </div>

    <script>function sel(el,d,p){var cards=document.getElementsByClassName('grid')[0].children;for(var i=0;i<cards.length;i++){cards[i].classList.remove('selected');}el.classList.add('selected');document.getElementById('p_val').value=d;document.getElementById('a_val').value=p;}</script>
</body></html>''', pkg_items=pkg_items, tu=TELEGRAM_USERNAME)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
    
