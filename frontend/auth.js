// auth.js — Hafesa · guard de autenticación compartido
const AUTH_TOKEN_KEY = 'hafesa_token'
const AUTH_USER_KEY  = 'hafesa_user'
const API_BASE_URL = 'http://localhost:8000'

const Auth = {
  getToken() { return localStorage.getItem(AUTH_TOKEN_KEY) },
  getUser()  { return JSON.parse(localStorage.getItem(AUTH_USER_KEY) || 'null') },

  save(tokenOut) {
    localStorage.setItem(AUTH_TOKEN_KEY, tokenOut.access_token)
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify({
      rol:         tokenOut.rol,
      nombre:      tokenOut.nombre,
      vendedor_id: tokenOut.vendedor_id,
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
    if (rol === 'vendedor') location.href = 'formulario_pedido.html'
    else location.href = 'backoffice.html'
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
