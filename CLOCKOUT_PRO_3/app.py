from __future__ import annotations
import streamlit as st
import streamlit.components.v1 as components
import sqlite3, json, uuid, base64
from pathlib import Path
from datetime import datetime, time, date

BASE = Path(__file__).parent
DB = BASE / 'clockout.db'
ASSETS = BASE / 'assets'

st.set_page_config(page_title='CLOCKOUT | Wake up different', page_icon='⏰', layout='wide', initial_sidebar_state='collapsed')

# --------------------------- DATABASE ---------------------------
def db():
    c = sqlite3.connect(DB, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS profile(id INTEGER PRIMARY KEY CHECK(id=1), name TEXT, email TEXT);
        CREATE TABLE IF NOT EXISTS alarms(id TEXT PRIMARY KEY, label TEXT, alarm_time TEXT, days TEXT, enabled INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS device(id INTEGER PRIMARY KEY CHECK(id=1), code TEXT, model TEXT, color TEXT, battery INTEGER, connected INTEGER);
        CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY, created TEXT, items TEXT, total REAL, status TEXT);
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT, detail TEXT, created TEXT);
        CREATE TABLE IF NOT EXISTS products(id TEXT PRIMARY KEY, name TEXT, shape TEXT, line TEXT, color TEXT, price REAL, stock INTEGER);
        ''')
        if not c.execute('SELECT 1 FROM profile WHERE id=1').fetchone():
            c.execute('INSERT INTO profile VALUES(1,?,?)', ('John', 'john@clockout.demo'))
        if not c.execute('SELECT 1 FROM products').fetchone():
            products = [
                ('rect','Rectangular Clásica','Rectangular','CLOCKOUT','Terracota',150,18),
                ('circ','Circular Confort','Circular','CLOCKOUT','Cream',150,14),
                ('wave','Ondulada','Ondulada','CLOCKOUT','Sage Green',150,12),
                ('tou','Ondulada Premium','Ondulada','TOUCLOCK','Sage Green',220,8),
                ('tou2','Circular Premium','Circular','TOUCLOCK','Gris',220,6),
            ]
            c.executemany('INSERT INTO products VALUES(?,?,?,?,?,?,?)', products)
        if not c.execute('SELECT 1 FROM device WHERE id=1').fetchone():
            c.execute('INSERT INTO device VALUES(1, NULL, NULL, NULL, 78, 0)')
        if not c.execute('SELECT 1 FROM alarms').fetchone():
            c.execute('INSERT INTO alarms VALUES(?,?,?,?,?)', ('a1','Despertar','07:00','Lun,Mar,Mié,Jue,Vie',1))
            c.execute('INSERT INTO alarms VALUES(?,?,?,?,?)', ('a2','Fin de semana','09:30','Sáb,Dom',0))

def event(kind, detail):
    with db() as c:
        c.execute('INSERT INTO events(kind,detail,created) VALUES(?,?,?)', (kind, detail, datetime.now().isoformat(timespec='seconds')))

init_db()

# --------------------------- GOOGLE ANALYTICS 4 ---------------------------
# Medición de visitas y vistas de sección. No se envían nombres, correos ni
# otros datos introducidos por los usuarios.
GA4_MEASUREMENT_ID = "G-ZHT2XGGQG4"


def track_analytics_view(section: str) -> None:
    """Envía una vista cuando cambia la sección visible de CLOCKOUT."""
    safe_section = json.dumps(section, ensure_ascii=False)

    html = f'''
    <script>
    (function() {{
        window.dataLayer = window.dataLayer || [];

        window.gtag = window.gtag || function() {{
            window.dataLayer.push(arguments);
        }};

        if (!document.getElementById('clockout-ga4-script')) {{
            var gaScript = document.createElement('script');
            gaScript.id = 'clockout-ga4-script';
            gaScript.async = true;
            gaScript.src = 'https://www.googletagmanager.com/gtag/js?id={GA4_MEASUREMENT_ID}';
            document.head.appendChild(gaScript);

            window.gtag('js', new Date());
            window.gtag('config', '{GA4_MEASUREMENT_ID}', {{
                send_page_view: false
            }});
        }}

        var sectionName = {safe_section};
        var pageLocation = window.location.href;

        try {{
            pageLocation = window.parent.location.href;
        }} catch (e) {{}}

        window.gtag('event', 'page_view', {{
            page_title: 'CLOCKOUT | ' + sectionName,
            page_location: pageLocation.split('?')[0] + '?vista=' + encodeURIComponent(sectionName),
            page_path: '/?vista=' + encodeURIComponent(sectionName)
        }});
    }})();
    </script>
    '''

    st.html(html, unsafe_allow_javascript=True)



# --------------------------- STYLE ---------------------------
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
:root{--forest:#102d23;--forest2:#183d30;--cream:#f6f3ed;--orange:#ef6b21;--sage:#dce8d5;--ink:#17231d;}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:var(--cream);color:var(--ink)}
header{visibility:hidden}.block-container{padding:0.7rem 1.05rem 2rem;max-width:1600px}
[data-testid="stSidebar"]{background:#102d23}
.topbar{background:linear-gradient(105deg,#0d281f,#194333);border:1px solid #315747;border-radius:15px;padding:12px 18px;color:white;margin-bottom:12px}
.brand{font-size:29px;font-weight:800;letter-spacing:2px;line-height:1;display:flex;align-items:center;gap:9px}
.brand span{color:#f2762e}
.brand-mark{width:31px;height:31px;border:2px solid #dcebdc;border-radius:9px;display:inline-flex;align-items:center;justify-content:center;position:relative;background:linear-gradient(145deg,#2d654b,#102d23);box-shadow:inset 0 0 0 2px rgba(255,255,255,.06)}
.brand-mark:before{content:' ';width:13px;height:13px;border:2px solid #dcebdc;border-radius:50%;display:block}
.brand-mark:after{content:'';position:absolute;width:2px;height:7px;background:#f2762e;top:7px;left:15px;transform:rotate(35deg);transform-origin:bottom}
.product-desc{font-size:12px;line-height:1.35;color:#59635c;min-height:34px;margin:4px 0}
.brand-sub{font-size:9px;letter-spacing:2px;color:#e3e9e2}
.hero{min-height:310px;border-radius:20px;overflow:hidden;padding:28px 32px;background-size:cover;background-position:center;display:flex;align-items:center;color:#fff;box-shadow:0 10px 28px rgba(10,35,25,.15)}
.hero h1{font-size:46px;line-height:1.02;margin:0;font-weight:800}.hero h1 em{color:#c9efad;font-style:normal}.hero p{font-size:16px;max-width:360px;color:#f4f2ec}
.panel{background:#fff;border:1px solid #e8e3da;border-radius:18px;padding:16px 18px;margin:12px 0;box-shadow:0 5px 18px rgba(27,38,30,.045)}
.panel-dark{background:linear-gradient(155deg,#173b2e,#0d281f);border:1px solid #365b49;border-radius:20px;padding:18px;color:white;box-shadow:0 8px 25px rgba(9,28,21,.16)}
.dashboard-card{background:linear-gradient(145deg,#204b39,#153426);border:1px solid #496b57;border-radius:13px;padding:12px 14px;color:#fff;margin:8px 0}
.dashboard-card .sub{font-size:11px;color:#d7e5db}
.topbar{box-shadow:0 5px 18px rgba(10,35,25,.12)}
.product img{height:155px;object-fit:cover}
.stSelectbox label,.stTextInput label{font-size:12px;font-weight:600}
@media(max-width:1050px){.hero{min-height:260px}.hero h1{font-size:36px}}
.section-title{font-size:24px;font-weight:800;margin:2px 0 12px;color:#101b16}.section-title:before{content:'';display:inline-block;width:5px;height:24px;background:#f2762e;border-radius:5px;margin-right:10px;vertical-align:-4px}
.metric{background:linear-gradient(145deg,#204b39,#153426);border:1px solid #4c705b;border-radius:14px;padding:13px 8px;text-align:center;color:white;min-height:100px}
.metric .big{font-size:26px;font-weight:800}.muted{color:#7b827c;font-size:12px}
.product{background:white;border:1px solid #e7e0d5;border-radius:16px;padding:10px;height:100%;box-shadow:0 4px 12px rgba(0,0,0,.05)}
.product-premium{border:2px solid #e9c65e;background:#fffdf6}
.price{font-size:22px;font-weight:800;color:#963c20}.tag{display:inline-block;border-radius:20px;padding:4px 10px;font-size:11px;font-weight:800;background:#e4eddf;color:#244b35}.tag-gold{background:#fff0c8;color:#6b4b00}
.rule{background:#f9eadf;border-left:5px solid #ef6b21;padding:13px 16px;border-radius:10px;color:#633d2b}
.small-note{font-size:11px;color:#8b918a}
.stButton>button{border-radius:11px;border:1px solid #d8ddd5;font-weight:700;min-height:38px}
.stButton>button[kind="primary"]{background:#ed6a21;border-color:#ed6a21;color:white}
.stTextInput input,.stNumberInput input,.stSelectbox div[data-baseweb="select"],.stTimeInput input{border-radius:10px}
div[data-testid="stForm"]{border:1px solid #e7e2d8;border-radius:14px;padding:14px}
hr{border-color:#e8e2d9}
@media(max-width:900px){.hero h1{font-size:34px}.block-container{padding:0.5rem}}
</style>
''', unsafe_allow_html=True)

# Hero fotográfico local para que la portada no dependa de Unsplash
hero_path = ASSETS / 'hero_clockout.jpg'
if hero_path.exists():
    hero_b64 = base64.b64encode(hero_path.read_bytes()).decode('ascii')
    st.markdown(f"<style>.hero{{background-image:linear-gradient(90deg,rgba(8,34,25,.98) 0%,rgba(8,34,25,.86) 34%,rgba(8,34,25,.05) 100%),url('data:image/jpeg;base64,{hero_b64}');}}</style>", unsafe_allow_html=True)

# --------------------------- HELPERS ---------------------------
COLORS = {'Terracota':'#b95f43','Sage Green':'#81957b','Gris':'#929895','Cream':'#e8d7b5'}
SHAPES = ['Rectangular','Circular','Ondulada']
DAYS = ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom']

def money(v): return f'S/ {v:,.2f}'
def get_profile():
    with db() as c: return c.execute('SELECT * FROM profile WHERE id=1').fetchone()
def get_device():
    with db() as c: return c.execute('SELECT * FROM device WHERE id=1').fetchone()
def get_alarms():
    with db() as c: return c.execute('SELECT * FROM alarms ORDER BY alarm_time').fetchall()
def get_products():
    with db() as c: return c.execute("""
        SELECT * FROM products
        ORDER BY CASE line WHEN 'CLOCKOUT' THEN 0 ELSE 1 END,
                 CASE shape WHEN 'Rectangular' THEN 0 WHEN 'Circular' THEN 1 WHEN 'Ondulada' THEN 2 ELSE 3 END,
                 name
        """).fetchall()
def rug_html(shape,color):
    """Fotografía local del modelo; no depende de enlaces externos."""
    import base64
    files = {
        'Rectangular': 'rug_rectangular.jpg',
        'Circular': 'rug_circular.jpg',
        'Ondulada': 'rug_wavy.jpg',
    }
    path = ASSETS / files.get(shape, 'rug_rectangular.jpg')
    if path.exists():
        encoded = base64.b64encode(path.read_bytes()).decode('ascii')
        return f'<img src="data:image/jpeg;base64,{encoded}" alt="Alfombra CLOCKOUT {shape}" style="width:100%;height:155px;object-fit:cover;display:block;border-radius:12px;background:#e8e2d8"/>'
    return '<div style="height:155px;background:#dce8d5;border-radius:12px;display:grid;place-items:center;color:#244b35;font-weight:700">CLOCKOUT SMART RUG</div>'

def nav_button(label, key, current):
    return st.button(('● ' if current==key else '')+label, key='nav_'+key, type='primary' if current==key else 'secondary', use_container_width=True)

# --------------------------- SESSION ---------------------------
if 'page' not in st.session_state: st.session_state.page='Inicio'
if 'cart' not in st.session_state: st.session_state.cart={}
if 'last_notice' not in st.session_state: st.session_state.last_notice=''
if 'sim_alarm' not in st.session_state: st.session_state.sim_alarm=False
if 'sim_steps' not in st.session_state: st.session_state.sim_steps=0

profile=get_profile(); device=get_device()

# --------------------------- HEADER ---------------------------
with st.container():
    st.markdown('<div class="topbar"><div class="brand"><span class="brand-mark"></span><span style="color:#fff">CLOCKOUT<span>.</span></span></div><div class="brand-sub">ALFOMBRAS DESPERTADOR INTELIGENTES · WAKE UP DIFFERENT</div></div>', unsafe_allow_html=True)
navs=['Inicio','Tienda','Mi Dispositivo','Rutinas','Comunidad','Soporte']
cols=st.columns([1.05,1,1.35,0.9,1,0.85,0.55,0.55])
for i,n in enumerate(navs):
    with cols[i]:
        if nav_button(n, n, st.session_state.page): st.session_state.page=n; st.rerun()
with cols[6]:
    if st.button(f'🛒 {sum(st.session_state.cart.values())}',use_container_width=True): st.session_state.page='Carrito'; st.rerun()
with cols[7]:
    if st.button('👤',use_container_width=True): st.session_state.page='Mi Perfil'; st.rerun()

# --------------------------- SIDEBAR PANEL ---------------------------
def sidebar_dashboard():
    """Panel derecho inspirado en el dashboard de referencia."""
    p=get_profile(); d=get_device(); alarms=get_alarms()
    events=0
    with db() as c:
        events=c.execute("SELECT COUNT(*) n FROM events WHERE kind='pisada'").fetchone()['n']
    st.markdown(f"<h3 style='margin:0;color:white'>👋 ¡Hola, {p['name']}!</h3><div style='font-size:12px;color:#d5e3d8'>Mantén tu rutina activa con CLOCKOUT</div>", unsafe_allow_html=True)
    st.markdown('<div style="height:1px;background:#456453;margin:14px 0"></div>', unsafe_allow_html=True)
    if d['code']:
        st.markdown(f"<div class='dashboard-card'><b>▰ Mi Alfombra</b><span style='float:right'>🔋 {d['battery']}%</span><div class='sub'>{d['code']} · {d['model']}</div><span style='color:#a8f0a5;font-size:12px'>● Conectada · simulación</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='dashboard-card'><b>▰ Mi Alfombra</b><div class='sub'>Aún no has vinculado un dispositivo</div></div>", unsafe_allow_html=True)
        if st.button('Vincular alfombra', key='side_pair', use_container_width=True):
            st.session_state.page='Mi Dispositivo'; st.rerun()
    a1,a2=st.columns([1.5,1])
    a1.markdown('### ⏰ Mis alarmas')
    if a2.button('+ Nueva',key='side_new',use_container_width=True):
        st.session_state.page='Rutinas'; st.rerun()
    for a in alarms[:2]:
        state='🟢' if a['enabled'] else '⚪'
        st.markdown(f"<div class='dashboard-card'><b style='font-size:22px'>{a['alarm_time']}</b><span style='float:right'>{state}</span><div class='sub'>▦ {a['days']}</div></div>",unsafe_allow_html=True)
    st.markdown('<div style="height:1px;background:#456453;margin:14px 0"></div>', unsafe_allow_html=True)
    st.markdown('### 📊 Mi progreso')
    m=st.columns(3)
    for col,val,label in zip(m,[f'{min(events,5)}/5',f'{events*5} min',f'{min(100,events*10)}%'],['Días activos','Tiempo estimado','Constancia']):
        col.markdown(f"<div class='metric'><div class='big'>{val}</div><div style='font-size:10px'>{label}</div></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='dashboard-card' style='margin-top:12px'><b>🔥 Racha de constancia</b><br><span style='font-size:24px;font-weight:800'>{min(events,12)} días</span><br><span class='sub'>Registra pisadas en el simulador para avanzar</span></div>",unsafe_allow_html=True)
    st.markdown('### 🏅 Logros')
    ach=st.columns(2)
    ach[0].markdown("<div class='metric'>🌱<br><b>Inicio activo</b><br><small>Primera pisada</small></div>",unsafe_allow_html=True)
    ach[1].markdown(f"<div class='metric'>⏰<br><b>Constante</b><br><small>{events} registros</small></div>",unsafe_allow_html=True)

# --------------------------- PAGES ---------------------------
def home():
    left,right=st.columns([2.12,0.95],gap='medium')
    with left:
        st.markdown('''<div class="hero"><div><h1>Despierta.<br>Levántate.<br><em>Conquista.</em></h1><p>La alfombra inteligente que convierte tu alarma en acción.</p><span class="tag">TECNOLOGÍA PARA TUS MAÑANAS</span></div></div>''',unsafe_allow_html=True)
        feats=st.columns(4)
        for col,icon,title,sub in zip(feats,['▦','👣','▣','▥'],['Tecnología inteligente','Desactivación física','App personalizada','Hábitos saludables'],['Pantalla LED y sensor de presión.','Solo se apaga al pisarla.','Vincula, programa y sigue tu progreso.','Más disciplina, mejor rendimiento.']):
            col.markdown(f"<div style='padding:12px 4px;text-align:center'><div style='font-size:25px;color:#244c37'>{icon}</div><b style='font-size:13px'>{title}</b><div class='muted'>{sub}</div></div>",unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="section-title">Nuestra Colección</div>',unsafe_allow_html=True)
        f1,f2,f3=st.columns([1,1,1]); shape_filter=f1.selectbox('Forma',['Todas']+SHAPES,key='home_shape'); line_filter=f2.selectbox('Línea',['Todas','CLOCKOUT','TOUCLOCK'],key='home_line'); color_filter=f3.selectbox('Color',['Todos']+list(COLORS),key='home_color')
        products=get_products()
        # Orden de escaparate: dos opciones CLOCKOUT de entrada y una TOUCLOCK destacada.
        if shape_filter=='Todas' and line_filter=='Todas' and color_filter=='Todos':
            by_id={p['id']:p for p in products}
            featured_ids=['rect','circ','tou']
            products=[by_id[x] for x in featured_ids if x in by_id]
        else:
            products=[p for p in products if (shape_filter=='Todas' or p['shape']==shape_filter) and (line_filter=='Todas' or p['line']==line_filter) and (color_filter=='Todos' or p['color']==color_filter)]
        grid=st.columns(3)
        for idx,p in enumerate(products[:6]):
            with grid[idx%3]:
                desc = ('Línea de entrada: diseño esencial, alarma LED integrada y desactivación mediante sensor de presión.' if p['line']=='CLOCKOUT' else 'Línea premium: diseño exclusivo TOUCLOCK, experiencia digital avanzada y acabados superiores.')
                st.markdown(f"<div class='product {'product-premium' if p['line']=='TOUCLOCK' else ''}'>{rug_html(p['shape'],p['color'])}<div style='margin-top:8px'><span class='tag {'tag-gold' if p['line']=='TOUCLOCK' else ''}'>{'♛ TOUCLOCK PREMIUM' if p['line']=='TOUCLOCK' else 'CLOCKOUT ESTÁNDAR'}</span></div><b>{p['name']}</b><div class='product-desc'>{desc}</div><div class='small-note'>Pantalla LED en carcasa rígida integrada al borde.</div><div class='price'>{money(p['price'])}</div></div>",unsafe_allow_html=True)
                chosen_color=st.selectbox('Color',list(COLORS),index=list(COLORS).index(p['color']),key='homecolor_'+p['id'])
                cart_key=p['id']+'|'+chosen_color
                if st.button('🛒 Añadir al carrito',key='add_'+p['id'],use_container_width=True):
                    st.session_state.cart[cart_key]=st.session_state.cart.get(cart_key,0)+1; st.toast(f"{p['name']} ({chosen_color}) añadido al carrito"); st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="section-title">¿Cómo funciona?</div>',unsafe_allow_html=True)
        steps=st.columns(4)
        for col,num,ico,txt in zip(steps,['01','02','03','04'],['🛒','📱','⏰','👣'],['Compra tu CLOCKOUT','Vincula tu alfombra','Programa tu alarma','Levántate y písala']): col.markdown(f"<div style='text-align:center'><div style='font-size:30px'>{ico}</div><b>{num}</b><div style='font-size:12px'>{txt}</div></div>",unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with right: sidebar_dashboard()

def shop():
    st.markdown('<div class="section-title">Tienda CLOCKOUT</div><p class="muted">Diseño inteligente para empezar el día con intención.</p>',unsafe_allow_html=True)
    q=st.text_input('Buscar producto',placeholder='Ej. rectangular, sage green...')
    a,b,c=st.columns(3); shape=a.selectbox('Forma',['Todas']+SHAPES); line=b.selectbox('Línea',['Todas','CLOCKOUT','TOUCLOCK']); color=c.selectbox('Color',['Todos']+list(COLORS))
    products=get_products(); products=[p for p in products if (shape=='Todas' or p['shape']==shape) and (line=='Todas' or p['line']==line) and (color=='Todos' or p['color']==color) and (q.lower() in (p['name']+' '+p['color']+' '+p['shape']).lower())]
    cols=st.columns(3)
    for i,p in enumerate(products):
        with cols[i%3]:
            st.markdown(f"<div class='product {'product-premium' if p['line']=='TOUCLOCK' else ''}'>{rug_html(p['shape'],p['color'])}<span class='tag'>{p['line']}</span><h3>{p['name']}</h3><p class='muted'>{p['shape']} · {p['color']} · Pantalla LED integrada en carcasa rígida.</p><div class='price'>{money(p['price'])}</div><small>Stock de demostración: {p['stock']}</small></div>",unsafe_allow_html=True)
            selected=st.selectbox('Color',list(COLORS),index=list(COLORS).index(p['color']),key='shopcolor_'+p['id'])
            cart_key=p['id']+'|'+selected
            if st.button('Añadir al carrito',key='shopadd_'+p['id'],type='primary',use_container_width=True): st.session_state.cart[cart_key]=st.session_state.cart.get(cart_key,0)+1; st.toast('Producto añadido'); st.rerun()

def cart_page():
    st.markdown('<div class="section-title">Mi carrito</div>',unsafe_allow_html=True)
    products={p['id']:p for p in get_products()}; total=0
    if not st.session_state.cart: st.info('Tu carrito está vacío. Explora la tienda para añadir tu primera alfombra.');
    else:
        for cart_key,qty in list(st.session_state.cart.items()):
            pid, chosen_color = cart_key.split('|',1) if '|' in cart_key else (cart_key, products.get(cart_key)['color'] if products.get(cart_key) else 'Sage Green')
            p=products.get(pid)
            if not p: continue
            x,y,z=st.columns([3,1,1]); x.markdown(f"**{p['name']}** · {chosen_color} · {p['line']}<br><span class='muted'>{money(p['price'])} por unidad</span>",unsafe_allow_html=True)
            newqty=y.number_input('Cantidad',1,10,qty,key='qty_'+cart_key)
            if newqty!=qty: st.session_state.cart[cart_key]=newqty
            if z.button('Eliminar',key='del_'+cart_key): del st.session_state.cart[cart_key]; st.rerun()
            total+=p['price']*st.session_state.cart[cart_key]
        st.markdown(f"### Total: {money(total)}")
        if st.button('Confirmar pedido de demostración',type='primary'):
            order_id='CO-'+uuid.uuid4().hex[:8].upper(); items=json.dumps(st.session_state.cart)
            with db() as c: c.execute('INSERT INTO orders VALUES(?,?,?,?,?)',(order_id,datetime.now().isoformat(timespec='minutes'),items,total,'Pedido de demostración'))
            event('pedido',f'Pedido {order_id} por {money(total)}'); st.session_state.cart={}; st.success(f'Pedido {order_id} registrado correctamente. No se realizó ningún cobro.'); st.rerun()
    if st.button('Seguir comprando'): st.session_state.page='Tienda'; st.rerun()

def device_page():
    st.markdown('<div class="section-title">Mi dispositivo</div>',unsafe_allow_html=True)
    d=get_device(); left,right=st.columns([1.2,1])
    with left:
        st.markdown('<div class="panel">### 🔗 Vincular una alfombra<br><span class="muted">Introduce el código incluido en el empaque de tu producto.</span></div>',unsafe_allow_html=True)
        with st.form('pair_form'):
            code=st.text_input('Código de vinculación',placeholder='CLOCK-2026-XXXX')
            model=st.selectbox('Modelo',['Rectangular Clásica','Circular Confort','Ondulada','TOUCLOCK Premium'])
            color=st.selectbox('Color',list(COLORS))
            ok=st.form_submit_button('Vincular dispositivo',type='primary',use_container_width=True)
        if ok:
            if len(code.strip())<6: st.error('El código debe tener al menos 6 caracteres.')
            else:
                with db() as c: c.execute('UPDATE device SET code=?,model=?,color=?,battery=78,connected=1 WHERE id=1',(code.strip().upper(),model,color))
                event('vinculacion',f'Dispositivo {code.strip().upper()} vinculado'); st.success('Dispositivo registrado en esta demostración.'); st.rerun()
    with right:
        st.markdown('<div class="panel-dark"><h3 style="color:white">Estado del dispositivo</h3>',unsafe_allow_html=True)
        if d['code']:
            st.markdown(f"<h2 style='color:white'>{d['model']}</h2><p>{d['code']}</p><h1>🔋 {d['battery']}%</h1><span style='color:#a8f0a5'>● Conectado · simulación</span>",unsafe_allow_html=True)
            if st.button('Simular batería al 100%',key='battery'): 
                with db() as c: c.execute('UPDATE device SET battery=100 WHERE id=1')
                st.rerun()
            if st.button('Desvincular dispositivo',key='unpair'):
                with db() as c: c.execute('UPDATE device SET code=NULL,model=NULL,color=NULL,connected=0 WHERE id=1')
                event('desvinculacion','Dispositivo desvinculado'); st.rerun()
        else: st.markdown('<p style="color:#dce8df">Todavía no hay una alfombra vinculada.</p>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="rule"><b>Regla de oro:</b> La app sirve para vincular y programar la alarma, pero NO se puede apagar desde la app. Debes pararte físicamente sobre la alfombra para desactivarla. En esta versión, la pisada se representa mediante un simulador.</div>',unsafe_allow_html=True)

def routines():
    st.markdown('<div class="section-title">Rutinas y alarmas</div>',unsafe_allow_html=True)
    with st.form('alarm_form'):
        label=st.text_input('Nombre de la alarma',value='Despertar')
        t=st.time_input('Hora',value=time(7,0),step=300)
        days=st.multiselect('Repetir',DAYS,default=['Lun','Mar','Mié','Jue','Vie'])
        submit=st.form_submit_button('Guardar nueva alarma',type='primary')
    if submit:
        aid=uuid.uuid4().hex[:10]
        with db() as c: c.execute('INSERT INTO alarms VALUES(?,?,?,?,1)',(aid,label,t.strftime('%H:%M'),','.join(days)))
        event('alarma',f'Alarma {label} creada a las {t.strftime("%H:%M")}'); st.success('Alarma guardada.'); st.rerun()
    st.markdown('### Tus alarmas')
    for a in get_alarms():
        x,y,z=st.columns([3,1,1]); x.markdown(f"**{a['alarm_time']} — {a['label']}**<br><span class='muted'>{a['days']}</span>",unsafe_allow_html=True)
        enabled=y.toggle('Activa',value=bool(a['enabled']),key='toggle_'+a['id'])
        if enabled!=bool(a['enabled']):
            with db() as c: c.execute('UPDATE alarms SET enabled=? WHERE id=?',(int(enabled),a['id']))
            event('alarma',f'Alarma {a["label"]} '+('activada' if enabled else 'desactivada')); st.rerun()
        if z.button('Eliminar',key='remove_'+a['id']):
            with db() as c: c.execute('DELETE FROM alarms WHERE id=?',(a['id'],))
            st.rerun()
    st.divider(); st.markdown('### 👣 Simulador de presión')
    st.write('Prueba el comportamiento conceptual: activa la alarma y luego registra una pisada sobre la alfombra.')
    if st.session_state.sim_alarm:
        st.error('🔔 ALARMA ACTIVADA — Debes levantarte y pisar la alfombra.')
        if st.button('👣 Simular pisada sobre CLOCKOUT',type='primary'):
            st.session_state.sim_alarm=False; st.session_state.sim_steps+=1; event('pisada','Alarma desactivada mediante pisada simulada'); st.success('Alarma desactivada por presión simulada.'); st.rerun()
    else:
        st.success('Alarma en espera. La desactivación desde la app está bloqueada en esta demostración.')
        if st.button('▶ Simular activación de alarma'): st.session_state.sim_alarm=True; st.rerun()

def profile_page():
    p=get_profile(); st.markdown('<div class="section-title">Mi perfil</div>',unsafe_allow_html=True)
    with st.form('profile'):
        name=st.text_input('Nombre',p['name']); email=st.text_input('Correo',p['email'])
        if st.form_submit_button('Guardar perfil',type='primary'):
            with db() as c: c.execute('UPDATE profile SET name=?,email=? WHERE id=1',(name,email))
            st.success('Perfil actualizado.'); st.rerun()
    st.caption('Perfil local de demostración; no es una cuenta autenticada ni protegida por contraseña.')

def community():
    st.markdown('<div class="section-title">Comunidad CLOCKOUT</div>',unsafe_allow_html=True)
    st.write('Un espacio conceptual para compartir experiencias y hábitos de despertar.')
    for title,body in [('Empieza el día con intención','Una rutina constante puede ayudarte a organizar tus mañanas.'),('Diseñado para espacios reales','Colores neutros y formas pensadas para habitaciones universitarias.'),('Tu progreso, a tu ritmo','Celebra cada pequeño avance sin competir con los demás.')]:
        st.markdown(f"<div class='panel'><h3>{title}</h3><p>{body}</p><span class='small-note'>Contenido demostrativo de CLOCKOUT</span></div>",unsafe_allow_html=True)
    with st.form('community_form'):
        msg=st.text_area('Comparte una idea o comentario')
        if st.form_submit_button('Enviar comentario'):
            if msg.strip(): event('comunidad',msg.strip()); st.success('Comentario guardado localmente.')

def support():
    st.markdown('<div class="section-title">Centro de soporte</div>',unsafe_allow_html=True)
    faqs={'¿Cómo vinculo mi alfombra?':'Ingresa el código de tu producto en Mi Dispositivo. En este prototipo el registro es local.','¿Puedo apagar la alarma desde el celular?':'No. La regla de diseño exige desactivación física mediante presión sobre la alfombra.','¿La app se conecta al hardware real?':'No en esta versión. La conexión Bluetooth/Wi-Fi y el sensor físico requieren electrónica y firmware.','¿Cómo cambio mi alarma?':'Entra en Rutinas para crear, activar, desactivar o eliminar horarios.'}
    for q,a in faqs.items():
        with st.expander(q): st.write(a)
    with st.form('support_form'):
        email=st.text_input('Tu correo'); topic=st.selectbox('Motivo',['Producto','Vinculación','Alarmas','Pedido','Otro']); message=st.text_area('Describe tu consulta')
        if st.form_submit_button('Enviar consulta'):
            if message.strip(): event('soporte',f'{topic} | {email} | {message}'); st.success('Consulta registrada en la demostración.')
            else: st.warning('Escribe tu consulta antes de enviarla.')

def admin():
    st.markdown('<div class="section-title">Administración CLOCKOUT</div>',unsafe_allow_html=True)
    st.warning('Panel académico de demostración. No incorpora control de acceso administrativo.')
    with st.expander('Inventario y precios',expanded=True):
        for p in get_products():
            x,y,z=st.columns([2,1,1]); x.write(f"{p['name']} · {p['line']}"); price=y.number_input('Precio S/',min_value=0.0,value=float(p['price']),step=5.0,key='price_'+p['id']); stock=z.number_input('Stock',min_value=0,value=int(p['stock']),key='stock_'+p['id'])
            if st.button('Guardar cambios',key='save_'+p['id']):
                with db() as c: c.execute('UPDATE products SET price=?,stock=? WHERE id=?',(price,stock,p['id']))
                event('admin',f'{p["name"]}: precio/stock actualizado'); st.success('Producto actualizado.'); st.rerun()
    with st.expander('Pedidos registrados'):
        with db() as c: orders=c.execute('SELECT * FROM orders ORDER BY created DESC').fetchall()
        if not orders: st.info('Aún no hay pedidos.')
        for o in orders: st.write(f"**{o['id']}** · {o['created']} · {money(o['total'])} · {o['status']}")
    with st.expander('Actividad reciente'):
        with db() as c: ev=c.execute('SELECT * FROM events ORDER BY id DESC LIMIT 30').fetchall()
        for e in ev: st.caption(f"{e['created']} · {e['kind']} · {e['detail']}")

def progress():
    st.markdown('<div class="section-title">Mi progreso</div>',unsafe_allow_html=True)
    with db() as c:
        count=c.execute("SELECT COUNT(*) n FROM events WHERE kind='pisada'").fetchone()['n']; rows=c.execute('SELECT kind,detail,created FROM events ORDER BY id DESC LIMIT 30').fetchall()
    a,b,c=st.columns(3)
    a.metric('Pisadas registradas',count); b.metric('Alarmas creadas',sum(1 for e in rows if e['kind']=='alarma')); c.metric('Logros',min(3,count))
    st.markdown('### Historial de actividad')
    if rows:
        for e in rows: st.write(f"{e['created']} · **{e['kind'].capitalize()}** · {e['detail']}")
    else: st.info('Tu actividad aparecerá aquí cuando utilices el simulador y las alarmas.')

# --------------------------- ROUTER ---------------------------
page=st.session_state.page
# Evita registrar una nueva vista en cada interacción interna de Streamlit.
if st.session_state.get('analytics_last_page') != page:
    track_analytics_view(page)
    st.session_state.analytics_last_page = page
if page=='Inicio': home()
elif page=='Tienda': shop()
elif page=='Carrito': cart_page()
elif page=='Mi Dispositivo': device_page()
elif page=='Rutinas': routines()
elif page=='Mi Perfil': profile_page()
elif page=='Comunidad': community()
elif page=='Soporte': support()
elif page=='Administración': admin()
elif page=='Mi Progreso': progress()
else: home()

st.markdown('<div style="text-align:center;padding:20px;color:#7c827b;font-size:11px">CLOCKOUT · WAKE UP DIFFERENT · Prototipo académico interactivo · Datos locales de demostración</div>',unsafe_allow_html=True)
with st.expander('Acceso a herramientas de demostración'):
    st.write('Panel de administración y métricas locales para presentación académica.')
    if st.button('Abrir administración'): st.session_state.page='Administración'; st.rerun()
    if st.button('Ver mi progreso'): st.session_state.page='Mi Progreso'; st.rerun()
