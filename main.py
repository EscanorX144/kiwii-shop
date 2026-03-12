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

# --- 💎 FULL GAMES DATA WITH ALL UPDATED PRICES ---
GAMES_DATA = [
    {
        "id": 1, "name": "Normal Server (🇲🇲)", "img": "https://flagcdn.com/w160/mm.png", 
        "cat_order": ["Normal Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], 
        "cats": {
            "Normal Dia": [{"d": "11 💎", "p": "700"}, {"d": "22 💎", "p": "1400"}, {"d": "33 💎", "p": "2100"}, {"d": "44 💎", "p": "2800"}, {"d": "56 💎", "p": "3500"}, {"d": "86 💎", "p": "4750"}, {"d": "112 💎", "p": "7000"}, {"d": "172 💎", "p": "9450"}, {"d": "257 💎", "p": "13800"}, {"d": "279 💎", "p": "15200"}, {"d": "343 💎", "p": "18600"}, {"d": "429 💎", "p": "23350"}, {"d": "514 💎", "p": "27650"}, {"d": "600 💎", "p": "32650"}, {"d": "706 💎", "p": "37450"}, {"d": "792 💎", "p": "42200"}, {"d": "878 💎", "p": "46850"}, {"d": "963 💎", "p": "51200"}, {"d": "1049 💎", "p": "56000"}, {"d": "1135 💎", "p": "60850"}, {"d": "1412 💎", "p": "74900"}, {"d": "2195 💎", "p": "114200"}, {"d": "3688 💎", "p": "190500"}, {"d": "5532 💎", "p": "287000"}, {"d": "7376 💎", "p": "381000"}, {"d": "9288 💎", "p": "475200"}],
            "Weekly Pass": [{"d": f"WP {i}X", "p": str(5900 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "3050"}, {"d": "150+150 💎", "p": "9100"}, {"d": "250+250 💎", "p": "14650"}, {"d": "500+500 💎", "p": "29950"}],
            "Bundle Pack": [{"d": "Weekly Elite", "p": "3050"}, {"d": "Monthly Bundle", "p": "15350"}, {"d": "Twilight Pass", "p": "31500"}]
        }
    },
    {
        "id": 2, "name": "Malaysia (🇲🇾) & Singapore (🇸🇬)", "img": "https://flagcdn.com/w160/my.png", 
        "cat_order": ["Direct Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], 
        "cats": {
            "Direct Dia": [{"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "56 💎", "p": "4350"}, {"d": "70 💎", "p": "5100"}, {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"}, {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"}, {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [{"d": f"WP {i}X", "p": str(8700 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+ 💎", "p": "4250"}, {"d": "150+ 💎", "p": "12200"}, {"d": "250+ 💎", "p": "20200"}, {"d": "500+ 💎", "p": "40600"}],
            "Bundle Pack": [{"d": "Weekly Elite Bundle", "p": "4250"}, {"d": "Monthly Epic Bundle", "p": "20000"}]
        }
    },
    {
        "id": 3, "name": "Indonesia (🇮🇩)", "img": "https://flagcdn.com/w160/id.png", 
        "cat_order": ["Indonesia Dia", "Weekly Pass", "Bundle Pack"], 
        "cats": {
            "Indonesia Dia": [{"d": "5 💎", "p": "450"}, {"d": "12 💎", "p": "950"}, {"d": "19 💎", "p": "1500"}, {"d": "28 💎", "p": "2200"}, {"d": "44 💎", "p": "3300"}, {"d": "59 💎", "p": "4300"}, {"d": "85 💎", "p": "5850"}, {"d": "170 💎", "p": "11700"}, {"d": "240 💎", "p": "16600"}, {"d": "296 💎", "p": "20500"}, {"d": "408 💎", "p": "28000"}, {"d": "568 💎", "p": "37500"}, {"d": "875 💎", "p": "58500"}, {"d": "2010 💎", "p": "123500"}, {"d": "4830 💎", "p": "299000"}],
            "Weekly Pass": [{"d": "WP 1X", "p": "7500"}],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "45000"}]
        }
    },
    {
        "id": 4, "name": "Russia (🇷🇺)", "img": "https://flagcdn.com/w160/ru.png", "cat_order": ["Russia Dia", "Weekly Pass"], 
        "cats": {
            "Russia Dia": [{"d": "35 💎", "p": "2750"}, {"d": "55 💎", "p": "4450"}, {"d": "165 💎", "p": "13000"}, {"d": "275 💎", "p": "22000"}, {"d": "565 💎", "p": "44500"}, {"d": "1155 💎", "p": "88000"}, {"d": "1765 💎", "p": "182000"}, {"d": "2975 💎", "p": "220000"}, {"d": "6000 💎", "p": "435000"}],
            "Weekly Pass": [{"d": "WP 1X", "p": "8600"}]
        }
    },
    {
        "id": 5, "name": "Philippines (🇵🇭)", "img": "https://flagcdn.com/w160/ph.png", "cat_order": ["Philippines Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], 
        "cats": {
            "Philippines Dia": [{"d": "11 💎", "p": "750"}, {"d": "22 💎", "p": "1500"}, {"d": "56 💎", "p": "3500"}, {"d": "112 💎", "p": "7000"}, {"d": "223 💎", "p": "14000"}, {"d": "336 💎", "p": "21300"}, {"d": "570 💎", "p": "36000"}, {"d": "1163 💎", "p": "70500"}, {"d": "2398 💎", "p": "140000"}, {"d": "6042 💎", "p": "350000"}],
            "Weekly Pass": [{"d": "WP 1X", "p": "6500"}],
            "2X Dia": [{"d": "50+50 💎", "p": "3600"}, {"d": "150+150 💎", "p": "10500"}, {"d": "250+250 💎", "p": "17200"}, {"d": "500+500 💎", "p": "34500"}],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "35500"}]
        }
    }
]

HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; margin:0; padding-bottom:80px; }
    .container { max-width:500px; margin:auto; }
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; padding: 15px; }
    .game-card { background:#1e293b; border-radius:15px; padding:20px; text-align:center; border:1px solid #334155; cursor:pointer; transition: 0.3s; }
    .game-card:active { transform: scale(0.95); }
    .cat-tab { padding:10px 18px; background:#1e293b; border-radius:10px; font-size:12px; cursor:pointer; border:1px solid #334155; white-space:nowrap; }
    .cat-tab.active { background:#fbbf24; color:black; font-weight:bold; border-color:#fbbf24; }
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:15px 0; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; cursor:pointer; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:10px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; outline:none; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; color:black; cursor:pointer; font-size:16px; }
    .nav-bar { position:fixed; bottom:0; left:0; right:0; background:#1e293b; display:flex; padding:12px; border-top:1px solid #334155; z-index:100; }
    .pay-box { background:#1e293b; border:2px solid #fbbf24; padding:15px; border-radius:12px; text-align:center; margin-bottom:15px; }
    .pay-icons { display:flex; justify-content:center; gap:10px; margin-bottom:10px; }
    .pay-icons img { height:35px; border-radius:5px; }
    .hist-item { background:#1e293b; padding:12px; border-radius:10px; margin-bottom:10px; border-left:4px solid #fbbf24; }
</style>
</head><body>
<div class="container">
    <div id="h-sec">
        <h1 style="text-align:center;color:#fbbf24;margin-top:20px;">KIWII GAME STORE</h1>
        <div class="game-grid" id="g-list"></div>
    </div>

    <div id="o-sec" style="display:none; padding:15px;">
        <button onclick="goH()" style="background:none;color:white;border:1px solid #334155;padding:8px;border-radius:8px;cursor:pointer;">← Back</button>
        <h2 id="g-title" style="color:#fbbf24; margin:15px 0;"></h2>
        <div style="display:flex;gap:8px;overflow-x:auto;padding-bottom:10px;" id="tabs"></div>
        <div class="pkg-grid" id="p-list"></div>
        
        <div class="pay-box">
            <div class="pay-icons">
                <img src="https://mmit.com.mm/wp-content/uploads/2021/04/kbzpay.png" alt="KPay">
                <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR611Dms-6X2P7P7uX9uE4u89v0_m00_v1vOw&s" alt="Wave">
                <img src="https://play-lh.googleusercontent.com/vH3I049n9S1rN4yW4V6m_G1l6_8z3iM-M-_WnL9rL0T-u2Z0V9yC7i4y1v_u2Q0R1A=w240-h480-rw" alt="AYA">
            </div>
            <b id="p-num" style="color:#fbbf24;font-size:22px;">09775394979</b> 
            <i class="fa-regular fa-copy" onclick="copyNum()" style="cursor:pointer;margin-left:5px;"></i><br>
            <b style="color:white; font-size:18px;">Name: Thansin Kyaw</b><br>
            <small style="color:#94a3b8;">Note: Payment သာရေးပါ</small>
        </div>

        <form id="orderForm" onsubmit="confirmOrder(event)">
            <input type="text" id="tg_u" placeholder="Telegram Username (History ပြန်ကြည့်ရန်)" required>
            <input type="tel" id="uid" placeholder="Game ID (e.g. 12345678)" required>
            <input type="tel" id="zid" placeholder="Zone ID (e.g. 1234)" required>
            <p style="font-size:12px;color:#94a3b8;margin:5px 0;">ငွေလွှဲပြေစာ (Screenshot) တင်ပေးပါ</p>
            <input type="file" id="photo" required accept="image/*">
            <button type="submit" id="submitBtn" class="buy-btn">PLACE ORDER</button>
        </form>
    </div>

    <div id="hist-sec" style="display:none; padding:15px;">
        <h3 style="color:#fbbf24;">Order History</h3>
        <div style="display:flex; gap:5px;">
            <input type="text" id="h_search" placeholder="Telegram Username ရိုက်ပါ">
            <button onclick="loadH()" class="buy-btn" style="width:100px; padding:0;">Search</button>
        </div>
        <div id="hist-list" style="margin-top:20px;"></div>
    </div>
</div>

<div class="nav-bar">
    <div onclick="goH()" style="flex:1; text-align:center; cursor:pointer;"><i class="fas fa-home"></i><br><small>Home</small></div>
    <div onclick="showH()" style="flex:1; text-align:center; cursor:pointer;"><i class="fas fa-history"></i><br><small>History</small></div>
    <div onclick="window.open('https://t.me/thansinkyaw144')" style="flex:1; text-align:center; cursor:pointer; color:#fbbf24;"><i class="fas fa-headset"></i><br><small>CS</small></div>
</div>

<script>
let sel_srv='', sel_pkg='', sel_prc='';
const games = {{ games | tojson }};

function init() { document.getElementById('g-list').innerHTML = games.map(g => `<div class="game-card" onclick="selG(${g.id})"><img src="${g.img}" width="45"><br><b style="font-size:14px;">${g.name}</b></div>`).join(''); }

function selG(id) {
    const g = games.find(i => i.id === id); sel_srv = g.name;
    document.getElementById('h-sec').style.display='none'; document.getElementById('o-sec').style.display='block';
    document.getElementById('g-title').innerText = g.name;
    document.getElementById('tabs').innerHTML = g.cat_order.map((c, i) => `<div class="cat-tab ${i===0?'active':''}" onclick="renderP(${id}, '${c}', this)">${c}</div>`).join('');
    renderP(id, g.cat_order[0]);
}

function renderP(id, cat, el) {
    if(el){document.querySelectorAll('.cat-tab').forEach(t=>t.classList.remove('active')); el.classList.add('active');}
    const pkgs = games.find(i=>i.id===id).cats[cat];
    document.getElementById('p-list').innerHTML = pkgs.map(p=>`<div class="pkg-card" onclick="selP(this, '${p.d}', '${p.p}')"><span>${p.d}</span><br><b>${p.p} Ks</b></div>`).join('');
    sel_pkg = '';
}

function selP(el, d, p) { document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected')); el.classList.add('selected'); sel_pkg=d; sel_prc=p; }

function confirmOrder(e) {
    e.preventDefault();
    if(!sel_pkg) return alert("ကျေးဇူးပြု၍ Package အရင်ရွေးပါ!");
    const id = document.getElementById('uid').value;
    const zone = document.getElementById('zid').value;
    const ok = confirm(`📢 Order အတည်ပြုပါ\\n\\nServer: ${sel_srv}\\nGame ID: ${id} (${zone})\\nPackage: ${sel_pkg}\\nPrice: ${sel_prc} Ks\\n\\nအချက်အလက်များ အကုန်မှန်ကန်ပါသလား?`);
    if(ok) submitOrder();
}

async function submitOrder() {
    const btn = document.getElementById('submitBtn'); btn.disabled = true; btn.innerText = "Processing...";
    const formData = new FormData(document.getElementById('orderForm'));
    formData.append('server', sel_srv); formData.append('p', sel_pkg); formData.append('a', sel_prc);

    try {
        const r = await fetch('/order', { method: 'POST', body: formData });
        if(await r.text() === "Success") { alert("Order အောင်မြင်ပါသည်! ✅"); location.reload(); }
        else { alert("Error! ကျေးဇူးပြု၍ ပြန်ကြိုးစားပါ"); btn.disabled = false; btn.innerText = "PLACE ORDER"; }
    } catch { alert("Network Error!"); btn.disabled = false; }
}

function goH() { document.getElementById('o-sec').style.display='none'; document.getElementById('hist-sec').style.display='none'; document.getElementById('h-sec').style.display='block'; }
function showH() { document.getElementById('h-sec').style.display='none'; document.getElementById('o-sec').style.display='none'; document.getElementById('hist-sec').style.display='block'; }

async function loadH() {
    const u = document.getElementById('h_search').value;
    if(!u) return alert("Username ရိုက်ထည့်ပါ");
    document.getElementById('hist-list').innerHTML = "Loading...";
    const r = await fetch('/api/history?user=' + encodeURIComponent(u));
    const data = await r.json();
    document.getElementById('hist-list').innerHTML = data.map(o => `
        <div class="hist-item">
            <b>${o.pkg}</b> (${o.price} Ks)<br>
            <small>${o.date}</small> | <span style="color:#fbbf24; font-weight:bold;">${o.status}</span>
        </div>
    `).join('') || "No history found for this user.";
}

function copyNum() { navigator.clipboard.writeText("09775394979").then(()=>alert("ဖုန်းနံပါတ် ကူးယူပြီးပါပြီ!")); }
init();
</script></body></html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_CODE, games=GAMES_DATA)

@app.route('/order', methods=['POST'])
def order():
    try:
        user = request.form.get('tg_u')
        server = request.form.get('server')
        uid = request.form.get('uid')
        zone = request.form.get('zid')
        pkg = request.form.get('p')
        amt = request.form.get('a')
        photo = request.files.get('photo')
        
        oid = str(orders_col.insert_one({
            "customer": user, "uid": uid, "zone": zone, "pkg": pkg, "price": amt, "status": "Pending",
            "date": datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%Y-%m-%d %H:%M")
        }).inserted_id)

        msg = f"🔔 *New Order!*\n👤 User: `{user}`\n🆔 ID: `{uid}` ({zone})\n🌍 Server: {server}\n💎 Pkg: {pkg}\n💰 Amt: {amt} Ks\n\n✅ [DONE]({request.host_url}admin/upd/{oid}/Completed) | ❌ [REJECT]({request.host_url}admin/upd/{oid}/Rejected)"
        
        photo.seek(0)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}, 
                      files={'photo': photo})
        return "Success"
    except Exception as e:
        print(f"Error: {e}")
        return "Error"

@app.route('/api/history')
def get_history():
    u = request.args.get('user')
    hist = list(orders_col.find({"customer": u}).sort("_id", -1))
    for h in hist: h["_id"] = str(h["_id"])
    return jsonify(hist)

@app.route('/admin/upd/<oid>/<status>')
def update_status(oid, status):
    orders_col.update_one({"_id": ObjectId(oid)}, {"$set": {"status": status}})
    return f"Order Status updated to {status}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    
