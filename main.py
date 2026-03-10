import os
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "1234"
BOT_TOKEN = "7544033321:AAEqM2098y-Y-pX0-23z0_n7Y7-vX3_yYyU"
ADMIN_ID = "7443306161"

packages = [
    {"d": "Weekly Pass", "p": "5,800"}, {"d": "Twilight Pass", "p": "32,000"},
    {"d": "86", "p": "4,800"}, {"d": "172", "p": "9,600"},
    {"d": "257", "p": "14,400"}, {"d": "343", "p": "19,200"},
    {"d": "429", "p": "24,000"}, {"d": "514", "p": "28,800"},
    {"d": "600", "p": "33,600"}, {"d": "706", "p": "38,400"},
    {"d": "878", "p": "48,000"}, {"d": "963", "p": "52,800"},
    {"d": "1049", "p": "57,600"}, {"d": "1135", "p": "62,400"},
    {"d": "1220", "p": "67,200"}, {"d": "1412", "p": "76,800"},
    {"d": "1667", "p": "91,200"}, {"d": "1841", "p": "100,800"},
    {"d": "2195", "p": "115,000"}, {"d": "3688", "p": "192,000"},
    {"d": "4390", "p": "230,000"}, {"d": "5532", "p": "288,000"},
    {"d": "7376", "p": "384,000"}, {"d": "9288", "p": "480,000"}
]

db = {}

@app.route('/order', methods=['POST'])
def order():
    uid = request.form.get('u'); zone = request.form.get('z')
    pkg = request.form.get('p'); amt = request.form.get('a')
    pay = request.form.get('pay'); photo = request.files.get('photo')
    if not pkg: return "Error: Please select a package!"
    oid = os.urandom(2).hex().upper()
    db[oid] = {'u': uid, 'z': zone, 'p': pkg, 'a': amt, 'status': 'Pending'}
    msg = f"🔔 *NEW ORDER: #{oid}*\n🆔 {uid} ({zone})\n💎 {pkg}\n💰 {amt} Ks\n💵 {pay}\n\n🔗 Admin: https://kiwiigameshop.onrender.com/admin?pw={ADMIN_PASSWORD}"
    if photo:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={'chat_id': ADMIN_ID, 'caption': msg, 'parse_mode': 'Markdown'}, 
                      files={'photo': photo.read()})
    return f"Order Success! ID: #{oid}"

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD: return "Unauthorized"
    orders = "".join([f"<div style='border:1px solid #444;margin:5px;padding:10px;'>#{k}: {v['u']} - {v['p']} ({v['a']} Ks)</div>" for k, v in db.items()])
    return f"<html><body style='background:#111;color:white;'><h1>Admin Panel</h1>{orders}</body></html>"

@app.route('/')
def index():
    pkg_items = "".join([f'<div onclick="sel(this,\'{p["d"]}\',\'{p["p"]}\')" style="background:#1e293b;border:1px solid #334155;padding:10px;border-radius:10px;cursor:pointer;text-align:center;">💎 {p["d"]}<br><b style="color:#facc15">{p["p"]} Ks</b></div>' for p in packages])
    return render_template_string(f'''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body {{ background:#0f172a; color:white; font-family:sans-serif; padding:20px; }}
    .grid {{ display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:20px; }}
    .selected {{ border-color: #facc15 !important; background: #334155 !important; }}
    input, select {{ width:100%; padding:12px; margin:5px 0; border-radius:8px; border:1px solid #334155; background:#1e293b; color:white; box-sizing:border-box; }}
    button {{ width:100%; padding:15px; background:#facc15; border:none; border-radius:10px; font-weight:bold; font-size:16px; margin-top:10px; cursor:pointer; }}
</style></head>
<body>
    <h2 style="text-align:center; color:#facc15;">KIWII GAME SHOP</h2>
    <div class="grid">{pkg_items}</div>
    <form action="/order" method="post" enctype="multipart/form-data" style="background:#1e293b; padding:20px; border-radius:15px;">
        <input name="u" placeholder="User ID" required>
        <input name="z" placeholder="Zone ID" required>
        <input id="p_val" name="p" type="hidden">
        <input id="a_val" name="a" type="hidden">
        <select name="pay"><option>KBZPay</option><option>WaveMoney</option></select>
        <p style="font-size:12px; color:#94a3b8; margin:10px 0 5px 0;">Payment Screenshot:</p>
        <input type="file" name="photo" required>
        <button type="submit">CONFIRM ORDER</button>
    </form>
    <script>
    function sel(el, d, p) {{
        var cards = document.getElementsByClassName('grid')[0].children;
        for (var i=0; i<cards.length; i++) {{ cards[i].classList.remove('selected'); }}
        el.classList.add('selected');
        document.getElementById('p_val').value = d;
        document.getElementById('a_val').value = p;
    }}
    </script>
</body></html>''')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    
