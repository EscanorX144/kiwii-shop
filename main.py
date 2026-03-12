import os, requests
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "KIWII_ULTIMATE_SECRET"

MONGO_URI = "mongodb+srv://EscanorX:Conti144@cluster0.m2mtomm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=30000)
db = client['kiwii_game_shop']
orders_col = db['orders']

# --- ⚙️ CONFIGURATION ---
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3Ygej3nAwOODsNj4ujVvk"
CHAT_ID = "7089720301"
CS_LINK = "https://t.me/Bby_kiwii7"

PAY_DATA = {
    "KPay": {"Number": "09775394979", "Name": "Thansin Kyaw", "img": "/static/kpay.jpg"},
    "Wave": {"Number": "09775394979", "Name": "Thansin Kyaw", "img": "/static/wave.jpg"},
    "AYAPay": {"Number": "09775394979", "Name": "Thansin Kyaw", "img": "/static/ayapay.jpg"},
    "Note": "Note - Payment သာရေးပါ"
}

GAMES_DATA = [
    {
        "id": 1, "name": "Normal Server (🇲🇲)", "img": "https://flagcdn.com/w160/mm.png",
        "cat_order": ["Normal Dia", "Weekly Pass", "2X Dia", "Bundle Pack"],
        "cats": {
            "Normal Dia": [
                {"d": "11 💎", "p": "700"}, {"d": "56 💎", "p": "3500"}, {"d": "112 💎", "p": "7000"}, 
                {"d": "223 💎", "p": "13800"}, {"d": "336 💎", "p": "19500"}, {"d": "514 💎", "p": "27650"}, 
                {"d": "706 💎", "p": "37500"}, {"d": "1049 💎", "p": "56000"}, {"d": "2195 💎", "p": "112000"},
                {"d": "3688 💎", "p": "185000"}, {"d": "5532 💎", "p": "278000"}, {"d": "9288 💎", "p": "465000"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(5900 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "3050"}, {"d": "150+150 💎", "p": "9100"}, {"d": "250+250 💎", "p": "14650"}, {"d": "500+500 💎", "p": "29950"}],
            "Bundle Pack": [{"d": "Weekly Elite", "p": "3050"}, {"d": "Monthly Bundle", "p": "15350"}, {"d": "Twilight Pass", "p": "31500"}]
        }
    },
    {
        "id": 2, "name": "Malaysia (🇲🇾)", "img": "https://flagcdn.com/w160/my.png",
        "cat_order": ["Malaysia Dia", "Weekly Pass", "2X Dia", "Bundle Pack"],
        "cats": {
            "Malaysia Dia": [
                {"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "56 💎", "p": "4350"}, {"d": "70 💎", "p": "5100"},
                {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"},
                {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"},
                {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"},
                {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8700 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+ 💎", "p": "4250"}, {"d": "150+ 💎", "p": "12200"}, {"d": "250+ 💎", "p": "20200"}, {"d": "500+ 💎", "p": "40600"}],
            "Bundle Pack": [{"d": "Weekly Elite Bundle", "p": "4250"}, {"d": "Monthly Epic Bundle", "p": "20000"}]
        }
    },
    {
        "id": 3, "name": "Singapore (🇸🇬)", "img": "https://flagcdn.com/w160/sg.png",
        "cat_order": ["Singapore Dia", "Weekly Pass", "2X Dia", "Bundle Pack"],
        "cats": {
            "Singapore Dia": [
                {"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "56 💎", "p": "4350"}, {"d": "70 💎", "p": "5100"},
                {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"},
                {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"},
                {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"},
                {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8700 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+ 💎", "p": "4250"}, {"d": "150+ 💎", "p": "12200"}, {"d": "250+ 💎", "p": "20200"}, {"d": "500+ 💎", "p": "40600"}],
            "Bundle Pack": [{"d": "Weekly Elite Bundle", "p": "4250"}, {"d": "Monthly Epic Bundle", "p": "20000"}]
        }
    },
    {
        "id": 4, "name": "Philippines (🇵🇭)", "img": "https://flagcdn.com/w160/ph.png",
        "cat_order": ["Philippines Dia", "Weekly Pass", "2X Dia", "Bundle Pack"],
        "cats": {
            "Philippines Dia": [
                {"d": "11 💎", "p": "750"}, {"d": "22 💎", "p": "1500"}, {"d": "56 💎", "p": "3500"}, {"d": "112 💎", "p": "7000"},
                {"d": "223 💎", "p": "14000"}, {"d": "336 💎", "p": "21300"}, {"d": "570 💎", "p": "36000"}, {"d": "1163 💎", "p": "70500"},
                {"d": "2398 💎", "p": "140000"}, {"d": "6042 💎", "p": "350000"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(6500 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "3600"}, {"d": "150+150 💎", "p": "10500"}, {"d": "250+250 💎", "p": "17200"}, {"d": "500+500 💎", "p": "34500"}],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "35500"}]
        }
    },
    {
        "id": 5, "name": "Indonesia (🇮🇩)", "img": "https://flagcdn.com/w160/id.png",
        "cat_order": ["Indonesia Dia", "Weekly Pass", "Bundle Pack"],
        "cats": {
            "Indonesia Dia": [
                {"d": "5 💎", "p": "450"}, {"d": "12 💎", "p": "950"}, {"d": "19 💎", "p": "1500"}, {"d": "28 💎", "p": "2200"},
                {"d": "44 💎", "p": "3300"}, {"d": "59 💎", "p": "4300"}, {"d": "85 💎", "p": "5850"}, {"d": "170 💎", "p": "11700"},
                {"d": "240 💎", "p": "16600"}, {"d": "296 💎", "p": "20500"}, {"d": "408 💎", "p": "28000"}, {"d": "568 💎", "p": "37500"},
                {"d": "875 💎", "p": "58500"}, {"d": "2010 💎", "p": "123500"}, {"d": "4830 💎", "p": "299000"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(7500 * i)} for i in range(1, 11)],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "45000"}]
        }
    },
    {
        "id": 6, "name": "Russia (🇷🇺)", "img": "https://flagcdn.com/w160/ru.png",
        "cat_order": ["Russia Dia", "Weekly Pass"],
        "cats": {
            "Russia Dia": [
                {"d": "35 💎", "p": "2750"}, {"d": "55 💎", "p": "4450"}, {"d": "165 💎", "p": "13000"}, {"d": "275 💎", "p": "22000"},
                {"d": "565 💎", "p": "44500"}, {"d": "1155 💎", "p": "88000"}, {"d": "1765 💎", "p": "182000"}, {"d": "2975 💎", "p": "220000"},
                {"d": "6000 💎", "p": "435000"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8600 * i)} for i in range(1, 11)]
        }
    }
]

HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; margin:0; padding:15px; padding-bottom:80px; }
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    .game-card { background: #1e293b; border-radius: 12px; padding: 25px 10px; text-align: center; border: 1px solid #334155; }
    .game-card img { width:55px; border-radius:8px; margin-bottom:10px; }
    .cat-tabs-container { display:flex; gap:8px; overflow-x:auto; padding-bottom:12px; margin-top:10px; scrollbar-width: none; }
    .cat-tab { padding:10px 18px; background:#1e293b; border-radius:10px; font-size:12px; cursor:pointer; border:1px solid #334155; white-space:nowrap; color:#94a3b8; }
    .cat-tab.active { background:#fbbf24; color:black; font-weight:bold; border-color:#fbbf24; }
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    .pay-icons { display:flex; justify-content:center; gap:15px; margin:25px 0; }
    .pay-icon { width:55px; height:55px; border-radius:12px; cursor:pointer; border:2px solid transparent; }
    .pay-icon.active { border-color:#fbbf24; box-shadow: 0 0 10px #fbbf24; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:10px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; outline:none; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; cursor:pointer; margin-top:15px; font-size:16px; color:black; }
    .nav-bar { position:fixed; bottom:0; left:0; right:0; background:#1e293b; display:flex; padding:12px; border-top:1px solid #334155; }
    .nav-btn { flex:1; text-align:center; color:#94a3b8; font-size:11px; text-decoration:none; cursor:pointer; }
    .payment-box { background:#1e293b; padding:18px; border-radius:12px; border:1px solid #fbbf24; margin:20px 0; text-align:center; }
    .note-text { color:#ef4444; background:rgba(239,68,68,0.1); padding:10px; border-radius:8px; border:1px solid #ef4444; margin-top:12px; display:block; font-size:14px; }
</style>
</head><body>
<div id="h-sec">
    <h1 style="text-align:center;color:#fbbf24;font-size:24px;margin-bottom:25px;">KIWII GAME SHOP</h1>
    <div class="game-grid" id="g-list"></div>
</div>

<div id="o-sec" style="display:none;">
    <button onclick="goH()" style="background:none;color:white;border:1px solid #334155;padding:8px 16px;border-radius:8px;cursor:pointer;">← Back</button>
    <h2 id="g-title" style="color:#fbbf24;margin:15px 0;"></h2>
    <div class="cat-tabs-container" id="tabs"></div>
    <div class="pkg-grid" id="p-list"></div>
    
    <div class="pay-icons">
        <img src="/static/kpay.jpg" class="pay-icon active" id="icon-KPay" onclick="setPay('KPay')">
        <img src="/static/ayapay.jpg" class="pay-icon" id="icon-AYAPay" onclick="setPay('AYAPay')">
        <img src="/static/wave.jpg" class="pay-icon" id="icon-Wave" onclick="setPay('Wave')">
    </div>

    <div class="payment-box">
        <b id="p-num" style="color:#fbbf24;font-size:24px;letter-spacing:1px;"></b><br>
        <span id="p-name" style="font-size:16px;"></span>
        <span class="note-text">{{ pay.Note }}</span>
    </div>

    <form action="/order" method="post" enctype="multipart/form-data">
        <input type="hidden" name="server" id="s_in"><input type="hidden" name="p" id="p_in"><input type="hidden" name="a" id="a_in">
        <input type="text" name="u" placeholder="Player ID" required>
        <input type="text" name="z" placeholder="Zone ID (Optional)">
        <div style="margin:10px 0; font-size:13px; color:#94a3b8;">Payment Screenshot:</div>
        <input type="file" name="photo" required accept="image/*" style="border:none; padding:5px 0;">
        <button type="submit" class="buy-btn">PLACE ORDER</button>
    </form>
</div>

<div id="hist-sec" style="display:none; padding:15px;">
    <h3 style="color:#fbbf24;">Recent Orders</h3>
    <div id="hist-list"></div>
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
        <div class="game-card" onclick="selG(${g.id})">
            <img src="${g.img}"><br><b>${g.name}</b>
        </div>`).join('');
    setPay('KPay');
}

function selG(id) {
    const g = games.find(i => i.id === id);
    document.getElementById('h-sec').style.display='none';
    document.getElementById('hist-sec').style.display='none';
    document.getElementById('o-sec').style.display='block';
    document.getElementById('g-title').innerText = g.name;
    document.getElementById('s_in').value = g.name;
    
    const cats = g.cat_order;
    document.getElementById('tabs').innerHTML = cats.map((c, i) => `
        <div class="cat-tab ${i===0?'active':''}" onclick="renderP(${id}, '${c}', this)">${c}</div>
    `).join('');
    renderP(id, cats[0]);
    window.scrollTo(0,0);
}

function renderP(id, catName, el) {
    if(el) {
        document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
        el.classList.add('active');
    }
    const g = games.find(i => i.id === id);
    const pkgs = g.cats[catName];
    document.getElementById('p-list').innerHTML = pkgs.map(p => `
        <div class="pkg-card" onclick="selP(this, '${p.d}', '${p.p}')">
            <span style="font-size:14px;">${p.d}</span><br><b style="color:#fbbf24;">${p.p} Ks</b>
        </div>`).join('');
}

function selP(el, d, p) {
    document.querySelectorAll('.pkg-card').forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');
    document.getElementById('p_in').value = d;
    document.getElementById('a_in').value = p;
}

function setPay(type) {
    document.querySelectorAll('.pay-icon').forEach(i => i.classList.remove('active'));
    document.getElementById('icon-' + type).classList.add('active');
    document.getElementById('p-num').innerText = pay[type].Number;
    document.getElementById('p-name').innerText = pay[type].Name;
}

function showH() {
    document.getElementById('h-sec').style.display='none';
    document.getElementById('o-sec').style.display='none';
    document.getElementById('hist-sec').style.display='block';
    fetch('/api/history').then(r=>r.json()).then(data=>{
        document.getElementById('hist-list').innerHTML = data.map(o=>`
            <div style="background:#1e293b;padding:15px;border-radius:10px;margin-bottom:10px;border-left:4px solid #fbbf24;">
                <small style="color:#94a3b8;">${o.date}</small><br>
                <b>${o.pkg}</b><br>
                <span style="color:#fbbf24;">${o.price} Ks</span> | ID: ${o.uid}
            </div>`).join('') || "No orders found.";
    });
}

function goH() {
    document.getElementById('o-sec').style.display='none';
    document.getElementById('hist-sec').style.display='none';
    document.getElementById('h-sec').style.display='block';
}

init();
</script>
</body></html>
'''

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template_string(HTML_CODE, games=GAMES_DATA, pay=PAY_DATA, cs=CS_LINK)

@app.route('/order', methods=['POST'])
def order():
    try:
        server = request.form.get('server')
        uid = request.form.get('u')
        zone = request.form.get('z') or "-"
        pkg = request.form.get('p')
        amt = request.form.get('a')
        photo = request.files.get('photo')
        
        # MongoDB Insert
        orders_col.insert_one({
            "uid": uid, "pkg": pkg, "price": amt,
            "date": datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%Y-%m-%d %H:%M")
        })

        # Telegram Notification
        msg = f"🔔 *New Order!*\nServer: {server}\nID: `{uid} ({zone})`\nPkg: {pkg}\nAmt: {amt} Ks"
        if photo:
            photo.seek(0)
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                          data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}, 
                          files={'photo': (photo.filename, photo.read(), photo.content_type)})

        return "<html><body style='background:#0f172a;color:white;text-align:center;padding-top:100px;'><h2>Order Success! ✅</h2><p>Wait for 5-10 mins.</p><script>setTimeout(()=>location.href='/', 3000);</script></body></html>"
    except Exception as e:
        return f"Error: {e}"

@app.route('/api/history')
def get_history():
    try:
        hist = list(orders_col.find().sort("_id", -1).limit(10))
        for h in hist: h["_id"] = str(h["_id"])
        return jsonify(hist)
    except:
        return jsonify([])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


