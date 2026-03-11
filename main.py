import os, json, requests
from flask import Flask, render_template_string, request, redirect, session
from datetime import datetime
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = "KIWII_SUPER_SECRET"
db = TinyDB('db.json')

# --- CONFIGURATION (သင့် ID များ ပြန်စစ်ပါ) ---
PAY_NO = "09775394979"
PAY_NAME = "THANSIN KYAW"
BOT_TOKEN = "7880962383:AAGUu9y1x0Xn0P677mO6rEiv_0Xf3_r0Y_I"
CHAT_ID = "6198647551"
CS_LINK = "https://t.me/Kiwii_144"
ADMIN_PASS = "kiwii123" 

# --- DIAMOND DATA ---
GAMES_DATA = {
    "Normal Server": {
        "img": "https://img.icons8.com/color/144/mobile-legends.png",
        "cats": {
            "Normal Dia": [{"d": "11", "p": "700"}, {"d": "22", "p": "1400"}, {"d": "33", "p": "2100"}, {"d": "44", "p": "2800"}, {"d": "56", "p": "3500"}, {"d": "112", "p": "7000"}, {"d": "86", "p": "4750"}, {"d": "172", "p": "9450"}, {"d": "257", "p": "13800"}, {"d": "279", "p": "15200"}, {"d": "343", "p": "18600"}, {"d": "429", "p": "23350"}, {"d": "514", "p": "27650"}, {"d": "600", "p": "32650"}, {"d": "706", "p": "37450"}, {"d": "792", "p": "42200"}, {"d": "878", "p": "46850"}, {"d": "963", "p": "51200"}, {"d": "1049", "p": "56000"}, {"d": "1135", "p": "60850"}, {"d": "1412", "p": "74900"}, {"d": "2195", "p": "114200"}, {"d": "3688", "p": "190500"}, {"d": "5532", "p": "287000"}, {"d": "7376", "p": "381000"}, {"d": "9288", "p": "475200"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(5900 * i)} for i in range(1, 11)],
            "Dia 2X": [{"d": "50+", "p": "3050"}, {"d": "150+", "p": "9100"}, {"d": "250+", "p": "14650"}, {"d": "500+", "p": "29950"}],
            "Bundle Pack": [{"d": "Weekly elite bundle", "p": "3050"}, {"d": "Monthly epic bundle", "p": "15350"}, {"d": "Twilight pass", "p": "31500"}]
        }
    },
    "Malaysia & Singapore (🇲🇾🇸🇬)": {
        "img": "https://img.icons8.com/color/144/malaysia.png",
        "cats": {
            "Mal & SGP Dia": [{"d": "14", "p": "1050"}, {"d": "42", "p": "3100"}, {"d": "56", "p": "4150"}, {"d": "70", "p": "5050"}, {"d": "140", "p": "10100"}, {"d": "210", "p": "15100"}, {"d": "284", "p": "20200"}, {"d": "355", "p": "25200"}, {"d": "429", "p": "30300"}, {"d": "583", "p": "41200"}, {"d": "716", "p": "50200"}, {"d": "870", "p": "61400"}, {"d": "1145", "p": "80500"}, {"d": "1446", "p": "100500"}, {"d": "2162", "p": "150500"}, {"d": "2976", "p": "201000"}, {"d": "3606", "p": "223000"}, {"d": "6012", "p": "371000"}, {"d": "7502", "p": "503500"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8400 * i)} for i in range(1, 11)],
            "Dia 2X": [{"d": "50+", "p": "4100"}, {"d": "150+", "p": "12000"}, {"d": "250+", "p": "19700"}, {"d": "500+", "p": "40000"}],
            "Bundle Pack": [{"d": "Weekly Elite Bundle", "p": "4000"}, {"d": "Monthly Epic Bundle", "p": "19600"}, {"d": "Twilight Pass", "p": "46000"}]
        }
    },
    "Indonesia (🇮🇩)": {
        "img": "https://img.icons8.com/color/144/indonesia.png",
        "cats": {
            "Indo Dia": [{"d": "5", "p": "450"}, {"d": "12", "p": "950"}, {"d": "19", "p": "1500"}, {"d": "28", "p": "2200"}, {"d": "44", "p": "3300"}, {"d": "59", "p": "4300"}, {"d": "85", "p": "5850"}, {"d": "170", "p": "11700"}, {"d": "240", "p": "16600"}, {"d": "296", "p": "20500"}, {"d": "408", "p": "28000"}, {"d": "568", "p": "37500"}, {"d": "875", "p": "58500"}, {"d": "2010", "p": "123500"}, {"d": "4830", "p": "299000"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(7500 * i)} for i in range(1, 11)],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "45000"}]
        }
    },
    "Russia (🇷🇺)": {
        "img": "https://img.icons8.com/color/144/russian-federation.png",
        "cats": {
            "Russia Dia": [{"d": "35", "p": "2750"}, {"d": "55", "p": "4450"}, {"d": "165", "p": "13000"}, {"d": "275", "p": "22000"}, {"d": "565", "p": "44500"}, {"d": "1155", "p": "88000"}, {"d": "1765", "p": "182000"}, {"d": "2975", "p": "220000"}, {"d": "6000", "p": "435000"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8600 * i)} for i in range(1, 11)]
        }
    },
    "Philippines (🇵🇭)": {
        "img": "https://img.icons8.com/color/144/philippines.png",
        "cats": {
            "Philippines Dia": [{"d": "11", "p": "750"}, {"d": "22", "p": "1500"}, {"d": "56", "p": "3500"}, {"d": "112", "p": "7000"}, {"d": "223", "p": "14000"}, {"d": "336", "p": "21300"}, {"d": "570", "p": "36000"}, {"d": "1163", "p": "70500"}, {"d": "2398", "p": "140000"}, {"d": "6042", "p": "350000"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(6500 * i)} for i in range(1, 11)],
            "Dia 2X": [{"d": "50+", "p": "3600"}, {"d": "150+", "p": "10500"}, {"d": "250+", "p": "17200"}, {"d": "500+", "p": "34500"}],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "35500"}]
        }
    }
}

# --- ROUTES ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, games=GAMES_DATA, pay_no=PAY_NO, name=PAY_NAME, cs=CS_LINK)

@app.route('/order', methods=['POST'])
def order():
    order_id = str(int(datetime.now().timestamp()))
    data = {
        'id': order_id,
        'server': request.form.get('server_name'),
        'uid': request.form.get('u'),
        'zid': request.form.get('z'),
        'pkg': request.form.get('p'),
        'amt': request.form.get('a'),
        'status': 'Pending',
        'time': datetime.now().strftime("%d/%m %I:%M %p")
    }
    db.insert(data)
    
    # Send to Telegram
    msg = f"🔔 *New Order!*\nID: #{order_id}\nServer: {data['server']}\nGameID: {data['uid']} ({data['zid']})\nPkg: {data['pkg']}\nAmt: {data['amt']} Ks\n\n[Check Admin Panel to Update Status]"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    
    return f"<h1>Success! ID: #{order_id}</h1><script>let h=JSON.parse(localStorage.getItem('kiwii_h')||'[]'); h.unshift({{id:'{order_id}', s:'{data['server']}', p:'{data['pkg']}', a:'{data['amt']}', t:'{data['time']}'}}); localStorage.setItem('kiwii_h', JSON.stringify(h)); setTimeout(()=>location.href='/', 1500);</script>"

@app.route('/get_status/<oid>')
def get_status(oid):
    res = db.search(Query().id == oid)
    return res[0]['status'] if res else "Unknown"

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return '<body style="background:#0f172a;color:white;display:flex;justify-content:center;padding:50px;"><form action="/login" method="post"><h2>Admin Login</h2><input name="pw" type="password" style="padding:10px;"><button style="padding:10px;">Login</button></form></body>'
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

# --- UI TEMPLATES (HTML/CSS) ---
HTML_TEMPLATE = '''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; padding:15px; max-width:500px; margin:auto; }
    .game-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
    .game-card { background: #1e293b; border: 1px solid #334155; border-radius: 15px; padding: 15px; text-align: center; cursor: pointer; }
    .game-card img { width: 60px; height: 60px; border-radius: 12px; margin-bottom: 10px; }
    #order-section, #history-section, #check-modal { display: none; }
    .cat-tabs { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 10px; margin-bottom: 15px; }
    .cat-tab { padding: 10px 18px; background: #1e293b; border-radius: 12px; cursor: pointer; border: 1px solid #334155; font-size: 12px; white-space: nowrap; color: #94a3b8; }
    .cat-tab.active { background: #10b981; color: white; }
    .pkg-grid { display:grid; grid-template-columns: 1fr 1fr; gap:12px; max-height: 400px; overflow-y: auto; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; cursor:pointer; text-align:center; }
    .pkg-card.selected { border: 2px solid #fbbf24; background: #1e3a8a; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:12px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; cursor:pointer; }
    .back-btn { background: #334155; color: white; border: none; padding: 8px 15px; border-radius: 8px; margin-bottom: 15px; }
    .nav-btn { flex: 1; padding: 12px; text-align: center; background:#1e293b; border-radius: 10px; text-decoration: none; color:white; font-size: 13px; }
    .hist-item { background: #1e293b; padding: 12px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #fbbf24; }
    .status-badge { font-size: 10px; padding: 2px 6px; border-radius: 4px; background: #334155; color: #fbbf24; }
    .modal { position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:100; display:flex; align-items:center; justify-content:center; padding:20px; box-sizing:border-box; }
</style></head>
<body>
    <div id="home-section">
        <h2 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h2>
        <div class="game-grid" id="game-list"></div>
        <div style="display:flex; gap:10px; margin-top:20px;">
            <div class="nav-btn" onclick="showHistory()" style="background:#3b82f6;">📜 History</div>
            <a href="{{cs}}" class="nav-btn">💬 CS Help</a>
        </div>
    </div>

    <div id="history-section">
        <button class="back-btn" onclick="goHome()">← Back</button>
        <h3 style="color:#fbbf24;">Order History</h3>
        <div id="history-list"></div>
    </div>

    <div id="order-section">
        <button class="back-btn" onclick="goHome()">← Back</button>
        <h3 id="selected-title" style="color:#fbbf24; margin:0 0 15px 0;"></h3>
        <div class="cat-tabs" id="tabs"></div>
        <div class="pkg-grid" id="pkg-list"></div>
        <div style="background:#1e3a8a; padding:15px; border-radius:15px; text-align:center; margin:15px 0; border: 1px dashed #fbbf24;">
            <b>{{pay_no}}</b><br><small>NAME: {{name}}</small>
            <p style="color:#fbbf24; font-size:11px; margin-top:5px;">⚠️ Note - Payment ပဲရေးပါ</p>
        </div>
        <form id="order-form" action="/order" method="post" enctype="multipart/form-data">
            <input type="hidden" name="server_name" id="s_name">
            <input type="number" name="u" id="user_id" placeholder="Game Player ID" required>
            <input type="number" name="z" id="zone_id" placeholder="Zone ID" required>
            <input id="p_val" name="p" type="hidden"><input id="a_val" name="a" type="hidden">
            <input type="file" name="photo" id="file_input" required accept="image/*">
            <button type="button" class="buy-btn" onclick="showCheck()">BUY NOW</button>
        </form>
    </div>

    <div id="check-modal" class="modal">
        <div style="background:#1e293b; padding:25px; border-radius:20px; width:100%;">
            <h3 style="color:#fbbf24; margin-top:0;">Confirm Order</h3>
            <p id="check-details" style="font-size:14px; line-height:1.6;"></p>
            <button class="buy-btn" onclick="document.getElementById('order-form').submit()">CONFIRM & SEND</button>
            <button class="back-btn" style="width:100%; margin-top:10px;" onclick="document.getElementById('check-modal').style.display='none'">Cancel</button>
        </div>
    </div>

    <script>
    const data = {{ games | tojson }};
    let currentServer = null;

    function init() {
        document.getElementById('game-list').innerHTML = Object.keys(data).map(name => `
            <div class="game-card" onclick="selectServer('${name}')">
                <img src="${data[name].img}"><h4>${name}</h4>
            </div>`).join('');
    }

    function selectServer(name) {
        currentServer = data[name];
        document.getElementById('home-section').style.display = 'none';
        document.getElementById('order-section').style.display = 'block';
        document.getElementById('selected-title').innerText = name;
        document.getElementById('s_name').value = name;
        const tabsBox = document.getElementById('tabs');
        tabsBox.innerHTML = Object.keys(currentServer.cats).map((cat, i) => `
            <div class="cat-tab ${i===0?'active':''}" onclick="renderPkgs('${cat}', this)">${cat}</div>`).join('');
        renderPkgs(Object.keys(currentServer.cats)[0]);
    }

    function renderPkgs(catName, el) {
        if(el) { document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active')); el.classList.add('active'); }
        document.getElementById('pkg-list').innerHTML = currentServer.cats[catName].map(p => `
            <div class="pkg-card" onclick="sel(this,'${p.d}','${p.p}')">
                <span>${p.d} 💎</span><br><b style="color:#fbbf24">${Number(p.p).toLocaleString()} Ks</b>
            </div>`).join('');
    }

    function sel(el, d, p) {
        document.querySelectorAll('.pkg-card').forEach(c => c.classList.remove('selected'));
        el.classList.add('selected');
        document.getElementById('p_val').value = d; document.getElementById('a_val').value = p;
    }

    function showCheck() {
        if(!document.getElementById('p_val').value || !document.getElementById('user_id').value || !document.getElementById('file_input').value) { alert("အချက်အလက်အကုန်ဖြည့်ပါ"); return; }
        document.getElementById('check-details').innerHTML = `ID: ${document.getElementById('user_id').value} (${document.getElementById('zone_id').value})<br>Diamond: ${document.getElementById('p_val').value}<br>Price: ${Number(document.getElementById('a_val').value).toLocaleString()} Ks`;
        document.getElementById('check-modal').style.display = 'flex';
    }

    async function showHistory() {
        document.getElementById('home-section').style.display = 'none';
        document.getElementById('history-section').style.display = 'block';
        const h = JSON.parse(localStorage.getItem('kiwii_h') || '[]');
        const list = document.getElementById('history-list');
        if(!h.length) { list.innerHTML = "No history."; return; }
        
        list.innerHTML = "";
        for(let i=0; i<h.length; i++){
            const status = await fetch('/get_status/'+h[i].id).then(r => r.text());
            list.innerHTML += `<div class="hist-item"><b>#${h[i].id}</b> <span class="status-badge">${status}</span><br><small>${h[i].s} | ${h[i].p} 💎 | ${h[i].t}</small></div>`;
        }
    }

    function goHome() { location.reload(); }
    init();
    </script>
</body></html>
'''

ADMIN_TEMPLATE = '''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { font-family:sans-serif; background:#0f172a; color:white; padding:15px; }
    .card { background:#1e293b; padding:15px; border-radius:12px; margin-bottom:12px; border:1px solid #334155; }
    .btn { padding:8px 15px; border-radius:6px; border:none; color:white; font-weight:bold; cursor:pointer; text-decoration:none; display:inline-block; margin-top:10px; }
    .success { background:#10b981; } .cancel { background:#ef4444; }
</style></head>
<body>
    <h2>Admin Panel</h2>
    {% for o in orders %}
    <div class="card">
        <b>ID: #{{o.id}}</b> [{{o.status}}]<br>
        Server: {{o.server}}<br>
        GameID: {{o.uid}} ({{o.zid}})<br>
        Diamond: {{o.pkg}} | Price: {{o.amt}} Ks<br>
        <a href="/update/{{o.id}}/Success" class="btn success">Success</a>
        <a href="/update/{{o.id}}/Cancel" class="btn cancel">Cancel</a>
    </div>
    {% endfor %}
</body></html>
'''

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


