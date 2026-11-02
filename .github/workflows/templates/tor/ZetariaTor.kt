package chat.simplex.common.platform

// Tor integrado (solo Android). En escritorio no está disponible.
expect object ZetariaTor {
  val isSupported: Boolean

  // Inicia Tor y devuelve el puerto SOCKS local cuando ya hay circuito, o null si falla.
  suspend fun start(): Int?

  fun stop()
}
