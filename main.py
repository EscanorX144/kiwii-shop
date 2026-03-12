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
users_col = db['users'] 

# Telegram Config (ဒီနေရာမှာ အပေါ်ဆုံးက ကြေညာထားမှ အောက်က function တွေက သိမှာပါ)
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
CHAT_ID = "7089720301"

# --- 💎 DIAMOND LISTS (လုံးဝမဖျက်ဘဲ အပြည့်အစုံ ပြန်ထည့်ထားသည်) ---
GAMES_DATA = [
    {
        "id": 1, "name": "Normal Server (🇲🇲)", "img": "https://flagcdn.com/w160/mm.png", 
        "cat_order": ["Normal Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], 
        "cats": {
            "Normal Dia": [{"d": "11 💎", "p": "700"}, {"d": "22 💎", "p": "1400"}, {"d": "33 💎", "p": "2100"}, {"d": "44 💎", "p": "2800"}, {"d": "56 💎", "p": "3500"}, {"d": "86 💎", "p": "4750"}, {"d": "112 💎", "p": "7000"}, {"d": "172 💎", "p": "9450"}, {"d": "257 💎", "p": "13800"}, {"d": "343 💎", "p": "18600"}, {"d": "429 💎", "p": "23350"}, {"d": "514 💎", "p": "27650"}, {"d": "600 💎", "p": "32650"}, {"d": "706 💎", "p": "37450"}, {"d": "1412 💎", "p": "74900"}, {"d": "2195 💎", "p": "114200"}, {"d": "9288 💎", "p": "475200"}],
            "Weekly Pass": [{"d": "WP 1X", "p": "5900"}, {"d": "WP 2X", "p": "11800"}, {"d": "WP 3X", "p": "17700"}, {"d": "WP 4X", "p": "23600"}, {"d": "WP 5X", "p": "29500"}, {"d": "WP 6X", "p": "35400"}, {"d": "WP 7X", "p": "41300"}, {"d": "WP 8X", "p": "47200"}, {"d": "WP 9X", "p": "53100"}, {"d": "WP 10X", "p": "59000"}],
            "2X Dia": [{"d": "50+50 💎", "p": "3050"}, {"d": "150+150 💎", "p": "9100"}, {"d": "250+250 💎", "p": "14650"}, {"d": "500+500 💎", "p": "29950"}],
            "Bundle Pack": [{"d": "Weekly Elite", "p": "3050"}, {"d": "Monthly Bundle", "p": "15350"}, {"d": "Twilight Pass", "p": "31500"}]
        }
    },
    {
        "id": 2, "name": "Malaysia (🇲🇾)", "img": "https://flagcdn.com/w160/my.png", 
        "cat_order": ["Malaysia Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], 
        "cats": {
            "Malaysia Dia": [{"d": "14 💎", "p": "1100"}, {"d": "56 💎", "p": "4350"}, {"d": "140 💎", "p": "10200"}, {"d": "284 💎", "p": "20200"}, {"d": "583 💎", "p": "41200"}, {"d": "1145 💎", "p": "80500"}, {"d": "2976 💎", "p": "201000"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [{"d": "WP 1X", "p": "8700"}, {"d": "WP 2X", "p": "17400"}, {"d": "WP 3X", "p": "26100"}, {"d": "WP 4X", "p": "34800"}, {"d": "WP 5X", "p": "43500"}, {"d": "WP 6X", "p": "52200"}, {"d": "WP 7X", "p": "60900"}, {"d": "WP 8X", "p": "69600"}, {"d": "WP 9X", "p": "78300"}, {"d": "WP 10X", "p": "87000"}],
            "2X Dia": [{"d": "50+ 💎", "p": "4250"}, {"d": "150+ 💎", "p": "12200"}, {"d": "500+ 💎", "p": "40600"}],
            "Bundle Pack": [{"d": "Weekly Elite Bundle", "p": "4250"}, {"d": "Monthly Epic Bundle", "p": "20000"}]
        }
    },
    {
        "id": 6, "name": "Singapore (🇸🇬)", "img": "https://flagcdn.com/w160/sg.png", 
        "cat_order": ["Singapore Dia", "Weekly Pass", "2X Dia"], 
        "cats": {
            "Singapore Dia": [{"d": "14 💎", "p": "1100"}, {"d": "56 💎", "p": "4350"}, {"d": "140 💎", "p": "10200"}, {"d": "284 💎", "p": "20200"}, {"d": "583 💎", "p": "41200"}, {"d": "1145 💎", "p": "80500"}],
            "Weekly Pass": [{"d": "WP 1X", "p": "8700"}, {"d": "WP 2X", "p": "17400"}, {"d": "WP 3X", "p": "26100"}, {"d": "WP 4X", "p": "34800"}, {"d": "WP 5X", "p": "43500"}, {"d": "WP 6X", "p": "52200"}, {"d": "WP 7X", "p": "60900"}, {"d": "WP 8X", "p": "69600"}, {"d": "WP 9X", "p": "78300"}, {"d": "WP 10X", "p": "87000"}],
            "2X Dia": [{"d": "50+ 💎", "p": "4250"}, {"d": "250+ 💎", "p": "20200"}]
        }
    },
    {
        "id": 3, "name": "Indonesia (🇮🇩)", "img": "https://flagcdn.com/w160/id.png", 
        "cat_order": ["Indonesia Dia", "Weekly Pass", "Bundle Pack"], 
        "cats": {
            "Indonesia Dia": [{"d": "5 💎", "p": "450"}, {"d": "12 💎", "p": "950"}, {"d": "44 💎", "p": "3300"}, {"d": "85 💎", "p": "5850"}, {"d": "170 💎", "p": "11700"}, {"d": "296 💎", "p": "20500"}, {"d": "568 💎", "p": "37500"}, {"d": "2010 💎", "p": "123500"}, {"d": "4830 💎", "p": "299000"}],
            "Weekly Pass": [{"d": "WP 1X", "p": "7500"}],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "45000"}]
        }
    },
    {
        "id": 4, "name": "Russia (🇷🇺)", "img": "https://flagcdn.com/w160/ru.png", "cat_order": ["Russia Dia", "Weekly Pass"], 
        "cats": {
            "Russia Dia": [{"d": "35 💎", "p": "2750"}, {"d": "165 💎", "p": "13000"}, {"d": "565 💎", "p": "44500"}, {"d": "1765 💎", "p": "182000"}, {"d": "6000 💎", "p": "435000"}],
            "Weekly Pass": [{"d": "WP 1X", "p": "8600"}]
        }
    },
    {
        "id": 5, "name": "Philippines (🇵🇭)", "img": "https://flagcdn.com/w160/ph.png", "cat_order": ["Philippines Dia", "Weekly Pass", "2X Dia"], 
        "cats": {
            "Philippines Dia": [{"d": "11 💎", "p": "750"}, {"d": "56 💎", "p": "3500"}, {"d": "112 💎", "p": "7000"}, {"d": "570 💎", "p": "36000"}, {"d": "1163 💎", "p": "70500"}, {"d": "6042 💎", "p": "350000"}],
            "Weekly Pass": [{"d": "WP 1X", "p": "6500"}],
            "2X Dia": [{"d": "150+150 💎", "p": "10500"}, {"d": "500+500 💎", "p": "34500"}]
        }
    }
]

# --- 🌐 HTML INTERFACE ---
HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; margin:0; padding-bottom:80px; }
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; padding: 15px; }
    .game-card { 
        position: relative; background:#1e293b; border-radius:15px; padding:35px 20px; 
        text-align:center; border:1px solid #334155; cursor:pointer; overflow: hidden;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .game-card::after {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-image: url('/static/hero.webp'); background-size: cover; opacity: 0.15; z-index: 1;
    }
    .game-card img, .game-card b { position: relative; z-index: 2; }
    .cat-tab { padding:10px 18px; background:#1e293b; border-radius:10px; font-size:12px; cursor:pointer; border:1px solid #334155; white-space:nowrap; }
    .cat-tab.active { background:#fbbf24; color:black; font-weight:bold; }
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:15px 0; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; cursor:pointer; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:10px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; color:black; cursor:pointer; }
    .nav-bar { position:fixed; bottom:0; left:0; right:0; background:#1e293b; display:flex; padding:12px; border-top:1px solid #334155; z-index:100; }
    .pay-box { background:#1e293b; border:2px solid #fbbf24; padding:15px; border-radius:12px; text-align:center; margin-bottom:15px; }
    .pay-icons img { height:40px; margin:0 5px; border-radius:5px; }
    .warning-box { background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #fca5a5; padding: 12px; border-radius: 10px; text-align: center; margin-bottom: 15px; font-weight: bold; }
    .logout-btn { background: #ef4444; color: white; padding: 10px; border: none; border-radius: 8px; margin-top: 20px; width: 100%; font-weight: bold; cursor: pointer; }
.my-rank-card {
    background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%);
    color: white; border: 2px solid #fbbf24;
    border-radius: 12px; padding: 15px; margin-bottom: 20px;
    display: flex; align-items: center; justify-content: space-between;
}
.my-rank-text { color: #fbbf24; font-weight: bold; font-size: 14px; }
    .top-buyer-card {
        background: white; color: #1e293b; border-radius: 12px;
        padding: 12px 15px; margin-bottom: 10px;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .rank-circle {
        background: #f1f5f9; width: 30px; height: 30px;
        border-radius: 50%; display: flex; align-items: center;
        justify-content: center; font-weight: bold; font-size: 14px;
    }
    .buyer-info { flex: 1; margin-left: 15px; }
    .buyer-name { font-weight: bold; font-size: 16px; display: block; }
    .buyer-amount { color: #059669; font-weight: bold; font-size: 14px; }
    .rank-icon { width: 40px; }
</style>
</head><body>
<div style="max-width:500px; margin:auto;">
    <div id="login-sec" style="padding:40px 20px; text-align:center;">
        <h1 style="color:#fbbf24;">KIWII GAME STORE</h1>
        <input type="text" id="l_user" placeholder="Telegram Username">
        <input type="password" id="l_pw" placeholder="Password">
        <button onclick="handleLogin()" class="buy-btn">LOGIN</button>
        <p onclick="showReg()" style="margin-top:20px; color:#fbbf24; cursor:pointer;">အကောင့်မရှိသေးပါက Register နှိပ်ပါ</p>
    </div>

    <div id="reg-sec" style="padding:40px 20px; text-align:center; display:none;">
        <h1 style="color:#fbbf24;">REGISTER</h1>
        <input type="text" id="r_name" placeholder="Full Name">
        <input type="text" id="r_user" placeholder="Telegram Username">
        <input type="password" id="r_pw" placeholder="Password">
        <input type="password" id="r_rpw" placeholder="Retype Password">
        <button onclick="handleRegister()" class="buy-btn">SIGN UP</button>
        <p onclick="showLogin()" style="margin-top:20px; color:#fbbf24; cursor:pointer;">အကောင့်ရှိလျှင် Login ဝင်ရန်</p>
    </div>

    <div id="main-shop" style="display:none;">
        <div id="h-sec">
            <h1 style="text-align:center;color:#fbbf24;margin-top:20px;">KIWII GAME STORE</h1>
            <div class="game-grid" id="g-list"></div>
        </div>

                        <div id="o-sec" style="display:none; padding:15px;">
            <button onclick="goH()" style="background:none;color:white;border:1px solid #334155;padding:8px;border-radius:8px;cursor:pointer;">← Back</button>
            <h2 id="g-title" style="color:#fbbf24; margin-top:10px;"></h2>
            <div id="tabs" style="display:flex; gap:8px; overflow-x:auto; padding-bottom:10px;"></div>
            <div id="p-list" class="pkg-grid"></div>

            <div class="pay-box">
                <div class="pay-icons">
                    <img src="/static/kpay.jpg"> <img src="/static/wave.jpg"> <img src="/static/ayapay.jpg">
                </div>
                <b style="color:#fbbf24; font-size:22px;">09775394979</b><br>
                <b style="color:white;">Name: Thansin Kyaw</b>
            </div>
            <div class="warning-box">⚠️ Note - Payment သာရေးပါ</div>

            <form id="orderForm" onsubmit="confirmOrder(event)">
                <input type="tel" id="uid" name="uid" placeholder="Game ID" required>
                <input type="tel" id="zid" name="zid" placeholder="Zone ID" required>
                <input type="file" id="photo" name="photo" required accept="image/*">
                <button type="submit" id="submitBtn" class="buy-btn">PLACE ORDER</button>
            </form>
        </div>

        <div id="hist-sec" style="display:none; padding:15px;">
            <h3 style="color:#fbbf24;">My History</h3>
            <div id="hist-list"></div>
            <button onclick="logout()" class="logout-btn">LOGOUT</button>
        </div>

        <div id="top-sec" style="display:none; padding:15px;">
            <h2 style="color:#fbbf24; text-align:center;">🏆 Top Buyers List</h2>
            <div id="top-list-container"></div>
        </div>

    </div> ```

---

### ၂။ JavaScript Function များကို စစ်ဆေးရန်
ဓာတ်ပုံ (၁၇) ရဲ့ အောက်ဆုံးနားက JavaScript ထဲမှာ `goH()` နဲ့ `showH()` function တွေကို အခုလို ပြင်ပေးမှ Section တစ်ခုဖွင့်ရင် တစ်ခု ပျောက်သွားမှာ ဖြစ်ပါတယ်-

```javascript
function goH() { 
    document.getElementById('o-sec').style.display='none'; 
    document.getElementById('hist-sec').style.display='none'; 
    document.getElementById('top-sec').style.display='none'; 
    document.getElementById('h-sec').style.display='block'; 
}

function showH() { 
    document.getElementById('h-sec').style.display='none'; 
    document.getElementById('o-sec').style.display='none'; 
    document.getElementById('top-sec').style.display='none'; 
    document.getElementById('hist-sec').style.display='block'; 
    loadH();
}

// showTop() function ကိုလည်း သေချာစစ်ပါ (ဓာတ်ပုံ ၁၁ အရ)
function showTop() {
    document.getElementById('h-sec').style.display='none';
    document.getElementById('o-sec').style.display='none';
    document.getElementById('hist-sec').style.display='none';
    document.getElementById('top-sec').style.display='block';
    loadTopBuyers();
}


<div class="nav-bar">
    <div onclick="goH()" style="flex:1; text-align:center; cursor:pointer;"><i class="fas fa-home"></i><br><small>Home</small></div>
    <div onclick="showH()" style="flex:1; text-align:center; cursor:pointer;"><i class="fas fa-history"></i><br><small>History</small></div>
    <div onclick="showTop()" style="flex:1; text-align:center; cursor:pointer;">
    <i class="fas fa-trophy"></i><br><small>Top 10</small>
</div>
    <div onclick="window.open('https://t.me/thansinkyaw144')" style="flex:1; text-align:center; cursor:pointer; color:#fbbf24;"><i class="fas fa-headset"></i><br><small>CS</small></div>
</div>

<script>
let sel_srv='', sel_pkg='', sel_prc='';
let currentUser = localStorage.getItem('logged_user') || "";
const games = {{ games | tojson }};

window.onload = function() {
    if(currentUser) {
        document.getElementById('login-sec').style.display = 'none';
        document.getElementById('main-shop').style.display = 'block';
        init();
    }
};

function showReg() { document.getElementById('login-sec').style.display='none'; document.getElementById('reg-sec').style.display='block'; }
function showLogin() { document.getElementById('reg-sec').style.display='none'; document.getElementById('login-sec').style.display='block'; }

async function handleRegister() {
    const name = document.getElementById('r_name').value;
    const tg_u = document.getElementById('r_user').value;
    const pw = document.getElementById('r_pw').value;
    const rpw = document.getElementById('r_rpw').value;
    if(!name || !tg_u || !pw) return alert("အချက်အလက်များ ဖြည့်ပါ");
    if(pw !== rpw) return alert("Password မတူပါ");
    const r = await fetch('/api/register', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name, tg_u, pw })
    });
    const res = await r.json();
    if(res.status === "success") { alert("Register အောင်မြင်ပါသည်!"); showLogin(); } else alert(res.msg);
}

// စာကြောင်း ၂၃၅ အောက်မှာ ထည့်ရန်
function showTop() {
    document.getElementById('h-sec').style.display='none';
    document.getElementById('o-sec').style.display='none';
    document.getElementById('hist-sec').style.display='none';
    document.getElementById('top-sec').style.display='block';
    loadTopBuyers();
}

async function loadTopBuyers() {
    try {
        const user = typeof currentUser !== 'undefined' ? currentUser : "";
        const r = await fetch(`/api/top-buyers?user=${encodeURIComponent(user)}`);
        const data = await r.json();
        const container = document.getElementById('top-list-container');
        
        let html = "";
        if (data.top_10 && data.top_10.length > 0) {
            html += data.top_10.map((u, i) => `
                <div class="top-buyer-card">
                    <div class="rank-circle">${i + 1}</div>
                    <div class="buyer-info">
                        <span class="buyer-name">${u._id}</span>
                        <span class="buyer-amount">${u.total_spent.toLocaleString()} ကျပ်</span>
                    </div>
                </div>
            `).join('');
        } else {
            html = "<p style='text-align:center; color:white; padding:20px;'>ယခုလအတွက် ဝယ်ယူထားသူ မရှိသေးပါ။</p>";
        }

        if (data.user_rank) {
            html += `
                <div style="margin: 20px 0 10px 0; text-align: center; color: #94a3b8; font-size: 12px;">— YOUR RANKING —</div>
                <div class="my-rank-card">
                    <div>
                        <span class="my-rank-text">Your Current Status</span>
                        <div class="buyer-name" style="color:white;">${user}</div>
                        <div class="buyer-amount" style="color:#fbbf24;">${data.user_rank.total_spent.toLocaleString()} ကျပ်</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:12px;">Rank</div>
                        <div style="font-size:24px; font-weight:bold; color:#fbbf24;">#${data.user_rank.rank}</div>
                    </div>
                </div>`;
        }
        container.innerHTML = html;
    } catch (e) { console.error(e); }
}

async function handleLogin() {
    const tg_u = document.getElementById('l_user').value;
    const pw = document.getElementById('l_pw').value;
    const r = await fetch('/api/login', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ tg_u, pw })
    });
    const res = await r.json();
    if(res.status === "success") { localStorage.setItem('logged_user', res.user); location.reload(); } else alert(res.msg);
}

function logout() { localStorage.removeItem('logged_user'); location.reload(); }

function init() { document.getElementById('g-list').innerHTML = games.map(g => `<div class="game-card" onclick="selG(${g.id})"><img src="${g.img}" width="40"><br><b>${g.name}</b></div>`).join(''); }

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
}

function selP(el, d, p) { document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected')); el.classList.add('selected'); sel_pkg=d; sel_prc=p; }

function confirmOrder(e) {
    e.preventDefault();
    if(!sel_pkg) return alert("Package အရင်ရွေးပါ!");
    if(confirm(`📢 အတည်ပြုပါ\\nServer: ${sel_srv}\\nPackage: ${sel_pkg}\\nဈေးနှုန်း: ${sel_prc} Ks`)) submitOrder();
}

async function submitOrder() {
# --- 🌐 HTML INTERFACE ---
HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; margin:0; padding-bottom:80px; }
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; padding: 15px; }
    .game-card { 
        position: relative; background:#1e293b; border-radius:15px; padding:35px 20px; 
        text-align:center; border:1px solid #334155; cursor:pointer; overflow: hidden;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .game-card::after {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background-image: url('/static/hero.webp'); background-size: cover; opacity: 0.15; z-index: 1;
    }
    .game-card img, .game-card b { position: relative; z-index: 2; }
    .cat-tab { padding:10px 18px; background:#1e293b; border-radius:10px; font-size:12px; cursor:pointer; border:1px solid #334155; white-space:nowrap; }
    .cat-tab.active { background:#fbbf24; color:black; font-weight:bold; }
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:15px 0; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; cursor:pointer; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:10px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; color:black; cursor:pointer; }
    .nav-bar { position:fixed; bottom:0; left:0; right:0; background:#1e293b; display:flex; padding:12px; border-top:1px solid #334155; z-index:100; }
    .pay-box { background:#1e293b; border:2px solid #fbbf24; padding:15px; border-radius:12px; text-align:center; margin-bottom:15px; }
    .pay-icons img { height:40px; margin:0 5px; border-radius:5px; }
    .warning-box { background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #fca5a5; padding: 12px; border-radius: 10px; text-align: center; margin-bottom: 15px; font-weight: bold; }
    .logout-btn { background: #ef4444; color: white; padding: 10px; border: none; border-radius: 8px; margin-top: 20px; width: 100%; font-weight: bold; cursor: pointer; }
    .my-rank-card { background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%); color: white; border: 2px solid #fbbf24; border-radius: 12px; padding: 15px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }
    .my-rank-text { color: #fbbf24; font-weight: bold; font-size: 14px; }
    .top-buyer-card { background: white; color: #1e293b; border-radius: 12px; padding: 12px 15px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .rank-circle { background: #f1f5f9; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; }
    .buyer-info { flex: 1; margin-left: 15px; }
    .buyer-name { font-weight: bold; font-size: 16px; display: block; }
    .buyer-amount { color: #059669; font-weight: bold; font-size: 14px; }
</style>
</head><body>
<div style="max-width:500px; margin:auto;">
    <div id="login-sec" style="padding:40px 20px; text-align:center;">
        <h1 style="color:#fbbf24;">KIWII GAME STORE</h1>
        <input type="text" id="l_user" placeholder="Telegram Username">
        <input type="password" id="l_pw" placeholder="Password">
        <button onclick="handleLogin()" class="buy-btn">LOGIN</button>
        <p onclick="showReg()" style="margin-top:20px; color:#fbbf24; cursor:pointer;">အကောင့်မရှိသေးပါက Register နှိပ်ပါ</p>
    </div>

    <div id="reg-sec" style="padding:40px 20px; text-align:center; display:none;">
        <h1 style="color:#fbbf24;">REGISTER</h1>
        <input type="text" id="r_name" placeholder="Full Name">
        <input type="text" id="r_user" placeholder="Telegram Username">
        <input type="password" id="r_pw" placeholder="Password">
        <input type="password" id="r_rpw" placeholder="Retype Password">
        <button onclick="handleRegister()" class="buy-btn">SIGN UP</button>
        <p onclick="showLogin()" style="margin-top:20px; color:#fbbf24; cursor:pointer;">အကောင့်ရှိလျှင် Login ဝင်ရန်</p>
    </div>

    <div id="main-shop" style="display:none;">
        <div id="h-sec">
            <h1 style="text-align:center;color:#fbbf24;margin-top:20px;">KIWII GAME STORE</h1>
            <div class="game-grid" id="g-list"></div>
        </div>

        <div id="o-sec" style="display:none; padding:15px;">
            <button onclick="goH()" style="background:none;color:white;border:1px solid #334155;padding:8px;border-radius:8px;cursor:pointer;">← Back</button>
            <h2 id="g-title" style="color:#fbbf24; margin-top:10px;"></h2>
            <div id="tabs" style="display:flex; gap:8px; overflow-x:auto; padding-bottom:10px;"></div>
            <div id="p-list" class="pkg-grid"></div>
            <div class="pay-box">
                <div class="pay-icons"><img src="/static/kpay.jpg"> <img src="/static/wave.jpg"> <img src="/static/ayapay.jpg"></div>
                <b style="color:#fbbf24; font-size:22px;">09775394979</b><br><b style="color:white;">Name: Thansin Kyaw</b>
            </div>
            <form id="orderForm" onsubmit="confirmOrder(event)">
                <input type="tel" id="uid" name="uid" placeholder="Game ID" required>
                <input type="tel" id="zid" name="zid" placeholder="Zone ID" required>
                <input type="file" id="photo" name="photo" required accept="image/*">
                <button type="submit" id="submitBtn" class="buy-btn">PLACE ORDER</button>
            </form>
        </div>

        <div id="hist-sec" style="display:none; padding:15px;">
            <h3 style="color:#fbbf24;">My History</h3>
            <div id="hist-list"></div>
            <button onclick="logout()" class="logout-btn">LOGOUT</button>
        </div>

        <div id="top-sec" style="display:none; padding:15px;">
            <h2 style="color:#fbbf24; text-align:center;">🏆 Top Buyers List</h2>
            <div id="top-list-container"></div>
        </div>
    </div>
</div>

<div class="nav-bar">
    <div onclick="goH()" style="flex:1; text-align:center; cursor:pointer;"><i class="fas fa-home"></i><br><small>Home</small></div>
    <div onclick="showH()" style="flex:1; text-align:center; cursor:pointer;"><i class="fas fa-history"></i><br><small>History</small></div>
    <div onclick="showTop()" style="flex:1; text-align:center; cursor:pointer;"><i class="fas fa-trophy"></i><br><small>Top 10</small></div>
    <div onclick="window.open('https://t.me/thansinkyaw144')" style="flex:1; text-align:center; cursor:pointer; color:#fbbf24;"><i class="fas fa-headset"></i><br><small>CS</small></div>
</div>

<script>
let sel_srv='', sel_pkg='', sel_prc='';
let currentUser = localStorage.getItem('logged_user') || "";
const games = {{ games | tojson }};

window.onload = function() {
    if(currentUser) {
        document.getElementById('login-sec').style.display = 'none';
        document.getElementById('main-shop').style.display = 'block';
        init();
    }
};

function showReg() { document.getElementById('login-sec').style.display='none'; document.getElementById('reg-sec').style.display='block'; }
function showLogin() { document.getElementById('reg-sec').style.display='none'; document.getElementById('login-sec').style.display='block'; }

async function handleRegister() {
    const name = document.getElementById('r_name').value;
    const tg_u = document.getElementById('r_user').value;
    const pw = document.getElementById('r_pw').value;
    const rpw = document.getElementById('r_rpw').value;
    if(!name || !tg_u || !pw) return alert("အချက်အလက်များ ဖြည့်ပါ");
    if(pw !== rpw) return alert("Password မတူပါ");
    const r = await fetch('/api/register', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ name, tg_u, pw }) });
    const res = await r.json();
    if(res.status === "success") { alert("Register အောင်မြင်ပါသည်!"); showLogin(); } else alert(res.msg);
}

async function handleLogin() {
    const tg_u = document.getElementById('l_user').value;
    const pw = document.getElementById('l_pw').value;
    const r = await fetch('/api/login', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ tg_u, pw }) });
    const res = await r.json();
    if(res.status === "success") { localStorage.setItem('logged_user', res.user); location.reload(); } else alert(res.msg);
}

function logout() { localStorage.removeItem('logged_user'); location.reload(); }

function init() { document.getElementById('g-list').innerHTML = games.map(g => `<div class="game-card" onclick="selG(${g.id})"><img src="${g.img}" width="40"><br><b>${g.name}</b></div>`).join(''); }

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
}

function selP(el, d, p) { document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected')); el.classList.add('selected'); sel_pkg=d; sel_prc=p; }

async function submitOrder() {
    const btn = document.getElementById('submitBtn'); btn.disabled = true; btn.innerText = "Processing...";
    const fd = new FormData(document.getElementById('orderForm'));
    fd.append('tg_u', currentUser); fd.append('server', sel_srv); fd.append('p', sel_pkg); fd.append('a', sel_prc);
    const r = await fetch('/order', { method: 'POST', body: fd });
    if(await r.text()==="Success") { alert("Order Success! ✅"); location.reload(); } else { alert("Error!"); btn.disabled = false; }
}

function confirmOrder(e) { e.preventDefault(); if(!sel_pkg) return alert("Package အရင်ရွေးပါ!"); if(confirm(`📢 အတည်ပြုပါ\\nServer: ${sel_srv}\\nPackage: ${sel_pkg}\\nဈေးနှုန်း: ${sel_prc} Ks`)) submitOrder(); }

function goH() { 
    document.getElementById('o-sec').style.display='none'; 
    document.getElementById('hist-sec').style.display='none'; 
    document.getElementById('top-sec').style.display='none';
    document.getElementById('h-sec').style.display='block'; 
}

function showH() { 
    document.getElementById('h-sec').style.display='none'; 
    document.getElementById('o-sec').style.display='none'; 
    document.getElementById('top-sec').style.display='none';
    document.getElementById('hist-sec').style.display='block'; 
    loadH();
}

async function loadH() {
    const r = await fetch('/api/history?user=' + encodeURIComponent(currentUser));
    const data = await r.json();
    document.getElementById('hist-list').innerHTML = data.map(o => `<div style="background:#1e293b;padding:12px;margin-bottom:10px;border-radius:10px;border-left:4px solid #fbbf24;"><b>${o.pkg}</b><br><small>${o.date}</small> | <b>${o.status}</b></div>`).join('') || "No history.";
}

function showTop() {
    document.getElementById('h-sec').style.display='none';
    document.getElementById('o-sec').style.display='none';
    document.getElementById('hist-sec').style.display='none';
    document.getElementById('top-sec').style.display='block';
    loadTopBuyers();
}

async function loadTopBuyers() {
    try {
        const r = await fetch(`/api/top-buyers?user=${encodeURIComponent(currentUser)}`);
        const data = await r.json();
        const container = document.getElementById('top-list-container');
        let html = "";
        if (data.top_10 && data.top_10.length > 0) {
            html += data.top_10.map((u, i) => `
                <div class="top-buyer-card">
                    <div class="rank-circle">${i + 1}</div>
                    <div class="buyer-info">
                        <span class="buyer-name">${u._id}</span>
                        <span class="buyer-amount">${u.total_spent.toLocaleString()} ကျပ်</span>
                    </div>
                </div>`).join('');
        } else { html = "<p style='text-align:center; color:white; padding:20px;'>ဒေတာ မရှိသေးပါ။</p>"; }
        if (data.user_rank) {
            html += `
                <div style="margin: 20px 0 10px 0; text-align: center; color: #94a3b8; font-size: 12px;">— YOUR RANKING —</div>
                <div class="my-rank-card">
                    <div><span class="my-rank-text">Your Current Status</span><div class="buyer-name" style="color:white;">${currentUser}</div><div class="buyer-amount" style="color:#fbbf24;">${data.user_rank.total_spent.toLocaleString()} ကျပ်</div></div>
                    <div style="text-align:center;"><div style="font-size:12px;">Rank</div><div style="font-size:24px; font-weight:bold; color:#fbbf24;">#${data.user_rank.rank}</div></div>
                </div>`;
        }
        container.innerHTML = html;
    } catch (e) { console.error(e); }
}
</script></body></html>
'''

# --- 🚀 SERVER ROUTES ---
@app.route('/')
def index():
    return render_template_string(HTML_CODE, games=GAMES_DATA)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    if users_col.find_one({"tg_u": data['tg_u']}):
        return jsonify({"status": "error", "msg": "ဤ Username မှာ အသုံးပြုပြီးသားဖြစ်သည်"})
    
    # DB ထဲသိမ်းခြင်း
    users_col.insert_one({"name": data['name'], "tg_u": data['tg_u'], "pw": data['pw']})
    
    # ✅ Telegram ဆီ Register Info ပို့ပေးသည့်အပိုင်း
    reg_msg = f"👤 *New Account Registered!*\n\n📛 Name: `{data['name']}`\n🆔 User: `@{data['tg_u']}`\n🔑 Pass: `{data['pw']}`"
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": reg_msg, "parse_mode": "Markdown"})
    except:
        pass
        
    return jsonify({"status": "success"})

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    user = users_col.find_one({"tg_u": data['tg_u'], "pw": data['pw']})
    if user: return jsonify({"status": "success", "user": user['tg_u']})
    return jsonify({"status": "error", "msg": "Username သို့မဟုတ် Password မှားယွင်းနေသည်"})

@app.route('/order', methods=['POST'])
def order():
    try:
        user, server, uid, zone, pkg, amt = request.form.get('tg_u'), request.form.get('server'), request.form.get('uid'), request.form.get('zid'), request.form.get('p'), request.form.get('a')
        photo = request.files.get('photo')
        oid = str(orders_col.insert_one({
            "customer": user, "uid": uid, "zone": zone, "pkg": pkg, "price": amt, "status": "Pending", 
            "date": datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%Y-%m-%d %H:%M")
        }).inserted_id)
        msg = f"🔔 *New Order!*\n👤 User: `{user}`\n🆔 ID: `{uid}` ({zone})\n🌍 Server: {server}\n💎 Pkg: {pkg}\n💰 Amt: {amt} Ks\n\n✅ [DONE]({request.host_url}admin/update/{oid}/Completed) | ❌ [REJECT]({request.host_url}admin/update/{oid}/Rejected)"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}, files={'photo': photo})
        return "Success"
    except: return "Error"

@app.route('/admin/update/<oid>/<status>')
def update_status(oid, status):
    orders_col.update_one({"_id": ObjectId(oid)}, {"$set": {"status": status}})
    return f"Order updated to {status}."

@app.route('/api/top-buyers')
def get_top_buyers():
    target_user = request.args.get('user')
    pipeline = [
        {"$match": {"status": "Completed"}},
        {"$group": {
            "_id": "$customer", 
            "total_spent": {"$sum": {"$toDouble": "$price"}}
        }},
        {"$sort": {"total_spent": -1}}
    ]
    all_ranks = list(orders_col.aggregate(pipeline))
    
    user_rank_data = None
    for index, u in enumerate(all_ranks):
        if u['_id'] == target_user:
            user_rank_data = {"rank": index + 1, "total_spent": u['total_spent']}
            break
            
    return jsonify({
        "top_10": all_ranks[:10],
        "user_rank": user_rank_data
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    
