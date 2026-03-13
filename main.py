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

BOT_TOKEN = "8424534925:AAGyfQ3q5TBPo5ggHt2OBktgGqMHOKMWSqU"
CHAT_ID = "-1003801691345"
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
            "Malaysia Dia": [{"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "56 💎", "p": "4350"}, {"d": "70 💎", "p": "5100"}, {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"}, {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"}, {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}],
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
            "Singapore Dia": [{"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "56 💎", "p": "4350"}, {"d": "70 💎", "p": "5100"}, {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"}, {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"}, {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}],
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
            "Indonesia Dia": [{"d": "5 💎", "p": "450"}, {"d": "12 💎", "p": "950"}, {"d": "19 💎", "p": "1500"}, {"d": "28 💎", "p": "2200"}, {"d": "44 💎", "p": "3300"}, {"d": "59 💎", "p": "4300"}, {"d": "85 💎", "p": "5850"}, {"d": "170 💎", "p": "11700"}, {"d": "240 💎", "p": "16600"}, {"d": "296 💎", "p": "20500"}, {"d": "408 💎", "p": "28000"}, {"d": "568 💎", "p": "37500"}, {"d": "875 💎", "p": "58500"}, {"d": "2010 💎", "p": "123500"}, {"d": "4830 💎", "p": "299000"}],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "7500"}, {"d": "Weekly Pass 2X", "p": "15000"}, {"d": "Weekly Pass 3X", "p": "22500"}, {"d": "Weekly Pass 4X", "p": "30000"}, {"d": "Weekly Pass 5X", "p": "37500"}, {"d": "Weekly Pass 6X", "p": "45000"}, {"d": "Weekly Pass 7X", "p": "52500"}, {"d": "Weekly Pass 8X", "p": "60000"}, {"d": "Weekly Pass 9X", "p": "67500"}, {"d": "Weekly Pass 10X", "p": "75000"}, {"d": "Twilight Pass", "p": "45000"}
            ]
        }
    },
    {
        "id": 5, "name": "Russia (🇷🇺)", "img": "https://flagcdn.com/w160/ru.png", 
        "cat_order": ["Russia Dia", "Weekly Pass"], 
        "cats": {
            "Russia Dia": [{"d": "35 💎", "p": "2750"}, {"d": "55 💎", "p": "4450"}, {"d": "165 💎", "p": "13000"}, {"d": "275 💎", "p": "22000"}, {"d": "565 💎", "p": "44500"}, {"d": "1155 💎", "p": "88000"}, {"d": "1765 💎", "p": "182000"}, {"d": "2975 💎", "p": "22000"}, {"d": "6000 💎", "p": "435000"}],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "8600"}, {"d": "Weekly Pass 2X", "p": "17200"}, {"d": "Weekly Pass 3X", "p": "25800"}, {"d": "Weekly Pass 4X", "p": "34400"}, {"d": "Weekly Pass 5X", "p": "43000"}, {"d": "Weekly Pass 6X", "p": "51600"}, {"d": "Weekly Pass 7X", "p": "60200"}, {"d": "Weekly Pass 8X", "p": "68800"}, {"d": "Weekly Pass 9X", "p": "77400"}, {"d": "Weekly Pass 10X", "p": "86000"}
            ]
        }
    },
    {
        "id": 6, "name": "Philippines (🇵🇭)", "img": "https://flagcdn.com/w160/ph.png", 
        "cat_order": ["Philippines Dia", "2X Dia", "Weekly Pass"], 
        "cats": {
            "Philippines Dia": [{"d": "11 💎", "p": "750"}, {"d": "22 💎", "p": "1500"}, {"d": "56 💎", "p": "3500"}, {"d": "112 💎", "p": "7000"}, {"d": "223 💎", "p": "14000"}, {"d": "336 💎", "p": "21300"}, {"d": "570 💎", "p": "36000"}, {"d": "1163 💎", "p": "70500"}, {"d": "2398 💎", "p": "140000"}, {"d": "6042 💎", "p": "350000"}],
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
    
    /* Auth UI */
    .auth-box { padding: 40px 20px; text-align: center; }
    .auth-box h2 { color: #fbbf24; margin-bottom: 20px; }
    .auth-input { width:100%; padding:15px; margin:10px 0; border-radius:12px; background:#1e293b; color:white; border:1px solid #334155; box-sizing:border-box; }
    .auth-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; color:black; cursor:pointer; }
    .auth-toggle { margin-top:20px; color:#94a3b8; font-size:14px; cursor:pointer; text-decoration: underline; }

    /* App UI */
    .user-banner { background:#1e293b; padding:12px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; }
    .logout-btn { color:#ef4444; font-weight:bold; cursor:pointer; font-size:13px; }
    
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:15px; padding:20px; }
    .game-card { background:rgba(30, 41, 59, 0.85); border-radius:15px; padding:20px; text-align:center; border:1px solid #334155; cursor:pointer; }
    
    .cat-tabs { display:flex; gap:10px; overflow-x:auto; padding:10px 0; margin-bottom:15px; scrollbar-width: none; }
    .tab-btn { background:#1e293b; border:1px solid #334155; color:#94a3b8; padding:10px 15px; border-radius:10px; white-space:nowrap; cursor:pointer; font-size:14px; }
    .tab-btn.active { background:#fbbf24; color:black; font-weight:bold; }

    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:15px 0; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; cursor:pointer; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    
    .pay-box { background: #1e293b; padding: 20px; border-radius: 20px; border: 1.5px solid #fbbf24; text-align: center; margin-bottom: 20px; }
    .pay-icons { display: flex; justify-content: center; gap: 15px; margin-bottom: 15px; }
    .pay-icons img { width: 55px; height: 55px; border-radius: 12px; cursor: pointer; opacity: 0.6; }
    .pay-icons img.active { border: 2px solid #fbbf24; opacity: 1; transform: scale(1.1); }
    
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; color:black; cursor:pointer; margin-top:10px; }
    .nav-bar { position:fixed; bottom:0; width:100%; max-width:500px; background:#1e293b; display:flex; padding:12px 0; border-top:1px solid #334155; z-index:1000; }
    .nav-item { flex:1; text-align:center; color:#94a3b8; cursor:pointer; font-size:12px; }
    .nav-item.active { color:#fbbf24; font-weight:bold; }
.glow-note {
    color: #ff4444;
    font-weight: bold;
    text-align: center;
    margin: 10px 0;
    padding: 10px;
    border: 1.5px solid #ff4444;
    border-radius: 12px;
    background: rgba(239, 68, 68, 0.1);
    animation: blink 1.5s infinite;
}
@keyframes blink { 
    0% { box-shadow: 0 0 5px #ff4444; opacity: 1; } 
    50% { box-shadow: 0 0 20px #ff4444; opacity: 0.7; } 
    100% { box-shadow: 0 0 5px #ff4444; opacity: 1; } 
}
.my-rank-status {
    background: #1e293b;
    border: 1px solid #fbbf24;
    padding: 15px;
    margin-top: 15px;
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
}

            /* Personal Rank Style */
    .my-rank-card {
        margin: 15px auto; 
        width: calc(100% - 30px); 
        max-width: 470px; 
        padding: 15px; 
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        border-radius: 12px; 
        color: black;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); 
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

</style>
</head><body>
<div id="main-container">
    <div id="auth-sec" class="auth-box">
        <div class="header-logo">KIWII GAME STORE</div>
        <div id="login-form">
            <h2>LOGIN</h2>
            <input type="text" id="l-user" class="auth-input" placeholder="Telegram Username (e.g. @kiwii)">
            <input type="password" id="l-pass" class="auth-input" placeholder="Password">
            <button class="auth-btn" onclick="handleAuth('login')">LOGIN</button>
            <div class="auth-toggle" onclick="toggleAuth()">No account? Register here</div>
        </div>
        <div id="reg-form" style="display:none;">
            <h2>REGISTER</h2>
            <p style="color:#94a3b8; font-size:13px; margin-bottom:10px;">Telegram Username ( Eg. @Bby_kiwii7 )</p>
            <input type="text" id="r-user" class="auth-input" placeholder="Username (must start with @)">
            <input type="password" id="r-pass" class="auth-input" placeholder="Create Password">
            <button class="auth-btn" onclick="handleAuth('register')">CREATE ACCOUNT</button>
            <div class="auth-toggle" onclick="toggleAuth()">Already have an account? Login</div>
        </div>
    </div>

    <div id="app-sec" style="display:none;">
        <div class="user-banner">
            <span>👤 <b id="display-user"></b></span>
            <span class="logout-btn" onclick="logout()">LOGOUT <i class="fas fa-sign-out-alt"></i></span>
        </div>

        <div id="h-sec">
            <div class="header-logo">KIWII GAME STORE</div>
            <div class="game-grid" id="g-list"></div>
        </div>

        <div id="o-sec" style="display:none; padding:15px;">
            <button onclick="goH()" style="background:none;color:white;border:1px solid #334155;padding:8px 15px;border-radius:8px;margin-bottom:15px;">← Back</button>
            <h2 id="g-title" style="color:#fbbf24;"></h2>
            <div id="cat-container" class="cat-tabs"></div>
            <div id="p-list" class="pkg-grid"></div>

            <div class="pay-box">
    <div class="pay-icons">
        <img src="/static/kpay.jpg" class="active" onclick="setPay(this, '09775394979', 'Kpay')">
        <img src="/static/wave.jpg" onclick="setPay(this, '09775394979', 'Wave')">
        <img src="/static/ayapay.jpg" onclick="setPay(this, '09775394979', 'Aya')">
    </div>
    <div style="margin-top:10px;">
        <b id="pay-type">KPAY ACCOUNT</b><br>
        <span id="pay-num" style="font-size:20px;">09775394979</span><br>
        <b style="color: #fbbf24;">Name - Thansin Kyaw</b> </div>
    <div class="glow-note">Note - Payment သာရေးပါ</div>
</div>

            <form id="orderForm" onsubmit="handleOrder(event)">
                <input type="text" id="uid" placeholder="Game ID" required class="auth-input">
                <input type="text" id="zid" placeholder="Zone ID" required class="auth-input">
                <input type="file" id="photo" required accept="image/*" class="auth-input">
                <button type="submit" class="buy-btn" id="submitBtn">PLACE ORDER</button>
            </form>
        </div>

        <div id="top-sec" style="display:none; padding:15px;"><h3 style="color:#fbbf24; text-align:center;">🏆 TOP 10 USERS</h3><div id="top-list"></div></div>
        <div id="hist-sec" style="display:none; padding:15px;"><h3 style="color:#fbbf24;">History</h3><div id="hist-list"></div></div>

        <div class="nav-bar">
            <div class="nav-item active" id="nav-home" onclick="goH()"><i class="fas fa-home"></i><br>Home</div>
            <div class="nav-item" id="nav-hist" onclick="showH()"><i class="fas fa-history"></i><br>History</div>
            <div class="nav-item" id="nav-top" onclick="showTop()"><i class="fas fa-trophy"></i><br>Top 10</div>
            <div class="nav-item" onclick="window.open('{{ cs_link }}')"><i class="fas fa-headset"></i><br>CS</div>
        </div>
    </div>
</div>

<script>
        let personalHtml = `
            <div class="my-rank-card">
                <p style="margin:0; font-size:14px; font-weight:bold; opacity:0.8;">MY CURRENT STATUS</p>
                <div style="font-size:22px; font-weight:bold; margin:5px 0;">Rank: #${data.userRank}</div>
                <p style="margin:0; font-size:14px;">Total Spent: ${data.userSpent.toLocaleString()} Ks</p>
            </div>`;

function checkAuth() {
    if(currentUser) {
        document.getElementById('auth-sec').style.display='none';
        document.getElementById('app-sec').style.display='block';
        document.getElementById('display-user').innerText = currentUser;
        init();
    }
}
checkAuth();

function toggleAuth() {
    const isLogin = document.getElementById('login-form').style.display !== 'none';
    document.getElementById('login-form').style.display = isLogin ? 'none' : 'block';
    document.getElementById('reg-form').style.display = isLogin ? 'block' : 'none';
}

async function handleAuth(type) {
    const user = document.getElementById(type === 'login' ? 'l-user' : 'r-user').value.trim();
    const pass = document.getElementById(type === 'login' ? 'l-pass' : 'r-pass').value;

    // အချက်အလက် ပြည့်စုံမှု ရှိ၊ မရှိ စစ်ဆေးခြင်း
    if (!user || !pass) return alert("Please fill all fields");
    if (!user.startsWith('@')) return alert("Username must start with @");

    // Register ဖြစ်ပါက Password နှစ်ခု တူ၊ မတူ စစ်ဆေးခြင်း
    if (type === 'register') {
        const p2 = document.getElementById('r-pass2').value;
        if (pass !== p2) return alert("Passwords များ မတူညီပါ!");
    }

    // Server ဆီသို့ ပို့ဆောင်ခြင်း
    const r = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, user, pass })
    });

    const res = await r.json();
    if (res.success) {
        localStorage.setItem('user', user);
        location.reload();
    } else {
        alert(res.msg);
    }
}

function logout() {
    localStorage.removeItem('user');
    location.reload();
}

function init() {
    document.getElementById('g-list').innerHTML = games.map(g => `
        <div class="game-card" onclick="selG(${g.id})">
            <img src="${g.img}" width="65" style="border-radius:12px;"><br>
            <b style="display:block;margin-top:12px;">${g.name}</b>
        </div>`).join('');
}

function selG(id) {
    const g = games.find(i => i.id === id);
    sel_srv = id;
    document.getElementById('h-sec').style.display='none';
    document.getElementById('o-sec').style.display='block';
    document.getElementById('g-title').innerText = g.name;
    const cats = g.cat_order;
    document.getElementById('cat-container').innerHTML = cats.map((c, i) => `<div class="tab-btn ${i===0?'active':''}" onclick="renderP('${c}', this)">${c}</div>`).join('');
    renderP(cats[0], document.querySelector('.tab-btn.active'));
}

function renderP(cat, btn) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const pkgs = games.find(i => i.id === sel_srv).cats[cat];
    document.getElementById('p-list').innerHTML = pkgs.map(p => `<div class="pkg-card" onclick="selP(this, '${p.d}', '${p.p}')"><span>${p.d}</span><br><b>${p.p} Ks</b></div>`).join('');
}

function selP(el, d, p) {
    document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected'));
    el.classList.add('selected'); sel_pkg=d; sel_prc=p;
}

function setPay(img, num, type) {
    document.querySelectorAll('.pay-icons img').forEach(i => i.classList.remove('active'));
    img.classList.add('active');
    document.getElementById('pay-num').innerText = num;
    document.getElementById('pay-type').innerText = type + " ACCOUNT";
}

function updateNav(id) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

async function handleOrder(e) {
    e.preventDefault();
    
    // ၁။ Package ရွေးမရွေး အရင်စစ်မယ်
    if(!sel_pkg) return alert("Package ရွေးပေးပါ။");

    // ၂။ Game ID နှင့် Zone ID တန်ဖိုးများကို ယူမယ်
    const uid = document.getElementById('uid').value;
    const zid = document.getElementById('zid').value;
    const photoInput = document.getElementById('photo');

    // ၃။ Customer ကို အချက်အလက်များ အတည်ပြုခိုင်းမယ် (Confirmation Box)
    const confirmMsg = `အတည်ပြုပေးပါ\n\nGame ID: ${uid}\nZone ID: ${zid}\nPackage: ${sel_pkg}\nPrice: ${sel_prc} Ks`;
    if(!confirm(confirmMsg)) return;

    // ၄။ အတည်ပြုပြီးမှ ခလုတ်ကို ပိတ်ပြီး စာသားပြောင်းမယ်
    const btn = document.getElementById('submitBtn');
    btn.innerText = "SENDING...";
    btn.disabled = true;

    // ၅။ Data များ စုစည်းပြီး Server ဆီ ပို့မယ်
    const fd = new FormData();
    fd.append('tg_user', currentUser);
    fd.append('uid', uid);
    fd.append('zid', zid);
    fd.append('server', games.find(i => i.id === sel_srv).name);
    fd.append('pkg', sel_pkg);
    fd.append('price', sel_prc);
    fd.append('photo', photoInput.files[0]);

    try {
        const r = await fetch('/order', { method: 'POST', body: fd });
        const resText = await r.text();
        
        if(resText === "Success") {
            alert("Order Success!");
            location.reload();
        } else {
            alert("Order Failed: " + resText);
            btn.innerText = "PLACE ORDER";
            btn.disabled = false;
        }
    } catch(err) {
        alert("Error: " + err.message);
        btn.innerText = "PLACE ORDER";
        btn.disabled = false;
    }
}

function goH() {
    document.getElementById('h-sec').style.display='block';
    document.getElementById('o-sec').style.display='none';
    document.getElementById('top-sec').style.display='none';
    document.getElementById('hist-sec').style.display='none';
    updateNav('nav-home');
}

async function showTop() {
    document.getElementById('h-sec').style.display='none';
    document.getElementById('o-sec').style.display='none';
    document.getElementById('hist-sec').style.display='none';
    document.getElementById('top-sec').style.display='block';
    updateNav('nav-top');
    const r = await fetch(`/api/top10?user=${currentUser}`);
    const data = await r.json();
    
    let topHtml = data.top10.map((u, i) => `
        <div style="background:#1e293b;padding:15px;margin-bottom:10px;border-radius:12px;display:flex;justify-content:space-between;align-items:center;">
            <span><b style="color:#fbbf24;">#${i+1}</b> ${u._id}</span>
            <b style="color:#fbbf24;">${u.totalSpent.toLocaleString()} Ks</b>
        </div>`).join('') || "No data";

            let personalHtml = `
    <div class="my-rank-card">
        <p style="margin:0; font-size:12px; font-weight:bold; text-transform:uppercase; opacity:0.7;">My Current Status</p>
        <div style="font-size:20px; font-weight:bold; margin:8px 0; display:flex; align-items:center; justify-content:center; gap:8px;">
            <span style="font-size:24px;">👤</span> ${currentUser}
        </div>
        <div style="font-size:18px; font-weight:bold;">Rank: #${data.userRank || 'N/A'}</div>
        <p style="margin:5px 0 0; font-size:13px; font-weight:500;">Total Spent: ${data.userSpent.toLocaleString()} Ks</p>
    </div>`;

    document.getElementById('top-list').innerHTML = topHtml + personalHtml;
}

async function showH() {
    document.getElementById('h-sec').style.display='none';
    document.getElementById('o-sec').style.display='none';
    document.getElementById('top-sec').style.display='none';
    document.getElementById('hist-sec').style.display='block';
    updateNav('nav-hist');
    const r = await fetch('/api/history');
    const data = await r.json();
    document.getElementById('hist-list').innerHTML = data.filter(o => o.tg_user === currentUser).map(o => {
        
        // Status အလိုက် အရောင်သတ်မှတ်ခြင်း
        let statusColor = '#fbbf24'; // Default: Pending (အဝါ)
        if (o.status === 'Completed') statusColor = '#22c55e'; // စိမ်း
        if (o.status === 'Rejected') statusColor = '#ef4444';  // နီ

        return `
            <div style="background:#1e293b; padding:15px; margin-bottom:10px; border-radius:12px; border-left:5px solid ${statusColor};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b>${o.pkg}</b>
                    <span style="color:${statusColor}; font-weight:bold; font-size:13px;">${o.status}</span>
                </div>
                <div style="margin-top:5px;">
                    <span>${o.price} Ks</span><br>
                    <small style="color:#94a3b8;">${o.date}</small>
                </div>
            </div>`;
    }).join('') || "No history";
}
</script></body></html>
'''

# --- 🚀 BACKEND ---
users_col = db['users']

@app.route('/')
def index():
    return render_template_string(HTML_CODE, games=GAMES_DATA, cs_link=CS_TELEGRAM)

@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.json
    utype, user, psw = data['type'], data['user'], data['pass']
    if utype == 'register':
        if users_col.find_one({"user": user}):
            return jsonify({"success": False, "msg": "Username already exists"})
        
        # Database သိမ်းခြင်း
        users_col.insert_one({"user": user, "pass": psw, "date": datetime.now().strftime("%d/%m/%Y")})
        
        # 🔔 Bot ဆီကို Register Info ပို့ခြင်း
        reg_msg = f"<b>🆕 New Account Registered!</b>\\n\\n👤 User: <code>{user}</code>\\n🔑 Pass: <code>{psw}</code>"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": reg_msg, "parse_mode": "HTML"})
        
        return jsonify({"success": True})
    else:
        u = users_col.find_one({"user": user, "pass": psw})
        if u: return jsonify({"success": True})
        return jsonify({"success": False, "msg": "Invalid Credentials"})

@app.route('/order', methods=['POST'])
def order():
    try:
        tg_user = request.form.get('tg_user')
        uid = request.form.get('uid')
        zid = request.form.get('zid')
        pkg = request.form.get('pkg')
        srv = request.form.get('server') # ဒီမှာ server လို့ ပြင်ထားတယ်
        photo = request.files.get('photo')
        
        raw_price = request.form.get('price', '0')
        price_str = str(raw_price).replace(' Ks', '').replace(',', '').strip()
        price = int(price_str) if price_str.isdigit() else 0
        
        # Date သတ်မှတ်ချက်
        order_date = datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%d/%m/%Y %I:%M %p")

        oid = orders_col.insert_one({
            "tg_user": tg_user, "uid": uid, "zone": zid, "pkg": pkg, "srv": srv, 
            "price": price, "status": "Pending", 
            "date": order_date
        }).inserted_id
        
        base_url = "https://kiwiigameshop.onrender.com"
        keyboard = {"inline_keyboard": [[
            {"text": "Done ✅", "url": f"{base_url}/admin/status/done/{oid}"},
            {"text": "Reject ❌", "url": f"{base_url}/admin/status/reject/{oid}"}
        ]]}

        # ဤစာကြောင်း ၂ ကြောင်းကို msg အပေါ်မှာ ထည့်ပေးပါ
        server = request.form.get('server')
        order_date = datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%d/%m/%Y %I:%M %p")

        # Telegram သို့ ပို့မည့် စာသားပုံစံ
        msg = (
            f"<b>🔔 New Order Received!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>👤 User:</b> <code>{tg_user}</code>\n"
            f"<b>🌍 Server:</b> {server}\n"
            f"<b>🆔 Game ID:</b> <code>{uid}</code>\n"
            f"<b>🎮 Zone ID:</b> <code>{zid}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>📦 Package:</b> {pkg}\n"
            f"<b>💰 Price:</b> {price} Ks\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>📅 Date:</b> {order_date}"
        )
        
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
            data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "HTML", "reply_markup": json.dumps(keyboard)}, 
            files={"photo": photo})
        
    except Exception as e:
        print(f"Error: {e}") # Error ကို log ထုတ်ကြည့်ဖို့
        return str(e), 500
    return "Success"

@app.route('/admin/status/<action>/<oid>')
def update_status(action, oid):
    new_status = "Completed" if action == "done" else "Rejected"
    orders_col.update_one({"_id": ObjectId(oid)}, {"$set": {"status": new_status}})
    return f"<html><body style='background:#0f172a;color:white;text-align:center;padding:50px;'><h1>Order {new_status}!</h1></body></html>"

@app.route('/api/history')
def history():
    hist = list(orders_col.find().sort("_id", -1).limit(30))
    for h in hist: h['_id'] = str(h['_id'])
    return jsonify(hist)

@app.route('/api/top10')
def top10():
    current_user = request.args.get('user')
    
    # User အားလုံးရဲ့ ဝယ်ယူမှုပမာဏ (Completed Order များသာ)
    pipeline = [
        {"$match": {"tg_user": {"$nin": ADMIN_USERNAMES}, "status": "Completed"}},
        {"$group": {"_id": "$tg_user", "totalSpent": {"$sum": "$price"}}},
        {"$sort": {"totalSpent": -1}}
    ]
    all_ranks = list(orders_col.aggregate(pipeline))
    
    # Top 10 list
    top10_list = all_ranks[:10]
    
    # Personal Rank ရှာခြင်း
    user_rank = "N/A"
    user_spent = 0
    for index, item in enumerate(all_ranks):
        if item['_id'] == current_user:
            user_rank = index + 1
            user_spent = item['totalSpent']
            break
            
    return jsonify({
        "top10": top10_list,
        "userRank": user_rank,
        "userSpent": user_spent
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    
