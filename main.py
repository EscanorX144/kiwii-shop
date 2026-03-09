import json, os, requests, base64
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
DB_FILE = "orders.json"

# Bot Settings
BOT_TOKEN = "8089066962:AAFOHBGeuDF7E3YgeJ3mUu000sQNJ4uJVok"
CHAT_ID = "7089720301"
ADMIN_PASSWORD = "1234"

# သင့်ရဲ့ အချက်အလက်များ
PHONE_NO = "09775394979"
OWNER_NAME = "Thansin Kyaw"

def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

@app.route('/send_order', methods=['POST'])
def send_order():
    u, z, it, p, a, pay = request.form.get('u'), request.form.get('z'), request.form.get('it'), request.form.get('p'), request.form.get('a'), request.form.get('pay')
    oid = str(os.urandom(2).hex()).upper()
    db = load_db()
    db[oid] = {"status": "⏳ စစ်ဆေးနေဆဲ", "u": u, "z": z, "it": it, "amt": a, "method": pay}
    save_db(db)
    
    msg = (f"🔔 **NEW ORDER: #{oid}**\n🆔 {u} ({z})\n💎 {it}\n💰 Price: {p} Ks\n💵 User Sent: {a} Ks ({pay})\n\n🔗 Admin: http://127.0.0.1:8080/admin?pw={ADMIN_PASSWORD}")
    try:
        f = request.files.get('s')
        if f: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data={'chat_id': CHAT_ID, 'caption': msg, 'parse_mode': 'Markdown'}, files={'photo': f.read()})
        return jsonify({"status": "success", "oid": oid})
    except: return jsonify({"status": "error"})

@app.route('/check_status/<oid>')
def check_status(oid):
    db = load_db()
    res = db.get(oid.upper())
    return jsonify(res if res else {"status": "❌ Order ID မမှန်ကန်ပါ"})

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD: return "🔒 Admin Password လိုအပ်ပါသည်။"
    db = load_db()
    rows = ""
    for k, v in reversed(list(db.items())):
        rows += f"""<div style='background:#1e293b; color:white; padding:15px; margin-bottom:10px; border-radius:15px; border:1px solid #475569;'>
            <b>ID: #{k}</b> | {v['u']} | {v['it']} ({v['amt']} Ks via {v.get('method','Kpay')})<br>
            Status: <span style='color:#fbbf24'>{v['status']}</span><br><br>
            <a href='/upd/{k}/Done?pw={pw}' style='background:#22c55e; color:white; padding:8px 15px; text-decoration:none; border-radius:8px; font-size:12px;'>✅ ပြီးစီး</a>
            <a href='/upd/{k}/Low?pw={pw}' style='background:#ef4444; color:white; padding:8px 15px; text-decoration:none; border-radius:8px; font-size:12px;'>⚠️ ငွေမပြည့်</a>
        </div>"""
    return f"<html><body style='background:#0f172a; color:white; font-family:sans-serif; padding:20px;'><h2>Order Management</h2>{rows if rows else 'No orders.'}</body></html>"

@app.route('/upd/<oid>/<st>')
def upd(oid, st):
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD: return "Unauthorized"
    db = load_db()
    if oid in db:
        db[oid]['status'] = "✅ ပြီးစီးပါပြီ" if st=="Done" else "⚠️ ငွေလွှဲမပြည့်ပါ"
        save_db(db)
    return f"Updated! <a href='/admin?pw={pw}' style='color:yellow'>Back</a>"

@app.route('/')
def index():
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
    
    pkg_html = "".join([f'''<div onclick="sel(this,'{p['d']}','{p['p']}')" class="pkg bg-[#2d3a4f] p-3 rounded-xl border border-slate-600 text-center cursor-pointer transition-all active:scale-95">
        <div class="text-[10px] text-gray-400 font-bold">💎 {p['d']}</div><div class="text-yellow-500 font-black text-sm">{p['p']} Ks</div></div>''' for p in packages])

    return render_template_string(f'''
    <!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script><style>.active{{border-color:#fbbf24!important;background:#334155!important;}}</style></head>
    <body class="bg-[#0f172a] text-white p-4 font-sans min-h-screen">
    <div id="mUI" class="max-w-md mx-auto bg-[#1e293b] p-6 rounded-[2.5rem] border border-slate-700 shadow-2xl">
        <h1 class="text-2xl font-black text-yellow-500 mb-6 text-center italic uppercase">KIWII GAME SHOP</h1>
        
        <div class="grid grid-cols-3 gap-2 mb-3">
            <input id="u" placeholder="User ID" class="col-span-2 bg-[#0f172a] p-3 rounded-xl border border-slate-600 outline-none text-sm">
            <input id="z" placeholder="Zone" class="bg-[#0f172a] p-3 rounded-xl border border-slate-600 outline-none text-sm">
        </div>
        
        <input id="amt" type="number" placeholder="လွှဲလိုက်သည့်ငွေ (Amount)" class="w-full bg-[#0f172a] p-3 rounded-xl border border-slate-600 outline-none text-yellow-500 font-bold mb-4">
        
        <div class="grid grid-cols-2 gap-2 mb-6 max-h-[160px] overflow-y-auto pr-1">{pkg_html}</div>
        
        <div class="flex gap-2 mb-4">
            <button onclick="setPay('Kpay')" id="bk" class="flex-1 py-2 rounded-xl border border-yellow-500 bg-yellow-500 text-black font-bold text-xs uppercase">KBZ Pay</button>
            <button onclick="setPay('Wave')" id="bw" class="flex-1 py-2 rounded-xl border border-slate-600 bg-slate-800 text-white font-bold text-xs uppercase">Wave Money</button>
        </div>

        <div class="bg-[#0f172a]/50 p-6 rounded-2xl border border-slate-700 text-center mb-6">
            <p id="payTitle" class="text-[10px] text-gray-400 mb-2 font-bold uppercase tracking-widest">KBZ Pay Number</p>
            <div class="flex items-center justify-center gap-3">
                <span id="pNo" class="text-2xl font-black text-white tracking-widest">{PHONE_NO}</span>
                <button onclick="copyNo()" class="bg-slate-700 px-3 py-1 rounded-lg text-[10px] font-black active:bg-green-500 transition-colors uppercase">Copy</button>
            </div>
            <p class="text-[10px] text-yellow-500 mt-3 font-bold uppercase tracking-wider">Name - {OWNER_NAME}</p>
            <div class="mt-2 inline-block px-3 py-1 bg-red-500/20 border border-red-500/50 rounded-full">
                <p class="text-[9px] text-red-400 font-bold uppercase">Note မှာ "Payment" လို့ရေးပေးပါ</p>
            </div>
        </div>

        <div class="mb-6">
            <label class="text-[10px] text-gray-400 block mb-2 font-bold uppercase">ပြေစာတင်ရန် (Screenshot)</label>
            <input id="ss" type="file" accept="image/*" class="text-xs bg-slate-800 w-full p-2 rounded-xl border border-slate-700">
        </div>
        
        <button onclick="send()" id="btn" class="w-full py-4 bg-yellow-500 text-black font-black rounded-2xl uppercase shadow-lg active:scale-95 transition-all">Confirm Order</button>
        
        <div class="mt-8 border-t border-slate-700 pt-6">
            <h3 class="text-sm font-bold mb-3 text-center text-blue-400 uppercase tracking-widest">Check Order Status</h3>
            <div class="flex gap-2">
                <input id="soid" placeholder="Order ID" class="flex-1 bg-slate-800 p-3 rounded-xl text-sm uppercase outline-none border border-slate-700 focus:border-blue-500">
                <button onclick="check()" class="bg-blue-600 px-6 rounded-xl text-sm font-bold active:scale-95 transition-all shadow-lg">Check</button>
            </div>
            <div id="stext" class="mt-4 p-4 bg-slate-900 rounded-xl text-center font-bold text-yellow-400 border border-slate-700" style="display: none;"></div>
        </div>
    </div>

    <script>
    let sd="", sp="", payMeth="Kpay";

    function setPay(m){{
        payMeth = m;
        document.getElementById('payTitle').innerText = m.toUpperCase() + " NUMBER";
        document.getElementById('bk').className = (m=='Kpay') ? "flex-1 py-2 rounded-xl border border-yellow-500 bg-yellow-500 text-black font-bold text-xs uppercase" : "flex-1 py-2 rounded-xl border border-slate-600 bg-slate-800 text-white font-bold text-xs uppercase";
        document.getElementById('bw').className = (m=='Wave') ? "flex-1 py-2 rounded-xl border border-yellow-500 bg-yellow-500 text-black font-bold text-xs uppercase" : "flex-1 py-2 rounded-xl border border-slate-600 bg-slate-800 text-white font-bold text-xs uppercase";
    }}

    function copyNo(){{
        const no = document.getElementById('pNo').innerText;
        navigator.clipboard.writeText(no);
        alert("Copied: " + no);
    }}

    function sel(el,d,p){{
        document.querySelectorAll('.pkg').forEach(c=>c.classList.remove('active')); 
        el.classList.add('active'); sd=d; sp=p;
    }}

    function send(){{
        const u=document.getElementById('u').value, z=document.getElementById('z').value, a=document.getElementById('amt').value, f=document.getElementById('ss').files[0], b=document.getElementById('btn');
        if(!u || !z || !a || !f || !sd) return alert("အချက်အလက်များကို အကုန်ဖြည့်ပါ!");
        b.innerText="Sending..."; b.disabled=true;
        const fd = new FormData(); fd.append('u',u); fd.append('z',z); fd.append('it',sd); fd.append('p',sp); fd.append('a',a); fd.append('s',f); fd.append('pay',payMeth);
        fetch('/send_order',{{method:'POST',body:fd}}).then(r=>r.json()).then(d=>{{
            alert("အောင်မြင်ပါသည်။ Order ID: #" + d.oid); location.reload();
        }}).catch(()=>{{ alert("Error!"); b.disabled=false; b.innerText="Confirm Order"; }});
    }}

    function check(){{
        let id = document.getElementById('soid').value.trim().toUpperCase().replace('#','');
        if(!id) return alert("Order ID ရိုက်ထည့်ပါ");
        fetch(window.location.origin + '/check_status/' + id).then(r=>r.json()).then(d=>{{
            const s=document.getElementById('stext'); s.innerText = d.status; s.style.display="block";
        }}).catch(()=>alert("ID မရှိပါ သို့မဟုတ် Error ဖြစ်နေပါသည်"));
    }}
    </script></body></html>''')

if __name__ == '__main__': app.run(host='0.0.0.0', port=8080)
