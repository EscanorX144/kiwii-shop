import os, json, requests, tempfile
from flask import Flask, render_template_string, request, redirect, session
from datetime import datetime
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "KIWII_SUPER_SECRET_2024")

# Render အတွက် temp directory မှာ db.json သိမ်းမယ်
DB_PATH = os.path.join(tempfile.gettempdir(), 'db.json')
print(f"Database path: {DB_PATH}")
db = TinyDB(DB_PATH)

# --- CONFIGURATION ---
PAY_DATA = {
    "Number": "09775394979",
    "Name": "Thansin Kyaw",
    "Note": "Payment"
}
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok")
CHAT_ID = os.environ.get("CHAT_ID", "7089720301")
CS_LINK = "https://t.me/Bby_kiwii7"
ADMIN_PASS = os.environ.get("ADMIN_PASS", "kiwii123")
ADMIN_URL = "https://kiwiigameshop.onrender.com/admin"

# --- DIAMOND DATA ---
GAMES_DATA = [
    {
        "name": "Normal Server",
        "img": "https://img.icons8.com/color/144/mobile-legends.png",
        "cats": {
            "Normal Dia": [{"d": "11", "p": "700"}, {"d": "22", "p": "1400"}, {"d": "33", "p": "2100"}, {"d": "44", "p": "2800"}, {"d": "56", "p": "3500"}, {"d": "112", "p": "7000"}, {"d": "86", "p": "4750"}, {"d": "172", "p": "9450"}, {"d": "257", "p": "13800"}, {"d": "279", "p": "15200"}, {"d": "343", "p": "18600"}, {"d": "429", "p": "23350"}, {"d": "514", "p": "27650"}, {"d": "600", "p": "32650"}, {"d": "706", "p": "37450"}, {"d": "792", "p": "42200"}, {"d": "878", "p": "46850"}, {"d": "963", "p": "51200"}, {"d": "1049", "p": "56000"}, {"d": "1135", "p": "60850"}, {"d": "1412", "p": "74900"}, {"d": "2195", "p": "114200"}, {"d": "3688", "p": "190500"}, {"d": "5532", "p": "287000"}, {"d": "7376", "p": "381000"}, {"d": "9288", "p": "475200"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(5900 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+", "p": "3050"}, {"d": "150+", "p": "9100"}, {"d": "250+", "p": "14650"}, {"d": "500+", "p": "29950"}],
            "Bundle Pack": [{"d": "Weekly elite bundle", "p": "3050"}, {"d": "Monthly epic bundle", "p": "15350"}, {"d": "Twilight pass", "p": "31500"}]
        }
    },
    {
        "name": "Indonesia (🇮🇩)",
        "img": "https://img.icons8.com/color/144/indonesia.png",
        "cats": {
            "Indo Dia": [{"d": "5", "p": "450"}, {"d": "12", "p": "950"}, {"d": "19", "p": "1500"}, {"d": "28", "p": "2200"}, {"d": "44", "p": "3300"}, {"d": "59", "p": "4300"}, {"d": "85", "p": "5850"}, {"d": "170", "p": "11700"}, {"d": "240", "p": "16600"}, {"d": "296", "p": "20500"}, {"d": "408", "p": "28000"}, {"d": "568", "p": "37500"}, {"d": "875", "p": "58500"}, {"d": "2010", "p": "123500"}, {"d": "4830", "p": "299000"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(7500 * i)} for i in range(1, 11)],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "45000"}]
        }
    },
    {
        "name": "Malaysia & Singapore (🇲🇾🇸🇬)",
        "img": "https://img.icons8.com/color/144/malaysia.png",
        "cats": {
            "Mal & SGP Dia": [{"d": "14", "p": "1050"}, {"d": "42", "p": "3100"}, {"d": "56", "p": "4150"}, {"d": "70", "p": "5050"}, {"d": "140", "p": "10100"}, {"d": "210", "p": "15100"}, {"d": "284", "p": "20200"}, {"d": "355", "p": "25200"}, {"d": "429", "p": "30300"}, {"d": "583", "p": "41200"}, {"d": "716", "p": "50200"}, {"d": "870", "p": "61400"}, {"d": "1145", "p": "80500"}, {"d": "1446", "p": "100500"}, {"d": "2162", "p": "150500"}, {"d": "2976", "p": "201000"}, {"d": "3606", "p": "223000"}, {"d": "6012", "p": "371000"}, {"d": "7502", "p": "503500"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8400 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+", "p": "4100"}, {"d": "150+", "p": "12000"}, {"d": "250+", "p": "19700"}, {"d": "500+", "p": "40000"}],
            "Bundle Pack": [{"d": "Weekly Elite Bundle", "p": "4000"}, {"d": "Monthly Epic Bundle", "p": "19600"}, {"d": "Twilight Pass", "p": "46000"}]
        }
    },
    {
        "name": "Philippines (🇵🇭)",
        "img": "https://img.icons8.com/color/144/philippines.png",
        "cats": {
            "Philippines Dia": [{"d": "11", "p": "750"}, {"d": "22", "p": "1500"}, {"d": "56", "p": "3500"}, {"d": "112", "p": "7000"}, {"d": "223", "p": "14000"}, {"d": "336", "p": "21300"}, {"d": "570", "p": "36000"}, {"d": "1163", "p": "70500"}, {"d": "2398", "p": "140000"}, {"d": "6042", "p": "350000"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(6500 * i)} for i in range(1, 11)],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "35500"}]
        }
    },
    {
        "name": "Russia (🇷🇺)",
        "img": "https://img.icons8.com/color/144/russian-federation.png",
        "cats": {
            "Russia Dia": [{"d": "35", "p": "2750"}, {"d": "55", "p": "4450"}, {"d": "165", "p": "13000"}, {"d": "275", "p": "22000"}, {"d": "565", "p": "44500"}, {"d": "1155", "p": "88000"}, {"d": "1765", "p": "182000"}, {"d": "2975", "p": "220000"}, {"d": "6000", "p": "435000"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8600 * i)} for i in range(1, 11)],
        }
    }
]

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, games=GAMES_DATA, pay=PAY_DATA, cs=CS_LINK)

@app.route('/order', methods=['POST'])
def order():
    order_id = str(int(datetime.now().timestamp()))
    u_id = request.form.get('u')
    z_id = request.form.get('z')
    pkg = request.form.get('p')
    amt = request.form.get('a')
    server = request.form.get('server_name')
    photo = request.files.get('photo')

    msg = f"🔔 *New Order!*\nID: #{order_id}\nServer: {server}\nGameID: {u_id} ({z_id})\nPkg: {pkg}\nAmt: {amt} Ks\n\nCheck Admin: {ADMIN_URL}"
    
    if photo and photo.filename != '':
        try:
            files = {'photo': (photo.filename, photo.read(), photo.content_type)}
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"},
                files=files,
                timeout=30
            )
        except Exception as e:
            print(f"Telegram send error: {e}")
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": msg + "\n\n(Photo upload failed)", "parse_mode": "Markdown"},
                timeout=30
            )
    else:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"},
            timeout=30
        )
    
    db.insert({'id': order_id, 'server': server, 'uid': u_id, 'zid': z_id, 'pkg': pkg, 'amt': amt, 'status': 'Pending', 'time': datetime.now().strftime("%d/%m %I:%M %p")})
    
    return f"""<html><body style='background:#0f172a;color:white;text-align:center;padding:50px;'>
        <h2>Order Success! ✅</h2>
        <p>Order ID: #{order_id}</p>
        <script>
        try {{
            let h = JSON.parse(localStorage.getItem('kiwii_h') || '[]');
            h.unshift({{id:'{order_id}', s:'{server}', p:'{pkg}', a:'{amt}', t:'{datetime.now().strftime("%d/%m %I:%M %p")}'}});
            localStorage.setItem('kiwii_h', JSON.stringify(h));
        }} catch(e) {{}}
        setTimeout(()=>location.href='/', 2000);
        </script>
    </body></html>"""

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return '''
        <body style="background:#0f172a;color:white;display:flex;justify-content:center;padding:50px;">
            <form action="/login" method="post" style="background:#1e293b;padding:30px;border-radius:15px;">
                <h2 style="color:#fbbf24;">Admin Login</h2>
                <input name="pw" type="password" style="width:100%;padding:12px;margin:10px 0;border-radius:8px;border:1px solid #334155;background:#0f172a;color:white;">
                <button type="submit" style="width:100%;padding:12px;background:#fbbf24;border:none;border-radius:8px;font-weight:bold;cursor:pointer;">Login</button>
            </form>
        </body>'''
    orders = db.all()[::-1]
    return render_template_string(ADMIN_TEMPLATE, orders=orders)

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('pw') == ADMIN_PASS: 
        session['logged_in'] = True
    return redirect('/admin')

@app.route('/update/<oid>/<status>')
def update(oid, status):
    if session.get('logged_in'): 
        db.update({'status': status}, Query().id == oid)
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/admin')

@app.route('/health')
def health():
    return "OK", 200

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background:#0f172a; color:white; font-family:sans-serif; padding:15px; max-width:500px; margin:auto; padding-bottom: 80px; }
        .game-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .game-card { background: #1e293b; border: 1px solid #334155; border-radius: 15px; padding: 15px; text-align: center; cursor: pointer; position: relative; overflow: hidden; }
        .game-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(145deg, #1e293b, #0f172a); opacity: 0.8; z-index: 0; }
        .game-card img { width: 80px; height: 80px; border-radius: 12px; margin-bottom: 10px; position: relative; z-index: 1; }
        .game-card h4 { position: relative; z-index: 1; color: #fbbf24; }
        #order-section, #history-section { display: none; }
        .cat-tabs { display: flex; gap: 8px; overflow-x: auto; margin: 15px 0; padding-bottom:5px; scrollbar-width: thin; }
        .cat-tab { padding: 10px 18px; background: #1e293b; border-radius: 12px; font-size: 12px; white-space:nowrap; border:1px solid #334155; color:#94a3b8; cursor: pointer; transition: all 0.2s; }
        .cat-tab.active { background: #10b981; color: white; border-color:#10b981; }
        .pkg-grid { display:grid; grid-template-columns: 1fr 1fr; gap:12px; max-height: 400px; overflow-y:auto; padding:5px 0; }
        .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; cursor: pointer; transition: all 0.2s; }
        .pkg-card:hover { border-color: #10b981; }
        .pkg-card.selected { border: 2px solid #fbbf24; background: #1e3a8a; transform: scale(0.98); }
        .input-group { margin: 10px 0; }
        input, .file-input { width:100%; padding:14px; margin:8px 0; border-radius:12px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; }
        .file-input { padding:10px; }
        .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; cursor:pointer; color:black; margin-top: 10px; font-size: 16px; }
        .nav-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #1e293b; display: flex; padding: 12px; gap: 10px; border-top: 1px solid #334155; max-width: 500px; margin: auto; z-index: 1000; }
        .nav-btn { flex: 1; text-align: center; font-size: 13px; color: white; text-decoration: none; cursor:pointer; padding: 8px; border-radius: 8px; transition: background 0.2s; }
        .nav-btn:hover { background: #334155; }
        .nav-btn i { display: block; font-size: 20px; margin-bottom: 4px; }
        .pay-card { background:#1e293b; padding:20px; border-radius:15px; border: 1px solid #334155; margin:20px 0; text-align:center; }
        .pay-methods { display: flex; justify-content: center; gap: 25px; margin-bottom: 20px; }
        .pay-icon { display: flex; flex-direction: column; align-items: center; gap: 8px; }
        .pay-icon .icon-box { width: 50px; height: 50px; background: #0f172a; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; border: 1px solid #334155; }
        .hist-item { background: #1e293b; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid #fbbf24; }
        .hist-header { display: flex; justify-content: space-between; margin-bottom: 8px; color: #94a3b8; font-size: 12px; }
        .hist-detail { font-size: 14px; margin: 5px 0; }
        .badge { background: #10b981; padding: 3px 8px; border-radius: 12px; font-size: 11px; color: white; }
        .back-btn { background:none; color:white; border:1px solid #334155; padding:8px 15px; border-radius:8px; margin-bottom:15px; cursor: pointer; display: inline-flex; align-items: center; gap: 5px; }
        .back-btn:hover { background:#334155; }
        h2, h3 { color: #fbbf24; margin-bottom: 15px; }
        .modal { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); display:flex; align-items:center; justify-content:center; z-index:9999; }
        .modal-content { background:#1e293b; width:90%; max-width:350px; padding:25px; border-radius:20px; color:white; text-align:center; }
        .modal-btn { width:100%; padding:12px; background:#fbbf24; border:none; border-radius:10px; font-weight:bold; cursor:pointer; margin:5px 0; }
        .modal-btn.secondary { background:#334155; color:#94a3b8; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #1e293b; }
        ::-webkit-scrollbar-thumb { background: #10b981; border-radius: 5px; }
    </style>
</head>
<body>
    <div id="home-section" style="display: block;">
        <h2 style="text-align:center;">KIWII GAME SHOP</h2>
        <div class="game-grid" id="game-list"></div>
    </div>

    <div id="history-section">
        <h3>Order History</h3>
        <div id="history-list"></div>
    </div>

    <div id="order-section">
        <button class="back-btn" onclick="goHome()"><i class="fas fa-arrow-left"></i> Back</button>
        <h3 id="selected-title"></h3>
        
        <div class="cat-tabs" id="tabs"></div>
        <div class="pkg-grid" id="pkg-list"></div>
        
        <div class="pay-card">
            <div class="pay-methods">
                <div class="pay-icon"><div class="icon-box">💳</div><span>KPay</span></div>
                <div class="pay-icon"><div class="icon-box">🏦</div><span>Wave</span></div>
                <div class="pay-icon"><div class="icon-box">📱</div><span>AyaPay</span></div>
            </div>
            <div style="border-top: 1px solid #334155; padding-top: 15px;">
                <small>Payment To</small><br>
                <b style="color:#fbbf24; font-size: 18px;">{{pay.Number}}</b><br>
                <small>Name: {{pay.Name}}</small><br>
                <small style="color:#94a3b8;">Note: {{pay.Note}}</small>
            </div>
        </div>

        <form id="order-form" action="/order" method="post" enctype="multipart/form-data">
            <input type="hidden" name="server_name" id="s_name">
            <input type="number" name="u" id="user_id" placeholder="Player ID" required>
            <input type="number" name="z" id="zone_id" placeholder="Zone ID" required>
            <input id="p_val" name="p" type="hidden">
            <input id="a_val" name="a" type="hidden">
            <label style="display:block; margin-top:10px; font-size:13px; color:#94a3b8;">Upload Screenshot (Payment Slip)</label>
            <input type="file" name="photo" class="file-input" required accept="image/*">
            <button type="button" class="buy-btn" onclick="showCheck()">
                <i class="fas fa-shopping-cart"></i> CONFIRM & BUY
            </button>
        </form>
    </div>

    <div class="nav-bar">
        <div class="nav-btn" onclick="goHome()"><i class="fas fa-home"></i>Home</div>
        <div class="nav-btn" onclick="showHistory()"><i class="fas fa-history"></i>History</div>
        <a href="{{cs}}" class="nav-btn" style="text-decoration:none;"><i class="fas fa-comment"></i>CS</a>
    </div>

    <script>
    const data = {{ games | tojson }};
    
    function init() {
        const gameList = document.getElementById('game-list');
        gameList.innerHTML = data.map(game => `
            <div class="game-card" onclick="selectServer('${game.name}')">
                <div class="game-bg"></div>
                <img src="${game.img}">
                <h4>${game.name}</h4>
            </div>
        `).join('');
    }

    function selectServer(name) {
        document.getElementById('home-section').style.display = 'none';
        document.getElementById('history-section').style.display = 'none';
        document.getElementById('order-section').style.display = 'block';
        document.getElementById('selected-title').innerHTML = `<i class="fas fa-server"></i> ${name}`;
        document.getElementById('s_name').value = name;
        
        const game = data.find(g => g.name === name);
        if (!game) return;
        
        const cats = game.cats;
        const order = ["Normal Dia", "Indo Dia", "Mal & SGP Dia", "Philippines Dia", "Russia Dia", "Weekly Pass", "2X Dia", "Bundle Pack"];
        
        const sortedKeys = Object.keys(cats).sort((a, b) => {
            let indexA = order.indexOf(a);
            let indexB = order.indexOf(b);
            return (indexA === -1 ? 99 : indexA) - (indexB === -1 ? 99 : indexB);
        });

        const tabsHtml = sortedKeys.map((c, i) => `
            <div class="cat-tab ${i === 0 ? 'active' : ''}" onclick="renderPkgs('${name}','${c}',this)">${c}</div>
        `).join('');
        
        document.getElementById('tabs').innerHTML = tabsHtml;
        if (sortedKeys.length > 0) renderPkgs(name, sortedKeys[0]);
    }

    function renderPkgs(sName, cat, el) {
        if(el) { 
            document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active')); 
            el.classList.add('active'); 
        }
        
        const game = data.find(g => g.name === sName);
        if (!game || !game.cats[cat]) return;
        
        const pkgList = document.getElementById('pkg-list');
        pkgList.innerHTML = game.cats[cat].map(p => `
            <div class="pkg-card" onclick="sel(this,'${p.d}','${p.p}')">
                <div style="font-size: 20px; margin-bottom: 5px;">💎</div>
                <span>${p.d}</span><br>
                <b style="color:#fbbf24;">${Number(p.p).toLocaleString()} Ks</b>
            </div>
        `).join('');
    }

    function sel(el, d, p) {
        document.querySelectorAll('.pkg-card').forEach(c => c.classList.remove('selected'));
        el.classList.add('selected');
        document.getElementById('p_val').value = d;
        document.getElementById('a_val').value = p;
    }

    function showCheck() {
        const p_val = document.getElementById('p_val').value;
        const a_val = document.getElementById('a_val').value;
        const u_id = document.getElementById('user_id').value;
        const z_id = document.getElementById('zone_id').value;
        const server = document.getElementById('s_name').value;
        
        if (!p_val) return alert("Please select a package!");
        if (!u_id) return alert("Please enter Player ID!");
        if (!z_id) return alert("Please enter Zone ID!");

        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h3 style="color:#fbbf24;">Confirm Order</h3>
                <div style="text-align:left; margin:20px 0; background:#0f172a; padding:15px; border-radius:10px;">
                    <p><strong>Server:</strong> ${server}</p>
                    <p><strong>ID:</strong> ${u_id} (${z_id})</p>
                    <p><strong>Package:</str
