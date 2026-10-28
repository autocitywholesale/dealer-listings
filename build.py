#!/usr/bin/env python3
"""Build the Auto City dealer listing site from vehicles.json into dist/.
Usage: python3 build.py [--deploy]  (prints each unsold car's private share URL)"""
import json, os, secrets, shutil, string, subprocess, sys, html, urllib.parse
from PIL import Image, ImageOps
ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
BASE = "https://autocitywholesale.github.io/dealer-listings/"
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
.noimg{display:flex;align-items:center;justify-content:center;width:100%;aspect-ratio:4/3;background:#e3e6eb;color:#6b7280;font-weight:600;font-size:.95rem;text-align:center}.hero.noimg{max-height:300px;border-radius:10px;background:#e3e6eb}
.empty{text-align:center;padding:60px 20px;background:#fff;border-radius:10px}.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px}
.gal img{width:100%;border-radius:6px}.hero{width:100%;max-height:600px;object-fit:contain;background:#000;border-radius:10px}
section{background:#fff;border-radius:10px;padding:16px;margin:16px 0}table{border-collapse:collapse;width:100%}td{padding:6px;border-bottom:1px solid #eee;vertical-align:top}td:first-child{font-weight:600;width:40%}
footer{text-align:center;padding:24px;color:#555;font-size:.9rem}
.titlebar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px;margin:0 0 12px}.titlebar h1{margin:0;font-size:1.6rem}
.sharebox{display:flex;flex-direction:column;align-items:flex-start;gap:4px}.sharebtn{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:#c0392b;color:#fff;border:0;border-radius:8px;padding:12px 22px;font-size:1.05rem;font-weight:700;cursor:pointer;font-family:inherit;box-shadow:0 1px 4px #0003}
.sharebtn:hover{background:#a93226}.sharebtn svg,.cardshare svg{width:1.2em;height:1.2em;fill:currentColor;flex:none}
.sharealt{font-size:.85rem;color:#555}.sharealt a{color:#13315c}.sharemsg{font-size:.85rem;font-weight:600;color:#1e7e34;min-height:1.1em}
.cardshare{margin-top:6px;background:none;border:1px solid #13315c;color:#13315c;border-radius:6px;padding:7px 12px;cursor:pointer;font-family:inherit;font-size:.95rem;display:inline-flex;align-items:center;justify-content:center;gap:6px}
.vinline{margin:4px 0 0;font-size:1.05rem}.vin{font-family:ui-monospace,Menlo,Consolas,monospace;font-weight:700;letter-spacing:.04em;user-select:all;-webkit-user-select:all;background:#eef2f7;padding:2px 6px;border-radius:4px}.vincopy{margin-left:6px;background:none;border:1px solid #13315c;color:#13315c;border-radius:5px;padding:2px 8px;font-size:.8rem;cursor:pointer;font-family:inherit}
@media(max-width:600px){.sharebox{width:100%}.sharebtn{width:100%;font-size:1.15rem;padding:14px}}"""
ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z"/></svg>'
SHARE_JS = """(function(){function note(el,t){var m=el.closest('[data-share-root]');m=m&&m.querySelector('.sharemsg');if(m){m.textContent=t;setTimeout(function(){m.textContent=''},3000)}else{alert(t)}}
function copy(u){if(navigator.clipboard&&window.isSecureContext)return navigator.clipboard.writeText(u);return new Promise(function(ok,no){var a=document.createElement('textarea');a.value=u;a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);a.select();try{document.execCommand('copy')?ok():no()}catch(x){no(x)}document.body.removeChild(a)})}
document.addEventListener('click',function(ev){var c=ev.target.closest('[data-copy-vin]');if(c){copy(c.getAttribute('data-copy-vin')).then(function(){c.textContent='Copied';setTimeout(function(){c.textContent='Copy'},2000)},function(){});return}});
document.addEventListener('click',function(ev){var b=ev.target.closest('[data-share-url]');if(!b)return;ev.preventDefault();var u=b.getAttribute('data-share-url'),t=b.getAttribute('data-share-title');
if(navigator.share){navigator.share({title:t,text:t,url:u}).catch(function(x){if(x&&x.name==='AbortError')return;copy(u).then(function(){note(b,'Link copied')},function(){note(b,'Copy this link: '+u)})})}
else{copy(u).then(function(){note(b,'Link copied')},function(){note(b,'Copy this link: '+u)})}})})();"""
def sharebtn(url, ttl, cls="sharebtn", label="Share"):
    return f'<button type="button" class="{cls}" data-share-url="{e(url)}" data-share-title="{e(ttl)}">{ICON} {label}</button>'
SITE_SHORT = "Auto City Wholesale"
def page(title, body, rel="", head=""):
    c = DEALER
    contact = " · ".join(x for x in [c["contact"], c["phone"], c["email"]] if x)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>{e(title)}</title>{head}<link rel="stylesheet" href="{rel}style.css"></head><body>
<header><h1>{e(c['name'])}</h1><p>Dealer-to-dealer inventory · {e(c['addr'])}</p></header>
<main>{body}</main><footer>{e(c['name'])} · {e(c['addr'])}<br>Dealer-to-dealer listing. Information provided as-is; verify before purchase.</footer><script>{SHARE_JS}</script></body></html>"""
SLUG_CHARS = string.ascii_lowercase + string.digits
def new_slug(): return "".join(secrets.choice(SLUG_CHARS) for _ in range(12))
def share_url(v): return BASE + "v/" + v["slug"] + "/"
def title(v): return " ".join(str(v.get(k, "")) for k in ("year", "make", "model", "trim") if v.get(k))
def money(x): return f"${x:,.0f}" if isinstance(x, (int, float)) else e(x)
def photos(v):
    out, d = [], os.path.join(DIST, "v", v["slug"]); os.makedirs(d, exist_ok=True)
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
    url = share_url(v); stitle = f"{title(v)} - {SITE_SHORT}"
    em = "mailto:?" + urllib.parse.urlencode({"subject": stitle, "body": f"{stitle}\n{url}"}, quote_via=urllib.parse.quote)
    sms = "sms:?&body=" + urllib.parse.quote(f"{stitle} {url}", safe="")
    b = (f'<div class="titlebar"><div><h1>{e(title(v))}</h1><p class="vinline">VIN: <span class="vin">{e(v['vin'])}</span><button type="button" class="vincopy" data-copy-vin="{e(v['vin'])}">Copy</button> · {v['km']:,} km</p></div><div class="sharebox" data-share-root>{sharebtn(url, stitle)}'
         f'<div class="sharemsg" role="status" aria-live="polite"></div>'
         f'<div class="sharealt">Or share by <a href="{e(em)}">Email</a> · <a href="{e(sms)}">Text</a></div></div></div>')
    if not imgs: b += '<div class="noimg hero" style="aspect-ratio:16/6">Photos coming soon</div>'
    if imgs: b += f'<img class="hero" src="{imgs[0]}" alt="">' + ('<h3>Photos</h3><div class="gal">' + "".join(f'<a href="{i}"><img src="{i}" loading="lazy" alt=""></a>' for i in imgs) + "</div>" if len(imgs) > 1 else "")
    b += f"<section><h2>Overview</h2><table><tr><td>VIN</td><td>{e(v['vin'])}</td></tr><tr><td>Kilometres</td><td>{v['km']:,} km</td></tr>{pr}</table>"
    if v.get("specs"): b += rows(v["specs"])
    if v.get("notes"): b += f"<p>{e(v['notes'])}</p>"
    b += "</section>"
    bs = v.get("build_sheet") or {}
    spec = bool(bs.get("spec_sheet"))  # NHTSA-decoded spec sheet (not a window sticker)
    b += f"<section><h2>{'Factory specifications' if spec else 'Factory build sheet'}</h2>"
    if bs:
        if bs.get("msrp"): b += f"<p><b>Original MSRP:</b> {money(bs['msrp'])}</p>"
        for k, lbl in (("packages","Packages"),("options","Options")):
            if bs.get(k): b += f"<h3>{lbl}</h3><ul>" + "".join(f"<li>{e(x)}</li>" for x in bs[k]) + "</ul>"
        if bs.get("pdf"): b += f'<p><a class="btn" href="{e(os.path.basename(bs["pdf"]))}">{"Factory specifications - NHTSA VIN decode (PDF)" if spec else "Window sticker / build sheet (PDF)"}</a></p>{"<p><small>Source: NHTSA VIN decode. Factory window sticker not available.</small></p>" if spec else ""}'
    else: b += "<p>Not available.</p>"
    cf = v.get("carfax") or {}
    b += "</section><section><h2>Carfax Canada history summary</h2>"
    if cf:
        b += rows({k: val for k, val in cf.items() if k not in ("pdf", "url", "records") and val not in (None, "")})
        if cf.get("records"): b += "<ul>" + "".join(f"<li>{e(r)}</li>" for r in cf["records"]) + "</ul>"
        if cf.get("pdf"): b += f'<p><a class="btn" href="{e(os.path.basename(cf["pdf"]))}">Full Carfax report (PDF)</a></p>'
        if cf.get("url"): b += f'<p><a href="{e(cf["url"])}" rel="noopener">View online Carfax report</a></p>'
    else: b += "<p>Not available.</p>"
    b += "</section>"
    desc = f"{title(v)} - {v['km']:,} km. Dealer-to-dealer wholesale listing."
    og = [("og:type", "website"), ("og:site_name", SITE_SHORT), ("og:title", stitle), ("og:description", desc), ("og:url", url)]
    if imgs: og.append(("og:image", url + imgs[0]))
    head = "".join(f'<meta property="{k}" content="{e(val)}">' for k, val in og)
    head += f'<meta name="twitter:card" content="{"summary_large_image" if imgs else "summary"}"><meta name="description" content="{e(desc)}">'
    return page(title(v) + " – " + DEALER["name"], b, "../../", head)
def load_vehicles():
    """Load vehicles.json; give every entry without a 'slug' a random one and save it (stable once set)."""
    path = os.path.join(ROOT, "vehicles.json"); data = json.load(open(path)); changed = False
    used = {v["slug"] for v in data["vehicles"] if v.get("slug")}
    if len(used) != sum(1 for v in data["vehicles"] if v.get("slug")): sys.exit("ERROR: duplicate slug in vehicles.json")
    for n, v in enumerate(data["vehicles"]):
        if v.get("slug"): continue
        if os.environ.get("GITHUB_ACTIONS") and not v.get("sold"):
            sys.exit(f"ERROR: {v['vin']} has no slug in vehicles.json. Run `python3 build.py --deploy` locally so the slug is saved and committed.")
        s = new_slug()
        while s in used: s = new_slug()
        used.add(s); changed = True
        data["vehicles"][n] = {k2: v2 for k, v0 in (("vin", v["vin"]), ("slug", s)) for k2, v2 in [(k, v0)]} | {k: x for k, x in v.items() if k != "vin"}
    if changed and not os.environ.get("GITHUB_ACTIONS"):
        json.dump(data, open(path, "w"), indent=1, ensure_ascii=False); open(path, "a").write("\n")
    return data["vehicles"]
HOME = (f'<div class="empty"><h2>Private dealer-to-dealer listings</h2><p>Vehicles are shared by private link only.</p>'
        f'<p>If you were sent a link, please open it directly. For inquiries, contact {e(DEALER["contact"])} at {e(DEALER["name"])}.</p></div>')
def build():
    shutil.rmtree(DIST, ignore_errors=True); os.makedirs(DIST)
    open(os.path.join(DIST, "style.css"), "w").write(CSS)
    open(os.path.join(DIST, "robots.txt"), "w").write("User-agent: *\nDisallow: /\n")
    vs = [v for v in load_vehicles() if not v.get("sold")]  # sold cars are never published
    for v in vs:
        imgs = photos(v); d = os.path.join(DIST, "v", v["slug"])
        for key in ("carfax", "build_sheet"):
            p = (v.get(key) or {}).get("pdf")
            if p: shutil.copy(p if os.path.isabs(p) else os.path.join(ROOT, p), d)
        open(os.path.join(d, "index.html"), "w").write(vpage(v, imgs))
    # Home + 404: branded, no car list, no links. Nothing else (no sitemap/feed/vehicles.json) is published.
    open(os.path.join(DIST, "index.html"), "w").write(page(DEALER["name"] + " – Private Listings", HOME))
    open(os.path.join(DIST, "404.html"), "w").write(page(DEALER["name"], '<div class="empty"><h2>Listing not found</h2><p>This link is not available. Please check with the person who sent it.</p></div>', BASE))
    print(f"Built {len(vs)} vehicle(s) into {DIST}")
    for v in vs: print(f"  SHARE URL  {title(v)} ({v['vin']}): {share_url(v)}")
if __name__ == "__main__":
    build()
    if "--deploy" in sys.argv:  # publish: commit + push to main; GitHub Actions builds and deploys Pages
        msg = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--msg=")), "Update listings")
        subprocess.run(["git", "-C", ROOT, "add", "-A"], check=True)
        subprocess.run(["git", "-C", ROOT, "commit", "-m", msg])  # no-op if nothing changed
        subprocess.run(["git", "-C", ROOT, "push", "origin", "main"], check=True)
        print("Pushed. Live in ~1-2 min. Share links:")
        for v in (x for x in load_vehicles() if not x.get("sold")): print(f"  {title(v)} ({v['vin']}): {share_url(v)}")
    if "--preview" in sys.argv:  # optional quick preview on surge.sh
        subprocess.run(["npx", "-y", "surge", DIST, DOMAIN], check=True); print("Preview: https://" + DOMAIN)
