package chat.simplex.common.platform

actual object ZetariaTor {
  actual val isSupported: Boolean = false

  actual suspend fun start(): Int? = null

  actual fun stop() {}
}
