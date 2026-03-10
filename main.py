import os
import pymongo
import json
from flask import Flask, render_template_string, request, redirect, url_for
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "1234"
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
ADMIN_ID = "7089720301"
CS_TELEGRAM = "Bby_kiwii7"

# --- PAYMENT INFO ---
PAY_NO = "09775394979"
PAY_NAME = "THANSIN KYAW"

# --- MONGODB SETUP ---
MONGO_URL = "mongodb+srv://contisarto_db_user:sta1YjKJxKmuvpxg@cluster0.m2mtomm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGO_URL)
db = client.gameshop_db
orders_col = db.orders

packages = [
    {"d": "Weekly Pass", "p": "5,800"}, {"d": "Twilight Pass", "p": "32,000"},
    {"d": "11", "p": "700"}, {"d": "22", "p": "1,400"}, {"d": "33", "p": "2,100"},
    {"d": "44", "p": "2,800"}, {"d": "56", "p": "3,500"}, {"d": "112", "p": "7,000"},
    {"d": "86", "p": "4,800"}, {"d": "172", "p": "9,600"}, {"d": "257", "p": "14,400"},
    {"d": "343", "p": "19,200"}, {"d": "429", "p": "24,000"}, {"d": "514", "p": "28,800"},
    {"d": "600", "p": "33,600"}, {"d": "706", "p": "38,400"}, {"d": "878", "p": "48,000"},
    {"d": "963", "p": "52,800"}, {"d": "1049", "p": "57,600"}, {"d": "1135", "p": "62,400"},
    {"d": "1221", "p": "67,200"}, {"d": "1412", "p": "76,800"}, {"d": "1667", "p": "91,200"},
    {"d": "1841", "p": "100,800"}, {"d": "2195", "p": "115,000"}, {"d": "3688", "p": "192,000"},
    {"d": "4390", "p": "230,000"}, {"d": "5532", "p": "288,000"}, {"d": "7376", "p": "384,000"},
    {"d": "9288", "p": "480,000"}
]

@app.route('/order', methods=['POST'])
def order():
    uid = request.form.get('u'); zone = request.form.get('z')
    pkg_name = request.form.get('p'); amt = request.form.get('a')
    pay = request.form.get('pay'); photo = request.files.get('photo')
    oid = os.urandom(2).hex().upper()
    
    orders_col.insert_one({"id": oid, "uid": uid, "zone": zone, "pkg": pkg_name, "amt": amt, "status": "Pending ⏳", "note": ""})
    
    msg = f"🔔 *NEW ORDER: #{oid}*\n🆔 *ID:* `{uid}` (`{zone}`)\n💎 *Item:* {pkg_name}\n💰 *Price:* {amt} Ks\n💵 *Pay:* {pay}"
    admin_url = f"https://kiwiigameshop.onrender.com/admin?pw={ADMIN_PASSWORD}"
    reply_markup = {"inline_keyboard": [[{"text": "📝 အော်ဒါစစ်ဆေးရန် (Admin Panel)", "url": admin_url}]]}
    
    if photo:
        photo.seek(0)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={'chat_id': ADMIN_ID, 'caption': msg, 'parse_mode': 'Markdown', 'reply_markup': json.dumps(reply_markup)}, 
                      files={'photo': photo})
    return render_template_string('<html><body style="background:#0f172a;color:white;text-align:center;padding:80px;font-family:sans-serif;"><h2>Order Success! ✅</h2><p>Order ID: #{{oid}}</p><a href="/" style="color:#fbbf24;">Back to Shop</a></body></html>', oid=oid)

@app.route('/')
def index():
    pkg_items = "".join([f'<div class="pkg-card" onclick="sel(this,\'{p["d"]}\',\'{p["p"]}\')"><span>{p["d"]} 💎</span><br><b style="color:#fbbf24">{p["p"]} Ks</b></div>' for p in packages])
    return render_template_string('''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; padding:15px; max-width:500px; margin:auto; }
    .scroll-box { display:grid; grid-template-columns: 1fr 1fr; gap:12px; height: 350px; overflow-y: auto; padding:15px; background:rgba(30, 41, 59, 0.5); border-radius:15px; margin-bottom:20px; border:1px solid #334155; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:18px; border-radius:12px; cursor:pointer; text-align:center; transition: all 0.4s; }
    .selected { border: 2px solid #fbbf24 !important; box-shadow: 0 0 20px rgba(251, 191, 36, 0.8); transform: scale(1.05); }
    input, select { width:100%; padding:14px; margin:8px 0; border-radius:12px; border:1px solid #334155; background:#0f172a; color:white; box-sizing:border-box; outline:none; }
    input:focus { border-color: #fbbf24; }
    
    /* Image 5 Style Payment Box */
    .pay-tabs { display: flex; gap: 10px; margin-bottom: 15px; }
    .pay-tab { flex: 1; padding: 12px; background: #1e293b; border-radius: 20px; text-align: center; cursor: pointer; border: 1px solid #334155; font-weight: bold; font-size: 14px; }
    .pay-tab.active { background: #fbbf24; color: #000; border-color: #fbbf24; }
    
    .pay-container { background:#1e293b; padding:25px; border-radius:20px; border:1px solid #334155; text-align:center; position: relative; }
    .pay-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; margin-bottom: 5px; }
    .pay-no { font-size: 32px; font-weight: bold; color: #fff; margin: 5px 0 10px 0; letter-spacing: 1px; }
    
    .copy-btn { position: absolute; right: 20px; top: 50%; transform: translateY(-50%); background: #334155; color: #fff; border: none; padding: 8px 15px; border-radius: 10px; cursor: pointer; font-size: 12px; font-weight: bold; text-transform: uppercase; }
    .copy-btn:active { background: #fbbf24; color: #000; }
    
    .pay-name { font-weight: bold; color: #fbbf24; font-size: 15px; margin: 10px 0; }
    .note-tag { background: #ef4444; color: white; padding: 6px 18px; border-radius: 20px; font-size: 13px; display: inline-block; font-weight: bold; margin-top: 5px; }
    
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; cursor:pointer; margin-top:20px; font-size: 18px; color:#000; }
</style></head>
<body>
    <h2 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h2>
    <div class="scroll-box">{{pkg_items | safe}}</div>
    
    <div style="background:#1e293b;padding:25px;border-radius:20px; border: 1px solid #334155; margin-bottom: 20px;">
        <div class="pay-tabs">
            <div id="tab-kbz" class="pay-tab active" onclick="setPay('KBZPay')">KBZ PAY</div>
            <div id="tab-wave" class="pay-tab" onclick="setPay('WaveMoney')">WAVE MONEY</div>
        </div>

        <div class="pay-container">
            <div class="pay-label">KBZ PAY NUMBER</div>
            <div id="pay-num-display" class="pay-no">{{pay_no}}</div>
            <button class="copy-btn" onclick="copyNum()">COPY</button>
            
            <div class="pay-name">NAME - {{name}}</div>
            <div class="note-tag">NOTE မှာ "PAYMENT" လို့ရေးပေးပါ</div>
        </div>
    </div>

    <form action="/order" method="post" enctype="multipart/form-data" style="background:#1e293b;padding:25px;border-radius:20px; border: 1px solid #334155;">
        <input name="u" placeholder="Game Player ID" required>
        <input name="z" placeholder="Zone ID" required>
        <input id="p_val" name="p" type="hidden" required><input id="a_val" name="a" type="hidden" required>
        <input id="pay_method_val" name="pay" type="hidden" value="KBZPay"> <p style="font-size:13px;color:#94a3b8;margin-top:20px; text-align:center;">ငွေလွှဲ Screenshot ထည့်ပေးပါ</p>
        <input type="file" name="photo" required accept="image/*">
        <button type="submit" class="buy-btn">CONFIRM ORDER</button>
    </form>
    
    <div style="text-align:center; margin-top:30px; color:#94a3b8; font-size:14px;">
        Website Support: <a href="https://t.me/{{cs}}" style="color:#fbbf24;text-decoration:none; font-weight:bold;">@{{cs}}</a>
    </div>

    <script>
    function sel(el,d,p){const cards=document.querySelectorAll('.pkg-card');cards.forEach(c=>c.classList.remove('selected'));el.classList.add('selected');document.getElementById('p_val').value=d;document.getElementById('a_val').value=p;}
    
    // Copy Function
    function copyNum() {
        const num = document.getElementById('pay-num-display').innerText;
        navigator.clipboard.writeText(num).then(() => {
            alert('Payment Number Copy လုပ်ပြီးပါပြီ: ' + num);
        });
    }

    // Payment Tab Switching (Image 5)
    function setPay(method) {
        document.getElementById('pay_method_val').value = method;
        const tabKbz = document.getElementById('tab-kbz');
        const tabWave = document.getElementById('tab-wave');
        if (method === 'KBZPay') {
            tabKbz.classList.add('active');
            tabWave.classList.remove('active');
        } else {
            tabWave.classList.add('active');
            tabKbz.classList.remove('active');
        }
    }
    </script>
</body></html>''', pkg_items=pkg_items, pay_no=PAY_NO, name=PAY_NAME, cs=CS_TELEGRAM)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
