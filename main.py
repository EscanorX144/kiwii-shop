import os, json, requests
from flask import Flask, render_template_string, request, redirect, session, url_for
from datetime import datetime, timedelta, timezone
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = "KIWII_ULTIMATE_SECRET_STAY_SAFE"
db = TinyDB('db.json')

# --- CONFIGURATION ---
PAY_DATA = {"Number": "09775394979", "Name": "Thansin Kyaw", "Note": "Payment"}
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
CHAT_ID = "7089720301"
CS_LINK = "https://t.me/Bby_kiwii7"
ADMIN_PASS = "kiwii123"
BASE_URL = "https://kiwiigameshop.onrender.com"

# --- 💎 DIAMOND LIST DATA (All Servers updated from your photos) ---
GAMES_DATA = [
    {
        "name": "Normal Server",
        "img": "https://img.icons8.com/color/144/mobile-legends.png",
        "cats": {
            "Normal Dia": [
                {"d": "11", "p": "700"}, {"d": "22", "p": "1400"}, {"d": "33", "p": "2100"}, {"d": "44", "p": "2800"}, 
                {"d": "56", "p": "3500"}, {"d": "112", "p": "7000"}, {"d": "172", "p": "9450"}, {"d": "257", "p": "13800"}, 
                {"d": "343", "p": "18600"}, {"d": "429", "p": "23350"}, {"d": "514", "p": "27650"}, {"d": "600", "p": "32650"}, 
                {"d": "706", "p": "37450"}, {"d": "878", "p": "46850"}, {"d": "963", "p": "51200"}, {"d": "1049", "p": "56000"}, 
                {"d": "1412", "p": "74900"}, {"d": "2195", "p": "114200"}, {"d": "3688", "p": "190500"}, {"d": "5532", "p": "287000"},
                {"d": "9288", "p": "475000"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(5900 * i)} for i in range(1, 11)],
            "2X Dia": [
                {"d": "50+50 💎", "p": "3200"}, {"d": "150+150 💎", "p": "9100"}, 
                {"d": "250+250 💎", "p": "14650"}, {"d": "500+500 💎", "p": "29950"}
            ],
            "Bundle Pack": [
                {"d": "Weekly elite bundle", "p": "3050"}, {"d": "Monthly epic bundle", "p": "15350"}, {"d": "Twilight pass", "p": "31500"}
            ]
        }
    },
    {
        "name": "Indonesia (🇮🇩)",
        "img": "https://img.icons8.com/color/144/indonesia.png",
        "cats": {
            "Normal Dia": [
                {"d": "5", "p": "450"}, {"d": "12", "p": "950"}, {"d": "28", "p": "2200"}, {"d": "44", "p": "3300"}, 
                {"d": "59", "p": "4300"}, {"d": "85", "p": "5850"}, {"d": "170", "p": "11700"}, {"d": "296", "p": "20500"}, 
                {"d": "408", "p": "28000"}, {"d": "568", "p": "37500"}, {"d": "875", "p": "58500"}, {"d": "2010", "p": "123500"},
                {"d": "4830", "p": "299000"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(7500 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "10+10 💎", "p": "800"}, {"d": "50+50 💎", "p": "3800"}, {"d": "100+100 💎", "p": "7000"}],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "32000"}]
        }
    },
    {
        "name": "Malaysia (🇲🇾)",
        "img": "https://img.icons8.com/color/144/malaysia.png",
        "cats": {
            "Normal Dia": [
                {"d": "14", "p": "1050"}, {"d": "42", "p": "3100"}, {"d": "70", "p": "5050"}, {"d": "140", "p": "10100"}, 
                {"d": "210", "p": "15100"}, {"d": "284", "p": "20200"}, {"d": "355", "p": "25200"}, {"d": "429", "p": "30300"}, 
                {"d": "716", "p": "50200"}, {"d": "1446", "p": "100500"}, {"d": "2976", "p": "201000"}, {"d": "7502", "p": "503500"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8400 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "20+20 💎", "p": "1500"}, {"d": "150+150 💎", "p": "10000"}],
            "Bundle Pack": [{"d": "Weekly Elite", "p": "3500"}]
        }
    },
    {
        "name": "Philippines (🇵🇭)",
        "img": "https://img.icons8.com/color/144/philippines.png",
        "cats": {
            "Normal Dia": [
                {"d": "11", "p": "750"}, {"d": "22", "p": "1500"}, {"d": "56", "p": "3500"}, {"d": "112", "p": "7000"}, 
                {"d": "223", "p": "14000"}, {"d": "336", "p": "21300"}, {"d": "570", "p": "36000"}, {"d": "1163", "p": "70500"}, 
                {"d": "2398", "p": "140000"}, {"d": "6042", "p": "350000"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(6500 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "3500"}, {"d": "250+250 💎", "p": "16000"}],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "33000"}]
        }
    },
    {
        "name": "Russia (🇷🇺)",
        "img": "https://img.icons8.com/color/144/russian-federation.png",
        "cats": {
            "Normal Dia": [
                {"d": "35", "p": "2750"}, {"d": "55", "p": "4450"}, {"d": "165", "p": "13000"}, {"d": "275", "p": "22000"}, 
                {"d": "565", "p": "44500"}, {"d": "1155", "p": "88000"}, {"d": "1765", "p": "132000"}, {"d": "2975", "p": "220000"},
                {"d": "6000", "p": "435000"}
            ],
            "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8600 * i)} for i in range(1, 11)],
            "2X Dia": [{"d": "50+50 💎", "p": "4000"}],
            "Bundle Pack": [{"d": "Twilight Pass", "p": "35000"}]
        }
    }
]

# --- HTML TEMPLATE (Optimized for Tabs) ---
HTML_CODE = '''
<!DOCTYPE html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; margin:0; padding:15px; padding-bottom:80px; }
    .game-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    .game-card { 
        background: linear-gradient(rgba(15, 23, 42, 0.7), rgba(15, 23, 42, 0.7)), url('/static/hero.webp');
        background-size: cover; background-position: center;
        border: 1px solid #334155; border-radius: 15px; padding: 25px 10px; text-align: center;
    }
    .game-card img { width:60px; height:60px; border-radius:12px; margin-bottom:10px; border:2px solid #fbbf24; }
    .section { display:none; }
    .cat-tabs-container { overflow-x: auto; white-space: nowrap; padding: 5px 0 15px 0; -webkit-overflow-scrolling: touch; }
    .cat-tab { padding:10px 18px; background:#1e293b; border-radius:10px; font-size:12px; border:1px solid #334155; display:inline-block; margin-right:5px; color:#94a3b8; }
    .cat-tab.active { background:#fbbf24; color:black; font-weight:bold; border-color:#fbbf24; }
    .pkg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:12px; border-radius:10px; text-align:center; }
    .pkg-card.selected { border:2px solid #fbbf24; background:#1e3a8a; }
    .pay-card { background:#1e293b; border-radius:15px; padding:15px; margin:20px 0; text-align:center; border:1px solid #334155; }
    .pay-logos { display:flex; justify-content:center; gap:10px; margin-bottom:10px; }
    .pay-logos img { width:40px; height:40px; border-radius:8px; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:10px; border:1px solid #334155; background:#0f172a; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:10px; font-weight:bold; color:black; cursor:pointer; }
    .nav-bar { position:fixed; bottom:0; left:0; right:0; background:#1e293b; display:flex; padding:12px; border-top:1px solid #334155; }
    .nav-btn { flex:1; text-align:center; color:#94a3b8; text-decoration:none; font-size:12px; cursor:pointer; }
    .modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:1000; align-items:center; justify-content:center; }
    .modal-box { background:#1e293b; width:85%; max-width:350px; padding:25px; border-radius:20px; text-align:center; border:1px solid #475569; }
</style>
</head><body>

<div id="home-sec" class="section" style="display:block;">
    <h2 style="text-align:center;color:#fbbf24;letter-spacing:1px;">KIWII GAME SHOP</h2>
    <div class="game-grid" id="game-list"></div>
</div>

<div id="order-sec" class="section">
    <button onclick="goHome()" style="background:none;color:white;border:1px solid #334155;padding:8px 15px;border-radius:8px;margin-bottom:15px;">← Back</button>
    <h3 id="game-title" style="color:#fbbf24;margin:0;"></h3>
    <div class="cat-tabs-container" id="tabs"></div>
    <div class="pkg-grid" id="pkg-list"></div>

    <div class="pay-card">
        <div class="pay-logos">
            <img src="/static/kpay.jpg"> <img src="/static/wave.jpg"> <img src="/static/ayapay.jpg">
        </div>
        <b style="color:#fbbf24;font-size:18px;">{{pay.Number}}</b><br>
        <small>{{pay.Name}} | {{pay.Note}}</small>
    </div>

    <form id="order-form" action="/order" method="post" enctype="multipart/form-data">
        <input type="hidden" name="server_name" id="s_name">
        <input type="number" name="u" id="user_id" placeholder="Player ID" required>
        <input type="number" name="z" id="zone_id" placeholder="Zone ID">
        <input type="hidden" name="p" id="p_val"><input type="hidden" name="a" id="a_val">
        <input type="file" name="photo" id="photo-input" required accept="image/*" style="font-size:12px;margin-bottom:10px;">
        <button type="button" class="buy-btn" onclick="showModal()">CONFIRM & BUY</button>
    </form>
</div>

<div id="hist-sec" class="section">
    <h3 style="color:#fbbf24;text-align:center;">History</h3>
    <div id="hist-list"></div>
</div>

<div id="confirm-modal" class="modal">
    <div class="modal-box">
        <h3 style="color:#fbbf24;margin:0;">Confirm Order</h3>
        <div id="modal-info" style="text-align:left; line-height:2; margin:20px 0; color:#cbd5e1;"></div>
        <button class="buy-btn" onclick="submitForm()">CONFIRM & SEND</button>
        <button onclick="closeModal()" style="background:none;border:none;color:#94a3b8;margin-top:15px;cursor:pointer;">Cancel</button>
    </div>
</div>

<div class="nav-bar">
    <div class="nav-btn" onclick="goHome()"><i class="fas fa-home"></i><br>Home</div>
    <div class="nav-btn" onclick="showHistory()"><i class="fas fa-history"></i><br>History</div>
    <a href="{{cs}}" class="nav-btn"><i class="fas fa-comment"></i><br>Contact</a>
</div>

<script>
const data = {{ games | tojson }};
function init() {
    document.getElementById('game-list').innerHTML = data.map(g => `<div class="game-card" onclick="selectGame('${g.name}')"><img src="${g.img}"><h4>${g.name}</h4></div>`).join('');
}
function selectGame(name) {
    document.querySelectorAll('.section').forEach(s=>s.style.display='none');
    document.getElementById('order-sec').style.display = 'block';
    document.getElementById('game-title').innerText = name;
    document.getElementById('s_name').value = name;
    const g = data.find(i => i.name === name);
    const keys = Object.keys(g.cats);
    document.getElementById('tabs').innerHTML = keys.map((c, i) => `<div class="cat-tab ${i===0?'active':''}" onclick="renderPkgs('${name}','${c}',this)">${c}</div>`).join('');
    renderPkgs(name, keys[0]);
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
    const u = document.getElementById('user_id').value, p = document.getElementById('p_val').value, f = document.getElementById('photo-input').files[0];
    if(!u || !p || !f) return alert("အချက်အလက်အားလုံးဖြည့်ပါ။");
    document.getElementById('modal-info').innerHTML = `Server: ${document.getElementById('s_name').value}<br>ID: ${u}<br>Package: ${p}<br>Price: ${document.getElementById('a_val').value} Ks`;
    document.getElementById('confirm-modal').style.display = 'flex';
}
function closeModal() { document.getElementById('confirm-modal').style.display = 'none'; }
function submitForm() { document.getElementById('order-form').submit(); }
async function showHistory() {
    document.querySelectorAll('.section').forEach(s=>s.style.display='none');
    document.getElementById('hist-sec').style.display='block';
    const h = JSON.parse(localStorage.getItem('kiwi_h') || '[]');
    let html = h.length === 0 ? '<p style="text-align:center;color:#94a3b8;margin-top:50px;">No History</p>' : '';
    for(let i=0; i<h.length; i++) {
        const res = await fetch('/get_status/' + h[i].id);
        const status = await res.text();
        let color = status === 'Success' ? '#10b981' : (status === 'Cancel' ? '#ef4444' : '#fbbf24');
        html += `<div style="background:#1e293b;padding:15px;border-radius:12px;margin-bottom:10px;border-left:5px solid ${color};">
            <b>#${h[i].id}</b> <small style="float:right;color:${color}">${status}</small><br>
            <small>${h[i].s} | ${h[i].p} | ${h[i].t}</small>
        </div>`;
    }
    document.getElementById('hist-list').innerHTML = html;
}
function goHome() { document.querySelectorAll('.section').forEach(s=>s.style.display='none'); document.getElementById('home-sec').style.display='block'; }
init();
</script></body></html>
'''

@app.route('/')
def index(): return render_template_string(HTML_CODE, games=GAMES_DATA, pay=PAY_DATA, cs=CS_LINK)

@app.route('/order', methods=['POST'])
def order():
    mm_tz = timezone(timedelta(hours=6, minutes=30))
    time_now = datetime.now(mm_tz).strftime('%d/%m %I:%M %p')
    order_id = str(int(datetime.now().timestamp()))
    u_id, z_id = request.form.get('u'), request.form.get('z') or "-"
    pkg, amt = request.form.get('p'), request.form.get('a')
    server, photo = request.form.get('server_name'), request.files.get('photo')
    msg = f"🔔 *New Order!*\nID: #{order_id}\nServer: {server}\nGameID: {u_id} ({z_id})\nPkg: {pkg}\nAmt: {amt} Ks\n\n🔗 [Open Admin]({BASE_URL}/admin)"
    if photo: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}, files={'photo': photo.read()})
    db.insert({'id': order_id, 'status': 'Pending', 'server': server, 'uid': u_id, 'pkg': pkg, 'amt': amt, 'time': time_now})
    return f"<html><body style='background:#0f172a;color:white;text-align:center;padding:50px;'><h2>Odrer Success! ✅</h2><script>let h=JSON.parse(localStorage.getItem('kiwi_h')||'[]'); h.unshift({{id:'{order_id}', s:'{server}', p:'{pkg}', t:'{time_now}'}}); localStorage.setItem('kiwi_h', JSON.stringify(h)); setTimeout(()=>location.href='/', 1500);</script></body></html>"

@app.route('/get_status/<id>')
def get_status(id):
    order = db.get(Query().id == id)
    return order['status'] if order else "Pending"

@app.route('/admin')
def admin():
    if not session.get('logged_in'): return '<body style="background:#0f172a;color:white;padding:50px;text-align:center;"><form action="/login" method="post"><h3 style="color:#fbbf24;">Admin Login</h3><input name="pw" type="password" style="padding:10px; width:80%; border-radius:10px;"><br><button style="margin-top:15px; padding:10px 30px; border-radius:10px; background:#fbbf24; border:none; font-weight:bold;">Login</button></form></body>'
    orders = db.all()[::-1]
    admin_html = '''
    <body style="background:#0f172a;color:white;padding:20px;font-family:sans-serif;">
    <h2 style="color:#fbbf24;">Orders <a href="/logout" style="font-size:12px;color:#ef4444;text-decoration:none;float:right;">Logout</a></h2>
    {% for o in orders %}
    <div style="background:#1e293b;padding:15px;border-radius:10px;margin-bottom:15px;border:1px solid #334155; border-left: 5px solid {% if o.status == 'Success' %}#10b981{% elif o.status == 'Cancel' %}#ef4444{% else %}#fbbf24{% endif %};">
        <b>ID: #{{o.id}}</b> <span style="float:right;">[{{o.status}}]</span><br>
        <div style="margin:10px 0; color:#cbd5e1;">
            Server: {{o.server}}<br>Package: {{o.pkg}}<br>Game ID: {{o.uid}}<br>Price: {{o.amt}} Ks<br>Time: {{o.time}}
        </div>
        <div style="display:flex; gap:10px;">
            <a href="/update/{{o.id}}/Success" style="flex:1; background:#10b981; color:white; padding:10px; text-align:center; text-decoration:none; border-radius:8px; font-size:14px;">Done</a>
            <a href="/update/{{o.id}}/Cancel" style="flex:1; background:#ef4444; color:white; padding:10px; text-align:center; text-decoration:none; border-radius:8px; font-size:14px;">Cancel</a>
        </div>
    </div>
    {% endfor %}</body>'''
    return render_template_string(admin_html, orders=orders)

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('pw') == ADMIN_PASS: session['logged_in'] = True
    return redirect('/admin')

@app.route('/logout')
def logout(): session.clear(); return redirect('/admin')

@app.route('/update/<oid>/<status>')
def update(oid, status):
    if session.get('logged_in'): db.update({'status': status}, Query().id == oid)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    
