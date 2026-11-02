package chat.simplex.common.platform

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.os.IBinder
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.delay
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withTimeoutOrNull
import org.torproject.jni.TorService

actual object ZetariaTor {
  actual val isSupported: Boolean = true

  private val mutex = Mutex()
  private var service: TorService? = null
  private var connection: ServiceConnection? = null

  actual suspend fun start(): Int? = mutex.withLock {
    try {
      val ctx = androidAppContext
      if (service == null) {
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
          Log.e(TAG, "ZetariaTor: bindService failed")
          return@withLock null
        }
        connection = c
        service = withTimeoutOrNull(20_000) { connected.await() }
        if (service == null) {
          release()
          return@withLock null
        }
      }
      val svc = service ?: return@withLock null
      var port: Int? = null
      // Espera a que Tor tenga un circuito establecido (hasta 2,5 min)
      withTimeoutOrNull(150_000) {
        while (port == null) {
          val p = svc.socksPort
          if (p > 0 && svc.getInfo("status/circuit-established")?.trim() == "1") {
            port = p
          } else {
            delay(1000)
          }
        }
      }
      if (port == null) release()
      port
    } catch (e: Exception) {
      Log.e(TAG, "ZetariaTor: start error: ${e.stackTraceToString()}")
      release()
      null
    }
  }

  actual fun stop() {
    release()
  }

  private fun release() {
    try {
      connection?.let { androidAppContext.unbindService(it) }
    } catch (e: Exception) {
      Log.e(TAG, "ZetariaTor: unbind error: ${e.message}")
    }
    connection = null
    service = null
  }
}
