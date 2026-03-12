import os, requests, json
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- ⚙️ CONFIGURATION ---
MONGO_URI = "mongodb+srv://EscanorX:Conti144@cluster0.m2mtomm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['kiwii_game_shop']
orders_col = db['orders']

BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
CHAT_ID = "7089720301"
CS_LINK = "https://t.me/Bby_kiwii7"

PAY_DATA = {
    "KPay": {"Number": "09775394979", "Name": "Thansin Kyaw", "img": "/static/kpay.jpg"},
    "Wave": {"Number": "09775394979", "Name": "Thansin Kyaw", "img": "/static/wave.jpg"},
    "AYAPay": {"Number": "09775394979", "Name": "Thansin Kyaw", "img": "/static/ayapay.jpg"},
    "Note": "Note - Payment သာရေးပါ"
}

# ဂိမ်းစာရင်းအားလုံး
GAMES_DATA = [
    {"id": 1, "name": "Normal Server (🇲🇲)", "img": "https://flagcdn.com/w160/mm.png", "cat_order": ["Normal Dia", "Weekly Pass"], "cats": {"Normal Dia": [{"d": "11 💎", "p": "700"}, {"d": "9288 💎", "p": "475200"}], "Weekly Pass": [{"d": "Weekly Pass 1X", "p": "5900"}]}},
    {"id": 2, "name": "Malaysia (🇲🇾)", "img": "https://flagcdn.com/w160/my.png", "cat_order": ["Malaysia Dia"], "cats": {"Malaysia Dia": [{"d": "14 💎", "p": "1100"}]}},
    {"id": 3, "name": "Singapore (🇸🇬)", "img": "https://flagcdn.com/w160/sg.png", "cat_order": ["Singapore Dia"], "cats": {"Singapore Dia": [{"d": "14 💎", "p": "1100"}]}},
    {"id": 4, "name": "Philippines (🇵🇭)", "img": "https://flagcdn.com/w160/ph.png", "cat_order": ["Philippines Dia"], "cats": {"Philippines Dia": [{"d": "11 💎", "p": "750"}]}},
    {"id": 5, "name": "Indonesia (🇮🇩)", "img": "https://flagcdn.com/w160/id.png", "cat_order": ["Indonesia Dia"], "cats": {"Indonesia Dia": [{"d": "5 💎", "p": "450"}]}},
    {"id": 6, "name": "Russia (🇷🇺)", "img": "https://flagcdn.com/w160/ru.png", "cat_order": ["Russia Dia"], "cats": {"Russia Dia": [{"d": "35 💎", "p": "2750"}]}}
]

HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; margin:0; padding-bottom:80px; }
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; padding: 15px; }
    .game-card { background-image: linear-gradient(rgba(30, 41, 59, 0.8), rgba(30, 41, 59, 0.8)), url('/static/hero.webp'); background-size: cover; border-radius:15px; padding:25px 10px; text-align:center; border:1px solid rgba(251, 191, 36, 0.3); }
    .game-card img { width:55px; border-radius:8px; margin-bottom:10px; }
    .cat-tab { padding:10px 18px; background:#1e293b; border-radius:10px; font-size:12px; cursor:pointer; white-space:nowrap; border:1px solid #334155; }
    .cat-tab.active { background:#fbbf24; color:black; font-weight:bold; }
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:10px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; color:black; margin-top:10px; }
    .nav-bar { position:fixed; bottom:0; left:0; right:0; background:#1e293b; display:flex; padding:12px; border-top:1px solid #334155; z-index:100; }
    .hist-item { background:#1e293b; padding:15px; margin-bottom:10px; border-left:4px solid #fbbf24; border-radius:8px; }
</style>
</head><body>
<div id="h-sec">
    <h1 style="text-align:center;color:#fbbf24; margin-top: 20px;">KIWII GAME STORE</h1>
    <div class="game-grid" id="g-list"></div>
</div>

<div id="o-sec" style="display:none; padding: 15px;">
    <button onclick="goH()" style="background:none;color:white;border:1px solid #334155;padding:8px;border-radius:8px; margin-bottom:10px;">← Back</button>
    <h2 id="g-title" style="color:#fbbf24;"></h2>
    <div style="display:flex;gap:8px;overflow-x:auto;padding-bottom:10px;" id="tabs"></div>
    <div class="pkg-grid" id="p-list"></div>
    
    <div id="pay-icons" style="display:flex;justify-content:center;margin:15px 0;"></div>
    <div class="note-box" style="background:#1e293b; border:2px solid #fbbf24; padding:15px; border-radius:12px; text-align:center;">
        <b id="p-num" style="color:#fbbf24;font-size:22px;"></b> <i class="fa-regular fa-copy" onclick="copyNum()"></i><br>
        <span id="p-name"></span><br>
        <small style="color:#fbbf24; display:block; margin-top:5px;">{{ pay.Note }}</small>
    </div>

    <form id="orderForm" onsubmit="event.preventDefault(); submitOrder();" style="margin-top:20px;">
        <input type="text" id="tg_u" placeholder="Your Telegram Username (@...)" required>
        <input type="tel" id="uid" placeholder="Game ID" required>
        <input type="tel" id="zid" placeholder="Zone ID" required>
        <div style="font-size:12px; color:#94a3b8; margin:10px 0 5px 0;">Upload Screenshot:</div>
        <input type="file" id="photo" required accept="image/*">
        <button type="submit" class="buy-btn">PLACE ORDER</button>
    </form>
</div>

<div id="hist-sec" style="display:none; padding:15px;">
    <h3 style="color:#fbbf24;">Order History</h3>
    <div id="hist-list"></div>
</div>

<div class="nav-bar">
    <div onclick="goH()" style="flex:1; text-align:center;"><i class="fas fa-home"></i><br>Home</div>
    <div onclick="showH()" style="flex:1; text-align:center;"><i class="fas fa-history"></i><br>History</div>
    <a href="{{cs}}" style="flex:1; text-align:center; color:white; text-decoration:none;"><i class="fas fa-headset"></i><br>CS</a>
</div>

<script>
let sel_srv='', sel_pkg='', sel_prc='';
const games = {{ games | tojson }}; const pay = {{ pay | tojson }};

const tg = window.Telegram.WebApp;
const user = tg.initDataUnsafe.user;
// Auto Username ကို Input Box မှာ ကြိုဖြည့်ပေးထားမယ်
if(user) document.getElementById('tg_u').value = user.username ? '@' + user.username : user.first_name;

function init() { document.getElementById('g-list').innerHTML = games.map(g => `<div class="game-card" onclick="selG(${g.id})"><img src="${g.img}"><br><b>${g.name}</b></div>`).join(''); }

function selG(id) {
    const g = games.find(i => i.id === id); sel_srv = g.name;
    document.getElementById('h-sec').style.display='none'; document.getElementById('hist-sec').style.display='none'; document.getElementById('o-sec').style.display='block';
    document.getElementById('g-title').innerText = g.name;
    document.getElementById('tabs').innerHTML = g.cat_order.map((c, i) => `<div class="cat-tab ${i===0?'active':''}" onclick="renderP(${id}, '${c}', this)">${c}</div>`).join('');
    document.getElementById('pay-icons').innerHTML = Object.keys(pay).filter(k=>k!='Note').map(k=>`<img src="${pay[k].img}" style="width:45px; margin:5px; border-radius:5px;" onclick="setPay('${k}')">`).join('');
    renderP(id, g.cat_order[0]); setPay('KPay');
}

function setPay(k) { document.getElementById('p-num').innerText = pay[k].Number; document.getElementById('p-name').innerText = pay[k].Name; }

function renderP(id, cat, el) {
    if(el){document.querySelectorAll('.cat-tab').forEach(t=>t.classList.remove('active')); el.classList.add('active');}
    const pkgs = games.find(i=>i.id===id).cats[cat];
    document.getElementById('p-list').innerHTML = pkgs.map(p=>`<div class="pkg-card" onclick="selP(this, '${p.d}', '${p.p}')"><span>${p.d}</span><br><b>${p.p} Ks</b></div>`).join('');
}

function selP(el, d, p) { document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected')); el.classList.add('selected'); sel_pkg=d; sel_prc=p; }

function showH() {
    const u = document.getElementById('tg_u').value || "Guest";
    document.getElementById('h-sec').style.display='none'; document.getElementById('o-sec').style.display='none'; document.getElementById('hist-sec').style.display='block';
    fetch('/api/history?user=' + encodeURIComponent(u)).then(r=>r.json()).then(data=>{
        document.getElementById('hist-list').innerHTML = data.map(o=>`<div class="hist-item"><small>${o.date}</small><br><b>${o.pkg}</b> - ${o.price} Ks<br><small>Status: ${o.status}</small></div>`).join('') || "No history found for this user.";
    });
}

function submitOrder() {
    if(!sel_pkg) return alert("Select Package!");
    const formData = new FormData();
    formData.append('username', document.getElementById('tg_u').value);
    formData.append('server', sel_srv); formData.append('u', document.getElementById('uid').value);
    formData.append('z', document.getElementById('zid').value); formData.append('p', sel_pkg);
    formData.append('a', sel_prc); formData.append('photo', document.getElementById('photo').files[0]);
    fetch('/order', { method: 'POST', body: formData }).then(r => r.text()).then(res => { alert(res); location.reload(); });
}

function goH() { document.getElementById('o-sec').style.display='none'; document.getElementById('hist-sec').style.display='none'; document.getElementById('h-sec').style.display='block'; }
function copyNum() { navigator.clipboard.writeText(document.getElementById('p-num').innerText).then(()=>alert("Copied!")); }
init();
</script></body></html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_CODE, games=GAMES_DATA, pay=PAY_DATA, cs=CS_LINK)

@app.route('/order', methods=['POST'])
def order():
    try:
        user_name = request.form.get('username')
        server, uid, zone, pkg, amt = request.form.get('server'), request.form.get('u'), request.form.get('z'), request.form.get('p'), request.form.get('a')
        photo = request.files.get('photo')
        res = orders_col.insert_one({
            "customer": user_name, "uid": uid, "zone": zone, "pkg": pkg, "price": amt, "status": "Pending",
            "date": datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%Y-%m-%d %H:%M")
        })
        oid = str(res.inserted_id)
        msg = (f"🔔 *New Order!*\n👤 Buyer: `{user_name}`\n📍 Server: {server}\n🆔 ID: `{uid}` ({zone})\n💎 Pkg: {pkg}\n💰 Amt: {amt} Ks\n\n"
               f"✅ [DONE]({request.host_url}admin/update/{oid}/Completed)\n❌ [REJECT]({request.host_url}admin/update/{oid}/Rejected)")
        if photo:
            photo.seek(0)
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}, files={'photo': (photo.filename, photo.read(), photo.content_type)})
        return "Order Success! ✅"
    except Exception as e: return str(e)

@app.route('/api/history')
def get_history():
    u = request.args.get('user')
    hist = list(orders_col.find({"customer": u}).sort("_id", -1).limit(10))
    for h in hist: h["_id"] = str(h["_id"])
    return jsonify(hist)

@app.route('/admin/update/<oid>/<status>')
def update_status(oid, status):
    orders_col.update_one({"_id": ObjectId(oid)}, {"$set": {"status": status}})
    return f"Order {status} Success!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    
