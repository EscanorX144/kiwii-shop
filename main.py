import os
from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "1234"
BOT_TOKEN = "7544033321:AAEqM2098y-Y-pX0-23z0_n7Y7-vX3_yYyU"
ADMIN_ID = "7089720301" # သင့် ID နံပါတ်
TELEGRAM_USERNAME = "Bby_kiwii7" # သင့် Username အသစ်

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

@app.route('/check_order', methods=['POST'])
def check_order():
    oid = request.form.get('oid').strip().replace("#", "").upper()
    order = db.get(oid)
    if order:
        st = order['status']
        color = "#ecc94b" if "Pending" in st else "#48bb78"
        return f'''<html><body style="background:#1a202c;color:white;text-align:center;padding-top:50px;font-family:sans-serif;"><div style="background:#2d3748;padding:20px;border-radius:15px;display:inline-block;border:1px solid #4a5568;"><h2 style="color:#ecc94b;">Order Status</h2><p>ID: #{oid}</p><p>Status: <b style="color:{color};">{st}</b></p><a href="/" style="color:#ecc94b;text-decoration:none;">[Back to Shop]</a></div></body></html>'''
    return '<html><body style="background:#1a202c;color:white;text-align:center;padding-top:50px;"><h2>Order Not Found!</h2><a href="/" style="color:#ecc94b;">Back</a></body></html>'

@app.route('/order', methods=['POST'])
def order():
    uid = request.form.get('u'); zone = request.form.get('z')
    pkg = request.form.get('p'); amt = request.form.get('a')
    pay = request.form.get('pay'); photo = request.files.get('photo')
    if not pkg: return "Error: Select Package!"
    oid = os.urandom(2).hex().upper()
    db[oid] = {'u': uid, 'z': zone, 'p': pkg, 'a': amt, 'status': 'Pending ⏳'}
    msg = f"🔔 *NEW ORDER: #{oid}*\n🆔 {uid} ({zone})\n💎 {pkg} Diamonds\n💰 {amt} Ks\n💵 {pay}"
    if photo:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data={'chat_id': ADMIN_ID, 'caption': msg, 'parse_mode': 'Markdown'}, files={'photo': photo.read()})
    return f'''<html><body style="background:#1a202c;color:white;text-align:center;padding-top:100px;font-family:sans-serif;"><h2 style="color:#ecc94b;">✅ Order Success!</h2><p>Your ID: <b style="font-size:24px;">#{oid}</b></p><a href="/" style="color:#ecc94b;text-decoration:none;border:1px solid #ecc94b;padding:10px 20px;border-radius:8px;">Back to Shop</a></body></html>'''

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD: return "Unauthorized"
    action = request.args.get('action'); oid = request.args.get('oid')
    if action == "done" and oid in db: db[oid]['status'] = "Completed ✅"
    orders = "".join([f"<div style='border:1px solid #4a5568;margin:10px;padding:15px;background:#2d3748;border-radius:10px;'><b>#{k}</b>: {v['u']} - {v['p']} [{v['status']}] <a href='/admin?pw={ADMIN_PASSWORD}&action=done&oid={k}' style='color:#ecc94b;margin-left:10px;'>[Mark Done]</a></div>" for k, v in db.items()])
    return f"<html><body style='background:#1a202c;color:white;font-family:sans-serif;padding:20px;'><h1>Admin Panel</h1>{orders}</body></html>"

@app.route('/')
def index():
    pkg_items = "".join([f'<div onclick="sel(this,\'{p["d"]}\',\'{p["p"]}\')" style="background:#2d3748;border:2px solid #4a5568;padding:12px;border-radius:10px;cursor:pointer;text-align:center;font-size:14px;">💎 {p["d"]}<br><b style="color:#ecc94b">{p["p"]} Ks</b></div>' for p in packages])
    return render_template_string(f'''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body {{ background:#1a202c; color:white; font-family:sans-serif; padding:10px; max-width:500px; margin:auto; }}
    .grid {{ display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:20px; }}
    .selected {{ border-color: #ecc94b !important; background: #4a5568 !important; }}
    input, select {{ width:100%; padding:12px; margin:5px 0; border-radius:8px; border:1px solid #4a5568; background:#2d3748; color:white; box-sizing:border-box; }}
    .btn {{ width:100%; padding:15px; background:#ecc94b; border:none; border-radius:10px; font-weight:bold; margin-top:10px; cursor:pointer; color:#1a202c; text-decoration:none; display:block; text-align:center; }}
</style></head>
<body>
    <h3 style="text-align:center;color:#ecc94b;">KIWII GAME SHOP</h3>
    <div class="grid">{pkg_items}</div>
    <form action="/order" method="post" enctype="multipart/form-data" style="background:#2d3748; padding:15px; border-radius:15px; border:1px solid #4a5568;">
        <input name="u" placeholder="User ID" required>
        <input name="z" placeholder="Zone ID" required>
        <input id="p_val" name="p" type="hidden"><input id="a_val" name="a" type="hidden">
        <select name="pay"><option>KBZPay</option><option>WaveMoney</option></select>
        <p style="font-size:12px; color:#a0aec0; margin-top:10px;">Payment Screenshot:</p>
        <input type="file" name="photo" required accept="image/*">
        <button type="submit" class="btn">CONFIRM ORDER</button>
    </form>
    <div style="margin-top:25px; border-top:1px solid #4a5568; padding-top:15px;">
        <form action="/check_order" method="post">
            <input name="oid" placeholder="Order ID (e.g. #A1B2)" required>
            <button type="submit" class="btn" style="background:#4a5568; color:white;">CHECK STATUS</button>
        </form>
        <a href="https://t.me/{TELEGRAM_USERNAME}" class="btn" style="background:#2b6cb0; color:white; margin-top:15px;">CONTACT ADMIN (CS)</a>
    </div>
    <script>function sel(el,d,p){{var cards=document.getElementsByClassName('grid')[0].children;for(var i=0;i<cards.length;i++){{cards[i].classList.remove('selected');}}el.classList.add('selected');document.getElementById('p_val').value=d;document.getElementById('a_val').value=p;}}</script>
</body></html>''')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    
