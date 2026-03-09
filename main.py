import os
from flask import Flask, render_template_string, request, redirect
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "1234"
# Telegram Bot Settings
BOT_TOKEN = "7544033321:AAEqM2098y-Y-pX0-23z0_n7Y7-vX3_yYyU" # သင့် Bot Token
ADMIN_ID = "7443306161" # သင့် Telegram ID

# Diamond Packages List (Rate: 4800 per 86 Gems)
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
    
    oid = os.urandom(2).hex().upper()
    db[oid] = {'u': uid, 'z': zone, 'p': pkg, 'a': amt, 'status': 'Pending'}
    
    msg = f"🔔 *NEW ORDER: #{oid}*\n🆔 {uid} ({zone})\n💎 {pkg}\n💰 Price: {amt} Ks\n💵 User Sent: {amt} Ks ({pay})\n\n🔗 Admin: https://kiwiigameshop.onrender.com/admin?pw={ADMIN_PASSWORD}"
    
    if photo:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={'chat_id': ADMIN_ID, 'caption': msg, 'parse_mode': 'Markdown'}, 
                      files={'photo': photo.read()})
    return f"Order Success! ID: #{oid}. Please wait for processing."

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD: return "Unauthorized"
    return f"<h1>Admin Panel</h1>" + "".join([f"<div>{k}: {v['u']} - {v['p']} [{v['status']}]</div>" for k, v in db.items()])

@app.route('/')
def index():
    pkg_html = "".join([f'<div onclick="sel(\'{p["d"]}\',\'{p["p"]}\')" class="border p-2 rounded cursor-pointer">💎 {p["d"]}<br><b>{p["p"]} Ks</b></div>' for p in packages])
    return render_template_string(f'''
<!DOCTYPE html><html><head><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-[#0f172a] text-white p-4 font-sans">
    <div id="mUI" class="max-w-md mx-auto">
        <h1 class="text-2xl font-black text-yellow-400 text-center mb-6">KIWII GAME SHOP</h1>
        <div class="grid grid-cols-2 gap-2 mb-4">{pkg_html}</div>
        <form action="/order" method="post" enctype="multipart/form-data" class="space-y-3">
            <input name="u" placeholder="User ID" class="w-full p-2 rounded bg-slate-800 border-none" required>
            <input name="z" placeholder="Zone ID" class="w-full p-2 rounded bg-slate-800 border-none" required>
            <input id="p_val" name="p" type="hidden">
            <input id="a_val" name="a" type="hidden">
            <select name="pay" class="w-full p-2 rounded bg-slate-800"><option>KBZPay</option><option>WaveMoney</option></select>
            <input type="file" name="photo" class="text-sm" required>
            <button class="w-full bg-yellow-500 p-3 rounded font-bold text-black">CONFIRM ORDER</button>
        </form>
    </div>
    <script>function sel(d,p){{document.getElementById('p_val').value=d;document.getElementById('a_val').value=p;alert('Selected: '+d);}}</script>
</body></html>''')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
    
