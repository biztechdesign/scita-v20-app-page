"""Assemble the Odoo app-store description.

Writes  odoo_description/index.html      -> copy to theme_scita/static/description/
        odoo_description/images/*         -> exported fold images + GIF
        odoo_description/preview.html    -> same content wrapped with Bootstrap 5 for local viewing
"""
import json, shutil, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP, OUT = ROOT / "export", ROOT / "odoo_description"
IMG = OUT / "images"; IMG.mkdir(parents=True, exist_ok=True)

FOLDS = [
    ("01-hero.jpg", "Scita for Odoo 20 - Faster, Smarter and More Immersive: 3D and AR product view, AI shopping assistant, price drop alerts"),
    ("02-image-hotspot.gif", "Image Hotspot with 3D and AR View - click a hotspot, explore the product in 3D, view it in your room"),
    ("03-ai-companion.jpg", "AI-Powered Shopping Companion - Shopping Assistant, Visual Search and Product Comparison"),
    ("04-stay-ahead.jpg", "Price Drop Alerts and Free Shipping Progress Bar"),
    ("05-pwa-speed.jpg", "Progressive Web App experience with Google PageSpeed scores"),
    ("06-predictive-search.jpg", "Predictive, Smarter, Faster Search"),
    ("07-b2b.jpg", "B2B features - Quick Order List, Request a Quote, Hide Price and Disable Cart and more"),
    ("08-industry.jpg", "Built for your industry - 84 production-grade snippets"),
    ("09-comparison.jpg", "Scita vs other Odoo themes - core features comparison"),
    ("10-essential-features.jpg", "Essential features driving business growth"),
]

TEAL, HERO, GREEN_BTN, INK, MINT, ICE = "#017E84", "#0F5C61", "#5FA832", "#333333", "#E6F4F3", "#F2FAFA"
FONT = "font-family:'Poppins', sans-serif"

# FAQ: live-page text with the client's fixes (doc + Odoo 20 decision)
faq = json.load(open(ROOT / "tools" / "faq_source.json", encoding="utf8"))
fix = {
    "This theme is compatible with Odoo V17,V18 and V19.": "This theme is compatible with Odoo v17, v18, v19, and v20. In line with Odoo's own support policy, we provide support and updates for the three latest Odoo versions, currently v18, v19, and v20.",
    "Is this theme compatible with Odoo's Multi Website Feature?": "Is this theme compatible with Odoo's Multi-Website feature?",
}
def clean(t):
    t = fix.get(t, t)
    t = t.replace('Please refer to our support policy ', 'We support the three latest Odoo versions (currently v18, v19, and v20). For full details, please refer to our support policy ')
    t = t.replace("Yes, our theme scita is compatible with Odoo's Multi Website Feature. You can add our theme scita for multiple websites if they all are on Odoo v12",
                  "Yes, our theme Scita is compatible with Odoo's Multi-Website feature. You can add our theme Scita for multiple websites if they all are on Odoo v17, v18, v19, or v20")
    t = t.replace('<span style="color:#00008B; font-weight:bold"> https://www.appjetty.com/support-policy.htm</span>',
                  f'<a href="https://www.appjetty.com/support-policy.htm" target="_blank" style="color:{TEAL}; font-weight:600">https://www.appjetty.com/support-policy.htm</a>')
    t = t.replace('<a href="mailto:support@appjetty.com">', f'<a href="mailto:support@appjetty.com" style="color:{TEAL}; font-weight:600">')
    return t
faq = [[clean(q), clean(a)] for q, a in faq]

def faq_html():
    items = []
    for i, (q, a) in enumerate(faq, 1):
        first = i == 1
        items.append(f'''
            <div class="accordion-item" style="border:0; border-bottom:1px solid #DCEBEA; background:transparent">
              <h3 class="accordion-header m-0" id="scita_faq_h{i}">
                <a class="accordion-button{'' if first else ' collapsed'}" data-bs-toggle="collapse" href="#scita_faq_{i}" role="button" aria-expanded="{'true' if first else 'false'}" aria-controls="scita_faq_{i}"
                   style="{FONT}; font-size:17px; font-weight:600; color:#1F2627; text-decoration:none; background:transparent; padding:20px 4px; line-height:1.4">{q}</a>
              </h3>
              <div id="scita_faq_{i}" class="accordion-collapse collapse{' show' if first else ''}" aria-labelledby="scita_faq_h{i}" data-bs-parent="#scita_faq">
                <div class="accordion-body" style="{FONT}; font-size:16px; line-height:1.65; color:{INK}; padding:0 4px 20px">{a}</div>
              </div>
            </div>''')
    return "".join(items)

def body():
    imgs = "".join(f'''
      <div class="shadow overflow-hidden" style="border-radius:30px; margin-bottom:50px">
        <img src="images/{f}" class="img img-fluid w-100" alt="{html.escape(alt)}" loading="lazy">
      </div>''' for f, alt in FOLDS)
    return f'''<section class="oe_container">
  <div class="container">{imgs}

      <!-- FAQs: Bootstrap 5 accordion (its built-in chevron flips on every open / close) -->
      <div class="shadow overflow-hidden px-3 py-4 p-md-5" style="margin-top:30px; background-color:#fff; border-radius:30px">
        <h2 class="text-center display-6" style="{FONT}; font-weight:700; color:{TEAL}; margin:0 0 6px">FAQs</h2>
        <p class="text-center" style="{FONT}; font-size:16.5px; color:#5B6466; margin:0 0 30px">Everything you need to know about Scita</p>
        <div class="accordion accordion-flush" id="scita_faq">{faq_html()}
        </div>
      </div>

      <!-- Changelog -->
      <div class="shadow overflow-hidden px-3 py-4 p-md-5" style="margin-top:50px; background-color:{ICE}; border-radius:30px">
        <h2 class="text-center display-6" style="{FONT}; font-weight:700; color:{TEAL}; margin:0 0 30px">Changelog</h2>
        <div class="row justify-content-center">
          <div class="col-md-10">
            <div style="background-color:{HERO}; padding:12px 22px; border-radius:14px 14px 0 0; color:#fff; {FONT}; font-weight:600; font-size:17px">Version 20.0</div>
            <div class="d-flex flex-wrap align-items-start" style="background-color:#fff; padding:18px 22px; border-radius:0 0 14px 14px; gap:16px">
              <span style="background-color:{MINT}; color:{TEAL}; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700; {FONT}">Release</span>
              <ul class="list-unstyled m-0" style="{FONT}; font-size:15.5px; line-height:1.6; color:{INK}; font-weight:500">
                <li class="mb-1">Initial release for Odoo 20</li>
                <li class="mb-1">New: 3D &amp; AR product view and Image Hotspot</li>
                <li class="mb-1">New: AI Shopping Assistant, Visual Search and Product Comparison</li>
                <li class="mb-1">New: Price Drop Alerts and Free Shipping Progress Bar</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- Support -->
      <div class="shadow overflow-hidden" style="margin-top:50px; border-radius:30px; background-color:{MINT}">
        <div class="row align-items-center p-4 p-lg-5 m-0">
          <div class="col-lg-8">
            <h2 class="fs-2" style="{FONT}; font-weight:700; color:#1F2627; margin:0 0 12px; line-height:1.25">Technical Help, Queries &amp; <span style="color:{TEAL}">Support</span></h2>
            <p style="{FONT}; font-size:16.5px; line-height:1.65; color:{INK}; margin:0 0 20px">We offer extremely convenient and quick support for all your technical help &amp; support requests. Our support service is the parameter that defines the success of our business and has earned us our brand name.</p>
            <a href="mailto:support@appjetty.com" style="display:inline-block; background-color:{GREEN_BTN}; color:#fff; height:44px; line-height:44px; padding:0 22px; border-radius:10px; box-shadow:0 4px 12px rgba(95,168,50,.28); {FONT}; font-weight:600; font-size:16px; text-decoration:none">support@appjetty.com</a>
          </div>
          <div class="col-lg-4 text-center mt-4 mt-lg-0">
            <img src="images/support_1.png" class="img img-fluid" alt="AppJetty support" loading="lazy" style="max-height:260px">
          </div>
        </div>
      </div>
  </div>
</section>
'''

# copy images
for f, _ in FOLDS:
    src = EXP / f
    if src.exists(): shutil.copy(src, IMG / f)
    else: print("MISSING", f)
shutil.copy(ROOT / "assets" / "source_extra" / "support_1.png", IMG / "support_1.png")

b = body()
(OUT / "index.html").write_text(b, encoding="utf8")
(OUT / "preview.html").write_text(f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Scita v20 App Page Preview</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>body{{background:#f5f7f7;padding:40px 0}} .container{{max-width:1140px}}</style></head>
<body>{b}<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script></body></html>''', encoding="utf8")
print("built", OUT)
