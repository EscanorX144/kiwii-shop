import os, requests, json
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- ⚙️ CONFIGURATION ---
# MongoDB ချိတ်ဆက်မှု
MONGO_URI = "mongodb+srv://EscanorX:Conti144@cluster0.m2mtomm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['kiwii_game_shop']
orders_col = db['orders']

# Telegram Bot အတွက် (CS Link ကို @Bby_kiwii7 ပြောင်းထားသည်)
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
CHAT_ID = "7089720301"
CS_TELEGRAM = "https://t.me/Bby_kiwii7"

# --- 💎 DIAMOND DATA ---
GAMES_DATA = [
    {"id": 1, "name": "Normal Server (🇲🇲)", "img": "https://flagcdn.com/w160/mm.png", "cat_order": ["Normal Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], "cats": {"Normal Dia": [{"d": "11 💎", "p": "700"}, {"d": "22 💎", "p": "1400"}, {"d": "33 💎", "p": "2100"}, {"d": "44 💎", "p": "2800"}, {"d": "56 💎", "p": "3500"}, {"d": "86 💎", "p": "4750"}, {"d": "112 💎", "p": "7000"}, {"d": "172 💎", "p": "9450"}, {"d": "257 💎", "p": "13800"}, {"d": "343 💎", "p": "18600"}, {"d": "429 💎", "p": "23350"}, {"d": "514 💎", "p": "27650"}, {"d": "600 💎", "p": "32650"}, {"d": "706 💎", "p": "37450"}, {"d": "1412 💎", "p": "74900"}, {"d": "2195 💎", "p": "114200"}, {"d": "9288 💎", "p": "475200"}], "Weekly Pass": [{"d": "WP 1X", "p": "5900"}, {"d": "WP 2X", "p": "11800"}], "2X Dia": [{"d": "50+50 💎", "p": "3050"}, {"d": "150+150 💎", "p": "9100"}], "Bundle Pack": [{"d": "Weekly Elite", "p": "3050"}, {"d": "Monthly Bundle", "p": "15350"}]}},
    {"id": 2, "name": "Malaysia (🇲🇾)", "img": "https://flagcdn.com/w160/my.png", "cat_order": ["Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], "cats": {"Dia": [{"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "56 💎", "p": "4350"}, {"d": "70 💎", "p": "5100"}, {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"}, {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"}, {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}], "Weekly Pass": [{"d": "WP", "p": "8700"}], "2X Dia": [{"d": "50+ 💎", "p": "4250"}, {"d": "150+ 💎", "p": "12200"}, {"d": "250+ 💎", "p": "20200"}, {"d": "500+ 💎", "p": "40600"}], "Bundle Pack": [{"d": "Weekly Elite", "p": "4250"}, {"d": "Monthly Epic", "p": "20000"}]}},
    {"id": 3, "name": "Singapore (🇸🇬)", "img": "https://flagcdn.com/w160/sg.png", "cat_order": ["Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], "cats": {"Dia": [{"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "56 💎", "p": "4350"}, {"d": "70 💎", "p": "5100"}, {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"}, {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"}, {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}], "Weekly Pass": [{"d": "WP", "p": "8700"}], "2X Dia": [{"d": "50+ 💎", "p": "4250"}, {"d": "150+ 💎", "p": "12200"}, {"d": "250+ 💎", "p": "20200"}, {"d": "500+ 💎", "p": "40600"}], "Bundle Pack": [{"d": "Weekly Elite", "p": "4250"}, {"d": "Monthly Epic", "p": "20000"}]}},
    {"id": 4, "name": "Indonesia (🇮🇩)", "img": "https://flagcdn.com/w160/id.png", "cat_order": ["Dia", "Pass"], "cats": {"Dia": [{"d": "5 💎", "p": "450"}, {"d": "12 💎", "p": "950"}, {"d": "19 💎", "p": "1500"}, {"d": "28 💎", "p": "2200"}, {"d": "44 💎", "p": "3300"}, {"d": "59 💎", "p": "4300"}, {"d": "85 💎", "p": "5850"}, {"d": "170 💎", "p": "11700"}, {"d": "240 💎", "p": "16600"}, {"d": "296 💎", "p": "20500"}, {"d": "408 💎", "p": "28000"}, {"d": "568 💎", "p": "37500"}, {"d": "875 💎", "p": "58500"}, {"d": "2010 💎", "p": "123500"}, {"d": "4830 💎", "p": "299000"}], "Pass": [{"d": "WP", "p": "7500"}, {"d": "Twilight Pass", "p": "45000"}]}},
    {"id": 5, "name": "Russia (🇷🇺)", "img": "https://flagcdn.com/w160/ru.png", "cat_order": ["Dia", "Pass"], "cats": {"Dia": [{"d": "35 💎", "p": "2750"}, {"d": "55 💎", "p": "4450"}, {"d": "165 💎", "p": "13000"}, {"d": "275 💎", "p": "22000"}, {"d": "565 💎", "p": "44500"}, {"d": "1155 💎", "p": "88000"}, {"d": "1765 💎", "p": "182000"}, {"d": "2975 💎", "p": "22000"}, {"d": "6000 💎", "p": "435000"}], "Pass": [{"d": "WP", "p": "8600"}, {"d": "Super Value Pass", "p": "4500"}]}},
    {"id": 6, "name": "Philippines (🇵🇭)", "img": "https://flagcdn.com/w160/ph.png", "cat_order": ["Dia", "2X Dia", "Pass"], "cats": {"Dia": [{"d": "11 💎", "p": "750"}, {"d": "22 💎", "p": "1500"}, {"d": "56 💎", "p": "3500"}, {"d": "112 💎", "p": "7000"}, {"d": "223 💎", "p": "14000"}, {"d": "336 💎", "p": "21300"}, {"d": "570 💎", "p": "36000"}, {"d": "1163 💎", "p": "70500"}, {"d": "2398 💎", "p": "140000"}, {"d": "6042 💎", "p": "350000"}], "2X Dia": [{"d": "50+50 💎", "p": "3600"}, {"d": "150+150 💎", "p": "10500"}, {"d": "250+250 💎", "p": "17200"}, {"d": "500+500 💎", "p": "34500"}], "Pass": [{"d": "WP", "p": "6500"}, {"d": "Twilight Pass", "p": "35500"}]}}
]

# --- 🌐 HTML CODE ---
HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; margin:0; padding-bottom:80px; }
    #main-container { max-width:500px; margin:auto; }
    .header-logo { text-align:center; padding:25px 0; color:#fbbf24; font-size:24px; font-weight:bold; }
    
    .game-grid { 
        display:grid; grid-template-columns:1fr 1fr; gap:15px; padding:20px; 
        background: url('https://hero.mebp.site/hero.webp') no-repeat center center; background-size: cover; 
    }
    .game-card { background:rgba(30, 41, 59, 0.9); border-radius:15px; padding:25px 15px; text-align:center; border:1px solid #334155; cursor:pointer; }

    .pay-icons { display:flex; gap:10px; justify-content:center; margin-bottom:12px; }
    .pay-icons img { width:40px; height:40px; border-radius:8px; border:1px solid #444; }
    
    .copy-btn { background:#fbbf24; border:none; border-radius:5px; padding:5px 10px; font-weight:bold; cursor:pointer; margin-left:10px; }
    
    .glow-box { 
        background:#1e293b; padding:15px; border-radius:10px; border:2px solid #fbbf24; 
        box-shadow: 0 0 15px #fbbf24; text-align:center; margin:15px 0; font-weight:bold; color:#fbbf24;
        animation: glow 1.5s infinite alternate;
    }
    @keyframes glow { from { box-shadow: 0 0 5px #fbbf24; } to { box-shadow: 0 0 20px #fbbf24; } }

    .nav-bar { position:fixed; bottom:0; width:100%; max-width:500px; background:#1e293b; display:flex; padding:12px 0; border-top:1px solid #334155; z-index:1000; }
    .nav-item { flex:1; text-align:center; color:#94a3b8; cursor:pointer; font-size:12px; }
    .nav-item.active { color:#fbbf24; }
    
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:15px 0; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; cursor:pointer; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; color:black; cursor:pointer; font-size:16px; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:10px; background:#1e293b; color:white; border:1px solid #334155; box-sizing:border-box; }
    
    .tab-scroll { display:flex; gap:8px; overflow-x:auto; padding-bottom:10px; }
    .cat-tab { padding:10px 15px; background:#1e293b; border-radius:8px; border:1px solid #334155; cursor:pointer; white-space:nowrap; }
    .cat-tab.active { background:#fbbf24; color:black; font-weight:bold; }

    .history-card { background:#1e293b; padding:12px; margin-bottom:10px; border-radius:10px; border-left:5px solid #fbbf24; }
    .status-done { color: #22c55e; border-left-color: #22c55e; }
    .status-reject { color: #ef4444; border-left-color: #ef4444; }
</style>
</head><body>
<div id="main-container">
    <div id="h-sec">
        <div class="header-logo">KIWII GAME STORE</div>
        <div class="game-grid" id="g-list"></div>
    </div>

    <div id="o-sec" style="display:none; padding:15px;">
        <button onclick="goH()" style="background:none;color:white;border:1px solid #334155;padding:8px;border-radius:8px;margin-bottom:10px;">← Back</button>
        <h2 id="g-title" style="color:#fbbf24; margin:0 0 15px 0;"></h2>
        <div id="tabs" class="tab-scroll"></div>
        <div id="p-list" class="pkg-grid"></div>
        
        <div style="background:#1e293b; padding:15px; border-radius:15px; border:1px solid #334155;">
            <div class="pay-icons">
                <img src="https://static.mebp.site/kpay.jpg"> 
                <img src="https://static.mebp.site/wave.jpg"> 
                <img src="https://static.mebp.site/ayapay.jpg">
            </div>
            <div style="text-align:center;">
                <b style="color:#fbbf24; font-size:20px;">09775394979</b>
                <button class="copy-btn" onclick="copyNum()">COPY</button><br>
                <small>Name: Thansin Kyaw</small>
            </div>
        </div>

        <div class="glow-box">⚠️ Note - Payment သာရေးပါ</div>

        <form id="orderForm" onsubmit="handleOrder(event)">
            <input type="tel" id="uid" placeholder="Game ID" required>
            <input type="tel" id="zid" placeholder="Zone ID" required>
            <p style="font-size:12px;color:#94a3b8;margin-top:10px;">Screenshot Upload:</p>
            <input type="file" id="photo" required accept="image/*">
            <button type="submit" class="buy-btn" id="submitBtn">PLACE ORDER</button>
        </form>
    </div>

    <div id="hist-sec" style="display:none; padding:15px;">
        <h3 style="color:#fbbf24;">My History</h3>
        <div id="hist-list"></div>
    </div>
</div>

<div class="nav-bar">
    <div class="nav-item active" id="nav-home" onclick="goH()"><i class="fas fa-home"></i><br>Home</div>
    <div class="nav-item" id="nav-hist" onclick="showH()"><i class="fas fa-history"></i><br>History</div>
    <div class="nav-item" onclick="window.open('{{ cs_link }}')"><i class="fas fa-headset"></i><br>CS</div>
</div>

<script>
let sel_srv='', sel_pkg='', sel_prc='';
const games = {{ games | tojson }};

function init() {
    document.getElementById('g-list').innerHTML = games.map(g => `
        <div class="game-card" onclick="selG(${g.id})">
            <img src="${g.img}" width="60" style="border-radius:10px;"><br>
            <b style="display:block;margin-top:10px;">${g.name}</b>
        </div>
    `).join('');
}
init();

function selG(id) {
    const g = games.find(i => i.id === id); sel_srv = g.name;
    document.getElementById('h-sec').style.display='none'; document.getElementById('o-sec').style.display='block';
    document.getElementById('hist-sec').style.display='none';
    document.getElementById('g-title').innerText = g.name;
    document.getElementById('tabs').innerHTML = g.cat_order.map((c, i) => `
        <div class="cat-tab ${i===0?'active':''}" onclick="renderP(${id}, '${c}', this)">${c}</div>
    `).join('');
    renderP(id, g.cat_order[0]);
}

function renderP(id, cat, el) {
    if(el){ document.querySelectorAll('.cat-tab').forEach(t=>t.classList.remove('active')); el.classList.add('active'); }
    const pkgs = games.find(i=>i.id===id).cats[cat];
    document.getElementById('p-list').innerHTML = pkgs.map(p=>`
        <div class="pkg-card" onclick="selP(this, '${p.d}', '${p.p}')">
            <span>${p.d}</span><br><b style="color:#fbbf24;">${p.p} Ks</b>
        </div>`).join('');
}

function selP(el, d, p) {
    document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected'));
    el.classList.add('selected'); sel_pkg=d; sel_prc=p;
}

function copyNum() {
    navigator.clipboard.writeText("09775394979");
    alert("ဖုန်းနံပါတ် 09775394979 ကို ကူးယူပြီးပါပြီ။");
}

async function handleOrder(e) {
    e.preventDefault();
    if(!sel_pkg) return alert("Package ရွေးပေးပါ။");
    const uid = document.getElementById('uid').value;
    const zid = document.getElementById('zid').value;
    
    if(confirm(`အော်ဒါအသေးစိတ်:\\n\\nServer: ${sel_srv}\\nPackage: ${sel_pkg}\\nPrice: ${sel_prc} Ks\\nID: ${uid} (${zid})\\n\\nမှန်ကန်ပါက အတည်ပြုနှိပ်ပါ။`)) {
        const btn = document.getElementById('submitBtn');
        btn.disabled = true; btn.innerText = "တင်ပို့နေသည်...";
        
        const fd = new FormData();
        fd.append('uid', uid); fd.append('zid', zid);
        fd.append('server', sel_srv); fd.append('pkg', sel_pkg);
        fd.append('price', sel_prc); fd.append('photo', document.getElementById('photo').files[0]);

        const r = await fetch('/order', { method: 'POST', body: fd });
        if(await r.text() === "Success") {
            alert("Order Received! ✅ အော်ဒါလက်ခံရရှိပါပြီ။ History မှာ စစ်ဆေးနိုင်ပါသည်။");
            location.reload();
        } else {
            alert("Error: အော်ဒါတင်ခြင်း မအောင်မြင်ပါ။");
            btn.disabled = false; btn.innerText = "PLACE ORDER";
        }
    }
}

async function showH() {
    document.getElementById('h-sec').style.display='none'; 
    document.getElementById('o-sec').style.display='none';
    document.getElementById('hist-sec').style.display='block';
    updateNav('nav-hist');
    const r = await fetch('/api/history');
    const data = await r.json();
    document.getElementById('hist-list').innerHTML = data.map(o => `
        <div class="history-card ${o.status==='Completed'?'status-done':(o.status==='Rejected'?'status-reject':'')}">
            <b>${o.pkg}</b> - ${o.price} Ks<br>
            <small>${o.server} | ID: ${o.uid}(${o.zone})</small><br>
            <div style="display:flex; justify-content:space-between; margin-top:5px;">
                <small>${o.date}</small>
                <b style="font-size:14px;">${o.status === 'Completed' ? 'ထည့်ပြီး ✅' : (o.status === 'Rejected' ? 'လက်မခံ ❌' : 'စောင့်ဆိုင်းဆဲ ⏳')}</b>
            </div>
        </div>
    `).join('') || "မှတ်တမ်းမရှိသေးပါ။";
}

function goH() { location.reload(); }
function updateNav(id) { 
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}
</script></body></html>
'''

# --- 🚀 BACKEND ---

@app.route('/')
def index():
    return render_template_string(HTML_CODE, games=GAMES_DATA, cs_link=CS_TELEGRAM)

@app.route('/order', methods=['POST'])
def order():
    try:
        uid, zid, server = request.form.get('uid'), request.form.get('zid'), request.form.get('server')
        pkg, price = request.form.get('pkg'), request.form.get('price')
        photo = request.files.get('photo')
        
        # MongoDB သို့ သိမ်းဆည်းခြင်း
        oid = orders_col.insert_one({
            "uid": uid, "zone": zid, "server": server, "pkg": pkg, "price": price,
            "status": "Pending", "date": datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%d/%m/%Y %I:%M %p")
        }).inserted_id
        
        # Telegram သို့ အော်ဒါပို့ခြင်း (Done/Reject Buttons ပါဝင်သည်)
        msg = f"🔔 *New Order!*\n\nID: `{uid}` ({zid})\nServer: {server}\nPackage: {pkg}\nPrice: {price} Ks"
        keyboard = {
            "inline_keyboard": [[
                {"text": "Done ✅", "callback_data": f"done_{oid}"},
                {"text": "Reject ❌", "callback_data": f"reject_{oid}"}
            ]]
        }
        
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown", "reply_markup": json.dumps(keyboard)}, 
                      files={'photo': photo})
        return "Success"
    except:
        return "Error"

@app.route('/api/history')
def get_history():
    # နောက်ဆုံးတင်ထားတဲ့ အော်ဒါ ၂၀ ခုကို ပြပါမယ်
    hist = list(orders_col.find().sort("_id", -1).limit(20))
    for h in hist: h['_id'] = str(h['_id'])
    return jsonify(hist)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

