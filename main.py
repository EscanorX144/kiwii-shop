import os, requests
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "KIWII_ULTIMATE_SECRET"

# --- 🛰️ MONGODB CONNECTION (Standard Format to fix DNS Issue) ---
# srv format မဟုတ်တဲ့အတွက် Render ပေါ်မှာ DNS error မတက်တော့ပါဘူး
MONGO_URI = "mongodb://EscanorX:Conti144@cluster0-shard-00-00.m2tomm.mongodb.net:27017,cluster0-shard-00-01.m2tomm.mongodb.net:27017,cluster0-shard-00-02.m2tomm.mongodb.net:27017/?ssl=true&replicaSet=atlas-m2tomm-shard-0&authSource=admin&retryWrites=true&w=majority"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
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

# --- 💎 GAME DATA (Full List) ---
GAMES_DATA = [
    {
        "name": "Normal Server (🇲🇲)",
        "img": "https://flagcdn.com/w160/mm.png",
        "cats": {
            "Normal Dia": [{"d": "11 💎", "p": "700"}, {"d": "56 💎", "p": "3500"}, {"d": "112 💎", "p": "7000"}, {"d": "172 💎", "p": "9450"}, {"d": "257 💎", "p": "13800"}, {"d": "514 💎", "p": "27650"}, {"d": "1049 💎", "p": "56000"}, {"d": "9288 💎", "p": "475000"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X 💎", "p": str(5900 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "3050"}, {"d": "500+500 💎", "p": "29950"}],
            "Bundle": [{"d": "Monthly epic bundle 💎", "p": "15350"}, {"d": "Twilight pass 💎", "p": "31500"}]
        }
    },
    {
        "name": "Malaysia (🇲🇾)",
        "img": "https://flagcdn.com/w160/my.png",
        "cats": {
            "Dia": [{"d": "14 💎", "p": "1050"}, {"d": "140 💎", "p": "10100"}, {"d": "716 💎", "p": "50200"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X 💎", "p": str(8400 * i)} for i in range(1, 11)]
        }
    },
    {
        "name": "Singapore (🇸🇬)", "img": "https://flagcdn.com/w160/sg.png",
        "cats": {"Dia": [{"d": "14 💎", "p": "1050"}, {"d": "716 💎", "p": "50200"}], "Weekly Pass": [{"d": "Weekly 1X", "p": "8400"}]}
    },
    {
        "name": "Philippines (🇵🇭)", "img": "https://flagcdn.com/w160/ph.png",
        "cats": {"Dia": [{"d": "11 💎", "p": "750"}, {"d": "570 💎", "p": "36000"}], "Weekly Pass": [{"d": "Weekly 1X", "p": "6500"}]}
    },
    {
        "name": "Indonesia (🇮🇩)", "img": "https://flagcdn.com/w160/id.png",
        "cats": {"Dia": [{"d": "5 💎", "p": "450"}, {"d": "170 💎", "p": "11700"}], "Weekly Pass": [{"d": "Weekly 1X", "p": "7500"}]}
    }
]

HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; margin:0; padding:15px; padding-bottom:80px; }
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    .game-card { 
        background: linear-gradient(rgba(30,41,59,0.8), rgba(30,41,59,0.9)), url('/static/hero.webp'); 
        background-size: cover; border-radius: 12px; padding: 25px 10px; text-align: center; border: 1px solid #334155;
    }
    .game-card img { width:50px; border-radius:50%; margin-bottom:10px; border:2px solid #fbbf24; }
    .cat-tab { padding:8px 15px; background:#1e293b; border-radius:8px; font-size:12px; cursor:pointer; border:1px solid #334155; white-space:nowrap; }
    .cat-tab.active { background:#fbbf24; color:black; font-weight:bold; }
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:10px; max-height: 350px; overflow-y:auto; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:12px; border-radius:10px; text-align:center; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    .pay-icon { width:45px; height:45px; border-radius:8px; cursor:pointer; border:2px solid transparent; }
    .pay-icon.active { border-color:#fbbf24; }
    input { width:100%; padding:12px; margin:5px 0; border-radius:8px; border:1px solid #334155; background:#0f172a; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:15px; background:#fbbf24; border:none; border-radius:10px; font-weight:bold; cursor:pointer; margin-top:10px; }
    .nav-bar { position:fixed; bottom:0; left:0; right:0; background:#1e293b; display:flex; padding:12px; border-top:1px solid #334155; }
    .nav-btn { flex:1; text-align:center; color:#94a3b8; font-size:11px; text-decoration:none; cursor:pointer; }
</style>
</head><body>
<div id="h-sec">
    <h1 style="text-align:center;color:#fbbf24;margin-bottom:20px;">KIWII SHOP</h1>
    <div class="game-grid" id="g-list"></div>
</div>
<div id="o-sec" style="display:none;">
    <button onclick="goH()" style="background:none;color:white;border:1px solid #334155;padding:6px 12px;border-radius:6px;">← Back</button>
    <h3 id="g-title" style="color:#fbbf24;"></h3>
    <div style="display:flex;gap:8px;overflow-x:auto;padding-bottom:10px;" id="tabs"></div>
    <div class="pkg-grid" id="p-list"></div>
    <div style="text-align:center;margin-top:15px;">
        <img src="/static/kpay.jpg" class="pay-icon active" onclick="setPay('KPay',this)">
        <img src="/static/wave.jpg" class="pay-icon" onclick="setPay('Wave',this)">
        <img src="/static/ayapay.jpg" class="pay-icon" onclick="setPay('AYAPay',this)">
    </div>
    <div style="background:#1e293b;padding:15px;border-radius:10px;margin:10px 0;text-align:center;border:1px solid #fbbf24;">
        <b id="p-num" style="color:#fbbf24;font-size:18px;"></b><br><span id="p-name"></span>
    </div>
    <form action="/order" method="post" enctype="multipart/form-data">
        <input type="hidden" name="server" id="s_in"><input type="hidden" name="p" id="p_in"><input type="hidden" name="a" id="a_in">
        <input type="text" name="u" placeholder="Player ID" required>
        <input type="text" name="z" placeholder="Zone ID (Optional)">
        <input type="file" name="photo" required accept="image/*" style="border:none;">
        <button type="submit" class="buy-btn">PLACE ORDER</button>
    </form>
</div>
<div id="hist-sec" style="display:none;">
    <h3 style="color:#fbbf24;padding:10px;">Order History</h3>
    <div id="hist-list" style="padding:10px;"></div>
</div>
<div class="nav-bar">
    <div class="nav-btn" onclick="goH()"><i class="fas fa-home"></i><br>Home</div>
    <div class="nav-btn" onclick="showH()"><i class="fas fa-history"></i><br>History</div>
    <a href="{{cs}}" class="nav-btn" target="_blank"><i class="fas fa-headset"></i><br>CS</a>
</div>
<script>
const games = {{ games | tojson }};
const pay = {{ pay | tojson }};
function init() {
    document.getElementById('g-list').innerHTML = games.map(g => `
        <div class="game-card" onclick="selG('${g.name}')">
            <img src="${g.img}"><br><b>${g.name}</b>
        </div>`).join('');
    setPay('KPay');
}
function selG(n) {
    document.getElementById('h-sec').style.display='none';
    document.getElementById('hist-sec').style.display='none';
    document.getElementById('o-sec').style.display='block';
    document.getElementById('g-title').innerText=n;
    document.getElementById('s_in').value=n;
    const g=games.find(i=>i.name===n);
    const cs=Object.keys(g.cats);
    document.getElementById('tabs').innerHTML=cs.map((c,i)=>`<div class="cat-tab ${i===0?'active':''}" onclick="renderP('${n}','${c}',this)">${c}</div>`).join('');
    renderP(n,cs[0]);
}
function renderP(n,c,el) {
    if(el){document.querySelectorAll('.cat-tab').forEach(t=>t.classList.remove('active')); el.classList.add('active');}
    const g=games.find(i=>i.name===n);
    document.getElementById('p_list').innerHTML=g.cats[c].map(p=>`
        <div class="pkg-card" onclick="selP(this,'${p.d}','${p.p}')">
            <span>${p.d}</span><br><b>${p.p} Ks</b>
        </div>`).join('');
}
function selP(el,d,p){
    document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected'));
    el.classList.add('selected');
    document.getElementById('p_in').value=d; document.getElementById('a_in').value=p;
}
function setPay(t, el) {
    if(el){document.querySelectorAll('.pay-icon').forEach(i=>i.classList.remove('active')); el.classList.add('active');}
    document.getElementById('p-num').innerText = pay[t].Number;
    document.getElementById('p-name').innerText = pay[t].Name;
}
function showH() {
    document.getElementById('h-sec').style.display='none';
    document.getElementById('o-sec').style.display='none';
    document.getElementById('hist-sec').style.display='block';
    fetch('/api/history').then(r=>r.json()).then(data=>{
        document.getElementById('hist-list').innerHTML = data.map(o=>`
            <div style="background:#1e293b;padding:12px;border-radius:10px;margin-bottom:10px;border-left:4px solid #fbbf24;">
                <small>${o.date}</small><br><b>${o.pkg}</b> - ${o.price} Ks<br>ID: ${o.uid}
            </div>`).join('') || "No orders yet.";
    });
}
function goH(){ document.getElementById('o-sec').style.display='none'; document.getElementById('hist-sec').style.display='none'; document.getElementById('h-sec').style.display='block'; }
init();
</script></body></html>
'''

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
        
        # Save to DB
        orders_col.insert_one({
            "uid": uid, "pkg": pkg, "price": amt,
            "date": datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%Y-%m-%d %H:%M")
        })

        # Send to Telegram
        msg = f"🔔 *New Order!*\nServer: {server}\nID: `{uid} ({zone})`\nPkg: {pkg}\nAmt: {amt} Ks"
        if photo:
            photo.seek(0)
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                          data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}, 
                          files={'photo': (photo.filename, photo.read(), photo.content_type)})

        return "<html><body style='background:#0f172a;color:white;text-align:center;padding-top:100px;'><h2>Order Success! ✅</h2><script>setTimeout(()=>location.href='/', 2000);</script></body></html>"
    except Exception as e:
        return f"Error: {e}"

@app.route('/api/history')
def get_history():
    try:
        hist = list(orders_col.find().sort("_id", -1).limit(10))
        for h in hist: h["_id"] = str(h["_id"])
        return jsonify(hist)
    except: return jsonify([])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


