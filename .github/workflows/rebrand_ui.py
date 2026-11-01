#!/usr/bin/env python3
"""Cambia 'SimpleX' -> 'Zetaria' en los textos visibles de la app y reemplaza
los logos de bienvenida. Deja intactos los textos que hablan de SimpleX como
empresa/servicio real (auditorías, servidores, Flux, nombres SimpleX, etc.)."""
import sys, re, pathlib
from PIL import Image

mp = pathlib.Path(sys.argv[1]); here = pathlib.Path(__file__).parent
NEW = "Zetaria"

# Claves que siguen diciendo SimpleX porque son afirmaciones sobre SimpleX real
KEEP_EXACT = {
    "v4_2_security_assessment_desc", "v6_1_better_security_descr",
    "onboarding_network_operators_simplex_flux_agreement",
    "onboarding_network_operators_app_will_use_for_routing",
    "you_can_connect_to_simplex_chat_founder", "icon_descr_simplex_team",
    "use_simplex_chat_servers__question", "using_simplex_chat_servers",
    "install_simplex_chat_for_terminal", "follow_simplex_network_news",
    "settings_section_title_support", "v7_0_invest", "invest_banner_title",
    "about_simplex_chat", "v6_5_non_profit_governance_descr",
    "if_you_received_simplex_invitation_link_you_can_open_in_browser",
}
KEEP_PATTERN = re.compile(r"simplex_name|simplex_domain|simplex_names|^badge_|names$")

pat = re.compile(r'(<string\b[^>]*\bname="([^"]+)"[^>]*>)(.*?)(</string>)', re.S)
res = mp / "common/src/commonMain/resources/MR"
changed = kept = 0
for f in sorted(res.glob("*/strings.xml")):
    txt = f.read_text(encoding="utf-8")
    def sub(m):
        global changed, kept
        head, key, body, tail = m.groups()
        if "SimpleX" not in body:
            return m.group(0)
        if key in KEEP_EXACT or KEEP_PATTERN.search(key):
            kept += 1; return m.group(0)
        changed += 1
        return head + body.replace("SimpleX", NEW) + tail
    new = pat.sub(sub, txt)
    if new != txt:
        f.write_text(new, encoding="utf-8")
print(f"   textos cambiados: {changed}, conservados como SimpleX: {kept}")

# Logos de la pantalla de bienvenida (modo claro/oscuro) y avatar por defecto
img = res / "images"
def put(src, dst_name):
    d = img / dst_name
    if d.exists():
        size = Image.open(d).size
        Image.open(src).convert("RGBA").resize(size, Image.LANCZOS).save(d)
        return 1
    return 0
n  = put(here / "branding/zetaria_logo.png", "logo@4x.png")
n += put(here / "branding/zetaria_logo_light.png", "logo_light@4x.png")
n += put(here / "branding/zetaria_icon.png", "ic_simplex_dark@4x.png")
n += put(here / "branding/zetaria_icon.png", "ic_simplex_light@4x.png")
print(f"   {n} imágenes de logo reemplazadas")
