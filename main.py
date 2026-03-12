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

# --- 💎 FULL DIAMOND LIST ---
GAMES_DATA = [
    {
        "id": 1, "name": "Normal Server (🇲🇲)", "img": "https://flagcdn.com/w160/mm.png", 
        "cat_order": ["Normal Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], 
        "cats": {
            "Normal Dia": [
                {"d": "11 💎", "p": "700"}, {"d": "22 💎", "p": "1400"}, {"d": "33 💎", "p": "2100"}, {"d": "44 💎", "p": "2800"}, {"d": "56 💎", "p": "3500"},
                {"d": "86 💎", "p": "4750"}, {"d": "112 💎", "p": "7000"}, {"d": "172 💎", "p": "9450"}, {"d": "257 💎", "p": "13800"}, {"d": "279 💎", "p": "15200"},
                {"d": "343 💎", "p": "18600"}, {"d": "429 💎", "p": "23350"}, {"d": "514 💎", "p": "27650"}, {"d": "600 💎", "p": "32650"}, {"d": "706 💎", "p": "37450"},
                {"d": "792 💎", "p": "42200"}, {"d": "878 💎", "p": "46850"}, {"d": "963 💎", "p": "51200"}, {"d": "1049 💎", "p": "56000"}, {"d": "1135 💎", "p": "60850"},
                {"d": "1412 💎", "p": "74900"}, {"d": "2195 💎", "p": "114200"}, {"d": "3688 💎", "p": "190500"}, {"d": "5532 💎", "p": "287000"}, {"d": "7376 💎", "p": "381000"}, {"d": "9288 💎", "p": "475200"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(5900 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "3050"}, {"d": "150+150 💎", "p": "9100"}, {"d": "250+250 💎", "p": "14650"}, {"d": "500+500 💎", "p": "29950"}],
            "Bundle Pack": [{"d": "Weekly Elite", "p": "3050"}, {"d": "Monthly Bundle", "p": "15350"}, {"d": "Twilight Pass", "p": "31500"}]
        }
    },
    {
        "id": 2, "name": "Malaysia (🇲🇾)", "img": "https://flagcdn.com/w160/my.png", 
        "cat_order": ["Malaysia Dia", "Weekly Pass", "2X Dia"], 
        "cats": {
            "Malaysia Dia": [{"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "70 💎", "p": "5100"}, {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"}, {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"}, {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8700 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+ 💎", "p": "4250"}, {"d": "150+ 💎", "p": "12200"}]
        }
    },
    {"id": 3, "name": "Singapore (🇸🇬)", "img": "https://flagcdn.com/w160/sg.png", "cat_order": ["Singapore Dia"], "cats": {"Singapore Dia": [{"d": "14 💎", "p": "1100"}, {"d": "70 💎", "p": "5100"}]}},
    {"id": 4, "name": "Philippines (🇵🇭)", "img": "https://flagcdn.com/w160/ph.png", "cat_order": ["Philippines Dia"], "cats": {"Philippines Dia": [{"d": "11 💎", "p": "750"}, {"d": "56 💎", "p": "3500"}]}},
    {"id": 5, "name": "Indonesia (🇮🇩)", "img": "https://flagcdn.com/w160/id.png", "cat_order": ["Indonesia Dia"], "cats": {"Indonesia Dia": [{"d": "5 💎", "p": "450"}, {"d": "12 💎", "p": "950"}]}},
    {"id": 6, "name": "Russia (🇷🇺)", "img": "https://flagcdn.com/w160/ru.png", "cat_order": ["Russia Dia"], "cats": {"Russia Dia": [{"d": "35 💎", "p": "2750"}, {"d": "55 💎", "p": "4450"}]}}
]

HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; margin:0; padding-bottom:80px; }
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; padding: 15px; }
    .game-card { background-image: linear-gradient(rgba(30, 41, 59, 0.8), rgba(30, 41, 59, 0.8)), url('/static/hero.webp'); background-size: cover; border-radius:15px; padding:25px 10px; text-align:center; border:1px solid rgba(251, 191, 36, 0.3); cursor:pointer; }
    .cat-tab { padding:10px 18px; background:#1e293b; border-radius:10px; font-size:12px; cursor:pointer; border:1px solid #334155; }
    .cat-tab.active { background:#fbbf24; color:black; font-weight:bold; }
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:15px 0; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; cursor:pointer; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:10px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; color:black; cursor:pointer; }
    .nav-bar { position:fixed; bottom:0; left:0; right:0; background:#1e293b; display:flex; padding:12px; border-top:1px solid #334155; }
</style>
</head><body>
<div id="h-sec">
    <h1 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h1>
    <div class="game-grid" id="g-list"></div>
</div>

<div id="o-sec" style="display:none; padding:15px;">
    <button onclick="goH()" style="background:none;color:white;border:1px solid #334155;padding:8px;border-radius:8px; margin-bottom:10px;">← Back</button>
    <h2 id="g-title" style="color:#fbbf24;"></h2>
    <div style="display:flex;gap:8px;overflow-x:auto;" id="tabs"></div>
    <div class="pkg-grid" id="p-list"></div>
    
    <div class="note-box" style="background:#1e293b; border:2px solid #fbbf24; padding:15px; border-radius:12px; text-align:center;">
        <b id="p-num" style="color:#fbbf24;font-size:22px;"></b> <i class="fa-regular fa-copy" onclick="copyNum()"></i><br>
        <small style="color:#fbbf24;">{{ pay.Note }}</small>
    </div>

    <form id="orderForm" onsubmit="submitOrder(event)">
        <input type="text" id="tg_u" placeholder="Telegram Username" required>
        <input type="tel" id="uid" placeholder="Game ID" required>
        <input type="tel" id="zid" placeholder="Zone ID" required>
        <div style="font-size:12px; color:#94a3b8; margin:8px 0;">Upload Payment Receipt:</div>
        <input type="file" id="photo" required accept="image/*">
        <button type="submit" id="submitBtn" class="buy-btn">PLACE ORDER</button>
    </form>
</div>

<div id="hist-sec" style="display:none; padding:15px;">
    <h3 style="color:#fbbf24;">History</h3>
    <div id="hist-list"></div>
</div>

<div class="nav-bar">
    <div onclick="goH()" style="flex:1; text-align:center; cursor:pointer;"><i class="fas fa-home"></i><br>Home</div>
    <div onclick="showH()" style="flex:1; text-align:center; cursor:pointer;"><i class="fas fa-history"></i><br>History</div>
</div>

<script>
let sel_srv='', sel_pkg='', sel_prc='';
const games = {{ games | tojson }}; const pay = {{ pay | tojson }};
const tg = window.Telegram.WebApp;

function init() { document.getElementById('g-list').innerHTML = games.map(g => `<div class="game-card" onclick="selG(${g.id})"><img src="${g.img}" width="50"><br><b>${g.name}</b></div>`).join(''); }

function selG(id) {
    const g = games.find(i => i.id === id); sel_srv = g.name;
    document.getElementById('h-sec').style.display='none'; document.getElementById('o-sec').style.display='block';
    document.getElementById('g-title').innerText = g.name;
    document.getElementById('tabs').innerHTML = g.cat_order.map((c, i) => `<div class="cat-tab ${i===0?'active':''}" onclick="renderP(${id}, '${c}', this)">${c}</div>`).join('');
    renderP(id, g.cat_order[0]); document.getElementById('p-num').innerText = pay.KPay.Number;
}

function renderP(id, cat, el) {
    if(el){document.querySelectorAll('.cat-tab').forEach(t=>t.classList.remove('active')); el.classList.add('active');}
    const pkgs = games.find(i=>i.id===id).cats[cat];
    document.getElementById('p-list').innerHTML = pkgs.map(p=>`<div class="pkg-card" onclick="selP(this, '${p.d}', '${p.p}')"><span>${p.d}</span><br><b>${p.p} Ks</b></div>`).join('');
    sel_pkg = '';
}

function selP(el, d, p) { document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected')); el.classList.add('selected'); sel_pkg=d; sel_prc=p; }

async function submitOrder(e) {
    e.preventDefault();
    if(!sel_pkg) return alert("Please select a Diamond Package!");
    const btn = document.getElementById('submitBtn');
    btn.innerText = "Processing..."; btn.disabled = true;

    const formData = new FormData();
    formData.append('username', document.getElementById('tg_u').value);
    formData.append('server', sel_srv); 
    formData.append('u', document.getElementById('uid').value);
    formData.append('z', document.getElementById('zid').value); 
    formData.append('p', sel_pkg);
    formData.append('a', sel_prc); 
    formData.append('photo', document.getElementById('photo').files[0]);

    try {
        const response = await fetch('/order', { method: 'POST', body: formData });
        const res = await response.text();
        if(res === "Success") {
            alert("Order Success! ✅"); location.reload();
        } else {
            alert(res); btn.disabled = false; btn.innerText = "PLACE ORDER";
        }
    } catch (err) { alert("System Error!"); btn.disabled = false; }
}

function goH() { document.getElementById('o-sec').style.display='none'; document.getElementById('hist-sec').style.display='none'; document.getElementById('h-sec').style.display='block'; }
function showH() {
    document.getElementById('h-sec').style.display='none'; document.getElementById('o-sec').style.display='none'; document.getElementById('hist-sec').style.display='block';
    const u = document.getElementById('tg_u').value;
    if(!u) { document.getElementById('hist-list').innerHTML = "Enter Username first."; return; }
    fetch('/api/history?user=' + encodeURIComponent(u)).then(r=>r.json()).then(data=>{
        document.getElementById('hist-list').innerHTML = data.map(o=>`<div style="background:#1e293b;padding:10px;margin:5px;border-radius:8px;">${o.pkg} - ${o.status}</div>`).join('') || "No History";
    });
}
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

        if not all([user_name, uid, zone, pkg, amt, photo]):
            return "Error: Information Missing!"

        res = orders_col.insert_one({
            "customer": user_name, "uid": uid, "zone": zone, "pkg": pkg, "price": amt, "status": "Pending",
            "date": datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%Y-%m-%d %H:%M")
        })
        oid = str(res.inserted_id)

        msg = (f"🔔 *New Order!*\n"
               f"👤 Buyer: `{user_name}`\n"
               f"📍 Server: {server}\n"
               f"🆔 ID: `{uid}` ({zone})\n"
               f"💎 Pkg: {pkg}\n"
               f"💰 Amt: {amt} Ks\n\n"
               f"✅ [DONE]({request.host_url}admin/update/{oid}/Completed)  "
               f"❌ [REJECT]({request.host_url}admin/update/{oid}/Rejected)")

        photo.seek(0)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}, 
                      files={'photo': (photo.filename, photo.read(), photo.content_type)})
        
        return "Success"
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
    
