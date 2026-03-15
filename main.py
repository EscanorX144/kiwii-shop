import os, requests, json
from flask import Flask, render_template_string, request, jsonify, make_response
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- ⚙️ SECURE CONFIGURATION ---
# Database URL ကို Code ထဲမှာ မထားတော့ဘဲ Render ကနေ လှမ်းယူပါမည်
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://EscanorX:Conti144@cluster0.m2mtomm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client['kiwii_game_shop']
orders_col = db['orders']
users_col = db['users']

# Telegram Tokens များကိုလည်း Render ကနေပဲ လှမ်းယူပါမည်
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8424534925:AAGyfQ3q5TBPo5ggHt2OBktgGqMHOKMWSqU")
CHAT_ID = os.environ.get("CHAT_ID", "-1003801691345") # Group ID ကိုတော့ ဒီတိုင်းထားခဲ့လို့ ရပါတယ်
CS_TELEGRAM = "https://t.me/Bby_kiwii7"
ADMIN_USERNAMES = ["@Escanor_XX", "@Escanor_X", "@Bby_kiwii7"]

GAMES_DATA = [
    {
        "id": 1, "name": "Normal Server (🇲🇲)", "img": "/static/normal.jpg", 
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
        "id": 2, "name": "Malaysia (🇲🇾)", "img": "/static/malaysia.png", 
        "cat_order": ["Malaysia Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], 
        "cats": {
            "Malaysia Dia": [{"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "56 💎", "p": "4350"}, {"d": "70 💎", "p": "5100"}, {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"}, {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"}, {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "8700"}, {"d": "Weekly Pass 2X", "p": "17400"}, {"d": "Weekly Pass 3X", "p": "26100"}, {"d": "Weekly Pass 4X", "p": "34800"}, {"d": "Weekly Pass 5X", "p": "43500"}, {"d": "Weekly Pass 6X", "p": "52200"}, {"d": "Weekly Pass 7X", "p": "60900"}, {"d": "Weekly Pass 8X", "p": "69600"}, {"d": "Weekly Pass 9X", "p": "78300"}, {"d": "Weekly Pass 10X", "p": "87000"}
            ],
            "2X Dia": [{"d": "50+50 💎", "p": "4250"}, {"d": "150+150 💎", "p": "12200"}, {"d": "250+250 💎", "p": "20200"}, {"d": "500+500 💎", "p": "40600"}],
            "Bundle Pack": [{"d": "Weekly Elite", "p": "4250"}, {"d": "Monthly Epic", "p": "20000"}]
        }
    },
    {
        "id": 3, "name": "Singapore (🇸🇬)", "img": "/static/singapore.png", 
        "cat_order": ["Singapore Dia", "Weekly Pass", "2X Dia", "Bundle Pack"], 
        "cats": {
            "Singapore Dia": [{"d": "14 💎", "p": "1100"}, {"d": "42 💎", "p": "3200"}, {"d": "56 💎", "p": "4350"}, {"d": "70 💎", "p": "5100"}, {"d": "140 💎", "p": "10200"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "583 💎", "p": "41200"}, {"d": "716 💎", "p": "50200"}, {"d": "870 💎", "p": "61400"}, {"d": "1145 💎", "p": "80500"}, {"d": "1446 💎", "p": "100500"}, {"d": "2162 💎", "p": "150500"}, {"d": "2976 💎", "p": "201000"}, {"d": "3606 💎", "p": "223000"}, {"d": "6012 💎", "p": "371000"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "8700"}, {"d": "Weekly Pass 2X", "p": "17400"}, {"d": "Weekly Pass 3X", "p": "26100"}, {"d": "Weekly Pass 4X", "p": "34800"}, {"d": "Weekly Pass 5X", "p": "43500"}, {"d": "Weekly Pass 6X", "p": "52200"}, {"d": "Weekly Pass 7X", "p": "60900"}, {"d": "Weekly Pass 8X", "p": "69600"}, {"d": "Weekly Pass 9X", "p": "78300"}, {"d": "Weekly Pass 10X", "p": "87000"}
            ],
            "2X Dia": [{"d": "50+50 💎", "p": "4250"}, {"d": "150+150 💎", "p": "12200"}, {"d": "250+250 💎", "p": "20200"}, {"d": "500+500 💎", "p": "40600"}],
            "Bundle Pack": [{"d": "Weekly Elite", "p": "4250"}, {"d": "Monthly Epic", "p": "20000"}]
        }
    },
    {
        "id": 4, "name": "Indonesia (🇮🇩)", "img": "/static/indonesia.png", 
        "cat_order": ["Indonesia Dia", "Weekly Pass"], 
        "cats": {
            "Indonesia Dia": [{"d": "5 💎", "p": "450"}, {"d": "12 💎", "p": "950"}, {"d": "19 💎", "p": "1500"}, {"d": "28 💎", "p": "2200"}, {"d": "44 💎", "p": "3300"}, {"d": "59 💎", "p": "4300"}, {"d": "85 💎", "p": "5850"}, {"d": "170 💎", "p": "11700"}, {"d": "240 💎", "p": "16600"}, {"d": "296 💎", "p": "20500"}, {"d": "408 💎", "p": "28000"}, {"d": "568 💎", "p": "37500"}, {"d": "875 💎", "p": "58500"}, {"d": "2010 💎", "p": "123500"}, {"d": "4830 💎", "p": "299000"}],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "7500"}, {"d": "Weekly Pass 2X", "p": "15000"}, {"d": "Weekly Pass 3X", "p": "22500"}, {"d": "Weekly Pass 4X", "p": "30000"}, {"d": "Weekly Pass 5X", "p": "37500"}, {"d": "Weekly Pass 6X", "p": "45000"}, {"d": "Weekly Pass 7X", "p": "52500"}, {"d": "Weekly Pass 8X", "p": "60000"}, {"d": "Weekly Pass 9X", "p": "67500"}, {"d": "Weekly Pass 10X", "p": "75000"}, {"d": "Twilight Pass", "p": "45000"}
            ]
        }
    },
    {
        "id": 5, "name": "Russia (🇷🇺)", "img": "/static/russia.jpeg", 
        "cat_order": ["Russia Dia", "Weekly Pass"], 
        "cats": {
            "Russia Dia": [{"d": "35 💎", "p": "2750"}, {"d": "55 💎", "p": "4450"}, {"d": "165 💎", "p": "13000"}, {"d": "275 💎", "p": "22000"}, {"d": "565 💎", "p": "44500"}, {"d": "1155 💎", "p": "88000"}, {"d": "1765 💎", "p": "182000"}, {"d": "2975 💎", "p": "22000"}, {"d": "6000 💎", "p": "435000"}],
            "Weekly Pass": [
                {"d": "Weekly Pass 1X", "p": "8600"}, {"d": "Weekly Pass 2X", "p": "17200"}, {"d": "Weekly Pass 3X", "p": "25800"}, {"d": "Weekly Pass 4X", "p": "34400"}, {"d": "Weekly Pass 5X", "p": "43000"}, {"d": "Weekly Pass 6X", "p": "51600"}, {"d": "Weekly Pass 7X", "p": "60200"}, {"d": "Weekly Pass 8X", "p": "68800"}, {"d": "Weekly Pass 9X", "p": "77400"}, {"d": "Weekly Pass 10X", "p": "86000"}
            ]
        }
    },
    {
        "id": 6, "name": "Philippines (🇵🇭)", "img": "/static/philippine.png", 
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
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
<style>
    body {
        background-color: #0f172a;
        background-image: repeating-linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.02) 0px,
            rgba(255, 255, 255, 0.02) 2px,
            transparent 2px,
            transparent 12px
        );
        background-attachment: fixed;
        color: white;
        margin: 0;
        padding-bottom: 70px;
        font-family: 'Arial', sans-serif;
    }
    #main-container { max-width:500px; margin:auto; }
    .header-logo { 
        text-align: center; 
        padding: 28px 0 20px; 
        font-size: 28px; 
        font-weight: 900; 
        letter-spacing: 2px; /* စာလုံးလေးတွေကို နည်းနည်းခွာလိုက်ပါတယ် */
        text-transform: uppercase;
        
        /* ရွှေရောင်ကို ပိုပြီး ကြွလာအောင်လုပ်ခြင်း */
        color: #fbbf24; 
        text-shadow: 0px 4px 6px rgba(0, 0, 0, 0.5), /* အောက်ခံအမည်းရိပ် */
                     0px 0px 15px rgba(251, 191, 36, 0.4); /* ရွှေရောင် Glow အလင်းရောင် */
    }
    .auth-box { padding: 40px 20px; text-align: center; }
    .auth-input { width:100%; padding:15px; margin:10px 0; border-radius:12px; background:#1e293b; color:white; border:1px solid #334155; box-sizing:border-box; }
    .auth-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; color:black; cursor:pointer; }
    .auth-toggle { margin-top:20px; color:#94a3b8; font-size:14px; cursor:pointer; text-decoration: underline; }
    .user-banner { background:#1e293b; padding:12px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; }
    /* Line 57 ကနေ စပြီး အစားထိုးရန် */
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:15px 0; }
    .pkg-card { 
        background:#1e293b; border:1px solid #334155; padding:15px 10px; 
        border-radius:16px; text-align:center; cursor:pointer; 
        display:flex; flex-direction:column; align-items:center; min-height:120px;
    }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    .pkg-dia-img { 
        width: 75px;  /* အရင် 48px ကနေ 75px အထိ ပိုကြီးပေးလိုက်ပါတယ် */
        height: 75px; /* အရင် 48px ကနေ 75px အထိ ပိုကြီးပေးလိုက်ပါတယ် */
        object-fit: contain; 
        margin-top: 5px; 
        margin-bottom: 8px;
    }
    
    .pkg-info { margin-top:auto; width:100%; }
    .pkg-d-text { font-size:13px; color:white; font-weight:bold; display:block; margin-bottom:2px; }
    .pkg-p-text { font-size:14px; color:#fbbf24; font-weight:bold; }

    /* Home Screen Server Grid ကို ၂ ခုစီ ပြန်ပြင်ခြင်း */
    .game-grid { 
        display: grid; 
        grid-template-columns: 1fr 1fr; /* ဘေးတိုက် ၂ ခုစီ ပြပေးမှာပါ */
        gap: 15px; 
        padding: 20px; 
    }

    .game-card {
        background: #1e293b;
        border-radius: 15px;
        padding: 10px;
        text-align: center;
        border: 1px solid #334155;
    }

    .game-card .img-box { 
        width: 100%; 
        aspect-ratio: 1/1; /* ပုံကို စတုရန်းကွက် ဖြစ်စေပါတယ် */
        border-radius: 12px; 
        overflow: hidden; 
        margin-bottom: 8px; 
    }

    .game-card img { 
        width: 100%; 
        height: 100%; 
        object-fit: cover; 
    }

    .cat-tabs { display:flex; gap:10px; overflow-x:auto; padding:10px 0; margin-bottom:15px; scrollbar-width: none; }
    .tab-btn { background:#1e293b; border:1px solid #334155; color:#94a3b8; padding:10px 15px; border-radius:10px; white-space:nowrap; cursor:pointer; font-size:14px; }
    .tab-btn.active { background:#fbbf24; color:black; font-weight:bold; }
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:15px 0; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; cursor:pointer; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    .pay-box { background: #1e293b; padding: 20px; border-radius: 20px; border: 1.5px solid #fbbf24; text-align: center; margin-bottom: 20px; }
    .pay-icons { display: flex; justify-content: center; gap: 15px; margin-bottom: 15px; }
    .pay-icons img { width: 55px; height: 55px; border-radius: 12px; cursor: pointer; opacity: 0.5; transition: 0.3s; margin: 0 5px; border: 2px solid transparent; }
    .pay-icons img.active { opacity: 1; transform: scale(1.1); border-color: #fbbf24; box-shadow: 0 0 10px rgba(251, 191, 36, 0.5); }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; color:black; cursor:pointer; margin-top:10px; }
    .nav-bar { position:fixed; bottom:0; width:100%; max-width:500px; background:#1e293b; display:flex; padding:12px 0; border-top:1px solid #334155; z-index:1000; }
    .nav-item { flex:1; text-align:center; color:#94a3b8; cursor:pointer; font-size:12px; }
    .nav-item.active { color:#fbbf24; font-weight:bold; }
    .my-rank-card { margin: 15px auto; width: calc(100% - 30px); padding: 15px; background: linear-gradient(135deg, #fbbf24, #f59e0b); border-radius: 12px; color: black; text-align: center; }
    .cs-float { position: fixed; bottom: 80px; right: 20px; background: #fbbf24; color: #0f172a; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 4px 15px rgba(251, 191, 36, 0.4); z-index: 1000; text-decoration: none; transition: transform 0.3s ease; }
    .cs-badge { position: absolute; top: -5px; right: -5px; background: red; color: white; font-size: 10px; padding: 2px 6px; border-radius: 10px; font-weight: bold; }
    .copy-btn { background: #334155; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; font-size: 12px; margin-left: 10px; transition: 0.2s; }
    .glow-note { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid #ef4444; padding: 8px 15px; border-radius: 8px; font-weight: bold; font-size: 14px; margin-top: 15px; display: inline-block; animation: glowPulse 1.5s infinite alternate; }
    @keyframes glowPulse { from { box-shadow: 0 0 5px rgba(239, 68, 68, 0.2); } to { box-shadow: 0 0 15px rgba(239, 68, 68, 0.8); } }
    /* Professional Logout Button */
    .logout-btn {
        background-color: rgba(239, 68, 68, 0.1); /* အနီရောင်ဖျော့ဖျော့ နောက်ခံ */
        color: #ef4444; 
        border: 1px solid #ef4444;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: bold;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: all 0.3s ease;
    }
    .logout-btn:hover {
        background-color: #ef4444;
        color: white;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.5); /* လက်တင်ရင် လင်းလာမည့် Effect */
    }
    
    /* User Profile Icon လေးပိုလှအောင် */
    .user-profile {
        display: flex; 
        align-items: center; 
        gap: 10px;
    }
    .user-icon {
        background: #334155; 
        padding: 6px 10px; 
        border-radius: 50%; 
        color: #fbbf24;
    }
</style>
</head><body>
<div id="main-container">
    <div id="auth-sec" style="max-width: 380px; width: 90%; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(15, 23, 42, 0.9); padding: 30px; border-radius: 15px; border: 1px solid rgba(147, 51, 234, 0.3); box-shadow: 0 0 20px rgba(147, 51, 234, 0.1); box-sizing: border-box;">
    
        <div id="login-box">
            <h2 style="text-align: center; color: #c084fc; margin-top: 0; margin-bottom: 25px; text-transform: uppercase; font-weight: 800;">LOGIN</h2>
            <input type="text" id="log-user" placeholder="Telegram Username (e.g., @Bby_kiwii7)" style="width: 100%; padding: 14px; margin-bottom: 15px; border-radius: 8px; border: none; background: #020617; color: white; box-sizing: border-box; font-size: 15px;">
            <input type="password" id="log-pass" placeholder="Password" style="width: 100%; padding: 14px; margin-bottom: 25px; border-radius: 8px; border: none; background: #020617; color: white; box-sizing: border-box; font-size: 15px;">
            <button onclick="auth('login')" style="width: 100%; padding: 14px; border-radius: 8px; background: linear-gradient(135deg, #a855f7, #7e22ce); color: white; border: none; font-weight: bold; cursor: pointer; font-size: 16px; text-transform: uppercase;">Login</button>
            <p style="text-align: center; margin-top: 20px; font-size: 14px;"><a href="#" onclick="toggleAuth('register')" style="color: #94a3b8; text-decoration: none;">Don't have an account? <span style="color: #c084fc;">Sign Up</span></a></p>
        </div>

        <div id="reg-box" style="display: none;">
            <h2 style="text-align: center; color: #4ade80; margin-top: 0; margin-bottom: 25px; text-transform: uppercase; font-weight: 800;">SIGN UP</h2>
            <input type="text" id="reg-name" placeholder="Name" style="width: 100%; padding: 14px; margin-bottom: 15px; border-radius: 8px; border: none; background: #020617; color: white; box-sizing: border-box; font-size: 15px;">
            <input type="text" id="reg-user" placeholder="Telegram Username (e.g., @Bby_kiwii7)" style="width: 100%; padding: 14px; margin-bottom: 15px; border-radius: 8px; border: none; background: #020617; color: white; box-sizing: border-box; font-size: 15px;">
            <input type="password" id="reg-pass" placeholder="Password" style="width: 100%; padding: 14px; margin-bottom: 15px; border-radius: 8px; border: none; background: #020617; color: white; box-sizing: border-box; font-size: 15px;">
            <input type="password" id="reg-repass" placeholder="Retype Password" style="width: 100%; padding: 14px; margin-bottom: 25px; border-radius: 8px; border: none; background: #020617; color: white; box-sizing: border-box; font-size: 15px;">
            <button onclick="auth('register')" style="width: 100%; padding: 14px; border-radius: 8px; background: linear-gradient(135deg, #22c55e, #16a34a); color: white; border: none; font-weight: bold; cursor: pointer; font-size: 16px; text-transform: uppercase;">Create Account</button>
            <p style="text-align: center; margin-top: 20px; font-size: 14px;"><a href="#" onclick="toggleAuth('login')" style="color: #94a3b8; text-decoration: none;">Already have an account? <span style="color: #4ade80;">Login</span></a></p>
        </div>
        
    </div>

    <div id="app-sec" style="display:none;">
        <div class="user-banner">
            <span class="user-profile">
                <div class="user-icon"><i class="fas fa-user"></i></div>
                <b id="display-user" style="font-size: 15px;"></b>
            </span>
            <button class="logout-btn" onclick="logout()">
                LOGOUT <i class="fas fa-sign-out-alt"></i>
            </button>
        </div>
        <div id="h-sec">
            <div class="header-logo">KIWII GAME STORE</div>
            <div class="game-grid" id="g-list"></div>
            
            <div style="text-align: center; margin-top: 40px; margin-bottom: 30px;">
                <a href="#" onclick="showPrivacy()" style="color: #94a3b8; font-size: 13px; text-decoration: none; margin-right: 20px; border-bottom: 1px solid #475569; padding-bottom: 2px;">Privacy Policy</a>
                <a href="#" onclick="showTerms()" style="color: #94a3b8; font-size: 13px; text-decoration: none; border-bottom: 1px solid #475569; padding-bottom: 2px;">Terms & Conditions</a>
            </div>

        </div>
        <div id="o-sec" style="display:none; padding:15px;">
            <button onclick="goH()" style="background:none;color:white;border:1px solid #334155;padding:8px 15px;border-radius:8px;margin-bottom:15px;">← Back</button>
            <h2 id="g-title" style="color:#fbbf24;"></h2>
            <div id="cat-container" class="cat-tabs"></div>
            <div id="p-list" class="pkg-grid"></div>
            
            <div class="pay-box">
                <div class="pay-icons">
                    <img src="/static/kpay.jpg" class="active" onclick="setPay(this, '09775394979', 'Kpay', 'Thansin Kyaw')">
                    <img src="/static/wave.jpg" onclick="setPay(this, '09775394979', 'Wave Pay', 'Thansin Kyaw')">
                    <img src="/static/ayapay.jpg" onclick="setPay(this, '09775394979', 'AYA Pay', 'Thansin Kyaw')">
                </div>
                <div style="margin-top:15px;">
                    <b id="pay-type" style="color: #94a3b8; font-size: 14px;">Kpay Account</b><br>
                    <div style="display: flex; align-items: center; justify-content: center; margin: 10px 0;">
                        <span id="pay-num" style="font-size:24px; font-weight: bold; letter-spacing: 1px;">09775394979</span>
                        <button class="copy-btn" onclick="copyNum(event)"><i class="fas fa-copy"></i> Copy</button>
                    </div>
                    <b style="color: #fbbf24; font-size: 15px;" id="pay-name">Name - Thansin Kyaw</b>
                </div>
                <div class="glow-note">⚠️ Note - Payment သာရေးပါ</div>
            </div>
            <form id="orderForm" onsubmit="handleOrder(event)">
                <input type="number" id="uid" placeholder="Game ID" required class="auth-input" inputmode="numeric">
                <input type="number" id="zid" placeholder="server ID" required class="auth-input" inputmode="numeric">
                <input type="file" id="photo" required accept="image/*" class="auth-input">
                <button type="submit" class="buy-btn" id="submitBtn">PLACE ORDER</button>
            </form>
        </div>
        <div id="top-sec" style="display:none; padding:15px;"><h3>🏆 TOP 10 USERS</h3><div id="top-list"></div></div>
        <div id="hist-sec" style="display:none; padding:15px;"><h3>History</h3><div id="hist-list"></div></div>
        
        <div class="nav-bar">
            <div class="nav-item active" id="nav-home" onclick="goH()"><i class="fas fa-home"></i><br>Home</div>
            <div class="nav-item" id="nav-hist" onclick="showH()"><i class="fas fa-history"></i><br>History</div>
            <div class="nav-item" id="nav-top" onclick="showTop()"><i class="fas fa-trophy"></i><br>Top 10</div>
        </div>
    </div>
</div>

<div id="privacy-sec" style="display:none; padding:15px; padding-bottom: 80px;">
            <h2 style="color:#c084fc; text-align:center; text-transform:uppercase; font-weight:800;">Privacy Policy</h2>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 20px; border-radius: 12px; border: 1px solid rgba(147, 51, 234, 0.2); color: #f1f5f9; font-size: 14px; line-height: 1.8;">
                <p><b>၁။ အချက်အလက်ရယူခြင်း:</b> Kiwii Game Shop သည် လူကြီးမင်း၏ Telegram Username, Game ID နှင့် ဝယ်ယူမှုမှတ်တမ်းများကိုသာ ဝန်ဆောင်မှုပေးရန်အတွက် သိမ်းဆည်းထားပါသည်။</p>
                <p><b>၂။ လုံခြုံရေး:</b> လူကြီးမင်း၏ အချက်အလက်များကို အခြားပြင်ပသို့ ပေါက်ကြားမှုမရှိစေရန် အထူးဂရုစိုက် ထိန်းသိမ်းထားပါသည်။</p>
                <p><b>၃။ ဆက်သွယ်ရန်:</b> အခက်အခဲတစ်စုံတစ်ရာရှိပါက Customer Service သို့ အချိန်မရွေး ဆက်သွယ်နိုင်ပါသည်။</p>
                <button onclick="goH()" style="margin-top:20px; width:100%; padding:12px; background: linear-gradient(135deg, #a855f7, #7e22ce); color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">နောက်သို့ ပြန်သွားမည်</button>
            </div>
        </div>

        <div id="terms-sec" style="display:none; padding:15px; padding-bottom: 80px;">
            <h2 style="color:#4ade80; text-align:center; text-transform:uppercase; font-weight:800;">Terms & Conditions</h2>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 20px; border-radius: 12px; border: 1px solid rgba(74, 222, 128, 0.2); color: #f1f5f9; font-size: 14px; line-height: 1.8;">
                <p><b>၁။ အချက်အလက်မှန်ကန်မှု:</b> Order တင်ရာတွင် Game ID , Zone ID နှင့် ငွေလွှဲပြေစာများ မှန်ကန်စေရန် သေချာစွာ စစ်ဆေးရပါမည်။ မှားယွင်းဖြည့်စွက်မှုကြောင့် Oder Cancel ခြင်းဖြစ်ပေါ်ပါမည်။</p>
                <p><b>၂။ ငွေလွှဲပြေစာ:</b> ငွေလွှဲပြေစာ (Screenshot) အတုများအသုံးပြုခြင်းများ စစ်ဆေးတွေ့ရှိပါက အကောင့်အား အပြီးတိုင် ပိတ်သိမ်းပါမည်။</p>
                <p><b>၃။ ငွေပြန်အမ်းခြင်း:</b> ဝယ်ယူမှု အောင်မြင်ပြီးသွားသော (Completed ဖြစ်သွားသော) Order များအတွက် ငွေပြန်အမ်းပေးမည် မဟုတ်ပါ။</p>
                <button onclick="goH()" style="margin-top:20px; width:100%; padding:12px; background: linear-gradient(135deg, #22c55e, #16a34a); color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">နောက်သို့ ပြန်သွားမည်</button>
            </div>
        </div>
<script>
    const games = JSON_DATA_HERE;
    let currentUser = localStorage.getItem('user');
    let sel_srv, sel_pkg, sel_prc;

    function checkAuth() {
        if(currentUser) {
            document.getElementById('auth-sec').style.display='none';
            document.getElementById('app-sec').style.display='block';
            document.getElementById('display-user').innerText = currentUser;
            init();
        }
    }
    checkAuth();

    function toggleAuth(type) {
            document.getElementById('login-box').style.display = type === 'login' ? 'block' : 'none';
            document.getElementById('reg-box').style.display = type === 'register' ? 'block' : 'none';
        }

        async function auth(type) {
            let user, pass;
            
            if (type === 'register') {
                const name = document.getElementById('reg-name').value.trim();
                user = document.getElementById('reg-user').value.trim();
                pass = document.getElementById('reg-pass').value;
                const repass = document.getElementById('reg-repass').value;

                if (!name || !user || !pass || !repass) return alert("❌ ကျေးဇူးပြု၍ အချက်အလက်အားလုံး ပြည့်စုံစွာ ဖြည့်ပါ!");
                if (!user.startsWith('@')) return alert("❌ Telegram Username ၏ အရှေ့တွင် '@' ပါရပါမည်!");
                if (pass !== repass) return alert("❌ Password နှစ်ခု တူညီမှုမရှိပါ!");
                
            } else {
                user = document.getElementById('log-user').value.trim();
                pass = document.getElementById('log-pass').value;
                
                if (!user || !pass) return alert("❌ Username နှင့် Password ဖြည့်ရန် လိုအပ်ပါသည်!");
                if (!user.startsWith('@')) return alert("❌ Telegram Username ၏ အရှေ့တွင် '@' ပါရပါမည်!");
            }

            try {
                const res = await fetch('/api/auth', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type: type, user: user, pass: pass }) 
                });
                const data = await res.json();
                
                if (data.success) {
                    if (type === 'register') {
                        alert("✅ အကောင့်ဖွင့်ခြင်း အောင်မြင်ပါသည်! ကျေးဇူးပြု၍ Login ဝင်ပါ။");
                        toggleAuth('login');
                    } else {
                        // 🔴 ဤနေရာတွင် မူလ Code အတိုင်း Page ကို အောင်မြင်စွာ Refresh လုပ်ပေးပါမည်
                        localStorage.setItem('user', user); 
                        location.reload(); 
                    }
                } else {
                    alert("❌ Error: " + data.msg);
                }
            } catch (error) {
                console.error(error);
                alert("❌ System Error: ကျေးဇူးပြု၍ ခဏစောင့်ပြီး ပြန်စမ်းကြည့်ပါ။");
            }
        }
    function logout() { localStorage.removeItem('user'); location.reload(); }

    function init() {
        document.getElementById('g-list').innerHTML = games.map(g => `
            <div class="game-card" onclick="selG(${g.id})">
                <div class="img-box">
                    <img src="${g.img}">
                </div>
                <b>${g.name}</b>
            </div>`).join('');
    }

    function selG(id) {
        const g = games.find(i => i.id === id); sel_srv = id;
        document.getElementById('h-sec').style.display='none';
        document.getElementById('o-sec').style.display='block';
        document.getElementById('g-title').innerText = g.name;
        document.getElementById('cat-container').innerHTML = g.cat_order.map((c, i) => 
            `<div class="tab-btn ${i===0?'active':''}" onclick="renderP('${c}', this)">${c}</div>`).join('');
        renderP(g.cat_order[0], document.querySelector('.tab-btn.active'));
    }

    function getPkgImg(text) {
        let lowerText = text.toLowerCase();
        let num = text.replace(/[^0-9]/g, ''); 

        if (lowerText.includes("50+50")) return "/static/dia50+50.png";
        if (lowerText.includes("150+150")) return "/static/dia150+150.png";
        if (lowerText.includes("250+250")) return "/static/dia250+250.png";
        if (lowerText.includes("500+500")) return "/static/dia500+500.png";
        if (lowerText.includes("weekly elite")) return "/static/weeklyelite.png";
        if (lowerText.includes("monthly epic")) return "/static/monthlyepic.png";
        if (lowerText.includes("weekly")) return "/static/weeklypass.png";
        if (lowerText.includes("twilight")) return "/static/twilight.png";
        
        // Diamond ပုံများအတွက် (dia11.png, dia22.png, ...)
        return `/static/dia${num}.png`;
    }

    function renderP(cat, btn) {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const pkgs = games.find(i => i.id === sel_srv).cats[cat];
        document.getElementById('p-list').innerHTML = pkgs.map(p => `
            <div class="pkg-card" onclick="selP(this, '${p.d}', '${p.p}')">
                <img src="${getPkgImg(p.d)}" class="pkg-dia-img" onerror="this.src='/static/dia1.png'"> 
                <div class="pkg-info">
                    <span class="pkg-d-text">${p.d}</span>
                    <span class="pkg-p-text">${p.p} Ks</span>
                </div>
            </div>`).join('');
    }

    function selP(el, d, p) {
        document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected'));
        el.classList.add('selected'); sel_pkg=d; sel_prc=p;
    }

    function setPay(img, num, type, name) {
        document.querySelectorAll('.pay-icons img').forEach(i => i.classList.remove('active'));
        img.classList.add('active');
        document.getElementById('pay-num').innerText = num;
        document.getElementById('pay-type').innerText = type + " Account";
        document.getElementById('pay-name').innerText = "Name - " + name;
    }

    function copyNum(e) {
        e.preventDefault();
        const numToCopy = document.getElementById('pay-num').innerText;
        navigator.clipboard.writeText(numToCopy).then(() => {
            const btn = e.target.closest('button');
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            btn.style.background = '#10b981';
            btn.style.color = 'white';
            setTimeout(() => {
                btn.innerHTML = originalHTML;
                btn.style.background = '#334155';
            }, 2000);
        });
    }

    async function handleOrder(e) {
        e.preventDefault();
        if(!sel_pkg) return alert("Please select a package");
        const btn = document.getElementById('submitBtn');
        btn.innerText = "Processing..."; btn.disabled = true;

        const fd = new FormData();
        fd.append('tg_user', currentUser);
        fd.append('uid', document.getElementById('uid').value);
        fd.append('zid', document.getElementById('zid').value);
        fd.append('srv', games.find(i => i.id === sel_srv).name);
        fd.append('pkg', sel_pkg);
        fd.append('price', sel_prc);
        fd.append('photo', document.getElementById('photo').files[0]);

        try {
            const r = await fetch('/order', { method:'POST', body:fd });
            if(await r.text() === "Success") {
                Swal.fire({
                    title: 'Order Success!',
                    text: 'သင်၏အော်ဒါတင်ခြင်း အောင်မြင်ပါသည်။ ခဏစောင့်ပေးပါခင်ဗျာ။',
                    icon: 'success',
                    confirmButtonColor: '#fbbf24',
                    confirmButtonText: 'OK',
                    background: '#1e293b',
                    color: '#fff'
                }).then(() => {
                    location.reload();
                });
            } else {
                Swal.fire({ title: 'Failed!', text: 'အော်ဒါတင်ခြင်း မအောင်မြင်ပါ။', icon: 'error', background: '#1e293b', color: '#fff' });
                btn.innerText = "PLACE ORDER"; btn.disabled = false;
            }
        } catch(err) {
            Swal.fire({ title: 'Error!', text: 'စနစ်ချို့ယွင်းချက် ဖြစ်ပေါ်နေပါသည်။', icon: 'error', background: '#1e293b', color: '#fff' });
            btn.innerText = "PLACE ORDER"; btn.disabled = false;
        }
    }
    function goH() {
        document.getElementById('h-sec').style.display='block';
        document.getElementById('o-sec').style.display='none';
        document.getElementById('top-sec').style.display='none';
        document.getElementById('hist-sec').style.display='none';
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        document.getElementById('nav-home').classList.add('active');
        document.getElementById('privacy-sec').style.display = 'none';
        document.getElementById('terms-sec').style.display = 'none';
    }
function showPrivacy() {
            document.getElementById('h-sec').style.display = 'none';
            document.getElementById('o-sec').style.display = 'none';
            document.getElementById('top-sec').style.display = 'none';
            document.getElementById('hist-sec').style.display = 'none';
            document.getElementById('terms-sec').style.display = 'none';
            document.getElementById('privacy-sec').style.display = 'block';
        }

        function showTerms() {
            document.getElementById('h-sec').style.display = 'none';
            document.getElementById('o-sec').style.display = 'none';
            document.getElementById('top-sec').style.display = 'none';
            document.getElementById('hist-sec').style.display = 'none';
            document.getElementById('privacy-sec').style.display = 'none';
            document.getElementById('terms-sec').style.display = 'block';
        }
    async function showTop() {
        document.getElementById('h-sec').style.display='none';
        document.getElementById('o-sec').style.display='none';
        document.getElementById('hist-sec').style.display='none';
        document.getElementById('top-sec').style.display='block';
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        document.getElementById('nav-top').classList.add('active');

        try {
            const r = await fetch(`/api/top10?user=${currentUser}`);
            const data = await r.json();
            let topHTML = data.top10.map((u, i) => `
                <div style="background:#1e293b;padding:15px;margin-bottom:10px;border-radius:12px;display:flex;justify-content:space-between;border-left:5px solid ${i===0?'#fbbf24':i===1?'#94a3b8':i===2?'#b45309':'#334155'};">
                    <span><b>#${i+1}</b> ${u.display_name}</span>
                    <b style="color:#fbbf24;">${u.totalSpent.toLocaleString()} Ks</b>
                </div>`).join('');
            document.getElementById('top-list').innerHTML = topHTML + `
                <div class="my-rank-card">
                    <p style="margin:0; font-size:12px; font-weight:bold;">YOUR CURRENT RANK</p>
                    <h3 style="margin:5px 0;">#${data.userRank}</h3>
                    <p style="margin:0; font-size:14px;">Total Spent: <b>${data.userSpent.toLocaleString()} Ks</b></p>
                </div>`;
        } catch(e) { console.error(e); }
    }

    async function showH() {
        document.getElementById('h-sec').style.display='none';
        document.getElementById('o-sec').style.display='none';
        document.getElementById('top-sec').style.display='none';
        document.getElementById('hist-sec').style.display='block';
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        document.getElementById('nav-hist').classList.add('active');
        try {
            const r = await fetch('/api/history');
            const data = await r.json();
            const myHist = data.filter(o => o.tg_user === currentUser);
            document.getElementById('hist-list').innerHTML = myHist.map(o => {
                // Status အရ အရောင်နှင့် Icon သတ်မှတ်ခြင်း (Rejected အစား Cancelled သို့ ပြောင်းထားပါသည်)
                    let statusColor = o.status === 'Completed' ? '#10b981' : (o.status === 'Cancelled' ? '#ef4444' : '#fbbf24');
                    let stIcon = o.status === 'Completed' ? '✅' : (o.status === 'Cancelled' ? '❌' : '⏳');
                    
                    // 🔴 Cancel ဖြစ်ပါက Admin ရွေးချယ်ခဲ့သည့် အကြောင်းပြချက်ကို ပြသမည်
                    let cancelMsg = '';
                    if (o.status === 'Cancelled') {
                        let reasonTxt = o.reason ? o.reason : "အချက်အလက် မှားယွင်းနေသဖြင့် ပယ်ဖျက်လိုက်ပါသည်။";
                        cancelMsg = `
                        <div style="background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 10px; margin-top: 12px; border-radius: 4px; font-size: 13px; color: #fca5a5;">
                            ⚠️ <b>ပယ်ဖျက်လိုက်ပါသည်:</b> ${reasonTxt} <br><br>
                            <i>ကျေးဇူးပြု၍ သေချာပြန်စစ်ပြီး Order အသစ် ထပ်တင်ပေးပါ။ (ငွေလွှဲပြဿနာဖြစ်ပါက @Bby_kiwii7 သို့ ဆက်သွယ်မေးမြန်းနိုင်ပါသည်)</i>
                        </div>`;
                    }

                    // 📦 Box Design အသစ် (Cancel Message နှင့် Icon ပါဝင်ပြီးသား)
                    return `
                    <div style="background:#1e293b;padding:15px;margin-bottom:10px;border-radius:12px;border-left:5px solid ${statusColor};">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b>💎 ${o.pkg}</b>
                            <span style="color:${statusColor}; font-weight:bold;">${stIcon} ${o.status}</span>
                        </div>
                        <div style="color:#94a3b8; font-size:12px; margin-top:5px;">
                            ID: ${o.uid} | Price: ${parseInt(o.price).toLocaleString()} Ks
                        </div>
                        ${cancelMsg}
                    </div>
                    `;
            }).join('');
        } catch (error) { document.getElementById('hist-list').innerHTML = "Failed to load history."; }
    }
</script>

<a href="https://t.me/Bby_kiwii7" target="_blank" class="cs-float">💬</a>
</body></html>
'''

# --- 🚀 BACKEND ---

@app.route('/')
def index():
    return render_template_string(HTML_CODE.replace("JSON_DATA_HERE", json.dumps(GAMES_DATA)))

@app.route('/api/auth', methods=['POST'])
def auth():
    try:
        data = request.json
        utype, user, psw = data['type'], data['user'], data['pass']
        
        if utype == 'register':
            if users_col.find_one({"user": user}): 
                return jsonify({"success": False, "msg": "User already exists!"})
            
            # 🛡️ အကောင့်သစ်များကို လုံခြုံသော Hash ဖြင့် သိမ်းဆည်းခြင်း
            hashed_pw = generate_password_hash(psw)
            users_col.insert_one({"user": user, "pass": hashed_pw})
            return jsonify({"success": True})
            
        else:
            u = users_col.find_one({"user": user})
            if u:
                stored_pass = u.get('pass', '')
                is_valid = False
                
                # စကားဝှက်သည် Hash ပြောင်းပြီးသားလား (အသစ်လား) စစ်ဆေးခြင်း
                if stored_pass.startswith('pbkdf2:') or stored_pass.startswith('scrypt:'):
                    is_valid = check_password_hash(stored_pass, psw)
                else:
                    # အကောင့်ဟောင်း (Password အစိမ်း) ဖြစ်နေလျှင် တိုက်ရိုက်စစ်ဆေးခြင်း
                    is_valid = (stored_pass == psw)
                    
                    # 💡 အရေးကြီး: အကောင့်ဟောင်းဖြစ်ပြီး Password မှန်ကန်ပါက Hash သို့ အလိုအလျောက် ပြောင်းလဲသိမ်းဆည်းပေးခြင်း
                    if is_valid:
                        new_hash = generate_password_hash(psw)
                        users_col.update_one({"_id": u["_id"]}, {"$set": {"pass": new_hash}})
                        
                if is_valid:
                    return jsonify({"success": True})
                    
            return jsonify({"success": False, "msg": "Invalid Login!"})
            
    except Exception as e: 
        return jsonify({"success": False, "msg": str(e)})
        
@app.route('/order', methods=['POST'])
def order():
    try:
        tg_user = request.form.get('tg_user')
        uid = request.form.get('uid')
        zid = request.form.get('zid')
        pkg = request.form.get('pkg')
        srv = request.form.get('srv')
        photo = request.files.get('photo')
        
        # --- 🛡️ SECURITY PATCH: ဈေးနှုန်းကို Backend မှ တိုက်စစ်ခြင်း ---
        actual_price = None
        
        # GAMES_DATA ထဲတွင် Server နှင့် Package နာမည်ကို လိုက်ရှာပြီး ဈေးနှုန်းအစစ်ကို ဆွဲထုတ်ပါမည်
        for server in GAMES_DATA:
            if server['name'] == srv:
                for cat_items in server['cats'].values():
                    for item in cat_items:
                        if item['d'] == pkg:
                            actual_price = int(item['p'])
                            break
                    if actual_price is not None:
                        break
            if actual_price is not None:
                break
        
        # အကယ်၍ မသမာသူက Package နာမည်ကိုပါ ထပ်ခိုးပြင်လာခဲ့လျှင် Order ကို လုံးဝ ပယ်ချပါမည်
        if actual_price is None:
            return "❌ Error: Invalid Server or Package!", 400
        
        # အစစ်အမှန် ဈေးနှုန်းကိုသာ အသုံးပြုပါမည်
        price = actual_price 
        # ----------------------------------------------------------------
        
        order_date = datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%d/%m/%Y %I:%M %p")
        oid = orders_col.insert_one({"tg_user": tg_user, "uid": uid, "zone": zid, "pkg": pkg, "srv": srv, "price": price, "status": "Pending", "date": order_date}).inserted_id
        
        msg_caption = f"""<b>🛍️ NEW ORDER RECEIVED</b>
━━━━━━━━━━━━━━━
👤 <b>Buyer:</b> {tg_user}
🌍 <b>Server:</b> {srv}
🆔 <b>Game ID:</b> <code>{uid} ({zid})</code>

💎 <b>Package:</b> {pkg}
💰 <b>Price:</b> {price:,} Ks
━━━━━━━━━━━━━━━
⏳ <b>Status:</b> Pending"""

        reply_markup = {"inline_keyboard": [
            [{"text": "✅ အောင်မြင်ပါသည် (Done)", "callback_data": f"st_Completed_None_{str(oid)}"}],
            [{"text": "❌ Cancel (ID မှား)", "callback_data": f"st_Cancelled_WrongID_{str(oid)}"}],
            [{"text": "❌ Cancel (ငွေမပြည့်)", "callback_data": f"st_Cancelled_BadReceipt_{str(oid)}"}],
            [{"text": "❌ Cancel (ငွေလွှဲပြေစာမှား)", "callback_data": f"st_Cancelled_Other_{str(oid)}"}]
        ]}
        
        # စာနှင့် ပုံကို တစ်စောင်တည်း ပေါင်း၍ ပို့ခြင်း (Send Photo with Caption)
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
            data={
                'chat_id': CHAT_ID, 
                'caption': msg_caption, 
                'parse_mode': 'HTML',
                'reply_markup': json.dumps(reply_markup)
            }, 
            files={'photo': photo}
        )
        
        return "Success"
        
    except Exception as e: 
        return str(e), 500

@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    try:
        import requests
        from bson.objectid import ObjectId

        data = request.json
        if "callback_query" in data:
            cb = data["callback_query"]
            call_data = cb.get("data", "")
            
            # ခလုတ် Data ဖမ်းယူခြင်း
            if call_data.startswith('st_'):
                parts = call_data.split('_')
                status = parts[1]
                # ခလုတ်အဟောင်းနဲ့ အသစ် ရောနှိပ်မိရင်တောင် Error မတက်အောင် ကာကွယ်ထားပါသည်
                reason_code = parts[2] if len(parts) > 2 else ""
                oid = parts[3] if len(parts) > 3 else (parts[2] if len(parts) > 2 else "")
                
                # 🔴 အကြောင်းရင်း (Reason) ပြင်ဆင်ခြင်း
                cancel_reason = ""
                if status == 'Cancelled':
                    if reason_code == "WrongID":
                        cancel_reason = "Game ID (သို့) Zone ID မှားယွင်းနေပါသည်။"
                    elif reason_code == "BadReceipt":
                        cancel_reason = "ကျသင့်ငွေ မပြည့်ခြင်းကြောင့် ဖြစ်ပါသည်။"
                    else:
                        cancel_reason = "ငွေလွှဲပြေစာ မှားယွင်းနေသဖြင့် ပယ်ဖျက်လိုက်ပါသည်။"

                # 💾 Database Update လုပ်ခြင်း
                update_data = {"status": status}
                if status == 'Cancelled':
                    update_data["reason"] = cancel_reason

                # Database တွင် Status သွားပြောင်းပါမည်
                orders_col.update_one({"_id": ObjectId(oid)}, {"$set": update_data})
                
                # 📩 Telegram Group ထဲက စာကို Update လုပ်ခြင်း
                msg_id = cb["message"]["message_id"]
                chat_id = cb["message"]["chat"]["id"]
                status_icon = '✅' if status == 'Completed' else '❌'
                
                caption = f"<b>🛍️ ORDER UPDATE</b>\n━━━━━━━━━━━━━━━\nOrder ID: {oid}\n{status_icon} Status: <b>{status}</b>"
                if status == 'Cancelled':
                    caption += f"\n⚠️ Reason: {cancel_reason}"
                    
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption", 
                    json={'chat_id': chat_id, 'message_id': msg_id, 'caption': caption, 'parse_mode': 'HTML'})
                
                # ✅ ခလုတ်နှိပ်ကြောင်း Telegram ကို အကြောင်းပြန်ခြင်း (Loading ရပ်သွားရန်)
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", 
                    json={'callback_query_id': cb['id'], 'text': f'Order {status} updated!'})
                
        return "OK", 200
        
    except Exception as e:
        # 🔴 Error တက်ပါက Render သွားစစ်စရာမလိုဘဲ Telegram Group ထဲသို့ Error Message ပို့ပေးမည့်စနစ်
        import traceback, requests
        error_details = traceback.format_exc()
        error_msg = f"⚠️ <b>Webhook Error တက်နေပါသည်</b> ⚠️\n\n<pre>{error_details[-500:]}</pre>"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={'chat_id': CHAT_ID, 'text': error_msg, 'parse_mode': 'HTML'})
        return "Error", 500

@app.route('/api/history')
def history():
    hist = list(orders_col.find().sort("_id", -1).limit(30))
    for h in hist: h['_id'] = str(h['_id'])
    return jsonify(hist)

@app.route('/api/top10')
def top10():
    try:
        current_user = request.args.get('user')
        pipeline = [{"$match": {"status": "Completed", "tg_user": {"$nin": ADMIN_USERNAMES}}}, {"$group": {"_id": "$tg_user", "totalSpent": {"$sum": "$price"}}}, {"$sort": {"totalSpent": -1}}]
        all_ranks = list(orders_col.aggregate(pipeline))
        
        user_rank, user_spent = 'N/A', 0
        for i, u in enumerate(all_ranks):
            if u['_id'] == current_user: 
                user_rank, user_spent = i + 1, u['totalSpent']
                break
                
        # 🔴 Top 10 အတွက် Username အစား Name ကို Database မှ လှမ်းယူခြင်း
        top_10_list = all_ranks[:10]
        for u in top_10_list:
            user_data = users_col.find_one({"user": u["_id"]})
            if user_data and "name" in user_data:
                u["display_name"] = user_data["name"] # Name တွေ့ပါက Name ကိုသုံးမည်
            else:
                u["display_name"] = u["_id"] # မတွေ့ပါက မူလ Username ကိုသာပြမည်

        return jsonify({"top10": top_10_list, "userRank": user_rank, "userSpent": user_spent})
        
    except Exception as e:
        print(e)
        return jsonify({"top10": [], "userRank": "N/A", "userSpent": 0})
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
