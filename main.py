import os
from flask import Flask, render_template_string, request, redirect
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
    uid = request.form.get('u')
    zone = request.form.get('z')
    pkg = request.form.get('p')
    amt = request.form.get('a')
    pay = request.form.get('pay')
    photo = request.files.get('photo')
    
    if not pkg:
        return "Please select a Diamond Package first!"
    
    oid = os.urandom(2).hex().upper()
    db[oid] = {'u': uid, 'z': zone, 'p': pkg, 'a': amt, 'status': 'Pending'}
    
    msg = f"🔔 *NEW ORDER: #{oid}*\n🆔 {uid} ({zone})\n💎 {pkg}\n💰 Price: {amt} Ks\n💵 Method: {pay}\n\n🔗 Admin: https://kiwiigameshop.onrender.com/admin?pw={ADMIN_PASSWORD}"
    
    if photo:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={'chat_id': ADMIN_ID, 'caption': msg, 'parse_mode': 'Markdown'}, 
                      files={'photo': photo.read()})
    return f"Order Success! ID: #{oid}. Please wait for processing."

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD: return "Unauthorized"
    return f"<h1>Admin Panel</h1>" + "".join([f"<div>#{k}: {v['u']} - {v['p']} [{v['status']}]</div>" for k, v in db.items()])

@app.route('/')
def index():
    pkg_html = "".join([f'<div onclick="sel(this, \'{p["d"]}\',\'{p["p"]}\')" class="pkg-card border border-slate-700 p-3 rounded-xl cursor-pointer bg-slate-800 hover:border-yellow-400 transition-all text-center">💎 {p["d"]}<br><b class="text-yellow-400">{p["p"]} Ks</b></div>' for p in packages])
    return render_template_string(f'''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><script src="https://cdn.tailwindcss.com"></script>
<style>.selected {{ border-color: #facc15 !important; background-color: #1e293b !important; }}</style></head>
<body class="bg-[#0f172a] text-white p-4 font-sans">
    <div id="mUI" class="max-w-md mx-auto">
        <h1 class="text-3xl font-black text-yellow-400 text-center mb-6 tracking-tighter">KIWII GAME SHOP</h1>
        <div class="grid grid-cols-2 gap-3 mb-6">{pkg_html}</div>
        <form action="/order" method="post" enctype="multipart/form-data" class="space-y-4 bg-slate-900 p-5 rounded-2xl shadow-xl">
            <div><label class="text-xs text-slate-400 ml-1">USER ID</label><input name="u" placeholder="e.g. 12345678" class="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 focus:outline-none focus:border-yellow-400" required></div>
            <div><label class="text-xs text-slate-400 ml-1">ZONE ID</label><input name="z" placeholder="e.g. 1234" class="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 focus:outline-none focus:border-yellow-400" required></div>
            <input id="p_val" name="p" type="hidden" required>
            <input id="a_val" name="a" type="hidden" required>
            <div><label class="text-xs text-slate-400 ml-1">PAYMENT METHOD</label><select name="pay" class="w-full p-3 rounded-xl bg-slate-800 border border-slate-700 focus:outline-none"><option>KBZPay</option><option>WaveMoney</option></select></div>
            <div><label class="text-xs text-slate-400 ml-1">PAYMENT RECEIPT</label><input type="file" name="photo" class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-yellow-500 file:text-black hover:file:bg-yellow-600" required></div>
            <button type="submit" class="w-full bg-yellow-500 p-4 rounded-xl font-black text-black text-lg shadow-lg shadow-yellow-500/20 active:scale-95 transition-transform">CONFIRM ORDER</button>
        </form>
    </div>
    <script>
    function sel(el, d, p) {{
        document.querySelectorAll('.pkg-card').forEach(c => c.classList.remove('selected'));
        el.classList.add('selected');
        document.getElementById('p_val').value = d;
        document.getElementById('a_val').value = p;
    }}
    </script>
</body></html>''')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    
