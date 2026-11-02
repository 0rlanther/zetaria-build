package chat.simplex.common.views.usersettings.networkAndServers

import SectionDividerSpaced
import SectionTextFooter
import SectionView
import androidx.compose.runtime.*
import chat.simplex.common.model.*
import chat.simplex.common.platform.*
import chat.simplex.common.views.helpers.*
import chat.simplex.common.views.usersettings.*
import chat.simplex.res.MR
import dev.icerock.moko.resources.compose.stringResource

// Estado compartido: la misma sección aparece en "Red y servidores" y en la pantalla de cada
// operador (SimpleX, Flux), y todas deben mostrar el mismo estado.
private val zetariaTorOn: MutableState<Boolean> by lazy {
  mutableStateOf(chatModel.controller.appPrefs.zetariaTorEnabled.get() && chatModel.controller.appPrefs.networkUseSocksProxy.get())
}
private val zetariaTorStatus: MutableState<String?> = mutableStateOf(null)
private val zetariaTorBusy: MutableState<Boolean> = mutableStateOf(false)

// Versión para la pantalla de cada operador (SimpleX / Flux): no recibe el estado del proxy
// de la pantalla padre, lo lee de las preferencias.
@Composable
fun ZetariaTorOperatorSection() {
  val useProxy = remember { mutableStateOf(chatModel.controller.appPrefs.networkUseSocksProxy.get()) }
  ZetariaTorSection(useProxy)
}

// Sección visible junto a los servidores predefinidos: interruptor de Tor integrado.
@Composable
fun ZetariaTorSection(networkUseSocksProxy: MutableState<Boolean>) {
  val enabled = zetariaTorOn
  val busy = zetariaTorBusy
  val status = zetariaTorStatus
  SectionView(stringResource(MR.strings.zetaria_tor_title)) {
    PreferenceToggle(
      stringResource(MR.strings.zetaria_tor_toggle),
      disabled = busy.value,
      checked = enabled.value,
      onChange = { on ->
        busy.value = true
        withBGApi {
          try {
            if (on) {
              enableZetariaTor(enabled, status, networkUseSocksProxy)
            } else {
              disableZetariaTor(enabled, status, networkUseSocksProxy)
            }
          } finally {
            busy.value = false
          }
        }
      }
    )
  }
  SectionTextFooter(status.value ?: stringResource(MR.strings.zetaria_tor_footer))
  SectionDividerSpaced()
}

private suspend fun enableZetariaTor(
  enabled: MutableState<Boolean>,
  status: MutableState<String?>,
  networkUseSocksProxy: MutableState<Boolean>
) {
  status.value = generalGetString(MR.strings.zetaria_tor_starting)
  val port = ZetariaTor.start()
  if (port == null) {
    ZetariaTor.stop()
    status.value = null
    enabled.value = false
    AlertManager.shared.showAlertMsg(
      title = generalGetString(MR.strings.zetaria_tor_error_title),
      text = generalGetString(MR.strings.zetaria_tor_error_text)
    )
    return
  }
  val def = NetCfg.defaults
  val proxyDef = NetCfg.proxyDefaults
  val controller = chatModel.controller
  controller.appPrefs.networkProxy.set(controller.appPrefs.networkProxy.get().copy(host = "localhost", port = port))
  var conf = controller.getNetCfg().withProxy(controller.appPrefs.networkProxy.get()).withOnionHosts(OnionHosts.PREFER)
  if (conf.tcpConnectTimeout == def.tcpConnectTimeout) {
    conf = conf.copy(tcpConnectTimeout = proxyDef.tcpConnectTimeout)
  }
  if (conf.tcpTimeout == def.tcpTimeout) {
    conf = conf.copy(tcpTimeout = proxyDef.tcpTimeout)
  }
  if (conf.tcpTimeoutPerKb == def.tcpTimeoutPerKb) {
    conf = conf.copy(tcpTimeoutPerKb = proxyDef.tcpTimeoutPerKb)
  }
  if (conf.rcvConcurrency == def.rcvConcurrency) {
    conf = conf.copy(rcvConcurrency = proxyDef.rcvConcurrency)
  }
  controller.apiSetNetworkConfig(conf)
  controller.setNetCfg(conf)
  controller.appPrefs.zetariaTorEnabled.set(true)
  networkUseSocksProxy.value = true
  enabled.value = true
  status.value = generalGetString(MR.strings.zetaria_tor_active).format(port)
}

private suspend fun disableZetariaTor(
  enabled: MutableState<Boolean>,
  status: MutableState<String?>,
  networkUseSocksProxy: MutableState<Boolean>
) {
  val def = NetCfg.defaults
  val proxyDef = NetCfg.proxyDefaults
  val controller = chatModel.controller
  var conf = controller.getNetCfg().copy(socksProxy = null)
  if (conf.tcpConnectTimeout == proxyDef.tcpConnectTimeout) {
    conf = conf.copy(tcpConnectTimeout = def.tcpConnectTimeout)
  }
  if (conf.tcpTimeout == proxyDef.tcpTimeout) {
    conf = conf.copy(tcpTimeout = def.tcpTimeout)
  }
  if (conf.tcpTimeoutPerKb == proxyDef.tcpTimeoutPerKb) {
    conf = conf.copy(tcpTimeoutPerKb = def.tcpTimeoutPerKb)
  }
  if (conf.rcvConcurrency == proxyDef.rcvConcurrency) {
    conf = conf.copy(rcvConcurrency = def.rcvConcurrency)
  }
  controller.apiSetNetworkConfig(conf)
  controller.setNetCfg(conf)
  controller.appPrefs.zetariaTorEnabled.set(false)
  networkUseSocksProxy.value = false
  ZetariaTor.stop()
  enabled.value = false
  status.value = null
}
