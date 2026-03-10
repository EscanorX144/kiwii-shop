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

@app.route('/order', methods=['POST'])
def order():
    uid = request.form.get('u'); zone = request.form.get('z')
    pkg_name = request.form.get('p'); amt = request.form.get('a')
    pay = request.form.get('pay'); photo = request.files.get('photo')
    oid = os.urandom(2).hex().upper()
    
    orders_col.insert_one({"id": oid, "uid": uid, "zone": zone, "pkg": pkg_name, "amt": amt, "status": "Pending ⏳", "note": ""})
    
    msg = f"🔔 *NEW ORDER: #{oid}*\n🆔 *ID:* `{uid}` (`{zone}`)\n💎 *Item:* {pkg_name}\n💰 *Price:* {amt} Ks\n💵 *Pay:* {pay}"
    admin_url = f"https://kiwiigameshop.onrender.com/admin?pw={ADMIN_PASSWORD}"
    reply_markup = json.dumps({"inline_keyboard": [[{"text": "📝 Admin Panel", "url": admin_url}]]})
    
    if photo:
        photo.seek(0)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={'chat_id': ADMIN_ID, 'caption': msg, 'parse_mode': 'Markdown', 'reply_markup': reply_markup}, 
                      files={'photo': photo})
    return render_template_string('<html><body style="background:#0f172a;color:white;text-align:center;padding:80px;font-family:sans-serif;"><h2>Order Success! ✅</h2><p>Order ID: #{{oid}}</p><a href="/" style="color:#fbbf24;">Back to Shop</a></body></html>', oid=oid)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD: return "Unauthorized", 401
    
    if request.method == 'POST':
        oid = request.form.get('oid'); action = request.form.get('action'); reason = request.form.get('reason', '')
        if action == 'done':
            orders_col.update_one({"id": oid}, {"$set": {"status": "Diamond ထည့်သွင်းပြီးပါပြီ ✅", "note": "ကျေးဇူးတင်ပါတယ်!"}})
        elif action == 'reject':
            orders_col.update_one({"id": oid}, {"$set": {"status": "Order ငြင်းပယ်ခံရသည် ❌", "note": reason}})
            
    orders = orders_col.find().sort("_id", -1)
    order_html = "".join([f'<div style="border:1px solid #334155;padding:15px;background:#1e293b;border-radius:12px;margin-bottom:15px;"><b>#{v["id"]}</b> | {v["uid"]} | {v["status"]}<form method="post" style="margin-top:10px;"><input type="hidden" name="oid" value="{v["id"]}"><input name="reason" placeholder="Reject Reason" style="margin-right:5px;padding:5px;border-radius:5px;"><button name="action" value="done" style="background:green;color:white;border:none;padding:5px 10px;border-radius:5px;cursor:pointer;">DONE</button> <button name="action" value="reject" style="background:red;color:white;border:none;padding:5px 10px;border-radius:5px;cursor:pointer;">REJECT</button></form></div>' for v in orders])
    return f"<html><body style='background:#0f172a;color:white;padding:20px;font-family:sans-serif;'><h2>Admin Panel</h2>{order_html}</body></html>"

@app.route('/check', methods=['GET', 'POST'])
def check():
    res = ""
    if request.method == 'POST':
        o = orders_col.find_one({"id": request.form.get('oid', '').upper().replace("#","")})
        if o: res = f"<div style='background:#1e293b;padding:20px;border-radius:15px;margin-top:20px;border:1px solid #334155;'>Order ID: <b>#{o['id']}</b><br>Status: <b style='color:#fbbf24;'>{o['status']}</b><br>Note: {o['note']}</div>"
        else: res = "<p style='color:#ef4444;margin-top:20px;'>Order ID မတွေ့ပါ၊ ပြန်စစ်ပေးပါဗျ။</p>"
    return render_template_string('''<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body style="background:#0f172a;color:white;text-align:center;padding:50px; font-family:sans-serif;"><h3>🔍 Check Order Status</h3><form method="post"><input name="oid" placeholder="Order ID (ဥပမာ- A1B2)" style="padding:12px;border-radius:10px;border:1px solid #334155;background:#1e293b;color:white;width:80%;max-width:300px;"><br><button type="submit" style="margin-top:15px;padding:10px 30px;background:#fbbf24;border:none;border-radius:10px;font-weight:bold;cursor:pointer;">CHECK</button></form>{{res|safe}}<br><a href="/" style="color:#94a3b8;text-decoration:none;display:block;margin-top:30px;">Back to Shop</a></body></html>''', res=res)

@app.route('/')
def index():
    # Category အလိုက် စျေးနှုန်းစာရင်းများ (ကော်မာ အကုန်ဖြုတ်ထားသည်)
    cats = {
        "Normal Dia": [
            {"d": "11", "p": "700"}, {"d": "22", "p": "1400"}, {"d": "33", "p": "2100"}, {"d": "44", "p": "2800"},
            {"d": "56", "p": "3500"}, {"d": "112", "p": "7000"}, {"d": "86", "p": "4750"}, {"d": "172", "p": "9450"},
            {"d": "257", "p": "13800"}, {"d": "279", "p": "15200"}, {"d": "343", "p": "18600"}, {"d": "429", "p": "23350"},
            {"d": "514", "p": "27650"}, {"d": "600", "p": "32650"}, {"d": "706", "p": "37450"}, {"d": "792", "p": "42200"},
            {"d": "878", "p": "46850"}, {"d": "963", "p": "51200"}, {"d": "1049", "p": "56000"}, {"d": "1135", "p": "60850"},
            {"d": "1412", "p": "74900"}, {"d": "2195", "p": "114200"}, {"d": "3688", "p": "190500"}, {"d": "5532", "p": "287000"},
            {"d": "7376", "p": "381000"}, {"d": "9288", "p": "475200"}
        ],
        "Weekly Pass": [
            {"d": "Weekly Pass", "p": "5900"}, {"d": "Weekly Pass 2X", "p": "11800"}, {"d": "Weekly Pass 3X", "p": "17700"},
            {"d": "Weekly Pass 4X", "p": "23600"}, {"d": "Weekly Pass 5X", "p": "29500"}, {"d": "Weekly Pass 6X", "p": "35400"},
            {"d": "Weekly Pass 7X", "p": "41300"}, {"d": "Weekly Pass 8X", "p": "47200"}, {"d": "Weekly Pass 9X", "p": "53100"},
            {"d": "Weekly Pass 10X", "p": "59000"}
        ],
        "Dia 2X": [
            {"d": "50+", "p": "3050"}, {"d": "150+", "p": "9100"}, {"d": "250+", "p": "14650"}, {"d": "500+", "p": "29950"}
        ],
        "Bundle Pack": [
            {"d": "Weekly elite bundle", "p": "3050"}, {"d": "Monthly epic bundle", "p": "15350"}, {"d": "Twilight pass", "p": "31500"}
        ]
    }
    
    import json
    return render_template_string('''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; padding:15px; max-width:500px; margin:auto; }
    .cat-tabs { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 10px; margin-bottom: 15px; scrollbar-width: none; }
    .cat-tabs::-webkit-scrollbar { display: none; }
    .cat-tab { padding: 10px 18px; background: #1e293b; border-radius: 12px; cursor: pointer; border: 1px solid #334155; font-size: 13px; white-space: nowrap; color: #94a3b8; }
    .cat-tab.active { background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3); }
    .scroll-box { display:grid; grid-template-columns: 1fr 1fr; gap:12px; max-height: 400px; overflow-y: auto; padding:12px; background:rgba(30, 41, 59, 0.4); border-radius:18px; border:1px solid #334155; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; cursor:pointer; text-align:center; transition: 0.3s; }
    .pkg-card.selected { border: 2px solid #fbbf24; background: #1e3a8a; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:12px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; }
    .pay-box { background:#1e293b; padding:20px; border-radius:18px; border:1px solid #334155; text-align:center; margin: 20px 0; }
    .copy-btn { background:#334155; color:#fff; border:none; padding:5px 12px; border-radius:8px; cursor:pointer; font-size:11px; margin-left:8px; }
    .note-tag { border: 1px solid rgba(239, 68, 68, 0.6); color: #f87171; padding: 7px 18px; border-radius: 20px; font-size: 11px; display: inline-block; margin-top: 12px; box-shadow: 0 0 10px rgba(239, 68, 68, 0.2); font-weight: bold; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; cursor:pointer; font-size: 18px; color:#000; }
</style></head>
<body>
    <h2 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h2>
    <div class="cat-tabs" id="tabs"></div>
    <div class="scroll-box" id="pkg-list"></div>
    <div class="pay-box">
        <div style="display: flex; gap: 8px; justify-content: center; margin-bottom: 15px;">
            <button id="kbz" class="cat-tab active" onclick="setPay('KBZPay')">KBZ PAY</button>
            <button id="wave" class="cat-tab" onclick="setPay('WaveMoney')">WAVE MONEY</button>
        </div>
        <span id="p-num" style="font-size: 26px; font-weight: bold;">{{pay_no}}</span>
        <button class="copy-btn" onclick="copyNum()">COPY</button>
        <div style="color:#fbbf24; font-size:14px; margin: 10px 0;">NAME - {{name}}</div>
        <div class="note-tag">NOTE မှာ "PAYMENT" လို့ရေးပေးပါ</div>
    </div>
    <form action="/order" method="post" enctype="multipart/form-data" onsubmit="return validateForm()">
        <input type="number" name="u" id="u_id" placeholder="Game Player ID" required>
        <input type="number" name="z" id="z_id" placeholder="Zone ID" required>
        <input id="p_val" name="p" type="hidden"><input id="a_val" name="a" type="hidden">
        <input id="pay_method" name="pay" type="hidden" value="KBZPay">
        <p style="font-size:13px;color:#94a3b8;text-align:center;">ငွေလွှဲ Screenshot တင်ပေးပါ</p>
        <input type="file" name="photo" id="photo_id" required accept="image/*">
        <button type="submit" class="buy-btn">CONFIRM ORDER</button>
    </form>
    <div style="display: flex; gap: 10px; margin-top: 20px; margin-bottom: 30px;">
        <a href="/check" style="flex:1; background:#334155; color:white; padding:12px; border-radius:10px; text-decoration:none; text-align:center; font-size: 14px;">🔍 Check</a>
        <a href="https://t.me/{{cs}}" style="flex:1; background:#fbbf24; color:black; padding:12px; border-radius:10px; text-decoration:none; text-align:center; font-weight:bold; font-size: 14px;">💬 Admin</a>
    </div>
    <script>
    const data = ''' + json.dumps(cats) + ''';
    const tabsBox = document.getElementById('tabs');
    const pkgBox = document.getElementById('pkg-list');
    function renderPkgs(catName, target) {
        if(target) {
            document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
            target.classList.add('active');
        }
        pkgBox.innerHTML = data[catName].map(p => `
            <div class="pkg-card" onclick="sel(this,'${p.d}','${p.p}')">
                <span>${p.d} ${catName.includes('Dia') ? '💎' : ''}</span><br>
                <b style="color:#fbbf24">${Number(p.p).toLocaleString()} Ks</b>
            </div>`).join('');
    }
    Object.keys(data).forEach((cat, i) => {
        const btn = document.createElement('div');
        btn.className = 'cat-tab' + (i === 0 ? ' active' : '');
        btn.innerText = cat; btn.onclick = (e) => renderPkgs(cat, e.target);
        tabsBox.appendChild(btn);
        if(i === 0) renderPkgs(cat);
    });
    function sel(el, d, p) {
        document.querySelectorAll('.pkg-card').forEach(c => c.classList.remove('selected'));
        el.classList.add('selected');
        document.getElementById('p_val').value = d; document.getElementById('a_val').value = p;
    }
    function setPay(m) {
        document.getElementById('pay_method').value = m;
        document.getElementById('kbz').classList.toggle('active', m === 'KBZPay');
        document.getElementById('wave').classList.toggle('active', m === 'WaveMoney');
    }
    function copyNum() {
        const num = document.getElementById('p-num').innerText;
        navigator.clipboard.writeText(num).then(() => alert('Copy ကူးလိုက်ပါပြီ- ' + num));
    }
    function validateForm() {
        if(!document.getElementById('p_val').value) { alert("အမျိုးအစား တစ်ခုရွေးချယ်ပေးပါ"); return false; }
        return true;
    }
    </script>
</body></html>''', pay_no=PAY_NO, name=PAY_NAME, cs=CS_TELEGRAM)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
