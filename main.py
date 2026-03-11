import os, json, requests
from flask import Flask, render_template_string, request, redirect, session, url_for
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "KIWII_ULTIMATE_SECRET_STAY_SAFE"

# --- 🛰️ MONGODB CONNECTION ---
# သင့်ပုံထဲမှာ Username က "Escanor X" (Space ပါတယ်) ဖြစ်လို့ Escanor%20X လို့ သုံးထားပါတယ်
MONGO_URI = "mongodb+srv://EscanorX:Conti144@cluster0.m2tomm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db_mongo = client['kiwii_game_shop']
orders_col = db_mongo['orders']

# --- ⚙️ CONFIGURATION ---
PAY_DATA = {"Number": "09775394979", "Name": "Thansin Kyaw", "Note": "Payment လေးပေးပို့ပါ"}
BOT_TOKEN = "8089066962:AAFOHB6euDF7E3Ygej3nAwOODSNj4ujVvk"
CHAT_ID = "7089720301"
CS_LINK = "https://t.me/Why_kiwii?"
ADMIN_PASS = "kiwi1123"

# --- 💎 DIAMOND LIST DATA ---
GAMES_DATA = [
    {
        "name": "Normal Server (🇲🇲)",
        "img": "https://flagcdn.com/w160/mm.png",
        "cats": {
            "Normal Dia": [{"d": "11 💎", "p": "700"}, {"d": "22 💎", "p": "1400"}, {"d": "33 💎", "p": "2100"}, {"d": "44 💎", "p": "2800"}, {"d": "56 💎", "p": "3500"}, {"d": "112 💎", "p": "7000"}, {"d": "172 💎", "p": "9450"}, {"d": "257 💎", "p": "13800"}, {"d": "343 💎", "p": "18600"}, {"d": "429 💎", "p": "23350"}, {"d": "514 💎", "p": "27650"}, {"d": "600 💎", "p": "32650"}, {"d": "706 💎", "p": "37450"}, {"d": "878 💎", "p": "46850"}, {"d": "963 💎", "p": "51200"}, {"d": "1049 💎", "p": "56000"}, {"d": "1412 💎", "p": "74900"}, {"d": "2195 💎", "p": "114200"}, {"d": "3688 💎", "p": "190500"}, {"d": "5532 💎", "p": "287000"}, {"d": "9288 💎", "p": "475000"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X 💎", "p": str(5900 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "3050"}, {"d": "150+150 💎", "p": "9100"}, {"d": "250+250 💎", "p": "14650"}, {"d": "500+500 💎", "p": "29950"}],
            "Bundle Pack": [{"d": "Weekly elite bundle 💎", "p": "3050"}, {"d": "Monthly epic bundle 💎", "p": "15350"}, {"d": "Twilight pass 💎", "p": "31500"}]
        }
    },
    {
        "name": "Malaysia (🇲🇾)",
        "img": "https://flagcdn.com/w160/my.png",
        "cats": {
            "Mal & SGP Dia": [{"d": "14 💎", "p": "1050"}, {"d": "42 💎", "p": "3100"}, {"d": "70 💎", "p": "5050"}, {"d": "140 💎", "p": "10100"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "716 💎", "p": "50200"}, {"d": "1446 💎", "p": "100500"}, {"d": "2976 💎", "p": "201000"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X 💎", "p": str(8400 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "4250"}, {"d": "150+150 💎", "p": "12200"}, {"d": "250+250 💎", "p": "20200"}, {"d": "500+500 💎", "p": "40600"}]
        }
    },
    {
        "name": "Singapore (🇸🇬)",
        "img": "https://flagcdn.com/w160/sg.png",
        "cats": {
            "Mal & SGP Dia": [{"d": "14 💎", "p": "1050"}, {"d": "42 💎", "p": "3100"}, {"d": "70 💎", "p": "5050"}, {"d": "140 💎", "p": "10100"}, {"d": "210 💎", "p": "15100"}, {"d": "284 💎", "p": "20200"}, {"d": "355 💎", "p": "25200"}, {"d": "429 💎", "p": "30300"}, {"d": "716 💎", "p": "50200"}, {"d": "1446 💎", "p": "100500"}, {"d": "2976 💎", "p": "201000"}, {"d": "7502 💎", "p": "503500"}],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X 💎", "p": str(8400 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "4250"}, {"d": "150+150 💎", "p": "12200"}, {"d": "250+250 💎", "p": "20200"}, {"d": "500+500 💎", "p": "40600"}]
        }
    }
]

# --- HTML TEMPLATE ---
HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; margin:0; padding:15px; padding-bottom:80px; }
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    .game-card { background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; border-radius: 15px; padding: 25px 10px; text-align: center; cursor:pointer; }
    .game-card img { width:60px; height:40px; border-radius:4px; margin-bottom:10px; border:1px solid #475569; }
    .section { display:none; }
    .cat-tabs-container { overflow-x: auto; white-space: nowrap; padding: 5px 0 15px 0; -webkit-overflow-scrolling: touch; }
    .cat-tab { padding:10px 18px; background:#1e293b; border-radius:10px; font-size:12px; border:1px solid #334155; display:inline-block; margin-right:5px; color:#94a3b8; cursor:pointer; }
    .cat-tab.active { background:#fbbf24; color:black; font-weight:bold; border-color:#fbbf24; }
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; max-height: 350px; overflow-y: auto; padding: 5px; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:12px; border-radius:10px; text-align:center; cursor:pointer; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    .glow-box { border: 1px solid #ff4444; padding: 4px 12px; border-radius: 8px; color: #ff4444; font-weight: bold; font-size: 13px; display: inline-block; margin-top: 8px; }
    .copy-btn { background: #fbbf24; color: black; border: none; padding: 4px 8px; border-radius: 5px; font-size: 12px; cursor: pointer; margin-left: 8px; font-weight: bold; }
    .pay-card { background:#1e293b; border-radius:15px; padding:15px; margin:20px 0; text-align:center; border:1px solid #334155; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:10px; border:1px solid #334155; background:#0f172a; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:10px; font-weight:bold; color:black; cursor:pointer; }
    .nav-bar { position:fixed; bottom:0; left:0; right:0; background:#1e293b; display:flex; padding:12px; border-top:1px solid #334155; }
    .nav-btn { flex:1; text-align:center; color:#94a3b8; text-decoration:none; font-size:12px; cursor:pointer; }
    .modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:1000; align-items:center; justify-content:center; }
    .modal-box { background:#1e293b; width:85%; max-width:350px; padding:25px; border-radius:20px; text-align:center; border:1px solid #475569; }
</style>
</head><body>

<div id="home-sec" class="section" style="display:block;">
    <h2 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h2>
    <div class="game-grid" id="game-list"></div>
</div>

<div id="order-sec" class="section">
    <button onclick="goHome()" style="background:none;color:white;border:1px solid #334155;padding:8px 15px;border-radius:8px;margin-bottom:15px;">← Back</button>
    <h3 id="game-title" style="color:#fbbf24;"></h3>
    <div class="cat-tabs-container" id="tabs"></div>
    <div class="pkg-grid" id="pkg-list"></div>

    <div class="pay-card">
        <b id="pay-num" style="color:#fbbf24;font-size:20px;">{{pay.Number}}</b>
        <button class="copy-btn" onclick="copyNum()">Copy</button><br>
        <span style="color:#cbd5e1;">{{pay.Name}}</span><br>
        <div class="glow-box">Note - {{pay.Note}}</div>
    </div>

    <form id="order-form" action="/order" method="post" enctype="multipart/form-data">
        <input type="hidden" name="server_name" id="s_name">
        <input type="text" name="u" id="user_id" placeholder="Player ID" required>
        <input type="text" name="z" id="zone_id" placeholder="Zone ID">
        <input type="hidden" name="p" id="p_val"><input type="hidden" name="a" id="a_val">
        <input type="file" name="photo" id="photo-input" required accept="image/*">
        <button type="button" class="buy-btn" onclick="showModal()">CONFIRM & BUY</button>
    </form>
</div>

<div id="hist-sec" class="section">
    <h3 style="color:#fbbf24;text-align:center;">Order History</h3>
    <div id="hist-list"></div>
</div>

<div id="confirm-modal" class="modal">
    <div class="modal-box">
        <h3 style="color:#fbbf24;">Confirm Order</h3>
        <div id="modal-info" style="text-align:left; color:#cbd5e1; margin:20px 0;"></div>
        <button class="buy-btn" onclick="submitForm()">CONFIRM & SEND</button>
        <button onclick="closeModal()" style="background:none;border:none;color:#94a3b8;margin-top:15px;">Cancel</button>
    </div>
</div>

<div class="nav-bar">
    <div class="nav-btn" onclick="goHome()"><i class="fas fa-home"></i><br>Home</div>
    <div class="nav-btn" onclick="showHistory()"><i class="fas fa-history"></i><br>History</div>
    <a href="{{cs}}" class="nav-btn" target="_blank"><i class="fas fa-comment"></i><br>Contact</a>
</div>

<script>
const data = {{ games | tojson }};
function init() { document.getElementById('game-list').innerHTML = data.map(g => `<div class="game-card" onclick="selectGame('${g.name}')"><img src="${g.img}"><h4>${g.name}</h4></div>`).join(''); }
function selectGame(name) {
    document.querySelectorAll('.section').forEach(s=>s.style.display='none');
    document.getElementById('order-sec').style.display = 'block';
    document.getElementById('game-title').innerText = name;
    document.getElementById('s_name').value = name;
    const g = data.find(i => i.name === name);
    const sortedKeys = Object.keys(g.cats);
    document.getElementById('tabs').innerHTML = sortedKeys.map((c, i) => `<div class="cat-tab ${i === 0 ? 'active' : ''}" onclick="renderPkgs('${name}','${c}',this)">${c}</div>`).join('');
    renderPkgs(name, sortedKeys[0]);
}
function renderPkgs(sName, cat, el) {
    if(el) { document.querySelectorAll('.cat-tab').forEach(t=>t.classList.remove('active')); el.classList.add('active'); }
    const g = data.find(i => i.name === sName);
    document.getElementById('pkg-list').innerHTML = g.cats[cat].map(p => `<div class="pkg-card" onclick="sel(this,'${p.d}','${p.p}')"><span>${p.d}</span><br><b>${p.p} Ks</b></div>`).join('');
}
function sel(el, d, p) {
    document.querySelectorAll('.pkg-card').forEach(c=>c.classList.remove('selected'));
    el.classList.add('selected');
    document.getElementById('p_val').value = d; document.getElementById('a_val').value = p;
}
function showModal() {
    const u = document.getElementById('user_id').value, p = document.getElementById('p_val').value;
    if(!u || !p) return alert("Please fill all info");
    document.getElementById('modal-info').innerHTML = `<b>ID:</b> ${u}<br><b>Item:</b> ${p}<br><b>Price:</b> ${document.getElementById('a_val').value} Ks`;
    document.getElementById('confirm-modal').style.display = 'flex';
}
function closeModal() { document.getElementById('confirm-modal').style.display = 'none'; }
function submitForm() { document.getElementById('order-form').submit(); }
function goHome() { document.querySelectorAll('.section').forEach(s=>s.style.display='none'); document.getElementById('home-sec').style.display='block'; }
function copyNum() { navigator.clipboard.writeText(document.getElementById('pay-num').innerText); alert("Copied!"); }

async function showHistory() {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.getElementById('hist-sec').style.display = 'block';
    let h = JSON.parse(localStorage.getItem('kiwi_h') || '[]');
    let html = '';
    for (let i = 0; i < h.length; i++) {
        const res = await fetch('/get_status/' + h[i].id);
        const status = await res.text();
        html += `<div style="background:#1e293b;padding:15px;border-radius:12px;margin-bottom:10px; border-left:4px solid ${status=='Success'?'#10b981':status=='Cancel'?'#ef4444':'#fbbf24'}"><b>${h[i].p}</b> <small style="float:right;">${status}</small><br><small>${h[i].t}</small></div>`;
    }
    document.getElementById('hist-list').innerHTML = html || '<p>No History</p>';
}
init();
</script></body></html>
'''

# --- ROUTES ---
@app.route('/')
def index(): 
    return render_template_string(HTML_CODE, games=GAMES_DATA, pay=PAY_DATA, cs=CS_LINK)

@app.route('/order', methods=['POST'])
def order():
    mm_tz = timezone(timedelta(hours=6, minutes=30))
    time_now = datetime.now(mm_tz).strftime('%d/%m %I:%M %p')
    order_id = str(int(datetime.now().timestamp()))
    u_id, z_id = request.form.get('u'), request.form.get('z') or "-"
    pkg, amt = request.form.get('p'), request.form.get('a')
    server, photo = request.form.get('server_name'), request.files.get('photo')
    
    msg = f"🔔 *New Order!*\nID: `#{order_id}`\nServer: {server}\nGameID: {u_id} ({z_id})\nPkg: {pkg}\nAmt: {amt} Ks"
    if photo: 
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}, 
                      files={'photo': photo.read()})
    
    orders_col.insert_one({'id': order_id, 'status': 'Pending', 'server': server, 'uid': u_id, 'pkg': pkg, 'amt': amt, 'time': time_now})
    return f"<html><body style='background:#0f172a;color:white;text-align:center;padding:50px;'><h2>Order Success! ✅</h2><script>let h=JSON.parse(localStorage.getItem('kiwi_h')||'[]'); h.unshift({{id:'{order_id}', p:'{pkg}', t:'{time_now}'}}); localStorage.setItem('kiwi_h', JSON.stringify(h)); setTimeout(()=>location.href='/', 1500);</script></body></html>"

@app.route('/get_status/<id>')
def get_status(id):
    order = orders_col.find_one({'id': id})
    return order['status'] if order else "Pending"

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('pw') == ADMIN_PASS: session['logged_in'] = True
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return '<body style="background:#0f172a;color:white;padding:50px;text-align:center;"><form action="/login" method="post"><h3 style="color:#fbbf24;">Admin Login</h3><input name="pw" type="password" style="padding:10px;"><br><button style="margin-top:10px;padding:10px 20px;">Login</button></form></body>'
    orders = list(orders_col.find().sort("id", -1))
    return render_template_string('''
    <body style="background:#0f172a;color:white;padding:20px;">
        <h2 style="color:#fbbf24;">Orders Panel <a href="/logout" style="font-size:14px;color:red;">Logout</a></h2>
        {% for o in orders %}
        <div style="background:#1e293b;padding:15px;border-radius:12px;margin-bottom:10px;">
            ID: #{{o.id}} | Status: <b>{{o.status}}</b><br>
            Server: {{o.server}} | UID: {{o.uid}}<br>
            Pkg: {{o.pkg}} | Amt: {{o.amt}} Ks<br>
            <a href="/update/{{o.id}}/Success" style="color:green;">Success</a> | 
            <a href="/update/{{o.id}}/Cancel" style="color:red;">Cancel</a> |
            <a href="/delete/{{o.id}}" style="color:grey;">Delete</a>
        </div>
        {% endfor %}
    </body>''', orders=orders)

@app.route('/update/<id>/<status>')
def update(id, status):
    if session.get('logged_in'): orders_col.update_one({'id': id}, {'$set': {'status': status}})
    return redirect(url_for('admin'))

@app.route('/delete/<id>')
def delete(id):
    if session.get('logged_in'): orders_col.delete_one({'id': id})
    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    
