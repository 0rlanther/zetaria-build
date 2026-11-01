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
import shutil
shutil.copy(here / "branding/zetaria_logo.png", img / "zetaria_logo@4x.png")
shutil.copy(here / "branding/zetaria_logo_light.png", img / "zetaria_logo_light@4x.png")
n = 2
n += put(here / "branding/zetaria_icon.png", "ic_simplex_dark@4x.png")
n += put(here / "branding/zetaria_icon.png", "ic_simplex_light@4x.png")
print(f"   {n} imágenes de logo reemplazadas")


# ---------- Bienvenida cósmica, capturas permitidas, textos nuevos ----------
def patch(path, old, new):
    t = path.read_text(encoding="utf-8")
    if old not in t:
        sys.exit(f"ERROR: no encontré el texto a modificar en {path}:\n{old[:120]}")
    path.write_text(t.replace(old, new, 1), encoding="utf-8")

kt = mp / "common/src/commonMain/kotlin/chat/simplex/common"
info = kt / "views/onboarding/SimpleXInfo.kt"
patch(info, """          SimpleXInfoLayout(
            user = chatModel.currentUser.value,
            onboardingStage = chatModel.controller.appPrefs.onboardingStage
          )
        }
      }
    }
  } else {""", """          ZetariaWelcome(chatModel.currentUser.value, chatModel.controller.appPrefs.onboardingStage)
        }
      }
    }
  } else {""")
patch(info, "painterResource(if (isInDarkTheme()) MR.images.logo_light else MR.images.logo)",
            "painterResource(if (isInDarkTheme()) MR.images.zetaria_logo_light else MR.images.zetaria_logo)")

# Capturas de pantalla permitidas por defecto (el ajuste sigue disponible en Privacidad)
patch(kt / "model/SimpleXAPI.kt", "mkBoolPreference(SHARED_PREFS_PRIVACY_PROTECT_SCREEN, true)",
                                  "mkBoolPreference(SHARED_PREFS_PRIVACY_PROTECT_SCREEN, false)")

# Código de la pantalla de bienvenida (+ mapa del reino si existe branding/reino_mapa.png)
tpl = (here / "templates/ZetariaWelcome.kt").read_text(encoding="utf-8")
mapfile = here / "branding/reino_mapa.png"
if mapfile.exists():
    shutil.copy(mapfile, img / "reino_mapa@4x.png")
    tpl = tpl.replace("//ZETARIA_MAP", """Image(
          painter = painterResource(MR.images.reino_mapa),
          contentDescription = null,
          contentScale = ContentScale.FillWidth,
          modifier = Modifier.fillMaxWidth().padding(top = DEFAULT_PADDING).clip(RoundedCornerShape(16.dp))
        )""")
    print("   mapa del reino incluido")
else:
    tpl = tpl.replace("//ZETARIA_MAP", "")
    print("   (sin branding/reino_mapa.png: se omite el mapa)")
(kt / "views/onboarding/ZetariaWelcome.kt").write_text(tpl, encoding="utf-8")

# Textos nuevos (el resto de idiomas usa este base como respaldo)
TEXT = (
 "El Reino Soberano de Zetaria existe en el cosmos, en la nave nodriza «Corazón de Zetaria», que viaja por dimensiones a través del universo. "
 "Se manifestó en este mundo terrenal por medio de un humano, en el hogar físico del Soberano, con 770 m² de terreno, "
 "y se extiende como un servidor a los espacios virtuales, como esta aplicación que acabas de instalar.\\n\\n"
 "Al instalar y usar esta app anónima, eres visitante de mi Reino, que te protegerá del espionaje de gobiernos corruptos, de izquierda y de derecha, "
 "y de los oligopolios tecnofeudales de empresas hambreadas.\\n\\n"
 "Siéntete cómodo de usar esta app, que modifiqué por medio de Vibecoding. Todo lo que haga falta corregir, me lo vas notificando y haré lo posible por arreglarlo. "
 "Seguirán habiendo actualizaciones con el objetivo de evolucionar a la humanidad para bien y evitar su extinción.")
base = res / "base/strings.xml"
x = base.read_text(encoding="utf-8")
new = ('  <string name="zetaria_welcome_title">Bienvenido al Reino Soberano de Zetaria</string>\n'
       f'  <string name="zetaria_welcome_text">{TEXT}</string>\n'
       '  <string name="zetaria_welcome_credit">Zetaria es una versión modificada de SimpleX Chat (licencia AGPL-3.0).</string>\n')
x = x.replace("</resources>", new + "</resources>")
base.write_text(x, encoding="utf-8")
print("   bienvenida cósmica instalada")
