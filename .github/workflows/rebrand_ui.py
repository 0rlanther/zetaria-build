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


# ---------- PNG sin pérdida en el chat + mejor compresión de fotos de perfil ----------
utils = kt / "views/helpers/Utils.kt"
patch(utils, """fun saveImage(uri: URI): CryptoFile? {
  val bitmap = getBitmapFromUri(uri) ?: return null
  return saveImage(bitmap)
}""", """// Zetaria: los PNG se envían tal cual (sin recomprimir ni reducir), hasta 30 MB
const val ZETARIA_MAX_ORIGINAL_PNG: Long = 31_457_280

private fun isPngFile(uri: URI): Boolean = try {
  uri.inputStream()?.use { s ->
    val h = ByteArray(8)
    s.read(h) == 8 && h[0] == 0x89.toByte() && h[1] == 0x50.toByte() && h[2] == 0x4E.toByte() && h[3] == 0x47.toByte()
  } ?: false
} catch (e: Exception) {
  false
}

fun saveOriginalPng(uri: URI): CryptoFile? {
  return try {
    val size = getFileSize(uri)
    if (size == null || size > ZETARIA_MAX_ORIGINAL_PNG || !isPngFile(uri)) return null
    val encrypted = chatController.appPrefs.privacyEncryptLocalFiles.get()
    val destFileName = generateNewFileName("IMG", "png", File(getAppFilePath("")))
    val destFile = File(getAppFilePath(destFileName))
    if (encrypted) {
      val bytes = uri.inputStream()?.use { it.readBytes() } ?: return null
      val args = writeCryptoFile(destFile.absolutePath, bytes)
      CryptoFile(destFileName, args)
    } else {
      uri.inputStream()?.use { Files.copy(it, destFile.toPath()) } ?: return null
      CryptoFile.plain(destFileName)
    }
  } catch (e: Exception) {
    Log.e(TAG, "Util.kt saveOriginalPng error: ${e.stackTraceToString()}")
    null
  }
}

fun saveImage(uri: URI): CryptoFile? {
  val original = saveOriginalPng(uri)
  if (original != null) return original
  val bitmap = getBitmapFromUri(uri) ?: return null
  return saveImage(bitmap)
}""")
# los PNG grandes se descargan solos en el receptor (hasta 15 MB)
patch(utils, "const val MAX_IMAGE_SIZE_AUTO_RCV: Long = MAX_IMAGE_SIZE * 2",
             "const val MAX_IMAGE_SIZE_AUTO_RCV: Long = 15_728_640")

imgs = mp / "common/src/androidMain/kotlin/chat/simplex/common/platform/Images.android.kt"
patch(imgs, """actual fun resizeImageToStrSize(image: ImageBitmap, maxDataSize: Long): String {
  var img = image""", """actual fun resizeImageToStrSize(image: ImageBitmap, maxDataSize: Long): String {
  // Zetaria: para fotos de perfil y miniaturas usa el mayor tamaño/calidad JPEG que quepa en el límite
  if (maxDataSize <= 100_000 && !image.hasAlpha()) return zetariaResizeJpeg(image, maxDataSize)
  var img = image""")
with open(imgs, "a", encoding="utf-8") as f:
    f.write("""

private fun zetariaJpegStr(img: Bitmap, quality: Int): String {
  val stream = ByteArrayOutputStream()
  img.compress(Bitmap.CompressFormat.JPEG, quality, stream)
  return "data:image/jpg;base64," + Base64.encodeToString(stream.toByteArray(), Base64.NO_WRAP)
}

private fun zetariaResizeJpeg(image: ImageBitmap, maxDataSize: Long): String {
  var bmp = image.asAndroidBitmap()
  val maxSide = 1024
  val longest = maxOf(bmp.width, bmp.height)
  if (longest > maxSide) {
    val f = maxSide.toDouble() / longest
    bmp = Bitmap.createScaledBitmap(bmp, maxOf(1, (bmp.width * f).toInt()), maxOf(1, (bmp.height * f).toInt()), true)
  }
  val probe = zetariaJpegStr(bmp, 75)
  if (probe.length > maxDataSize) {
    val f = minOf(1.0, sqrt(maxDataSize.toDouble() / probe.length) * 1.15)
    bmp = Bitmap.createScaledBitmap(bmp, maxOf(1, (bmp.width * f).toInt()), maxOf(1, (bmp.height * f).toInt()), true)
  }
  while (true) {
    var lo = 55
    var hi = 95
    var best: String? = null
    while (lo <= hi) {
      val mid = (lo + hi) / 2
      val s = zetariaJpegStr(bmp, mid)
      if (s.length <= maxDataSize) {
        best = s
        lo = mid + 1
      } else {
        hi = mid - 1
      }
    }
    if (best != null) return best
    bmp = Bitmap.createScaledBitmap(bmp, maxOf(1, (bmp.width * 0.9).toInt()), maxOf(1, (bmp.height * 0.9).toInt()), true)
  }
}
""")
print("   PNG original + compresión de perfil aplicados")


# ---------- PNG fluido en pantalla completa ----------
# Pantalla completa: limitar la decodificación a 2560 px (antes: tamaño original, que traba la app)
patch(mp / "common/src/androidMain/kotlin/chat/simplex/common/views/chat/item/ImageFullScreenView.android.kt",
      ".size(Size.ORIGINAL)", ".size(Size(2560, 2560))")
print("   PNG fluido en pantalla completa aplicado")


# ---------- "Barra de herramientas accesible" desactivada por defecto ----------
# Solo cambia el valor inicial de instalaciones nuevas; quien ya la tenga activada la conserva.
import re
api = kt / "model/SimpleXAPI.kt"
if api.exists():
    src = api.read_text(encoding="utf-8")
    new_src, n = re.subn(r"(SHARED_PREFS_ONE_HAND_UI\s*,\s*)(true|appPlatform\.isAndroid)", r"\1false", src, count=1)
    if n:
        api.write_text(new_src, encoding="utf-8")
        print("   Barra de herramientas accesible: desactivada por defecto")
    else:
        print("   AVISO: no encontré la preferencia SHARED_PREFS_ONE_HAND_UI; se omite")
else:
    print("   AVISO: no existe SimpleXAPI.kt; se omite")


# ---------- Interfaz morada oscura por defecto (la bienvenida usa colores propios y no cambia) ----------
# Parches opcionales: si algo no coincide con el código de SimpleX, se avisa con AVISO y se omite.
def _value_end(t, i):
    """Devuelve el índice donde termina el valor que empieza en i (coma o salto de línea
    fuera de paréntesis, o el paréntesis que cierra el bloque)."""
    depth = 0
    while i < len(t):
        c = t[i]
        if c == "(":
            depth += 1
        elif c == ")":
            if depth == 0:
                return i
            depth -= 1
        elif c in ",\n" and depth == 0:
            return i
        i += 1
    return i

def set_palette(text, block, values):
    """Cambia valores `clave = ...` dentro de `val <block> = algo(...)`. Devuelve (texto, faltantes)."""
    m = re.search(r"\bval\s+" + re.escape(block) + r"\b", text)
    if not m:
        return text, None
    open_i = text.find("(", m.end())
    if open_i < 0:
        return text, None
    depth, j = 0, open_i
    while j < len(text):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    body = text[open_i + 1:j]
    missing = []
    for key, color in values.items():
        km = re.search(r"(?<![\w.])" + re.escape(key) + r"\s*=\s*", body)
        if not km:
            missing.append(key)
            continue
        end = _value_end(body, km.end())
        body = body[:km.end()] + color + body[end:]
    return text[:open_i + 1] + body + text[j:], missing

theme_dir = kt / "ui/theme"
palette = {
    "DarkColorPalette": {
        "primary": "Color(0xFFA678FF)",      # acento violeta
        "primaryVariant": "Color(0xFFA678FF)",
        "background": "Color(0xFF0F0A1A)",   # fondo morado casi negro
        "surface": "Color(0xFF1B1230)",      # tarjetas y listas
    },
    "DarkColorPaletteApp": {
        "title": "Color(0xFFA678FF)",
        "primaryVariant2": "Color(0xFF2E1A5C)",
        "sentMessage": "Color(0xFF2E1A5C)",
        "sentQuote": "Color(0xFF3B2477)",
        "receivedMessage": "Color(0xFF221A33)",
        "receivedQuote": "Color(0xFF2E2445)",
    },
}
done = 0
for block, values in palette.items():
    applied = False
    for f in sorted(theme_dir.glob("*.kt")) if theme_dir.exists() else []:
        src = f.read_text(encoding="utf-8")
        new_src, missing = set_palette(src, block, values)
        if missing is None:
            continue
        f.write_text(new_src, encoding="utf-8")
        applied = True
        done += 1
        if missing:
            print(f"   AVISO: en {block} no encontré: {', '.join(missing)} (el resto sí se cambió)")
        break
    if not applied:
        print(f"   AVISO: no encontré {block} en ui/theme; se omite")
print(f"   paleta morada oscura aplicada a {done} de {len(palette)} bloques")

# Modo de color por defecto: oscuro (antes seguía al sistema)
if api.exists():
    src = api.read_text(encoding="utf-8")
    new_src, n = re.subn(r"(SHARED_PREFS_CURRENT_THEME\s*,\s*)DefaultTheme\.SYSTEM_THEME_NAME", r'\1"DARK"', src, count=1)
    if n:
        api.write_text(new_src, encoding="utf-8")
        print("   modo de color por defecto: oscuro")
    else:
        print("   AVISO: no encontré el modo de color por defecto; se omite")
