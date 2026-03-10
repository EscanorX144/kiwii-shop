import os, json
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

PAY_NO = "09775394979"
PAY_NAME = "THANSIN KYAW"
CS_TELEGRAM = "Kiwii_144"

@app.route('/')
def index():
    # Server data စုစည်းမှု
    games = {
        "Normal Server": {
            "img": "https://img.icons8.com/color/144/mobile-legends.png",
            "cats": {
                "Normal Dia": [{"d": "11", "p": "700"}, {"d": "22", "p": "1400"}, {"d": "86", "p": "4750"}, {"d": "172", "p": "9450"}, {"d": "257", "p": "13800"}],
                "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(5900 * i)} for i in range(1, 11)],
                "Dia 2X": [{"d": "50+", "p": "3050"}, {"d": "150+", "p": "9100"}],
                "Bundle Pack": [{"d": "Twilight pass", "p": "31500"}]
            }
        },
        "Malaysia & Singapore (🇲🇾🇸🇬)": {
            "img": "https://img.icons8.com/color/144/malaysia.png",
            "cats": {
                "Mal & SGP Dia": [{"d": "14", "p": "1050"}, {"d": "42", "p": "3100"}, {"d": "70", "p": "5050"}],
                "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8400 * i)} for i in range(1, 11)],
                "Dia 2X": [{"d": "50+", "p": "4100"}, {"d": "150+", "p": "12000"}],
                "Bundle Pack": [{"d": "Twilight Pass", "p": "46000"}]
            }
        },
        "Indonesia (🇮🇩)": {
            "img": "https://img.icons8.com/color/144/indonesia.png",
            "cats": {
                "Indo Dia": [{"d": "5", "p": "450"}, {"d": "12", "p": "950"}, {"d": "85", "p": "5850"}],
                "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(7500 * i)} for i in range(1, 11)],
                "Bundle Pack": [{"d": "Twilight Pass", "p": "45000"}]
            }
        },
        "Russia (🇷🇺)": {
            "img": "https://img.icons8.com/color/144/russian-federation.png",
            "cats": {
                "Russia Dia": [{"d": "35", "p": "2750"}, {"d": "55", "p": "4450"}, {"d": "165", "p": "13000"}],
                "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(8600 * i)} for i in range(1, 11)]
            }
        },
        "Philippines (🇵🇭)": {
            "img": "https://img.icons8.com/color/144/philippines.png",
            "cats": {
                "Philippines Dia": [{"d": "11", "p": "750"}, {"d": "22", "p": "1500"}, {"d": "56", "p": "3500"}],
                "Weekly Pass": [{"d": f"Weekly Pass {i}X", "p": str(6500 * i)} for i in range(1, 11)],
                "Dia 2X": [{"d": "50+", "p": "3600"}, {"d": "150+", "p": "10500"}],
                "Bundle Pack": [{"d": "Twilight Pass", "p": "35500"}]
            }
        }
    }
    
    return render_template_string('''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; padding:15px; max-width:500px; margin:auto; }
    .game-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
    .game-card { background: #1e293b; border: 1px solid #334155; border-radius: 15px; padding: 15px; text-align: center; cursor: pointer; }
    .game-card img { width: 60px; height: 60px; border-radius: 12px; margin-bottom: 10px; }
    .game-card h4 { margin: 5px 0; font-size: 13px; color: #fbbf24; }
    #order-section { display: none; }
    .cat-tabs { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 10px; margin-bottom: 15px; }
    .cat-tab { padding: 10px 18px; background: #1e293b; border-radius: 12px; cursor: pointer; border: 1px solid #334155; font-size: 12px; white-space: nowrap; color: #94a3b8; }
    .cat-tab.active { background: #10b981; color: white; border: none; }
    .pkg-grid { display:grid; grid-template-columns: 1fr 1fr; gap:12px; max-height: 400px; overflow-y: auto; padding:5px; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; cursor:pointer; text-align:center; }
    .pkg-card.selected { border: 2px solid #fbbf24; background: #1e3a8a; }
    input { width:100%; padding:14px; margin:8px 0; border-radius:12px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; cursor:pointer; font-size: 18px; color:#000; }
    .back-btn { background: #334155; color: white; border: none; padding: 8px 15px; border-radius: 8px; cursor: pointer; margin-bottom: 15px; }
</style></head>
<body>
    <div id="home-section">
        <h2 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h2>
        <div class="game-grid" id="game-list"></div>
    </div>
    <div id="order-section">
        <button class="back-btn" onclick="goHome()">← Back</button>
        <h3 id="selected-title" style="color:#fbbf24; margin-bottom:15px;"></h3>
        <div class="cat-tabs" id="tabs"></div>
        <div class="pkg-grid" id="pkg-list"></div>
        <div style="background:#1e3a8a; padding:15px; border-radius:15px; text-align:center; margin:15px 0;">
            <b style="font-size:20px;">{{pay_no}}</b><br><small>NAME: {{name}}</small>
        </div>
        <form action="/order" method="post" enctype="multipart/form-data">
            <input type="number" name="u" placeholder="Game ID" required>
            <input type="number" name="z" placeholder="Zone ID" required>
            <input id="p_val" name="p" type="hidden"><input id="a_val" name="a" type="hidden">
            <input type="file" name="photo" required>
            <button type="submit" class="buy-btn">CONFIRM ORDER</button>
        </form>
    </div>
    <script>
    const data = ''' + json.dumps(games) + ''';
    let currentServer = null;
    function init() {
        const list = document.getElementById('game-list');
        list.innerHTML = Object.keys(data).map(name => `
            <div class="game-card" onclick="selectServer('${name}')">
                <img src="${data[name].img}"><h4>${name}</h4>
            </div>`).join('');
    }
    function selectServer(name) {
        currentServer = data[name];
        document.getElementById('home-section').style.display = 'none';
        document.getElementById('order-section').style.display = 'block';
        document.getElementById('selected-title').innerText = name;
        const tabsBox = document.getElementById('tabs');
        tabsBox.innerHTML = Object.keys(currentServer.cats).map((cat, i) => `
            <div class="cat-tab ${i===0?'active':''}" onclick="renderPkgs('${cat}', this)">${cat}</div>`).join('');
        renderPkgs(Object.keys(currentServer.cats)[0]);
    }
    function renderPkgs(catName, el) {
        if(el) { document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active')); el.classList.add('active'); }
        const pkgBox = document.getElementById('pkg-list');
        pkgBox.innerHTML = currentServer.cats[catName].map(p => `
            <div class="pkg-card" onclick="sel(this,'${p.d}','${p.p}')">
                <span>${p.d} 💎</span><br><b style="color:#fbbf24">${Number(p.p).toLocaleString()} Ks</b>
            </div>`).join('');
    }
    function sel(el, d, p) {
        document.querySelectorAll('.pkg-card').forEach(c => c.classList.remove('selected'));
        el.classList.add('selected');
        document.getElementById('p_val').value = d; document.getElementById('a_val').value = p;
    }
    function goHome() {
        document.getElementById('home-section').style.display = 'block';
        document.getElementById('order-section').style.display = 'none';
    }
    init();
    </script>
</body></html>''', pay_no=PAY_NO, name=PAY_NAME, cs=CS_TELEGRAM)

@app.route('/order', methods=['POST'])
def order():
    return "Order Success!"

if __name__ == '__main__':
    app.run(debug=True)


