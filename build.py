#!/usr/bin/env python3
"""Build the Auto City dealer listing site from vehicles.json into dist/.
Usage: python3 build.py [--deploy]"""
import json, os, shutil, subprocess, sys, html
from PIL import Image, ImageOps
ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
DOMAIN = "autocity-fredericton-dealers.surge.sh"
DEALER = {"name": "Auto City Fredericton", "addr": "40 Main St., Fredericton, NB",
          "contact": "Derek", "phone": "", "email": ""}
e = lambda s: html.escape(str(s if s is not None else ""))
CSS = """*{box-sizing:border-box}body{margin:0;font-family:system-ui,Arial,sans-serif;background:#f4f5f7;color:#1d1f23}
header{background:#0b2545;color:#fff;padding:18px 20px}header a{color:#fff;text-decoration:none}header h1{margin:0;font-size:1.5rem}header p{margin:4px 0 0;opacity:.85;font-size:.9rem}
main{max-width:1150px;margin:auto;padding:20px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px}
.card{background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px #0002;display:flex;flex-direction:column}.card img{width:100%;aspect-ratio:4/3;object-fit:cover;background:#ddd}
.card .b{padding:12px 14px;flex:1;display:flex;flex-direction:column;gap:4px}.card h2{font-size:1.05rem;margin:0}.price{color:#c0392b;font-weight:700}
.btn{display:inline-block;margin-top:auto;background:#13315c;color:#fff;padding:8px 12px;border-radius:6px;text-decoration:none;text-align:center}
.empty{text-align:center;padding:60px 20px;background:#fff;border-radius:10px}.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px}
.gal img{width:100%;border-radius:6px}.hero{width:100%;max-height:600px;object-fit:contain;background:#000;border-radius:10px}
section{background:#fff;border-radius:10px;padding:16px;margin:16px 0}table{border-collapse:collapse;width:100%}td{padding:6px;border-bottom:1px solid #eee;vertical-align:top}td:first-child{font-weight:600;width:40%}
footer{text-align:center;padding:24px;color:#555;font-size:.9rem}"""
def page(title, body, rel=""):
    c = DEALER
    contact = " · ".join(x for x in [c["contact"], c["phone"], c["email"]] if x)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><link rel="stylesheet" href="{rel}style.css"></head><body>
<header><a href="{rel}index.html"><h1>{e(c['name'])}</h1></a><p>Dealer-to-dealer inventory · {e(c['addr'])}</p></header>
<main>{body}</main><footer>{e(c['name'])} · {e(c['addr'])}<br>Dealer-to-dealer listing. Information provided as-is; verify before purchase.</footer></body></html>"""
def title(v): return " ".join(str(v.get(k, "")) for k in ("year", "make", "model", "trim") if v.get(k))
def money(x): return f"${x:,.0f}" if isinstance(x, (int, float)) else e(x)
def photos(v):
    out, d = [], os.path.join(DIST, "v", v["vin"]); os.makedirs(d, exist_ok=True)
    for i, p in enumerate(v.get("photos", [])):
        src = p if os.path.isabs(p) else os.path.join(ROOT, p)
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB"); im.thumbnail((1600, 1600))
        n = f"{i+1:02d}.jpg"; im.save(os.path.join(d, n), quality=82, optimize=True)
        if i == 0: t = im.copy(); t.thumbnail((640, 640)); t.save(os.path.join(d, "thumb.jpg"), quality=80)
        out.append(n)
    return out
def rows(dct): return "<table>" + "".join(f"<tr><td>{e(k)}</td><td>{e(val)}</td></tr>" for k, val in dct.items()) + "</table>"
def vpage(v, imgs):
    pr = "".join(f"<tr><td>{lbl}</td><td class=price>{money(v[k])}</td></tr>" for k, lbl in (("asking_price","Asking"),("wholesale_price","Wholesale")) if v.get(k))
    b = f"<h1>{e(title(v))}</h1>"
    if imgs: b += f'<img class="hero" src="{imgs[0]}" alt="">' + ('<h3>Photos</h3><div class="gal">' + "".join(f'<a href="{i}"><img src="{i}" loading="lazy" alt=""></a>' for i in imgs) + "</div>" if len(imgs) > 1 else "")
    b += f"<section><h2>Overview</h2><table><tr><td>VIN</td><td>{e(v['vin'])}</td></tr><tr><td>Kilometres</td><td>{v['km']:,} km</td></tr>{pr}</table>"
    if v.get("specs"): b += rows(v["specs"])
    if v.get("notes"): b += f"<p>{e(v['notes'])}</p>"
    b += "</section>"
    bs = v.get("build_sheet") or {}
    b += "<section><h2>Factory build sheet</h2>"
    if bs:
        if bs.get("msrp"): b += f"<p><b>Original MSRP:</b> {money(bs['msrp'])}</p>"
        for k, lbl in (("packages","Packages"),("options","Options")):
            if bs.get(k): b += f"<h3>{lbl}</h3><ul>" + "".join(f"<li>{e(x)}</li>" for x in bs[k]) + "</ul>"
        if bs.get("pdf"): b += f'<p><a class="btn" href="{e(os.path.basename(bs["pdf"]))}">Window sticker / build sheet (PDF)</a></p>'
    else: b += "<p>Not available.</p>"
    cf = v.get("carfax") or {}
    b += "</section><section><h2>Carfax Canada history summary</h2>"
    if cf:
        b += rows({k: val for k, val in cf.items() if k not in ("pdf", "records") and val not in (None, "")})
        if cf.get("records"): b += "<ul>" + "".join(f"<li>{e(r)}</li>" for r in cf["records"]) + "</ul>"
        if cf.get("pdf"): b += f'<p><a class="btn" href="{e(os.path.basename(cf["pdf"]))}">Full Carfax report (PDF)</a></p>'
    else: b += "<p>Not available.</p>"
    b += "</section>"
    return page(title(v) + " – " + DEALER["name"], b, "../../")
def build():
    shutil.rmtree(DIST, ignore_errors=True); os.makedirs(DIST)
    open(os.path.join(DIST, "style.css"), "w").write(CSS)
    vs = [v for v in json.load(open(os.path.join(ROOT, "vehicles.json")))["vehicles"] if not v.get("sold")]
    cards = []
    for v in vs:
        imgs = photos(v); d = os.path.join(DIST, "v", v["vin"])
        for key in ("carfax", "build_sheet"):
            p = (v.get(key) or {}).get("pdf")
            if p: shutil.copy(p if os.path.isabs(p) else os.path.join(ROOT, p), d)
        open(os.path.join(d, "index.html"), "w").write(vpage(v, imgs))
        pr = v.get("asking_price") or v.get("wholesale_price")
        cards.append(f'<div class="card">{"<img src=v/%s/thumb.jpg alt=\'\' loading=lazy>" % v["vin"] if imgs else ""}<div class="b"><h2>{e(title(v))}</h2><div>{v["km"]:,} km</div>'
                     f'{f"<div class=price>{money(pr)}</div>" if pr else ""}<a class="btn" href="v/{v["vin"]}/index.html">View details</a></div></div>')
    body = f'<div class="grid">{"".join(cards)}</div>' if cards else '<div class="empty"><h2>No vehicles listed yet</h2><p>Check back soon — new dealer-to-dealer units will appear here.</p></div>'
    open(os.path.join(DIST, "index.html"), "w").write(page(DEALER["name"] + " – Dealer Inventory", body))
    print(f"Built {len(vs)} vehicle(s) into {DIST}")
if __name__ == "__main__":
    build()
    if "--deploy" in sys.argv:  # publish: commit + push to main; GitHub Actions builds and deploys Pages
        msg = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--msg=")), "Update listings")
        subprocess.run(["git", "-C", ROOT, "add", "-A"], check=True)
        subprocess.run(["git", "-C", ROOT, "commit", "-m", msg])  # no-op if nothing changed
        subprocess.run(["git", "-C", ROOT, "push", "origin", "main"], check=True)
        print("Pushed. Live in ~1-2 min: https://autocitywholesale.github.io/dealer-listings/")
    if "--preview" in sys.argv:  # optional quick preview on surge.sh
        subprocess.run(["npx", "-y", "surge", DIST, DOMAIN], check=True); print("Preview: https://" + DOMAIN)
