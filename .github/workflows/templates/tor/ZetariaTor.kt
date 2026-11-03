package chat.simplex.common.platform

// Tor integrado (solo Android). En escritorio no está disponible.
expect object ZetariaTor {
  val isSupported: Boolean

  // Etapa en la que se interrumpió el arranque de Tor en la sesión anterior (la app se cerró
  // a mitad de arranque), o null si todo terminó bien.
  val interruptedStage: String?

  // Motivo del último fallo al iniciar Tor (para mostrarlo al usuario).
  var lastError: String?

  // Inicia Tor y devuelve el puerto SOCKS local cuando ya hay circuito, o null si falla.
  suspend fun start(): Int?

  fun stop()
}
