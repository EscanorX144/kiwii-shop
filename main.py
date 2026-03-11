import os, json, requests
from flask import Flask, render_template_string, request, redirect, session
from datetime import datetime
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = "KIWII_SUPER_SECRET"
db = TinyDB('db.json')

# --- CONFIGURATION ---
PAY_DATA = {
    "Number": "09775394979",
    "Name": "Thansin Kyaw",
    "Note": "Payment"
}
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
CHAT_ID = "7089720301"
CS_LINK = "https://t.me/Bby_kiwii7"
ADMIN_PASS = "kiwii123"
ADMIN_URL = "https://kiwiigameshop.onrender.com/admin"

# --- DIAMOND DATA (သေချာ အစဉ်စီထားသည်) ---
GAMES_DATA = [
    {
        "name": "Normal Server",
        "img": "https://img.icons8.com/color/144/mobile-legends.png",
        "cats": {
            "Normal Dia": [{"d": "11", "p": "700"}, {"d": "22", "p": "1400"}, {"d": "33", "p": "2100"}, {"d": "44", "p": "2800"}, {"d": "56", "p": "3500"}, {"d": "112", "p": "7000"}, {"d": "86", "p": "4750"}, {"d": "172", "p": "9450"}, {"d": "257", "p": "13800"}, {"d": "279", "p": "15200"}, {"d": "343", "p": "18600"}, {"d": "429", "p": "23350"}, {"d": "514", "p": "27650"}, {"d": "600", "p": "32650"}, {"d": "706", "p": "37450"}, {"d": "792", "p": "42200"}, {"d": "878", "p": "46850"}, {"d": "963", "p": "51200"}, {"d": "1049", "p": "56000"}, {"d": "1135", "p": "60850"}, {"d": "1412", "p": "74900"}, {"d": "2195", "p": "114200"}, {"d": "3688", "p": "190500"}, {"d": "5532", "p": "287000"}, {"d": "7376", "p": "381000"}, {"d": "9288", "p": "475200"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(5900 * i)} for i in range(1, 11)],
            "Dia 2X": [{"d": "50+", "p": "3050"}, {"d": "150+", "p": "9100"}, {"d": "250+", "p": "14650"}, {"d": "500+", "p": "29950"}],
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
            "Dia 2X": [{"d": "50+", "p": "4100"}, {"d": "150+", "p": "12000"}, {"d": "250+", "p": "19700"}, {"d": "500+", "p": "40000"}],
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
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8600 * i)} for i in range(1, 11)]
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
    if photo:
        files = {'photo': photo.read()}
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}, files=files)
    
    db.insert({'id': order_id, 'server': server, 'uid': u_id, 'zid': z_id, 'pkg': pkg, 'amt': amt, 'status': 'Pending', 'time': datetime.now().strftime("%d/%m %I:%M %p")})
    return f"<html><body style='background:#0f172a;color:white;text-align:center;padding:50px;'><h2>Order Success! ✅</h2><script>let h=JSON.parse(localStorage.getItem('kiwii_h')||'[]'); h.unshift({{id:'{order_id}', s:'{server}', p:'{pkg}', a:'{amt}', t:'{datetime.now().strftime('%d/%m %I:%M %p')}'}}); localStorage.setItem('kiwii_h', JSON.stringify(h)); setTimeout(()=>location.href='/', 1500);</script></body></html>"

@app.route('/get_status/<oid>')
def get_status(oid):
    res = db.search(Query().id == oid)
    return res[0]['status'] if res else "Pending"

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return '<body style="background:#0f172a;color:white;display:flex;justify-content:center;padding:50px;"><form action="/login" method="post"><h2>Admin Login</h2><input name="pw" type="password"><button>Login</button></form></body>'
    orders = db.all()[::-1]
    return render_template_string(ADMIN_TEMPLATE, orders=orders)

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('pw') == ADMIN_PASS: session['logged_in'] = True
    return redirect('/admin')

@app.route('/update/<oid>/<status>')
def update(oid, status):
    if session.get('logged_in'): db.update({'status': status}, Query().id == oid)
    return redirect('/admin')

# --- UI TEMPLATES ---
HTML_TEMPLATE = '''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; padding:15px; max-width:500px; margin:auto; padding-bottom: 80px; }
    .game-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .game-card { background: #1e293b; border: 1px solid #334155; border-radius: 15px; padding: 15px; text-align: center; cursor: pointer; }
    .game-card img { width: 80px; height: 80px; border-radius: 12px; margin-bottom: 10px; }
    #order-section, #history-section { display: none; }
    .cat-tabs { display: flex; gap: 8px; overflow-x: auto; margin-bottom: 15px; padding-bottom:5px; }
    .cat-tab { padding: 10px 18px; background: #1e293b; border-radius: 12px; font-size: 12px; white-space:nowrap; border:1px solid #334155; color:#94a3b8; cursor: pointer; }
    .cat-tab.active { background: #10b981; color: white; border-color:#10b981; }
    .pkg-grid { display:grid; grid-template-columns: 1fr 1fr; gap:12px; max-height: 400px; overflow-y:auto; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; cursor: pointer; }
    .pkg-card.selected { border: 2px solid #fbbf24; background: #1e3a8a; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:12px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; cursor:pointer; color:black; margin-top: 10px; }
    .nav-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #1e293b; display: flex; padding: 12px; gap: 10px; border-top: 1px solid #334155; max-width: 500px; margin: auto; z-index: 1000; }
    .nav-btn { flex: 1; text-align: center; font-size: 13px; color: white; text-decoration: none; cursor:pointer; }
    .pay-card { background:#1e293b; padding:15px; border-radius:15px; border: 1px solid #334155; margin:15px 0; text-align:center; }
    .pay-methods { display: flex; justify-content: center; gap: 20px; margin-bottom: 15px; }
    .pay-icon { display: flex; flex-direction: column; align-items: center; gap: 5px; }
    .pay-icon img { width: 45px; height: 45px; border-radius: 10px; object-fit: cover; }
    .hist-item { background: #1e293b; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid #fbbf24; position: relative; }
    .status-badge { position: absolute; right: 15px; top: 15px; font-size: 11px; padding: 4px 8px; border-radius: 6px; background: #fbbf24; color: black; font-weight: bold; }
</style></head>
<body>
    <div id="home-section">
        <h2 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h2>
        <div class="game-grid" id="game-list"></div>
    </div>

    <div id="history-section">
        <h3 style="color:#fbbf24;">Order History</h3>
        <div id="history-list"></div>
    </div>

    <div id="order-section">
        <button onclick="goHome()" style="background:none; color:white; border:1px solid #334155; padding:8px 15px; border-radius:8px; margin-bottom:15px; cursor: pointer;">← Back</button>
        <h3 id="selected-title" style="color:#fbbf24;"></h3>
        <div class="cat-tabs" id="tabs"></div>
        <div class="pkg-grid" id="pkg-list"></div>
        
        <div class="pay-card">
    <div class="pay-methods">
        <div class="pay-icon">
            <img src="https://raw.githubusercontent.com/EscanorX144/kiwii-shop/main/static/kpay.png" 
                 onerror="this.src='https://img.icons8.com/color/144/kbz-pay.png'" 
                 alt="KPay" style="width:45px; height:45px; border-radius:10px;">
            <br><span>KPay</span>
        </div>
        <div class="pay-icon">
            <img src="https://raw.githubusercontent.com/EscanorX144/kiwii-shop/main/static/wave.png" 
                 onerror="this.src='https://img.icons8.com/color/144/wave-money.png'" 
                 alt="Wave" style="width:45px; height:45px; border-radius:10px;">
            <br><span>Wave</span>
        </div>
        <div class="pay-icon">
            <img src="https://raw.githubusercontent.com/EscanorX144/kiwii-shop/main/static/ayapay.png" 
                 onerror="this.src='https://img.icons8.com/fluency/144/bank-card-back-side.png'" 
                 alt="Aya" style="width:45px; height:45px; border-radius:10px;">
            <br><span>AyaPay</span>
        </div>
    </div>
    <div style="border-top: 1px solid #334155; padding-top: 15px; margin-top:10px;">
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
            <input id="p_val" name="p" type="hidden"><input id="a_val" name="a" type="hidden">
            <label style="display:block; margin-top:10px; font-size:13px; color:#94a3b8;">Upload Screenshot (Payment Slip)</label>
            <input type="file" name="photo" required accept="image/*">
            <button type="button" class="buy-btn" onclick="showCheck()">CONFIRM & BUY</button>
        </form>
    </div>

    <div class="nav-bar">
        <div class="nav-btn" onclick="goHome()"><i class="fas fa-home"></i><br>Home</div>
        <div class="nav-btn" onclick="showHistory()"><i class="fas fa-history"></i><br>History</div>
        <a href="{{cs}}" class="nav-btn" style="text-decoration:none;"><i class="fas fa-comment"></i><br>CS</a>
    </div>

    <script>
    const data = {{ games | tojson }};
    function init() {
        document.getElementById('game-list').innerHTML = data.map(game => `
            <div class="game-card" onclick="selectServer('${game.name}')">
                <img src="${game.img}"><h4>${game.name}</h4>
            </div>`).join('');
    }
    function selectServer(name) {
        document.getElementById('home-section').style.display = 'none';
        document.getElementById('history-section').style.display = 'none';
        document.getElementById('order-section').style.display = 'block';
        document.getElementById('selected-title').innerText = name;
        document.getElementById('s_name').value = name;
        const game = data.find(g => g.name === name);
        const cats = game.cats;
        document.getElementById('tabs').innerHTML = Object.keys(cats).map((c, i) => `
            <div class="cat-tab ${i===0?'active':''}" onclick="renderPkgs('${name}','${c}',this)">${c}</div>`).join('');
        renderPkgs(name, Object.keys(cats)[0]);
    }
    function renderPkgs(sName, cat, el) {
        if(el) { document.querySelectorAll('.cat-tab').forEach(t=>t.classList.remove('active')); el.classList.add('active'); }
        const game = data.find(g => g.name === sName);
        document.getElementById('pkg-list').innerHTML = game.cats[cat].map(p => `
            <div class="pkg-card" onclick="sel(this,'${p.d}','${p.p}')">
                <span>${p.d} 💎</span><br><b>${p.p} Ks</b>
            </div>`).join('');
    }
    function sel(el, d, p) {
        document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected'));
        el.classList.add('selected');
        document.getElementById('p_val').value = d; document.getElementById('a_val').value = p;
    }
    function showCheck() {
        if(!document.getElementById('p_val').value || !document.getElementById('user_id').value) return alert("Please fill all information!");
        if(confirm("Confirm Purchase?")) document.getElementById('order-form').submit();
    }
    async function showHistory() {
        document.getElementById('home-section').style.display='none';
        document.getElementById('order-section').style.display='none';
        document.getElementById('history-section').style.display='block';
        const h = JSON.parse(localStorage.getItem('kiwii_h') || '[]');
        let html = h.length ? "" : "<div style='text-align:center; margin-top:50px; color:#94a3b8;'>No history found.</div>";
        for(let i=0; i<h.length; i++){
            const status = await fetch('/get_status/'+h[i].id).then(r=>r.text());
            html += `<div class="hist-item"><span class="status-badge">${status}</span><b>ID: #${h[i].id}</b><br><small>${h[i].s} | ${h[i].p} 💎</small><br><small style="color:#94a3b8;">${h[i].t}</small></div>`;
        }
        document.getElementById('history-list').innerHTML = html;
    }
    function goHome() { 
        document.getElementById('home-section').style.display = 'grid';
        document.getElementById('order-section').style.display = 'none';
        document.getElementById('history-section').style.display = 'none';
    }
    init();
    </script>
</body></html>
'''

ADMIN_TEMPLATE = '''
<!DOCTYPE html><html><body style="background:#0f172a;color:white;font-family:sans-serif;padding:20px;">
    <h2>Admin Panel</h2>
    {% for o in orders %}
    <div style="background:#1e293b;padding:15px;border-radius:10px;margin-bottom:15px; border-left: 4px solid #10b981;">
        <b>Order ID: #{{o.id}}</b> [{{o.status}}]<br>
        Server: {{o.server}}<br>
        Player: {{o.uid}} ({{o.zid}})<br>
        Package: {{o.pkg}} 💎 | Price: {{o.amt}} Ks<br>
        <div style="margin-top:10px;">
            <a href="/update/{{o.id}}/Success" style="background:#10b981; color:white; padding:5px 15px; text-decoration:none; border-radius:5px;">Success</a>
            <a href="/update/{{o.id}}/Cancel" style="background:#ef4444; color:white; padding:5px 15px; text-decoration:none; border-radius:5px; margin-left:10px;">Cancel</a>
        </div>
    </div>
    {% endfor %}
</body></html>
'''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


