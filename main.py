import os
import random
from flask import Flask, render_template_string, request, redirect, url_for
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "1234"
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
ADMIN_ID = "7089720301"

# Product List
packages = [
    {"d": "Weekly Pass", "p": "5,800", "id": "632"}, {"d": "Twilight Pass", "p": "32,000", "id": "629"},
    {"d": "86", "p": "4,800", "id": "258"}, {"d": "172", "p": "9,600", "id": "259"},
    {"d": "257", "p": "14,400", "id": "260"}, {"d": "343", "p": "19,200", "id": "261"},
    {"d": "429", "p": "24,000", "id": "262"}, {"d": "514", "p": "28,800", "id": "263"},
    {"d": "600", "p": "33,600", "id": "264"}, {"d": "706", "p": "38,400", "id": "265"},
    {"d": "878", "p": "48,000", "id": "266"}, {"d": "963", "p": "52,800", "id": "267"},
    {"d": "1049", "p": "57,600", "id": "268"}, {"d": "1135", "p": "62,400", "id": "269"},
    {"d": "1220", "p": "67,200", "id": "270"}, {"d": "1412", "p": "76,800", "id": "271"},
    {"d": "1667", "p": "91,200", "id": "272"}, {"d": "1841", "p": "100,800", "id": "273"},
    {"d": "2195", "p": "115,000", "id": "274"}, {"d": "3688", "p": "192,000", "id": "275"},
    {"d": "4390", "p": "230,000", "id": "276"}, {"d": "5532", "p": "288,000", "id": "277"},
    {"d": "7376", "p": "384,000", "id": "278"}, {"d": "9288", "p": "480,000", "id": "279"}
]

db = {}

@app.route('/order', methods=['POST'])
def order():
    try:
        uid = request.form.get('u'); zone = request.form.get('z')
        pkg_name = request.form.get('p'); amt = request.form.get('a')
        pay = request.form.get('pay'); photo = request.files.get('photo')
        
        if not pkg_name: return "Package ရွေးပေးပါဦးဗျ။", 400
        
        # Order ID ထုတ်လုပ်ခြင်း
        oid = os.urandom(2).hex().upper()
        db[oid] = {'u': uid, 'z': zone, 'p': pkg_name, 'a': amt, 'status': 'Pending ⏳', 'note': ''}
        
        # Admin Panel Link သတ်မှတ်ခြင်း (Smile One link အစားထိုးရန်)
        admin_link = f"https://kiwiigameshop.onrender.com/admin?pw={ADMIN_PASSWORD}"
        
        # Telegram Message (Smile One link များ ဖယ်ရှားပြီး Admin Link ထည့်သွင်းထားသည်)
        caption_msg = (f"🔔 *NEW ORDER: #{oid}*\n"
                       f"🆔 *ID:* `{uid}` (`{zone}`)\n"
                       f"💎 *Item:* {pkg_name}\n"
                       f"💰 *Price:* {amt} Ks\n"
                       f"💵 *Pay:* {pay}\n\n"
                       f"🔗 [Open Admin Panel]({admin_link})")

        if photo:
            photo.seek(0)
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                          data={'chat_id': ADMIN_ID, 'caption': caption_msg, 'parse_mode': 'Markdown'}, 
                          files={'photo': photo}, timeout=15)
                          
        return render_template_string('<html><body style="background:#0f172a;color:white;text-align:center;padding-top:100px;font-family:sans-serif;"><h2>Order Success! ✅</h2><p>Order ID: #{{oid}}</p><a href="/" style="color:#fbbf24;text-decoration:none;">Back to Shop</a></body></html>', oid=oid)
    except Exception as e:
        print(f"Error: {e}")
        return "Error", 500

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD: return "Unauthorized", 401
    order_rows = ""
    for k, v in db.items():
        order_rows += f'''
        <div style="border:1px solid #334155; margin-bottom:10px; padding:15px; background:#1e293b; border-radius:12px;">
            <b>#{k}</b>: {v['u']} ({v['z']}) - {v['p']} <br> Status: <b style="color:#fbbf24">{v['status']}</b> {f'({v["note"]})' if v['note'] else ''}<br><br>
            {f'<a href="/done/{k}?pw={ADMIN_PASSWORD}" style="background:#22c55e; color:white; padding:8px 16px; border-radius:8px; text-decoration:none; margin-right:5px;">DONE</a>' if 'Pending' in v['status'] else ''}
            {f'<form action="/reject/{k}" style="display:inline;margin-left:5px;"><input name="pw" type="hidden" value="{ADMIN_PASSWORD}"><input name="msg" placeholder="Reason" style="padding:8px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:white;"><button type="submit" style="background:#ef4444; color:white; border:none; padding:8px 16px; border-radius:8px; margin-left:5px;">REJECT</button></form>' if 'Pending' in v['status'] else ''}
        </div>'''
    return f"<html><body style='background:#0f172a;color:white;padding:20px;font-family:sans-serif;'><h2>Admin Control</h2>{order_rows or 'No orders'}</body></html>"

@app.route('/done/<oid>')
def done(oid):
    pw = request.args.get('pw')
    if pw == ADMIN_PASSWORD and oid in db: db[oid]['status'] = "Success ✅"
    return redirect(url_for('admin', pw=ADMIN_PASSWORD))

@app.route('/reject/<oid>', methods=['POST', 'GET'])
def reject(oid):
    pw = request.form.get('pw') or request.args.get('pw')
    msg = request.form.get('msg') or "Payment/Info Incorrect"
    if pw == ADMIN_PASSWORD and oid in db:
        db[oid]['status'] = "Rejected ❌"; db[oid]['note'] = msg
    return redirect(url_for('admin', pw=ADMIN_PASSWORD))

@app.route('/check', methods=['GET', 'POST'])
def check():
    res = ""
    if request.method == 'POST':
        oid = request.form.get('oid', '').strip().upper().replace("#", "")
        if oid in db:
            o = db[oid]
            color = "#fbbf24" if "Pending" in o['status'] else "#22c55e" if "Success" in o['status'] else "#ef4444"
            res = f"<div style='background:#1e293b;padding:20px;border-radius:15px;border:1px solid {color};margin-top:20px;'>Status: <b style='color:{color};'>{o['status']}</b><br><small>{o['note']}</small></div>"
        else: res = "<p style='color:#ef4444;margin-top:15px;'>ID မမှန်ပါဗျ။</p>"
    return render_template_string('<html><body style="background:#0f172a;color:white;text-align:center;padding:50px 20px;font-family:sans-serif;"><h3>Check Status</h3><form method="post"><input name="oid" placeholder="Order ID" style="padding:14px;border-radius:10px;width:100%;max-width:300px;"><br><button type="submit" style="padding:12px 30px;background:#fbbf24;border:none;border-radius:10px;margin-top:15px;">CHECK</button></form>{{res|safe}}<br><a href="/" style="color:#94a3b8;text-decoration:none;">← Back</a></body></html>', res=res)

@app.route('/')
def index():
    pkg_items = "".join([f'<div class="pkg-card" onclick="sel(this,\'{p["d"]}\',\'{p["p"]}\',\'{p["id"]}\')"><span>{p["d"]}</span><br><b style="color:#fbbf24">{p["p"]} Ks</b></div>' for p in packages])
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
    .nav-link { display:block; padding:12px; margin-top:10px; border-radius:12px; text-decoration:none; text-align:center; border:1px solid #334155; color:white; background:#334155; }
</style></head>
<body>
    <h2 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h2>
    <div class="grid">{{pkg_items | safe}}</div>
    <div class="form-box">
        <form action="/order" method="post" enctype="multipart/form-data">
            <input name="u" placeholder="User ID" required>
            <input name="z" placeholder="Zone ID" required>
            <input id="p_val" name="p" type="hidden"><input id="a_val" name="a" type="hidden"><input id="pid_val" name="pid" type="hidden">
            <select name="pay"><option>KBZPay</option><option>WaveMoney</option></select>
            <input type="file" name="photo" required accept="image/*">
            <button type="submit" class="buy-btn">PLACE ORDER NOW</button>
        </form>
        <a href="/check" class="nav-link">🔍 CHECK ORDER STATUS</a>
    </div>
    <script>function sel(el,d,p,id){var cards=document.getElementsByClassName('pkg-card');for(var i=0;i<cards.length;i++){cards[i].classList.remove('selected');}el.classList.add('selected');document.getElementById('p_val').value=d;document.getElementById('a_val').value=p;document.getElementById('pid_val').value=id;}</script>
</body></html>''', pkg_items=pkg_items)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
    
