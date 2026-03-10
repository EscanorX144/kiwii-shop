import os
import pymongo
from flask import Flask, render_template_string, request, redirect, url_for
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "1234"
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
ADMIN_ID = "7089720301"
CS_TELEGRAM = "@Bby_kiwii7" # Customer Service Username

# --- MONGODB SETUP ---
MONGO_URL = "mongodb+srv://contisarto_db_user:sta1YjKJxKmuvpxg@cluster0.m2mtomm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = pymongo.MongoClient(MONGO_URL)
db = client.gameshop_db
orders_col = db.orders

# Diamond List
packages = [
    {"d": "11", "p": "700"}, {"d": "22", "p": "1,400"}, {"d": "33", "p": "2,100"},
    {"d": "44", "p": "2,800"}, {"d": "56", "p": "3,500"}, {"d": "112", "p": "7,000"},
    {"d": "Weekly Pass", "p": "5,800"}, {"d": "Twilight Pass", "p": "32,000"},
    {"d": "86", "p": "4,800"}, {"d": "172", "p": "9,600"}, {"d": "257", "p": "14,400"},
    {"d": "343", "p": "19,200"}, {"d": "429", "p": "24,000"}, {"d": "514", "p": "28,800"},
    {"d": "600", "p": "33,600"}, {"d": "706", "p": "38,400"}, {"d": "878", "p": "48,000"},
    {"d": "963", "p": "52,800"}, {"d": "1049", "p": "57,600"}, {"d": "1135", "p": "62,400"},
    {"d": "1221", "p": "67,200"}, {"d": "1412", "p": "76,800"}, {"d": "1667", "p": "91,200"},
    {"d": "1841", "p": "100,800"}, {"d": "2195", "p": "115,000"}, {"d": "3688", "p": "192,000"},
    {"d": "4390", "p": "230,000"}, {"d": "5532", "p": "288,000"}, {"d": "7376", "p": "384,000"},
    {"d": "9288", "p": "480,000"}
]

@app.route('/order', methods=['POST'])
def order():
    uid = request.form.get('u'); zone = request.form.get('z')
    pkg_name = request.form.get('p'); amt = request.form.get('a')
    pay = request.form.get('pay'); photo = request.files.get('photo')
    oid = os.urandom(2).hex().upper()
    
    orders_col.insert_one({
        "id": oid, "uid": uid, "zone": zone, "pkg": pkg_name, 
        "amt": amt, "status": "Pending ⏳", "note": ""
    })
    
    admin_link = f"https://kiwiigameshop.onrender.com/admin?pw={ADMIN_PASSWORD}"
    msg = f"🔔 *NEW ORDER: #{oid}*\n🆔 *ID:* `{uid}` (`{zone}`)\n💎 *Item:* {pkg_name}\n💰 *Price:* {amt} Ks\n💵 *Pay:* {pay}\n\n🔗 [Open Admin Panel]({admin_link})"

    if photo:
        photo.seek(0)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      data={'chat_id': ADMIN_ID, 'caption': msg, 'parse_mode': 'Markdown'}, 
                      files={'photo': photo})
                      
    return render_template_string('''
    <html><body style="background:#0f172a;color:white;text-align:center;padding:80px 20px;font-family:sans-serif;">
        <h2 style="color:#22c55e;">Order Success! ✅</h2>
        <p style="font-size:18px;">Order ID: <b style="color:#fbbf24;">#{{oid}}</b></p>
        <p>Status ကို Website တွင် ပြန်စစ်နိုင်ပါသည်</p>
        <div style="margin:30px 0; padding:20px; background:#1e293b; border-radius:15px;">
            <p>တစ်ခုခု အဆင်မပြေပါက ဆက်သွယ်ရန်</p>
            <a href="https://t.me/{{cs_link}}" style="color:#38bdf8;text-decoration:none;font-weight:bold;">💬 Customer Service: {{cs}}</a>
        </div>
        <a href="/" style="background:#fbbf24;color:#0f172a;padding:12px 25px;border-radius:10px;text-decoration:none;font-weight:bold;">Back to Shop</a>
    </body></html>''', oid=oid, cs=CS_TELEGRAM, cs_link=CS_TELEGRAM.replace("@",""))

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD: return "Unauthorized", 401
    order_rows = ""
    for v in orders_col.find().sort("_id", -1):
        order_rows += f'''
        <div style="border:1px solid #334155; margin-bottom:10px; padding:15px; background:#1e293b; border-radius:12px;">
            <b>#{v['id']}</b>: {v['uid']} ({v['zone']}) - {v['pkg']} <br> Status: <b style="color:#fbbf24">{v['status']}</b> {f'({v["note"]})' if v['note'] else ''}<br><br>
            <a href="/done/{v['id']}?pw={ADMIN_PASSWORD}" style="background:#22c55e; color:white; padding:8px 16px; border-radius:8px; text-decoration:none;">DONE</a>
            <form action="/reject/{v['id']}" style="display:inline;margin-left:10px;">
                <input name="pw" type="hidden" value="{ADMIN_PASSWORD}">
                <input name="msg" placeholder="Reason" style="padding:8px;border-radius:8px;background:#0f172a;color:white;border:1px solid #334155;">
                <button type="submit" style="background:#ef4444; color:white; border:none; padding:8px 16px; border-radius:8px;">REJECT</button>
            </form>
        </div>'''
    return f"<html><body style='background:#0f172a;color:white;padding:20px;font-family:sans-serif;'><h2>Admin Control</h2>{order_rows or 'No orders'}</body></html>"

@app.route('/done/<oid>')
def done(oid):
    if request.args.get('pw') == ADMIN_PASSWORD:
        orders_col.update_one({"id": oid}, {"$set": {"status": "Success ✅"}})
    return redirect(url_for('admin', pw=ADMIN_PASSWORD))

@app.route('/reject/<oid>')
def reject(oid):
    pw = request.args.get('pw'); msg = request.args.get('msg') or "Payment Incorrect"
    if pw == ADMIN_PASSWORD:
        orders_col.update_one({"id": oid}, {"$set": {"status": "Rejected ❌", "note": msg}})
    return redirect(url_for('admin', pw=ADMIN_PASSWORD))

@app.route('/check', methods=['GET', 'POST'])
def check():
    res = ""
    if request.method == 'POST':
        oid = request.form.get('oid', '').strip().upper().replace("#", "")
        o = orders_col.find_one({"id": oid})
        if o:
            res = f"<div style='background:#1e293b;padding:20px;border-radius:15px;margin-top:20px;border:1px solid #fbbf24;'>Status: <b>{o['status']}</b><br>Note: {o['note'] or '-'}</div>"
        else: res = "<p style='color:#ef4444;margin-top:15px;'>ID မမှန်ပါဗျ။</p>"
    return render_template_string('<html><body style="background:#0f172a;color:white;text-align:center;padding:50px;font-family:sans-serif;"><h3>Check Order Status</h3><form method="post"><input name="oid" placeholder="Order ID" style="padding:14px;border-radius:10px;"><button type="submit" style="padding:14px;background:#fbbf24;border:none;border-radius:10px;margin-left:5px;">CHECK</button></form>{{res|safe}}<br><a href="/" style="color:#94a3b8;text-decoration:none;">Back</a></body></html>', res=res)

@app.route('/')
def index():
    pkg_items = "".join([f'<div class="pkg-card" onclick="sel(this,\'{p["d"]}\',\'{p["p"]}\')"><span>{p["d"]} 💎</span><br><b style="color:#fbbf24">{p["p"]} Ks</b></div>' for p in packages])
    return render_template_string('''
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
    body { background:#0f172a; color:white; font-family:sans-serif; padding:15px; max-width:500px; margin:auto; }
    .grid { display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:20px; }
    .pkg-card { background:#1e293b; border:1px solid #334155; padding:15px; border-radius:12px; cursor:pointer; text-align:center; transition: 0.3s; }
    .selected { border-color: #fbbf24; background: #334155; transform: scale(0.95); }
    input, select { width:100%; padding:14px; margin:8px 0; border-radius:12px; border:1px solid #334155; background:#0f172a; color:white; box-sizing:border-box; }
    .buy-btn { width:100%; padding:16px; background:#fbbf24; border:none; border-radius:12px; font-weight:bold; cursor:pointer; font-size:16px; margin-top:10px; }
    .footer { text-align:center; margin-top:30px; padding:20px; color:#94a3b8; font-size:14px; }
</style></head>
<body>
    <h2 style="text-align:center;color:#fbbf24;">KIWII GAME SHOP</h2>
    <div class="grid">{{pkg_items | safe}}</div>
    <form action="/order" method="post" enctype="multipart/form-data" style="background:#1e293b;padding:20px;border-radius:20px;">
        <input name="u" placeholder="User ID" required>
        <input name="z" placeholder="Zone ID" required>
        <input id="p_val" name="p" type="hidden"><input id="a_val" name="a" type="hidden">
        <select name="pay"><option>KBZPay</option><option>WaveMoney</option></select>
        <p style="font-size:12px;color:#94a3b8;">ငွေလွှဲ Screenshot ထည့်ပေးပါ</p>
        <input type="file" name="photo" required accept="image/*">
        <button type="submit" class="buy-btn">PLACE ORDER</button>
        <a href="/check" style="display:block;text-align:center;margin-top:15px;color:#94a3b8;text-decoration:none;">🔍 Check Status</a>
    </form>
    <div class="footer">
        <p>Support: <a href="https://t.me/{{cs_link}}" style="color:#fbbf24;text-decoration:none;">{{cs}}</a></p>
    </div>
    <script>function sel(el,d,p){var cards=document.getElementsByClassName('pkg-card');for(var i=0;i<cards.length;i++){cards[i].classList.remove('selected');}el.classList.add('selected');document.getElementById('p_val').value=d;document.getElementById('a_val').value=p;}</script>
</body></html>''', pkg_items=pkg_items, cs=CS_TELEGRAM, cs_link=CS_TELEGRAM.replace("@",""))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
