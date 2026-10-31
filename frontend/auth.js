// auth.js — Hafesa · guard de autenticación compartido
const AUTH_TOKEN_KEY = 'hafesa_token'
const AUTH_USER_KEY  = 'hafesa_user'
// En local (puerto 3000) el backend está en 8000. En producción nginx hace el proxy.
const API_BASE_URL = (location.port === '3000') ? 'http://localhost:8000' : ''

const Auth = {
  getToken() { return localStorage.getItem(AUTH_TOKEN_KEY) },
  getUser()  { return JSON.parse(localStorage.getItem(AUTH_USER_KEY) || 'null') },

  save(tokenOut) {
    localStorage.setItem(AUTH_TOKEN_KEY, tokenOut.access_token)
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify({
      rol:         tokenOut.rol,
      nombre:      tokenOut.nombre,
      vendedor_id: tokenOut.vendedor_id,
      pantallas:   tokenOut.pantallas || [],
    }))
  },

  logout() {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    localStorage.removeItem(AUTH_USER_KEY)
    location.href = 'login.html'
  },

  // Llama al inicio de cada página protegida.
  // allowedRoles: null = cualquier rol autenticado, o ['administrador', 'logistica']
  require(allowedRoles = null) {
    const token = this.getToken()
    const user  = this.getUser()
    if (!token || !user) { location.href = 'login.html'; return null }
    if (allowedRoles && !allowedRoles.includes(user.rol)) {
      this._redirectByRole(user.rol); return null
    }
    return user
  },

  _redirectByRole(rol) {
    location.href = this.inicio() || (rol === 'vendedor' ? 'formulario_pedido.html' : 'backoffice.html')
  },

  // ¿El usuario tiene asignada esta pantalla? (clave del catálogo del backend)
  tiene(clave) {
    const user = this.getUser()
    return !!user && Array.isArray(user.pantallas) && user.pantallas.some(p => p.key === clave)
  },

  // Página de inicio: vendedores a Nuevo pedido, el resto a Gestión de pedidos;
  // si no tienen esa, a la primera pantalla que sí tengan.
  inicio(user = this.getUser()) {
    const pantallas = (user && user.pantallas) || []
    const preferidas = user && user.rol === 'vendedor' ? ['nuevo_pedido', 'pedidos'] : ['pedidos', 'nuevo_pedido']
    const elegida = preferidas.map(k => pantallas.find(p => p.key === k)).find(Boolean) || pantallas[0]
    return elegida ? elegida.url : null
  },

  // Guard por pantalla (reemplaza a require() con roles). Decide con los permisos guardados
  // al ingresar y los refresca en segundo plano para reflejar cambios hechos por el administrador.
  requirePantalla(clave) {
    const token = this.getToken()
    const user  = this.getUser()
    if (!token || !user) { location.href = 'login.html'; return null }
    // Sesión iniciada antes de existir los permisos por pantalla: ingresar de nuevo los carga
    if (!Array.isArray(user.pantallas)) { this.logout(); return null }
    if (!this.tiene(clave)) { this._reintentar(clave); return null }
    this._actualizarPantallas(clave)
    return user
  },

  // La lista guardada dice que no: antes de rechazar se pide la vigente, por si el administrador
  // acaba de concederle la pantalla. Si ahora sí la tiene, se recarga la página.
  async _reintentar(clave) {
    await this._actualizarPantallas(null)
    if (this.tiene(clave)) location.reload()
    else this._denegado()
  },

  _denegado() {
    const destino = this.inicio()
    if (destino) { location.href = destino; return }
    alert('No tienes pantallas asignadas. Consulta con el administrador.')
    this.logout()
  },

  async _actualizarPantallas(clave) {
    try {
      const res = await this.fetch(`${API_BASE_URL}/api/permisos/mis-pantallas`)
      if (!res || !res.ok) return
      const { pantallas } = await res.json()
      const user = this.getUser()
      if (!user) return
      user.pantallas = pantallas
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user))
      window.dispatchEvent(new Event('hafesa:pantallas'))
      if (clave && !this.tiene(clave)) this._denegado()
    } catch (e) { /* sin red: se mantiene lo guardado */ }
  },

  // fetch con Authorization header automático; redirige a login si 401
  async fetch(url, options = {}) {
    const token = this.getToken()
    const headers = {
      ...(options.headers || {}),
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    }
    // No forzar Content-Type si el body es FormData (para uploads)
    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = headers['Content-Type'] || 'application/json'
    }
    // Resolver URL relativa a URL absoluta del backend
    const fullUrl = url.startsWith('/api/') ? API_BASE_URL + url : url
    const res = await fetch(fullUrl, { ...options, headers })
    if (res.status === 401) { this.logout(); return null }
    return res
  },
}
