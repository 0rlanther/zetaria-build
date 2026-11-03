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


# ---------- Tor integrado + PNG fluido en pantalla completa ----------
# 1) Pantalla completa: limitar la decodificación a 2560 px (antes: tamaño original, que traba la app)
patch(mp / "common/src/androidMain/kotlin/chat/simplex/common/views/chat/item/ImageFullScreenView.android.kt",
      ".size(Size.ORIGINAL)", ".size(Size(2560, 2560))")

# 2) Dependencias de Tor (librería oficial del Guardian Project)
patch(mp / "build.gradle.kts", """        maven("https://jitpack.io")
    }""", """        maven("https://jitpack.io")
        maven("https://raw.githubusercontent.com/guardianproject/gpmaven/master") {
            content { includeGroup("info.guardianproject") }
        }
    }""")
patch(mp / "common/build.gradle.kts", """        implementation("io.coil-kt:coil-gif:2.6.0")""", """        implementation("io.coil-kt:coil-gif:2.6.0")

        // Zetaria: Tor integrado
        implementation("info.guardianproject:tor-android:0.4.8.16") {
            exclude(group = "org.jetbrains.kotlin", module = "kotlin-stdlib")
        }
        implementation("info.guardianproject:jtorctl:0.4.5.7")""")

# 3) Preferencia, código y pantalla
patch(kt / "model/SimpleXAPI.kt", "  val networkRequiredHostMode = mkBoolPreference(SHARED_PREFS_NETWORK_REQUIRED_HOST_MODE, false)",
      "  val networkRequiredHostMode = mkBoolPreference(SHARED_PREFS_NETWORK_REQUIRED_HOST_MODE, false)\n  val zetariaTorEnabled = mkBoolPreference(\"ZetariaTorEnabled\", false)")
tor = here / "templates/tor"
(mp / "common/src/commonMain/kotlin/chat/simplex/common/platform/ZetariaTor.kt").write_text((tor / "ZetariaTor.kt").read_text(encoding="utf-8"), encoding="utf-8")
(mp / "common/src/androidMain/kotlin/chat/simplex/common/platform/ZetariaTor.android.kt").write_text((tor / "ZetariaTor.android.kt").read_text(encoding="utf-8"), encoding="utf-8")
(mp / "common/src/desktopMain/kotlin/chat/simplex/common/platform/ZetariaTor.desktop.kt").write_text((tor / "ZetariaTor.desktop.kt").read_text(encoding="utf-8"), encoding="utf-8")
(kt / "views/usersettings/networkAndServers/ZetariaTorSection.kt").write_text((tor / "ZetariaTorSection.kt").read_text(encoding="utf-8"), encoding="utf-8")
patch(kt / "views/usersettings/networkAndServers/NetworkAndServers.kt",
      "    SectionView(generalGetString(MR.strings.settings_section_title_messages)) {",
      "    if (appPlatform.isAndroid && currentRemoteHost == null) {\n      ZetariaTorSection(networkUseSocksProxy)\n    }\n\n    SectionView(generalGetString(MR.strings.settings_section_title_messages)) {")

# 4) Arranque automático de Tor si quedó activado
patch(mp / "android/src/main/java/chat/simplex/app/SimplexApp.kt", "\n    deleteOldChatArchive()\n", """
    deleteOldChatArchive()
    // Zetaria: iniciar Tor integrado si el usuario lo dejó activado
    if (appPrefs.zetariaTorEnabled.get() && appPrefs.networkUseSocksProxy.get()) {
      if (chat.simplex.common.platform.ZetariaTor.interruptedStage != null) {
        // El arranque anterior de Tor se cortó a mitad: no reintentar (evita cierres en bucle)
        appPrefs.zetariaTorEnabled.set(false)
        appPrefs.networkUseSocksProxy.set(false)
      } else {
        withLongRunningApi {
          val torPort = chat.simplex.common.platform.ZetariaTor.start()
          if (torPort != null && torPort != appPrefs.networkProxy.get().port) {
            appPrefs.networkProxy.set(appPrefs.networkProxy.get().copy(port = torPort))
            if (chatModel.chatRunning.value == true) {
              chatModel.controller.apiSetNetworkConfig(chatModel.controller.getNetCfg())
            }
          }
        }
      }
    }
""")

# 5) Textos
x = base.read_text(encoding="utf-8")
new = (
 '  <string name="zetaria_tor_title">Red Tor</string>\n'
 '  <string name="zetaria_tor_toggle">Usar Tor integrado (.onion)</string>\n'
 '  <string name="zetaria_tor_footer">Conecta a los servidores a través de la red Tor, usando sus direcciones .onion cuando existen. Aumenta la privacidad, pero puede ser más lento y gastar más batería.</string>\n'
 '  <string name="zetaria_tor_starting">Iniciando Tor… puede tardar hasta un par de minutos.</string>\n'
 '  <string name="zetaria_tor_active">Tor activo (proxy local en el puerto %1$d). Tu tráfico sale por la red Tor.</string>\n'
 '  <string name="zetaria_tor_error_title">No se pudo iniciar Tor</string>\n'
 '  <string name="zetaria_tor_error_text">Tor no logró conectarse. Revisa tu conexión a internet e inténtalo de nuevo. La app sigue funcionando sin Tor.</string>\n')
x = x.replace("</resources>", new + "</resources>")
base.write_text(x, encoding="utf-8")
print("   Tor integrado + PNG fluido aplicados")


# ---------- Tor visible también en cada operador (SimpleX, Flux) ----------
# Estos parches son opcionales: si el código de SimpleX no coincide con lo esperado,
# se avisa y se omiten, sin romper la compilación que ya funciona.
def patch_optional(path, old, new, what):
    if not path.exists():
        print(f"   AVISO: no existe {path.name}; se omite: {what}")
        return False
    t = path.read_text(encoding="utf-8")
    if old not in t:
        print(f"   AVISO: no encontré el punto de inserción en {path.name}; se omite: {what}")
        return False
    path.write_text(t.replace(old, new, 1), encoding="utf-8")
    return True

def insert_after_call(path, func_name, call_name, insertion, what):
    """Inserta `insertion` justo después de la primera llamada `call_name(...)`
    dentro de `fun func_name(`, contando paréntesis para hallar el cierre."""
    if not path.exists():
        print(f"   AVISO: no existe {path.name}; se omite: {what}")
        return False
    t = path.read_text(encoding="utf-8")
    start = t.find(f"fun {func_name}(")
    if start < 0:
        print(f"   AVISO: no encontré fun {func_name} en {path.name}; se omite: {what}")
        return False
    if "ZetariaTorOperatorSection" in t:
        return True  # ya aplicado
    call = t.find(f"{call_name}(", start)
    if call < 0:
        print(f"   AVISO: no encontré {call_name}( en {func_name}; se omite: {what}")
        return False
    i = call + len(call_name)
    depth = 0
    while i < len(t):
        c = t[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    else:
        print(f"   AVISO: paréntesis sin cerrar en {path.name}; se omite: {what}")
        return False
    t = t[:i + 1] + insertion + t[i + 1:]
    path.write_text(t, encoding="utf-8")
    return True

nas = kt / "views/usersettings/networkAndServers"
ok = insert_after_call(
    nas / "OperatorView.kt", "OperatorViewLayout", "AppBarTitle",
    "\n    if (appPlatform.isAndroid && chatModel.currentRemoteHost.value == null) {\n"
    "      ZetariaTorOperatorSection()\n    }",
    "sección Tor dentro de cada operador (SimpleX y Flux)")
print("   Tor visible en operadores SimpleX/Flux" if ok else "   Tor en operadores: omitido (ver avisos)")

# R8/ProGuard: la librería de Tor usa JNI; si se ofusca, la app se cierra al iniciar Tor.
pg = mp / "android/proguard-rules.pro"
rules = ("\n# Zetaria: Tor integrado (JNI)\n"
         "-keep class org.torproject.jni.** { *; }\n"
         "-keep class net.freehaven.tor.control.** { *; }\n"
         "-dontwarn org.torproject.jni.**\n")
if pg.exists():
    if "org.torproject.jni" not in pg.read_text(encoding="utf-8"):
        with open(pg, "a", encoding="utf-8") as f:
            f.write(rules)
    print("   reglas ProGuard para Tor añadidas")
else:
    print("   AVISO: no existe proguard-rules.pro; se omiten reglas de Tor")


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
