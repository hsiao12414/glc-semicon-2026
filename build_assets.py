"""Build GLC site assets: process 7 approved photos, generate the two QR codes, write contact.vcf."""
from pathlib import Path
from PIL import Image, ImageOps
import qrcode
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_Q

SRC  = Path(r"C:\Users\user\Desktop\glc_photos")
SITE = Path(r"C:\Users\user\Desktop\glc_semicon_site")
OUT  = SITE / "img"
OUT.mkdir(parents=True, exist_ok=True)

# Approved set "D" — pure process / capability shots only, no identifiable product.
MAPPING = [
    ("S__153436547.jpg",   "p1-welded-frame.jpg"),
    ("S__153436550.jpg",   "p2-coating-line.jpg"),
    ("S__153436554_0.jpg", "p3-coating-parts.jpg"),
]
KEEP = {name for _, name in MAPPING} | {"qr_company_profile.png", "qr_vcard.png"}

# wipe stale images from earlier builds
for f in OUT.iterdir():
    if f.is_file() and f.name not in KEEP:
        f.unlink()
        print(f"removed stale {f.name}")

MAX_EDGE, QUALITY = 1600, 82
for src_name, out_name in MAPPING:
    src = SRC / src_name
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    w, h = im.size
    s = min(1.0, MAX_EDGE / max(w, h))
    if s < 1.0:
        im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    dst = OUT / out_name
    im.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    print(f"{out_name:<28} {im.size[0]}x{im.size[1]}  {dst.stat().st_size//1024} KB")

FG, BG = "#12203A", "#F1EEE4"

# 1) company / work page QR
URL = "https://hsiao12414.github.io/glc-semicon-2026/glc_profile.html"
q = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=20, border=4)
q.add_data(URL); q.make(fit=True)
q.make_image(fill_color=FG, back_color=BG).convert("RGB").save(OUT / "qr_company_profile.png")
print(f"\nqr_company_profile.png  -> {URL}")

# 2) add-to-contacts vCard QR
vcard = "\r\n".join([
    "BEGIN:VCARD",
    "VERSION:3.0",
    "N;CHARSET=UTF-8:紀;曉菁;;;",
    "FN;CHARSET=UTF-8:紀曉菁 Chi Hsiao Ching",
    "ORG;CHARSET=UTF-8:廣利成股份有限公司 (KWAN LI CHENG CO., LTD.)",
    "TITLE;CHARSET=UTF-8:業務經理 Sales Manager",
    "TEL;TYPE=CELL:+886921258767",
    "TEL;TYPE=WORK,VOICE:+88647873712",
    "EMAIL;TYPE=INTERNET,WORK:klccdltd@ms10.hinet.net",
    "URL:http://www.klccdltd.com/index.php?lang=tw",
    "ADR;TYPE=WORK;CHARSET=UTF-8:;;彰化縣花壇鄉南方一巷385號;;;;台灣",
    "END:VCARD",
    "",
])
q = qrcode.QRCode(error_correction=ERROR_CORRECT_Q, box_size=12, border=4)
q.add_data(vcard); q.make(fit=True)
q.make_image(fill_color=FG, back_color=BG).convert("RGB").save(OUT / "qr_vcard.png")
print("qr_vcard.png            -> vCard (add to contacts)")

# 3) downloadable .vcf
(SITE / "contact.vcf").write_bytes(vcard.encode("utf-8"))
print("contact.vcf written")
