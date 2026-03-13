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
CS_TELEGRAM = "https://t.me/Bby_kiwii7"
ADMIN_USERNAMES = ["@Escanor_XX", "@Escanor_X", "@Bby_kiwii7"]

GAMES_DATA = [
    {
        "id": 1, "name": "Normal Server (🇲🇲)", "img": "https://flagcdn.com/w160/mm.png", 
        "cat_order": ["Normal Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], 
        "cats": {
            "Normal Dia": [
                {"d": "11 💎", "p": "700"}, {"d": "22 💎", "p": "1400"}, {"d": "33 💎", "p": "2100"}, {"d": "44 💎", "p": "2800"}, {"d": "56 💎", "p": "3500"}, {"d": "86 💎", "p": "4750"}, {"d": "112 💎", "p": "7000"}, {"d": "172 💎", "p": "9450"}, {"d": "257 💎", "p": "13800"}, {"d": "279 💎", "p": "15200"}, {"d": "343 💎", "p": "18600"}, {"d": "429 💎", "p": "23350"}, {"d": "514 💎", "p": "27650"}, {"d": "600 💎", "p": "32650"}, {"d": "706 💎", "p": "37450"}, {"d": "792 💎", "p": "42200"}, {"d": "878 💎", "p": "46850"}, {"d": "963 💎", "p": "51200"}, {"d": "1049 💎", "p": "56000"}, {"d": "1135 💎", "p": "60850"}, {"d": "1412 💎", "p": "74900"}, {"d": "2195 💎", "p": "114200"}, {"d": "3688 💎", "p": "190500"}, {"d": "5532 💎", "p": "287000"}, {"d": "7376 💎", "p": "381000"}, {"d": "9288 💎", "p": "475200"}
            ],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "5900"}, {"d": "Weekly Pass 2X", "p": "11800"}, {"d": "Weekly Pass 3X", "p": "17700"}, {"d": "Weekly Pass 4X", "p": "23600"}, {"d": "Weekly Pass 5X", "p": "29500"}, {"d": "Weekly Pass 6X", "p": "35400"}, {"d": "Weekly Pass 7X", "p": "41300"}, {"d": "Weekly Pass 8X", "p": "47200"}, {"d": "Weekly Pass 9X", "p": "53100"}, {"d": "Weekly Pass 10X", "p": "59000"}
            ],
            "2X Dia": [
                {"d": "50+50 💎", "p": "3050"}, {"d": "150+150 💎", "p": "9100"}, {"d": "250+250 💎", "p": "14650"}, {"d": "500+500 💎", "p": "29950"}
            ],
            "Bundle Pack": [
                {"d": "Weekly Elite", "p": "3050"}, {"d": "Monthly Epic", "p": "15350"}, {"d": "Twilight Pass", "p": "31300"}
            ]
        }
    },
    {
        "id": 2, "name": "Malaysia (🇲🇾)", "img": "https://flagcdn.com/w160/my.png", 
        "cat_order": ["Malaysia Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], 
        "cats": {
            "Dia": [{"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "56 💎", "p": "4350"}, {"d": "70 💎", "p": "5100"}, {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"}, {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"}, {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "8700"}, {"d": "Weekly Pass 2X", "p": "17400"}, {"d": "Weekly Pass 3X", "p": "26100"}, {"d": "Weekly Pass 4X", "p": "34800"}, {"d": "Weekly Pass 5X", "p": "43500"}, {"d": "Weekly Pass 6X", "p": "52200"}, {"d": "Weekly Pass 7X", "p": "60900"}, {"d": "Weekly Pass 8X", "p": "69600"}, {"d": "Weekly Pass 9X", "p": "78300"}, {"d": "Weekly Pass 10X", "p": "87000"}
            ],
            "2X Dia": [{"d": "50+ 💎", "p": "4250"}, {"d": "150+ 💎", "p": "12200"}, {"d": "250+ 💎", "p": "20200"}, {"d": "500+ 💎", "p": "40600"}],
            "Bundle Pack": [{"d": "Weekly Elite", "p": "4250"}, {"d": "Monthly Epic", "p": "20000"}]
        }
    },
    {
        "id": 3, "name": "Singapore (🇸🇬)", "img": "https://flagcdn.com/w160/sg.png", 
        "cat_order": ["Singapore Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], 
        "cats": {
            "Dia": [{"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "56 💎", "p": "4350"}, {"d": "70 💎", "p": "5100"}, {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"}, {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"}, {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "8700"}, {"d": "Weekly Pass 2X", "p": "17400"}, {"d": "Weekly Pass 3X", "p": "26100"}, {"d": "Weekly Pass 4X", "p": "34800"}, {"d": "Weekly Pass 5X", "p": "43500"}, {"d": "Weekly Pass 6X", "p": "52200"}, {"d": "Weekly Pass 7X", "p": "60900"}, {"d": "Weekly Pass 8X", "p": "69600"}, {"d": "Weekly Pass 9X", "p": "78300"}, {"d": "Weekly Pass 10X", "p": "87000"}
            ],
            "2X Dia": [{"d": "50+ 💎", "p": "4250"}, {"d": "150+ 💎", "p": "12200"}, {"d": "250+ 💎", "p": "20200"}, {"d": "500+ 💎", "p": "40600"}],
            "Bundle Pack": [{"d": "Weekly Elite", "p": "4250"}, {"d": "Monthly Epic", "p": "20000"}]
        }
    },
    {
        "id": 4, "name": "Indonesia (🇮🇩)", "img": "https://flagcdn.com/w160/id.png", 
        "cat_order": ["Indonesia Dia", "Weekly Pass"], 
        "cats": {
            "Dia": [{"d": "5 💎", "p": "450"}, {"d": "12 💎", "p": "950"}, {"d": "19 💎", "p": "1500"}, {"d": "28 💎", "p": "2200"}, {"d": "44 💎", "p": "3300"}, {"d": "59 💎", "p": "4300"}, {"d": "85 💎", "p": "5850"}, {"d": "170 💎", "p": "11700"}, {"d": "240 💎", "p": "16600"}, {"d": "296 💎", "p": "20500"}, {"d": "408 💎", "p": "28000"}, {"d": "568 💎", "p": "37500"}, {"d": "875 💎", "p": "58500"}, {"d": "2010 💎", "p": "123500"}, {"d": "4830 💎", "p": "299000"}],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "7500"}, {"d": "Weekly Pass 2X", "p": "15000"}, {"d": "Weekly Pass 3X", "p": "22500"}, {"d": "Weekly Pass 4X", "p": "30000"}, {"d": "Weekly Pass 5X", "p": "37500"}, {"d": "Weekly Pass 6X", "p": "45000"}, {"d": "Weekly Pass 7X", "p": "52500"}, {"d": "Weekly Pass 8X", "p": "60000"}, {"d": "Weekly Pass 9X", "p": "67500"}, {"d": "Weekly Pass 10X", "p": "75000"}, {"d": "Twilight Pass", "p": "45000"}
            ]
        }
    },
    {
        "id": 5, "name": "Russia (🇷🇺)", "img": "https://flagcdn.com/w160/ru.png", 
        "cat_order": ["Russia Dia", "Weekly Pass"], 
        "cats": {
            "Dia": [{"d": "35 💎", "p": "2750"}, {"d": "55 💎", "p": "4450"}, {"d": "165 💎", "p": "13000"}, {"d": "275 💎", "p": "22000"}, {"d": "565 💎", "p": "44500"}, {"d": "1155 💎", "p": "88000"}, {"d": "1765 💎", "p": "182000"}, {"d": "2975 💎", "p": "22000"}, {"d": "6000 💎", "p": "435000"}],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "8600"}, {"d": "Weekly Pass 2X", "p": "17200"}, {"d": "Weekly Pass 3X", "p": "25800"}, {"d": "Weekly Pass 4X", "p": "34400"}, {"d": "Weekly Pass 5X", "p": "43000"}, {"d": "Weekly Pass 6X", "p": "51600"}, {"d": "Weekly Pass 7X", "p": "60200"}, {"d": "Weekly Pass 8X", "p": "68800"}, {"d": "Weekly Pass 9X", "p": "77400"}, {"d": "Weekly Pass 10X", "p": "86000"}
            ]
        }
    },
    {
        "id": 6, "name": "Philippines (🇵🇭)", "img": "https://flagcdn.com/w160/ph.png", 
        "cat_order": ["Philippines Dia", "2X Dia", "Weekly Pass"], 
        "cats": {
            "Dia": [{"d": "11 💎", "p": "750"}, {"d": "22 💎", "p": "1500"}, {"d": "56 💎", "p": "3500"}, {"d": "112 💎", "p": "7000"}, {"d": "223 💎", "p": "14000"}, {"d": "336 💎", "p": "21300"}, {"d": "570 💎", "p": "36000"}, {"d": "1163 💎", "p": "70500"}, {"d": "2398 💎", "p": "140000"}, {"d": "6042 💎", "p": "350000"}],
            "2X Dia": [{"d": "50+50 💎", "p": "3600"}, {"d": "150+150 💎", "p": "10500"}, {"d": "250+250 💎", "p": "17200"}, {"d": "500+500 💎", "p": "34500"}],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "6500"}, {"d": "Weekly Pass 2X", "p": "13000"}, {"d": "Weekly Pass 3X", "p": "19500"}, {"d": "Weekly Pass 4X", "p": "26000"}, {"d": "Weekly Pass 5X", "p": "32500"}, {"d": "Weekly Pass 6X", "p": "39000"}, {"d": "Weekly Pass 7X", "p": "45500"}, {"d": "Weekly Pass 8X", "p": "52000"}, {"d": "Weekly Pass 9X", "p": "58500"}, {"d": "Weekly Pass 10X", "p": "65000"}, {"d": "Twilight Pass", "p": "35500"}
            ]
        }
    }
]

HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; margin:0; padding-bottom:80px; }
    #main-container { max-width:500px; margin:auto; }
    .header-logo { text-align:center; padding:25px 0; color:#fbbf24; font-size:26px; font-weight:bold; }
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:15px; padding:20px; }
    .game-card { background:rgba(30, 41, 59, 0.85); border-radius:15px; padding:20px; text-align:center; border:1px solid #334155; cursor:pointer; }
    
    .cat-tabs { display:flex; gap:10px; overflow-x:auto; padding:10px 0; margin-bottom:15px; scrollbar-width: none; }
    .cat-tabs::-webkit-scrollbar { display: none; }
    .tab-btn { background:#1e293b; border:1px solid #334155; color:#94a3b8; padding:10px 15px; border-radius:10px; white-space:nowrap; cursor:pointer; font-size:14px; }
    .tab-btn.active { background:#fbbf24; color:black; border-color:#fbbf24; font-weight:bold; }

    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:15px 0; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; cursor:pointer; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    
    /* --- Payment Section Styling --- */
    .pay-box { background:#1e293b; padding:20px; border-radius:15px; border:1px solid #fbbf24; text-align:center; margin-bottom:15px; }
    .pay-icons { display:flex; justify-content:center; gap:15px; margin-bottom:15px; }
    .pay-icons img { width:55px; height:55px; border-radius:12px; cursor:pointer; border:2px solid transparent; transition: 0.3s; }
    .pay-icons img:active { transform: scale(0.9); }
    
    .copy-btn { background:#fbbf24; color:black; border:none; padding:6px 12px; border-radius:8px; font-size:12px; font-weight:bold; cursor:pointer; margin-left:10px; vertical-align: middle; }
    
    /* Blinking Red Glow Box */
    .note-box { 
        background: rgba(239, 68, 68, 0.1); 
        border: 2px solid #ef4444; 
        color: #ef4444; 
        padding: 10px; 
        border-radius: 10px; 
        font-weight: bold; 
        margin-top: 15px;
        animation: blink-glow 1.5s infinite;
    }
    @keyframes blink-glow {
        0% { box-shadow: 0 0 5px #ef4444; opacity: 1; }
        50% { box-shadow: 0 0 20px #ef4444; opacity: 0.8; }
        100% { box-shadow: 0 0 5px #ef4444; opacity: 1; }
    }

    .nav-bar { position:fixed; bottom:0; width:100%; max-width:500px; background:#1e293b; display:flex; padding:12px 0; border-top:1px solid #334155; z-index:1000; }
    .nav-item { flex:1; text-align:center; color:#94a3b8; cursor:pointer; font-size:12px; }
    .nav-item.active { color:#fbbf24; }
    
    input { width:100%; padding:14px; margin:8px 0; border-radius:10px; background:#1e293b; color:white; border:1px solid #334155; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; color:black; cursor:pointer; margin-top:10px; }
</style>
</head><body>
<div id="main-container">
    <div id="h-sec">
        <div class="header-logo">KIWII GAME STORE</div>
        <div class="game-grid" id="g-list"></div>
    </div>

    <div id="o-sec" style="display:none; padding:15px;">
        <button onclick="goH()" style="background:none;color:white;border:1px solid #334155;padding:8px 15px;border-radius:8px;margin-bottom:15px;">← Back</button>
        <h2 id="g-title" style="color:#fbbf24; margin-bottom:5px;"></h2>
        <div id="cat-container" class="cat-tabs"></div>
        <div id="p-list" class="pkg-grid"></div>

        <div class="pay-box">
            <div class="pay-icons">
                <img src="/static/kpay.jpg" onclick="setPay('09775394979', 'Kpay')">
                <img src="/static/wave.jpg" onclick="setPay('09775394979', 'Wave')">
                <img src="/static/ayapay.jpg" onclick="setPay('09775394979', 'Ayapay')">
            </div>
            <div style="margin-bottom:10px;">
                <b id="pay-type" style="color:#fbbf24; font-size:14px;">Select Payment</b><br>
                <span id="pay-num" style="font-size:24px; font-weight:bold; color:white;">09775394979</span>
                <button class="copy-btn" onclick="copyNum()">COPY</button>
            </div>
            <div style="color:#94a3b8; font-size:14px;">Name - Thansin Kyaw</div>
            
            <div class="note-box">
                Note - Payment သာရေးပါ
            </div>
        </div>

        <form id="orderForm" onsubmit="handleOrder(event)">
            <input type="tel" id="uid" placeholder="Game ID" required>
            <input type="tel" id="zid" placeholder="Zone ID" required>
            <input type="file" id="photo" required accept="image/*">
            <button type="submit" class="buy-btn" id="submitBtn">PLACE ORDER</button>
        </form>
    </div>

    <div id="top-sec" style="display:none; padding:15px;">
        <h3 style="color:#fbbf24; text-align:center;">🏆 TOP 10 USERS</h3>
        <div id="top-list"></div>
    </div>

    <div id="hist-sec" style="display:none; padding:15px;">
        <h3 style="color:#fbbf24;">History</h3>
        <div id="hist-list"></div>
    </div>
</div>

<div class="nav-bar">
    <div class="nav-item active" id="nav-home" onclick="goH()"><i class="fas fa-home"></i><br>Home</div>
    <div class="nav-item" id="nav-hist" onclick="showH()"><i class="fas fa-history"></i><br>History</div>
    <div class="nav-item" id="nav-top" onclick="showTop()"><i class="fas fa-trophy"></i><br>Top 10</div>
    <div class="nav-item" onclick="window.open('{{ cs_link }}')"><i class="fas fa-headset"></i><br>CS</div>
</div>

<script>
let sel_srv='', sel_pkg='', sel_prc='';
const games = {{ games | tojson }};

function init() {
    document.getElementById('g-list').innerHTML = games.map(g => `
        <div class="game-card" onclick="selG(${g.id})">
            <img src="${g.img}" width="65" style="border-radius:12px;"><br>
            <b style="display:block;margin-top:12px;">${g.name}</b>
        </div>`).join('');
}
init();

function selG(id) {
    const g = games.find(i => i.id === id);
    sel_srv = id;
    document.getElementById('h-sec').style.display='none';
    document.getElementById('o-sec').style.display='block';
    document.getElementById('g-title').innerText = g.name;

    const cats = g.cat_order;
    document.getElementById('cat-container').innerHTML = cats.map((c, index) => `
        <div class="tab-btn ${index===0?'active':''}" onclick="renderP('${c}', this)">${c}</div>
    `).join('');
    renderP(cats[0], document.querySelector('.tab-btn.active'));
}

function renderP(catName, btnEl) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    if(btnEl) btnEl.classList.add('active');
    const g = games.find(i => i.id === sel_srv);
    const pkgs = g.cats[catName];
    document.getElementById('p-list').innerHTML = pkgs.map(p => `
        <div class="pkg-card" onclick="selP(this, '${p.d}', '${p.p}')">
            <span>${p.d}</span><br><b style="color:#fbbf24;">${p.p} Ks</b>
        </div>`).join('');
}

function selP(el, d, p) {
    document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected'));
    el.classList.add('selected'); sel_pkg=d; sel_prc=p;
}

// Payment Functions
function setPay(num, type) {
    document.getElementById('pay-num').innerText = num;
    document.getElementById('pay-type').innerText = type + " Account";
}

function copyNum() {
    const num = document.getElementById('pay-num').innerText;
    navigator.clipboard.writeText(num).then(() => {
        const btn = document.querySelector('.copy-btn');
        btn.innerText = "COPIED!";
        btn.style.background = "#22c55e";
        setTimeout(() => { 
            btn.innerText = "COPY"; 
            btn.style.background = "#fbbf24";
        }, 2000);
    });
}

async function handleOrder(e) {
    e.preventDefault();
    if(!sel_pkg) return alert("Package ရွေးပေးပါ။");
    const btn = document.getElementById('submitBtn');
    btn.innerText = "SENDING..."; btn.disabled = true;

    const fd = new FormData();
    fd.append('tg_user', "@Bby_kiwii7"); // Fixed user for now
    fd.append('uid', document.getElementById('uid').value);
    fd.append('zid', document.getElementById('zid').value);
    fd.append('server', games.find(i=>i.id===sel_srv).name);
    fd.append('pkg', sel_pkg);
    fd.append('price', sel_prc);
    fd.append('photo', document.getElementById('photo').files[0]);

    try {
        const r = await fetch('/order', { method: 'POST', body: fd });
        if(await r.text() === "Success") {
            alert("Order Successful!");
            location.reload();
        } else { alert("Order Failed."); }
    } catch(err) { alert("Error: " + err); }
    btn.innerText = "PLACE ORDER"; btn.disabled = false;
}

async function showTop() {
    document.getElementById('h-sec').style.display='none'; document.getElementById('o-sec').style.display='none';
    document.getElementById('hist-sec').style.display='none'; document.getElementById('top-sec').style.display='block';
    const r = await fetch('/api/top10');
    const data = await r.json();
    document.getElementById('top-list').innerHTML = data.map((u, i) => `
        <div style="background:#1e293b;padding:15px;margin-bottom:10px;border-radius:12px;display:flex;align-items:center;">
            <div style="width:30px;height:30px;background:#fbbf24;color:black;border-radius:50%;text-align:center;line-height:30px;margin-right:15px;font-weight:bold;">${i+1}</div>
            <div style="flex:1;"><b>${u._id}</b></div>
            <div style="color:#fbbf24;font-weight:bold;">${u.totalSpent.toLocaleString()} Ks</div>
        </div>`).join('') || "No data";
}

async function showH() {
    document.getElementById('h-sec').style.display='none'; document.getElementById('o-sec').style.display='none';
    document.getElementById('top-sec').style.display='none'; document.getElementById('hist-sec').style.display='block';
    const r = await fetch('/api/history');
    const data = await r.json();
    document.getElementById('hist-list').innerHTML = data.map(o => `
        <div style="background:#1e293b;padding:15px;margin-bottom:10px;border-radius:12px;border-left:5px solid #fbbf24;">
            <b>${o.pkg}</b> - ${o.price} Ks<br><small>${o.status} | ${o.date}</small>
        </div>`).join('') || "No history";
}
function goH() { location.reload(); }
</script></body></html>
'''

# --- 🚀 BACKEND ---
@app.route('/')
def index():
    return render_template_string(HTML_CODE, games=GAMES_DATA, cs_link=CS_TELEGRAM)

@app.route('/order', methods=['POST'])
def order():
    try:
        tg_user = request.form.get('tg_user')
        uid = request.form.get('uid'); zid = request.form.get('zid')
        price_str = request.form.get('price', '0').replace(' Ks', '').replace(',', '')
        price = int(price_str)
        pkg = request.form.get('pkg'); srv = request.form.get('server')
        photo = request.files.get('photo')
        
        oid = orders_col.insert_one({
            "tg_user": tg_user, "uid": uid, "zone": zid, "pkg": pkg, "price": price, "status": "Pending", 
            "date": datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%d/%m/%Y %I:%M %p")
        }).inserted_id
        
        base_url = "https://kiwiigameshop.onrender.com"
        keyboard = {"inline_keyboard": [[
            {"text": "Done ✅", "url": f"{base_url}/admin/status/done/{oid}"},
            {"text": "Reject ❌", "url": f"{base_url}/admin/status/reject/{oid}"}
        ]]}
        
        msg = f"<b>⚠️ New Order!</b>\n\n<b>👤 User:</b> {tg_user}\n<b>🌍 Server:</b> {srv}\n<b>🆔 ID:</b> <code>{uid}</code> ({zid})\n<b>📦 Package:</b> {pkg}\n<b>💰 Price:</b> {price} Ks"
        
        if photo:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "HTML", "reply_markup": json.dumps(keyboard)}, 
                files={"photo": photo})
        else:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML", "reply_markup": json.dumps(keyboard)})
        
        return "Success"
    except Exception as e:
        return str(e), 500

@app.route('/admin/status/<action>/<oid>')
def update_status(action, oid):
    try:
        new_status = "Completed" if action == "done" else "Rejected"
        orders_col.update_one({"_id": ObjectId(oid)}, {"$set": {"status": new_status}})
        return f"<html><body style='background:#0f172a;color:white;text-align:center;padding:50px;'><h1>Order {new_status}!</h1></body></html>"
    except Exception as e:
        return str(e), 500

@app.route('/api/history')
def history():
    hist = list(orders_col.find().sort("_id", -1).limit(15))
    for h in hist: h['_id'] = str(h['_id'])
    return jsonify(hist)

@app.route('/api/top10')
def top10():
    pipeline = [{"$match": {"tg_user": {"$nin": ADMIN_USERNAMES}}}, {"$group": {"_id": "$tg_user", "totalSpent": {"$sum": "$price"}}}, {"$sort": {"totalSpent": -1}}, {"$limit": 10}]
    return jsonify(list(orders_col.aggregate(pipeline)))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
