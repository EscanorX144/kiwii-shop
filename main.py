import os
import pymongo
from flask import Flask, render_template_string, request, redirect, url_for
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "1234"
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
ADMIN_ID = "7089720301"
CS_TELEGRAM = "@Bby_kiwii7"

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
    if photo:
        photo.seek(0)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data={'chat_id': ADMIN_ID, 'caption': msg, 'parse_mode': 'Markdown'}, files={'photo': photo})
    return render_template_string('<html><body style="background:#0f172a;color:white;text-align:center;padding:80px;font-family:sans-serif;"><h2>Order Success! ✅</h2><p>Order ID: #{{oid}}</p><a href="/" style="color:#fbbf24;">Back to Shop</a></body></html>', oid=oid)

@app.route('/')
def index():
    pkg_items = "".join([f'<div class="pkg-card" onclick="sel(this,\'{p["d"]}\',\'{p["p"]}\')"><span>{p["d"]} 💎</span><br><b style="color:#fbbf24">{p["p"]} Ks</b></div>' for p in packages])
    return render_template_string('''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; padding:15px; max-width:500px; margin:auto; }
    .scroll-box { display:grid; grid-template-columns: 1fr 1fr; gap:10px; height: 350px; overflow-y: auto; padding:10px; background:#111827; border-radius:15px; margin-bottom:20px; border:1px solid #334155; }
    
    .pkg-card { background:#1e293b; border:2px solid #334155; padding:15px; border-radius:12px; cursor:pointer; text-align:center; transition: all 0.3s ease; }
    
    /* နှိပ်လိုက်ရင် ရွှေရောင်ဖြာထွက်မည့် ပတန် effect */
    .pkg-card.selected { 
        border-color: #fbbf24 !important; 
        background: #334155; 
        box-shadow: 0 0 15px #fbbf24, inset 0 0 10px rgba(251, 191, 36, 0.4); 
        transform: scale(1.02);
    }

    input, select { width:100%; padding:14px; margin:8px 0; border-radius:12px; border:1px solid #334155; background:#0f172a; color:white; box-sizing:border-box; }
    .pay-container { background:#1e293b; padding:20px; border-radius:20px; border:1px solid #334155; margin-top:20px; text-align:center; }
    .pay-no { font-size: 24px; font-weight: bold; color: #fbbf24; margin: 10px 0; letter-spacing: 1px; }
    .note-tag { background: #ef4444; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; display: inline-block; margin-top: 5px; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; cursor:pointer; margin-top:10px; font-size: 16px; }
</style></head>
<body>
    <h2 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h2>
    <div class="scroll-box">{{pkg_items | safe}}</div>
    <form action="/order" method="post" enctype="multipart/form-data" style="background:#1e293b;padding:20px;border-radius:20px;">
        <input name="u" placeholder="User ID" required>
        <input name="z" placeholder="Zone ID" required>
        <input id="p_val" name="p" type="hidden"><input id="a_val" name="a" type="hidden">
        
        <div class="pay-container">
            <p style="margin:0; font-size:12px; color:#94a3b8; text-transform: uppercase;">KBZPay / Wave Pay Number</p>
            <div class="pay-no">{{pay_no}}</div>
            <p style="margin:0; font-size:14px; font-weight: bold;">NAME - {{name}}</p>
            <div class="note-tag">NOTE မှာ "PAYMENT" လို့ရေးပေးပါ</div>
            <select name="pay" style="margin-top:15px;"><option>KBZPay</option><option>WaveMoney</option></select>
        </div>

        <p style="font-size:12px;color:#94a3b8;margin-top:20px;">ငွေလွှဲ Screenshot ထည့်ပေးပါ</p>
        <input type="file" name="photo" required accept="image/*">
        <button type="submit" class="buy-btn">CONFIRM ORDER</button>
    </form>
    <div style="text-align:center; margin-top:30px; color:#94a3b8; font-size:13px;">Support: <a href="https://t.me/Bby_kiwii7" style="color:#fbbf24;text-decoration:none;">{{cs}}</a></div>
    
    <script>
    function sel(el, d, p){
        var cards = document.getElementsByClassName('pkg-card');
        for(var i=0; i<cards.length; i++){
            cards[i].classList.remove('selected');
        }
        el.classList.add('selected');
        document.getElementById('p_val').value = d;
        document.getElementById('a_val').value = p;
    }
    </script>
</body></html>''', pkg_items=pkg_items, pay_no=PAY_NO, name=PAY_NAME, cs=CS_TELEGRAM)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
