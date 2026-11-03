package chat.simplex.common.platform

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.IBinder
import java.io.File
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.delay
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withTimeoutOrNull
import org.torproject.jni.TorService

actual object ZetariaTor {
  actual val isSupported: Boolean = true
  actual var lastError: String? = null

  private val mutex = Mutex()
  private var service: TorService? = null
  private var connection: ServiceConnection? = null

  private fun stageFile() = File(androidAppContext.filesDir, "zetaria-tor-stage.txt")

  // Deja anotada la etapa actual: si la app se cierra de golpe (fallo nativo), en el
  // siguiente inicio sabremos en qué etapa ocurrió.
  private fun mark(stage: String) {
    try {
      stageFile().writeText(stage)
    } catch (_: Throwable) {
    }
  }

  actual val interruptedStage: String? = try {
    val f = stageFile()
    val s = if (f.exists()) f.readText().trim() else ""
    f.writeText("visto")
    if (s.isEmpty() || s in setOf("ok", "fallo", "detenido", "visto")) null else s
  } catch (_: Throwable) {
    null
  }

  private fun fail(reason: String): Int? {
    lastError = reason
    Log.e(TAG, "ZetariaTor: $reason")
    mark("fallo")
    release()
    return null
  }

  actual suspend fun start(): Int? = mutex.withLock {
    lastError = null
    try {
      mark("inicio")
      val ctx = androidAppContext
      if (service == null) {
        mark("enlazando el servicio de Tor")
        val connected = CompletableDeferred<TorService?>()
        val c = object : ServiceConnection {
          override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
            connected.complete((binder as? TorService.LocalBinder)?.service)
          }

          override fun onServiceDisconnected(name: ComponentName?) {
            service = null
          }
        }
        if (!ctx.bindService(Intent(ctx, TorService::class.java), c, Context.BIND_AUTO_CREATE)) {
          return@withLock fail("no se pudo enlazar el servicio de Tor")
        }
        connection = c
        mark("esperando respuesta del servicio de Tor")
        service = withTimeoutOrNull(20_000) { connected.await() }
        if (service == null) {
          return@withLock fail("el servicio de Tor no respondió")
        }
      }
      val svc = service ?: return@withLock fail("servicio de Tor no disponible")
      mark("esperando circuito de Tor")
      var port: Int? = null
      // Espera a que Tor tenga un circuito establecido (hasta 2,5 min)
      withTimeoutOrNull(150_000) {
        while (port == null) {
          val p = try {
            svc.socksPort
          } catch (_: Exception) {
            0
          }
          val ready = try {
            svc.getInfo("status/circuit-established")?.trim() == "1"
          } catch (_: Exception) {
            false // el control de Tor aún no está listo; se reintenta
          }
          if (p > 0 && ready) {
            port = p
          } else {
            delay(1000)
          }
        }
      }
      if (port == null) {
        return@withLock fail("Tor no estableció un circuito a tiempo")
      }
      mark("ok")
      port
    } catch (e: CancellationException) {
      mark("detenido")
      release()
      throw e
    } catch (e: Throwable) {
      // Throwable (no solo Exception): así un fallo al cargar la librería nativa
      // (UnsatisfiedLinkError, NoClassDefFoundError...) no cierra la app.
      Log.e(TAG, "ZetariaTor: start error: ${e.stackTraceToString()}")
      fail("${e.javaClass.simpleName}: ${e.message ?: "sin detalle"}")
    }
  }

  actual fun stop() {
    release()
    mark("detenido")
  }

  private fun release() {
    try {
      connection?.let { androidAppContext.unbindService(it) }
    } catch (e: Throwable) {
      Log.e(TAG, "ZetariaTor: unbind error: ${e.message}")
    }
    connection = null
    service = null
  }
}
