import os, json, requests
from flask import Flask, render_template_string, request, redirect, session
from datetime import datetime, timedelta, timezone
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = "KIWII_SUPER_SECRET"
db = TinyDB('db.json')

# --- CONFIGURATION ---
PAY_DATA = {"Number": "09775394979", "Name": "Thansin Kyaw", "Note": "Payment"}
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
CHAT_ID = "7089720301"
CS_LINK = "https://t.me/Bby_kiwii7"
ADMIN_PASS = "kiwii123"
# သင့် Website URL ကို ဒီမှာမှန်အောင်ပြင်ပေးပါ
BASE_URL = "https://kiwiigameshop.onrender.com" 

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
    }
]

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, games=GAMES_DATA, pay=PAY_DATA, cs=CS_LINK)

@app.route('/order', methods=['POST'])
def order():
    # မြန်မာစံတော်ချိန် သတ်မှတ်ခြင်း (GMT+6:30)
    mm_tz = timezone(timedelta(hours=6, minutes=30))
    time_now = datetime.now(mm_tz).strftime('%d/%m %I:%M %p')
    
    order_id = str(int(datetime.now().timestamp()))
    u_id = request.form.get('u')
    z_id = request.form.get('z')
    pkg = request.form.get('p')
    amt = request.form.get('a')
    server = request.form.get('server_name')
    photo = request.files.get('photo')

    # Bot ဆီပို့မယ့် Message (Admin Link တွဲလျက်)
    admin_link = f"{BASE_URL}/admin"
    msg = f"🔔 *New Order!*\nID: #{order_id}\nServer: {server}\nGameID: {u_id} ({z_id})\nPkg: {pkg}\nAmt: {amt} Ks\n\n🔗 [Open Admin Panel]({admin_link})"
    
    if photo:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "Markdown"}, 
                      files={'photo': photo.read()})
    
    db.insert({'id': order_id, 'server': server, 'uid': u_id, 'zid': z_id, 'pkg': pkg, 'amt': amt, 'status': 'Pending', 'time': time_now})
    
    return f"""
    <html><body style='background:#0f172a;color:white;text-align:center;padding:50px;'>
        <h2>Order Success! ✅</h2>
        <script>
            let h = JSON.parse(localStorage.getItem('kiwi_h') || '[]');
            h.unshift({{ id:'{order_id}', s:'{server}', u:'{u_id}', z:'{z_id}', p:'{pkg}', a:'{amt}', t:'{time_now}' }});
            localStorage.setItem('kiwi_h', JSON.stringify(h));
            setTimeout(() => location.href='/', 1500);
        </script>
    </body></html>
    """

@app.route('/get_status/<id>')
def get_status(id):
    order = db.get(Query().id == id)
    return order['status'] if order else "Pending"

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return '<body style="background:#0f172a;color:white;display:flex;justify-content:center;padding:50px;"><form action="/login" method="post"><h2>Admin Login</h2><input name="pw" type="password" style="padding:10px;border-radius:5px;"><button style="padding:10px;margin-left:5px;">Login</button></form></body>'
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
    .cat-tabs { display: flex; gap: 8px; overflow-x: auto; margin-bottom: 15px; }
    .cat-tab { padding: 10px 18px; background: #1e293b; border-radius: 12px; font-size: 12px; white-space:nowrap; border:1px solid #334155; color:#94a3b8; cursor: pointer; }
    .cat-tab.active { background: #fbbf24; color: black; border-color:#fbbf24; }
    .pkg-grid { display:grid; grid-template-columns: 1fr 1fr; gap:12px; max-height: 350px; overflow-y:auto; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; text-align:center; cursor: pointer; }
    .pkg-card.selected { border: 2px solid #fbbf24; background: #1e3a8a; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:12px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; cursor:pointer; color:black; margin-top: 10px; }
    .nav-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #1e293b; display: flex; padding: 12px; border-top: 1px solid #334155; max-width: 500px; margin: auto; z-index: 1000; }
    .nav-btn { flex: 1; text-align: center; font-size: 13px; color: white; text-decoration: none; cursor:pointer; }
    /* Modal Style */
    #confirm-modal { display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:2000; align-items:center; justify-content:center; }
    .modal-content { background:#1e293b; width:85%; max-width:350px; padding:25px; border-radius:20px; text-align:center; }
</style></head>
<body>
    <div id="home-section">
        <h2 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h2>
        <div class="game-grid" id="game-list"></div>
    </div>

    <div id="history-section">
        <button onclick="goHome()" style="background:none; color:white; border:1px solid #334155; padding:5px 12px; border-radius:8px; margin-bottom:15px;">← Back</button>
        <h3 style="color:#fbbf24;">Order History</h3>
        <div id="history-list"></div>
    </div>

    <div id="order-section">
        <button onclick="goHome()" style="background:none; color:white; border:1px solid #334155; padding:8px 15px; border-radius:8px; margin-bottom:15px;">← Back</button>
        <h3 id="selected-title" style="color:#fbbf24;"></h3>
        <div class="cat-tabs" id="tabs"></div>
        <div class="pkg-grid" id="pkg-list"></div>
        <form id="order-form" action="/order" method="post" enctype="multipart/form-data">
            <input type="hidden" name="server_name" id="s_name">
            <input type="number" name="u" id="user_id" placeholder="Player ID" required>
            <input type="number" name="z" id="zone_id" placeholder="Zone ID (If any)">
            <input id="p_val" name="p" type="hidden"><input id="a_val" name="a" type="hidden">
            <input type="file" name="photo" id="photo-input" required accept="image/*" style="font-size:12px;">
            <button type="button" class="buy-btn" onclick="showConfirm()">CONFIRM & BUY</button>
        </form>
    </div>

    <div id="confirm-modal">
        <div class="modal-content">
            <h3 style="color:#fbbf24; margin-top:0;">Confirm Order</h3>
            <div id="modal-info" style="text-align:left; line-height:1.8; margin-bottom:20px;"></div>
            <button class="buy-btn" onclick="submitOrder()">CONFIRM & SEND</button>
            <button onclick="closeModal()" style="background:none; color:#94a3b8; border:none; margin-top:15px; cursor:pointer;">Cancel</button>
        </div>
    </div>

    <div class="nav-bar">
        <div class="nav-btn" onclick="goHome()"><i class="fas fa-home"></i><br>Home</div>
        <div class="nav-btn" onclick="showHistory()"><i class="fas fa-history"></i><br>History</div>
        <a href="{{cs}}" class="nav-btn"><i class="fas fa-comment"></i><br>CS</a>
    </div>

    <script>
    const data = {{ games | tojson }};
    function init() {
        document.getElementById('game-list').innerHTML = data.map(game => `
            <div class="game-card" onclick="selectServer('${game.name}')">
                <img src="${game.img}"><h4>${game.name}</h4>
            </div>
        `).join('');
    }

    function selectServer(name) {
        document.getElementById('home-section').style.display = 'none';
        document.getElementById('order-section').style.display = 'block';
        document.getElementById('selected-title').innerText = name;
        document.getElementById('s_name').value = name;
        const g = data.find(i => i.name === name);
        const keys = Object.keys(g.cats);
        document.getElementById('tabs').innerHTML = keys.map((c, i) => `<div class="cat-tab ${i === 0 ? 'active' : ''}" onclick="renderPkgs('${name}','${c}',this)">${c}</div>`).join('');
        renderPkgs(name, keys[0]);
    }

    function renderPkgs(sName, cat, el) {
        if(el) { document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active')); el.classList.add('active'); }
        const g = data.find(i => i.name === sName);
        document.getElementById('pkg-list').innerHTML = g.cats[cat].map(p => `
            <div class="pkg-card" onclick="sel(this,'${p.d}','${p.p}')"><span>${p.d} 💎</span><br><b>${p.p} Ks</b></div>
        `).join('');
    }

    function sel(el, d, p) {
        document.querySelectorAll('.pkg-card').forEach(c => c.classList.remove('selected'));
        el.classList.add('selected');
        document.getElementById('p_val').value = d; document.getElementById('a_val').value = p;
    }

    function showConfirm() {
        const u = document.getElementById('user_id').value;
        const z = document.getElementById('zone_id').value || '-';
        const p = document.getElementById('p_val').value;
        const a = document.getElementById('a_val').value;
        const file = document.getElementById('photo-input').files[0];
        if(!u || !p || !file) return alert("Please fill all info and upload photo!");

        document.getElementById('modal-info').innerHTML = `
            ID: <b>${u} (${z})</b><br>
            Diamond: <b>${p}</b><br>
            Price: <b>${a} Ks</b>
        `;
        document.getElementById('confirm-modal').style.display = 'flex';
    }

    function closeModal() { document.getElementById('confirm-modal').style.display = 'none'; }
    function submitOrder() { document.getElementById('order-form').submit(); }

    async function showHistory() {
        document.getElementById('home-section').style.display = 'none';
        document.getElementById('order-section').style.display = 'none';
        document.getElementById('history-section').style.display = 'block';
        const h = JSON.parse(localStorage.getItem('kiwi_h') || '[]');
        let html = h.length === 0 ? '<div style="text-align:center;margin-top:50px;color:#94a3b8;">No history found.</div>' : '';
        for(let i=0; i < h.length; i++) {
            const res = await fetch('/get_status/' + h[i].id);
            const status = await res.text();
            let color = status === 'Success' ? '#10b981' : (status === 'Cancel' ? '#ef4444' : '#fbbf24');
            html += `
                <div style="background:#1e293b; padding:15px; border-radius:12px; margin-bottom:12px; border-left:5px solid ${color};">
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <b>#${h[i].id}</b> <span style="font-size:11px; color:${color};">${status}</span>
                    </div>
                    <div style="font-size:13px; color:#cbd5e1;">
                        ${h[i].s} | ${h[i].p} 💎 | ${h[i].t}
                    </div>
                </div>`;
        }
        document.getElementById('history-list').innerHTML = html;
    }

    function goHome() {
        document.getElementById('home-section').style.display = 'block';
        document.getElementById('order-section').style.display = 'none';
        document.getElementById('history-section').style.display = 'none';
        closeModal();
    }
    init();
    </script>
</body></html>
'''

ADMIN_TEMPLATE = '''
<!DOCTYPE html><html><body style="background:#0f172a;color:white;font-family:sans-serif;padding:20px;">
    <h2>Admin Panel</h2>
    {% for o in orders %}
    <div style="background:#1e293b;padding:15px;border-radius:10px;margin-bottom:15px;">
        <b>#{{o.id}}</b> ({{o.status}})<br>
        {{o.server}} | {{o.uid}} ({{o.zid}})<br>
        {{o.pkg}} 💎 | {{o.amt}} Ks<br>
        <div style="margin-top:10px;">
            <a href="/update/{{o.id}}/Success" style="background:#10b981; color:white; padding:5px 10px; text-decoration:none; border-radius:5px;">Success</a>
            <a href="/update/{{o.id}}/Cancel" style="background:#ef4444; color:white; padding:5px 10px; text-decoration:none; border-radius:5px; margin-left:10px;">Cancel</a>
        </div>
    </div>
    {% endfor %}
</body></html>
'''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
