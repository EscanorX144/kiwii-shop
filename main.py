import os, requests
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "KIWII_ULTIMATE_SECRET"

# --- 🛰️ MONGODB CONNECTION (Standard Driver Format) ---
MONGO_URI = "mongodb://EscanorX:Conti144@cluster0-shard-00-00.m2tomm.mongodb.net:27017,cluster0-shard-00-01.m2tomm.mongodb.net:27017,cluster0-shard-00-02.m2tomm.mongodb.net:27017/?ssl=true&replicaSet=atlas-m2tomm-shard-0&authSource=admin"
client = MongoClient(MONGO_URI, connectTimeoutMS=30000)
db_mongo = client['kiwii_game_shop']
orders_col = db_mongo['orders']

# --- ⚙️ CONFIGURATION ---
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3Ygej3nAwOODSNj4ujVvk"
CHAT_ID = "7089720301"
CS_LINK = "https://t.me/Bby_kiwii7"

PAY_DATA = {
    "KPay": {"Number": "09775394979", "Name": "Thansin Kyaw", "img": "/static/kpay.jpg"},
    "Wave": {"Number": "09775394979", "Name": "Thansin Kyaw", "img": "/static/wave.jpg"},
    "AYAPay": {"Number": "09775394979", "Name": "Thansin Kyaw", "img": "/static/ayapay.jpg"},
    "Note": "Payment သာရေးပါ"
}

# --- 💎 FULL GAME DATA ---
GAMES_DATA = [
    {
        "name": "Normal Server (🇲🇲)",
        "img": "https://flagcdn.com/w160/mm.png",
        "cats": {
            "Normal Dia": [{"d": "11 💎", "p": "700"}, {"d": "22 💎", "p": "1400"}, {"d": "33 💎", "p": "2100"}, {"d": "44 💎", "p": "2800"}, {"d": "56 💎", "p": "3500"}, {"d": "112 💎", "p": "7000"}, {"d": "172 💎", "p": "9450"}, {"d": "257 💎", "p": "13800"}, {"d": "343 💎", "p": "18600"}, {"d": "429 💎", "p": "23350"}, {"d": "514 💎", "p": "27650"}, {"d": "600 💎", "p": "32650"}, {"d": "706 💎", "p": "37450"}, {"d": "878 💎", "p": "46850"}, {"d": "1049 💎", "p": "56000"}, {"d": "1412 💎", "p": "74900"}, {"d": "2195 💎", "p": "114200"}, {"d": "3688 💎", "p": "190500"}, {"d": "5532 💎", "p": "287000"}, {"d": "9288 💎", "p": "475000"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X 💎", "p": str(5900 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "3050"}, {"d": "150+150 💎", "p": "9100"}, {"d": "250+250 💎", "p": "14650"}, {"d": "500+500 💎", "p": "29950"}],
            "Bundle Pack": [{"d": "Weekly elite 💎", "p": "3050"}, {"d": "Monthly epic 💎", "p": "15350"}, {"d": "Twilight pass 💎", "p": "31500"}]
        }
    },
    {
        "name": "Malaysia (🇲🇾)",
        "img": "https://flagcdn.com/w160/my.png",
        "cats": {
            "Normal Dia": [{"d": "14 💎", "p": "1050"}, {"d": "42 💎", "p": "3100"}, {"d": "70 💎", "p": "5050"}, {"d": "140 💎", "p": "10100"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "716 💎", "p": "50200"}, {"d": "1446 💎", "p": "100500"}, {"d": "2976 💎", "p": "201000"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X 💎", "p": str(8400 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "4250"}, {"d": "150+150 💎", "p": "12200"}, {"d": "250+250 💎", "p": "20200"}, {"d": "500+500 💎", "p": "40600"}]
        }
    },
    {
        "name": "Singapore (🇸🇬)",
        "img": "https://flagcdn.com/w160/sg.png",
        "cats": {
            "Normal Dia": [{"d": "14 💎", "p": "1050"}, {"d": "42 💎", "p": "3100"}, {"d": "70 💎", "p": "5050"}, {"d": "140 💎", "p": "10100"}, {"d": "210 💎", "p": "15100"}, {"d": "355 💎", "p": "25200"}, {"d": "716 💎", "p": "50200"}, {"d": "1446 💎", "p": "100500"}, {"d": "2976 💎", "p": "201000"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X 💎", "p": str(8400 * i)} for i in range(1, 11)]
        }
    },
    {
        "name": "Philippines (🇵🇭)",
        "img": "https://flagcdn.com/w160/ph.png",
        "cats": {
            "Normal Dia": [{"d": "11 💎", "p": "750"}, {"d": "22 💎", "p": "1500"}, {"d": "56 💎", "p": "3500"}, {"d": "112 💎", "p": "7000"}, {"d": "223 💎", "p": "14000"}, {"d": "336 💎", "p": "21300"}, {"d": "570 💎", "p": "36000"}, {"d": "1163 💎", "p": "70500"}, {"d": "2398 💎", "p": "140000"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X 💎", "p": str(6500 * i)} for i in range(1, 11)]
        }
    },
    {
        "name": "Indonesia (🇮🇩)",
        "img": "https://flagcdn.com/w160/id.png",
        "cats": {
            "Normal Dia": [{"d": "5 💎", "p": "450"}, {"d": "12 💎", "p": "950"}, {"d": "28 💎", "p": "2200"}, {"d": "44 💎", "p": "3300"}, {"d": "59 💎", "p": "4300"}, {"d": "85 💎", "p": "5850"}, {"d": "170 💎", "p": "11700"}, {"d": "296 💎", "p": "20500"}, {"d": "408 💎", "p": "28000"}, {"d": "875 💎", "p": "58500"}, {"d": "2010 💎", "p": "123500"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X 💎", "p": str(7500 * i)} for i in range(1, 11)]
        }
    },
    {
        "name": "Russia (🇷🇺)",
        "img": "https://flagcdn.com/w160/ru.png",
        "cats": {
            "Normal Dia": [{"d": "35 💎", "p": "2750"}, {"d": "55 💎", "p": "4450"}, {"d": "165 💎", "p": "13000"}, {"d": "275 💎", "p": "22000"}, {"d": "565 💎", "p": "44500"}, {"d": "1155 💎", "p": "88000"}, {"d": "1765 💎", "p": "132000"}, {"d": "2975 💎", "p": "220000"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X 💎", "p": str(8600 * i)} for i in range(1, 11)]
        }
    }
]

# --- UI HTML ---
HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    @keyframes glow { 0%, 100% { box-shadow: 0 0 5px #ff4444; } 50% { box-shadow: 0 0 15px #ff4444; } }
    body { background: #0f172a; color:white; font-family:sans-serif; margin:0; padding:15px; padding-bottom:80px; }
    
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:15px; }
    .game-card { 
        background: linear-gradient(rgba(30, 41, 59, 0.75), rgba(30, 41, 59, 0.9)), url('/static/hero.webp'); 
        background-size: cover; background-position: center; border-radius: 15px; 
        padding: 25px 10px; text-align: center; border: 1px solid rgba(255,255,255,0.1);
    }
    .game-card img { width:55px; border-radius:6px; margin-bottom:12px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }

    .cat-tabs-container { display:flex; gap:8px; overflow-x:auto; padding-bottom:10px; margin: 15px 0; }
    .cat-tab { padding:10px 18px; background:#1e293b; border-radius:10px; font-size:12px; border:1px solid #334155; color:#94a3b8; cursor:pointer; white-space: nowrap; }
    .cat-tab.active { background:#fbbf24; color:black; font-weight:bold; }
    
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; max-height: 380px; overflow-y: auto; padding-right:5px; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:12px; border-radius:10px; text-align:center; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }

    .pay-card { background:rgba(30, 41, 59, 0.95); border-radius:15px; padding:20px; text-align:center; border:1px solid #fbbf24; margin: 15px 0; }
    .pay-btn-icon { width: 50px; height: 50px; border-radius: 10px; border: 2px solid transparent; cursor: pointer; margin: 0 5px; }
    .pay-btn-icon.active { border-color: #fbbf24; }
    .glow-box { animation: glow 1.5s infinite; background: rgba(255, 68, 68, 0.1); border: 1px solid #ff4444; padding: 10px; border-radius: 8px; color: #ff4444; font-size: 13px; margin-top:10px; }
    
    input { width:100%; padding:14px; margin:8px 0; border-radius:10px; border:1px solid #334155; background:#0f172a; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:10px; font-weight:bold; color:black; font-size:16px; margin-top:10px; cursor:pointer;}

    .nav-bar { position:fixed; bottom:0; left:0; right:0; background:#1e293b; display:flex; padding:12px; border-top:1px solid #334155; }
    .nav-btn { flex:1; text-align:center; color:#94a3b8; font-size:12px; text-decoration:none; cursor:pointer; }
</style>
</head><body>

<div id="home-sec">
    <h1 style="text-align:center;color:#fbbf24;font-family:serif;">KIWII GAME SHOP</h1>
    <div class="game-grid" id="game-list"></div>
</div>

<div id="history-sec" style="display:none; padding:10px;">
    <h2 style="color:#fbbf24;">Order History</h2>
    <div id="history-list"></div>
</div>

<div id="order-sec" style="display:none;">
    <button onclick="goHome()" style="background:none;color:white;border:1px solid #334155;padding:8px 15px;border-radius:8px;margin-bottom:15px;">← Back</button>
    <h3 id="game-title" style="color:#fbbf24; margin-top:0;"></h3>
    <div class="cat-tabs-container" id="tabs"></div>
    <div class="pkg-grid" id="pkg-list"></div>

    <div style="text-align:center; margin-top:20px;">
        <img src="{{pay.KPay.img}}" class="pay-btn-icon active" onclick="setPay('KPay', this)">
        <img src="{{pay.Wave.img}}" class="pay-btn-icon" onclick="setPay('Wave', this)">
        <img src="{{pay.AYAPay.img}}" class="pay-btn-icon" onclick="setPay('AYAPay', this)">
    </div>

    <div class="pay-card">
        <b id="pay-num" style="color:#fbbf24;font-size:22px;"></b><br>
        <span id="pay-name" style="color:#cbd5e1; font-size:14px;"></span>
        <div class="glow-box">Note - {{pay.Note}}</div>
    </div>

    <form action="/order" method="post" enctype="multipart/form-data">
        <input type="hidden" name="server" id="s_name"><input type="hidden" name="p" id="p_val"><input type="hidden" name="a" id="a_val">
        <input type="text" name="u" placeholder="Player ID" required>
        <input type="text" name="z" placeholder="Zone ID">
        <input type="file" name="photo" required accept="image/*" style="border:none; margin:10px 0;">
        <button type="submit" class="buy-btn">CONFIRM & BUY</button>
    </form>
</div>

<div class="nav-bar">
    <div class="nav-btn" onclick="goHome()"><i class="fas fa-home"></i><br>Home</div>
    <div class="nav-btn" onclick="showHistory()"><i class="fas fa-history"></i><br>History</div>
    <a href="{{cs}}" class="nav-btn" target="_blank"><i class="fas fa-comment"></i><br>Contact</a>
</div>

<script>
const data = {{ games | tojson }};
const payInfo = {{ pay | tojson }};

function init() {
    document.getElementById('game-list').innerHTML = data.map(g => `
        <div class="game-card" onclick="selectGame('${g.name}')">
            <img src="${g.img}"><h4>${g.name}</h4>
        </div>`).join('');
    setPay('KPay');
}

function selectGame(name) {
    hideAll(); document.getElementById('order-sec').style.display='block';
    document.getElementById('game-title').innerText=name;
    document.getElementById('s_name').value=name;
    const g=data.find(i=>i.name===name);
    const cats=Object.keys(g.cats);
    document.getElementById('tabs').innerHTML=cats.map((c,i)=>`<div class="cat-tab ${i===0?'active':''}" onclick="renderPkgs('${name}','${c}',this)">${c}</div>`).join('');
    renderPkgs(name,cats[0]);
}

function renderPkgs(sN,c,el) {
    if(el){document.querySelectorAll('.cat-tab').forEach(t=>t.classList.remove('active')); el.classList.add('active');}
    const g=data.find(i=>i.name===sN);
    document.getElementById('pkg-list').innerHTML=g.cats[c].map(p=>`
        <div class="pkg-card" onclick="selPkg(this,'${p.d}','${p.p}')">
            <span>${p.d}</span><br><b>${p.p} Ks</b>
        </div>`).join('');
}

function selPkg(el,d,p){
    document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected')); 
    el.classList.add('selected');
    document.getElementById('p_val').value=d; document.getElementById('a_val').value=p;
}

function setPay(type, el) {
    if(el){document.querySelectorAll('.pay-btn-icon').forEach(b=>b.classList.remove('active')); el.classList.add('active');}
    document.getElementById('pay-num').innerText = payInfo[type].Number;
    document.getElementById('pay-name').innerText = payInfo[type].Name;
}

function showHistory() {
    hideAll(); document.getElementById('history-sec').style.display='block';
    fetch('/api/history').then(res=>res.json()).then(orders=>{
        document.getElementById('history-list').innerHTML = orders.length ? orders.map(o=>`
            <div style="background:#1e293b; border-radius:12px; padding:15px; margin-bottom:12px; border-left:4px solid #fbbf24;">
                <small style="color:#94a3b8;">${o.date}</small>
                <div style="font-weight:bold; margin:3px 0;">${o.pkg}</div>
                <div style="font-size:13px;">ID: ${o.uid} | ${o.price} Ks</div>
                <div style="color:#fbbf24; font-size:12px; margin-top:5px;">Status: Pending ⏳</div>
            </div>`).join('') : '<p style="text-align:center; color:#94a3b8;">No orders yet.</p>';
    });
}

function goHome(){ hideAll(); document.getElementById('home-sec').style.display='block'; }
function hideAll(){ ['home-sec','history-sec','order-sec'].forEach(id=>document.getElementById(id).style.display='none'); }
init();
</script></body></html>
'''

# --- ROUTES ---
@app.route('/')
def index(): return render_template_string(HTML_CODE, games=GAMES_DATA, pay=PAY_DATA, cs=CS_LINK)

@app.route('/order', methods=['POST'])
def order():
    try:
        server = request.form.get('server')
        uid = request.form.get('u')
        zone = request.form.get('z') or "-"
        pkg = request.form.get('p')
        amt = request.form.get('a')
        photo = request.files.get('photo')
        
        orders_col.insert_one({
            "uid": uid, "pkg": pkg, "price": amt,
            "date": datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%Y-%m-%d %H:%M"),
            "status": "pending"
        })

        msg = f"🔔 *New Order!*\nServer: {server}\nID: `{uid} ({zone})`\nPkg: {pkg}\nAmt: {amt} Ks"
        if photo:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                          data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}, 
                          files={'photo': (photo.filename, photo.read(), photo.content_type)})
    except Exception as e: print(f"Error: {e}")
    return "<html><body style='background:#0f172a;color:white;text-align:center;padding-top:100px;'><h2>Order Success! ✅</h2><script>setTimeout(()=>location.href='/', 2000);</script></body></html>"

@app.route('/api/history')
def get_history():
    try:
        history = list(orders_col.find().sort("_id", -1).limit(10))
        for h in history: h["_id"] = str(h["_id"])
        return jsonify(history)
    except: return jsonify([])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


