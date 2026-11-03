package chat.simplex.common.platform

actual object ZetariaTor {
  actual val isSupported: Boolean = false
  actual val interruptedStage: String? = null
  actual var lastError: String? = null

  actual suspend fun start(): Int? = null

  actual fun stop() {}
}
