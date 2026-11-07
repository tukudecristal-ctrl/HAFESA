// etiquetas.js — Etiquetas de envío de 100 x 100 mm para la impresora térmica de etiquetas.
// Cada pedido genera una etiqueta; si tiene más de 6 productos, genera las que hagan falta.
// Se imprime desde el navegador (diálogo de impresión del sistema) con una etiqueta por página.

const Etiquetas = (() => {
  const PRODUCTOS_POR_ETIQUETA = 6   // más de 6 productos continúan en otra etiqueta
  const PRODUCTOS_LETRA_GRANDE = 3   // hasta 3 productos: letra grande; de 4 a 6: letra más chica

  const REDES = [
    { icono: 'facebook',  texto: 'Verde' },
    { icono: 'instagram', texto: 'VerdeES' },
    { icono: 'tiktok',    texto: 'verdees1' },
  ]

  const ICONOS = {
    facebook:  '<svg viewBox="0 0 24 24"><path fill="#000" d="M14 8V6.5c0-.8.2-1.2 1.3-1.2H17V2h-2.6C11.2 2 10 3.7 10 6.2V8H7.5v3.3H10V22h4V11.3h2.7L17 8z"/></svg>',
    instagram: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="#000" stroke-width="2.2"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="#000" stroke-width="2.2"/><circle cx="17.4" cy="6.6" r="1.3" fill="#000"/></svg>',
    tiktok:    '<svg viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="5" fill="#000"/><path fill="#fff" d="M13.1 5.5h-1.9v8.2a1.7 1.7 0 1 1-1.7-1.7c.2 0 .3 0 .5.1V10a3.6 3.6 0 1 0 3.1 3.6V9.4c.7.5 1.5.8 2.4.8V8.4a2.5 2.5 0 0 1-2.4-2.9z"/></svg>',
  }

  const CSS = `
    @page { size: 100mm 100mm; margin: 0 }
    * { box-sizing: border-box; margin: 0; padding: 0 }
    html, body { width: 100mm; background: #fff; color: #000;
                 font-family: Arial, Helvetica, sans-serif;
                 -webkit-print-color-adjust: exact; print-color-adjust: exact }
    .etiqueta { width: 100mm; height: 99.5mm; padding: 3.5mm 4.5mm 2.5mm; overflow: hidden;
                display: flex; flex-direction: column;
                break-after: page; page-break-after: always }
    .etiqueta:last-child { break-after: auto; page-break-after: auto }

    .cab { display: flex; align-items: center; gap: 3mm; height: 20.5mm; flex: none;
           padding-bottom: 1.2mm; border-bottom: .35mm dashed #000 }
    .cab .logo { height: 15mm; width: auto; flex: none }
    .redes { list-style: none; flex: 1; min-width: 0; font-size: 8.5pt; line-height: 1.35 }
    .redes li { display: flex; align-items: center; gap: 1.6mm; white-space: nowrap }
    .redes svg { width: 3.4mm; height: 3.4mm; flex: none }
    .cab .qr { height: 19mm; width: 19mm; flex: none }

    .cliente { margin-top: 1.2mm; flex: none }
    .rot { font-size: 6.5pt; letter-spacing: .3pt; text-transform: uppercase }
    .nombre { font-weight: 800; text-transform: uppercase; line-height: 1.1; white-space: nowrap;
              overflow: hidden; text-overflow: ellipsis }
    .doc { font-size: 10pt; line-height: 1.2 }

    .destino { margin-top: 1.2mm; flex: none; text-align: center; font-size: 7.5pt; font-weight: 700;
               line-height: 1.15; max-height: 9.3mm; overflow: hidden;
               display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 3 }

    .productos { margin-top: 1.4mm; flex: 1 1 auto; min-height: 0; overflow: hidden }
    .prod-cab { font-size: 6.5pt; text-transform: uppercase; letter-spacing: .3pt; display: flex;
                align-items: baseline; gap: 1.2mm }
    .prod-cab b { font-size: 10pt; letter-spacing: 0 }
    .prod-cab .pag { margin-left: auto; letter-spacing: 0 }
    .prod { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 700 }
    .prod.grande { font-size: 10.5pt; line-height: 1.3 }
    .prod.chica  { font-size: 7.5pt;  line-height: 1.22 }

    .montos { margin-top: 1mm; flex: none; display: flex; align-items: flex-end; gap: 5mm }
    .montos .rot { display: block }
    .montos .resta b { font-size: 15pt; line-height: 1.1 }
    .montos .envio { padding-bottom: .4mm }
    .montos .envio b { font-size: 10.5pt }

    .detalle { margin-top: 1mm; flex: none; font-size: 7.5pt; line-height: 1.2; max-height: 6.4mm;
               overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2 }
    .detalle .rot { font-size: 6.5pt }
    .detalle b { font-weight: 700 }

    .pie { margin-top: 1mm; flex: none; padding-top: .8mm; border-top: .35mm dashed #000;
           text-align: center; font-size: 6.5pt; line-height: 1.25 }
    .pie i { font-family: Georgia, 'Times New Roman', serif }
  `

  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))

  const soles = (n) => {
    const v = parseFloat(n || 0)
    return 'S/. ' + (Number.isInteger(v) ? v : v.toFixed(2))
  }

  // "Pedro Vargas Soto" -> "PEDRO V."
  function nombreAsesor(nombre) {
    const partes = String(nombre || '').trim().split(/\s+/).filter(Boolean)
    if (!partes.length) return ''
    return (partes[0] + (partes[1] ? ' ' + partes[1][0] + '.' : '')).toUpperCase()
  }

  function tamanoNombre(nombre) {
    const n = String(nombre || '').length
    if (n <= 24) return 15
    if (n <= 29) return 12.5
    if (n <= 35) return 10.5
    return 9
  }

  function textoDestino(p) {
    if (p.tipo_destino === 'otro') return p.direccion_otra_agencia || 'DESTINO NO ESPECIFICADO'
    return p.direccion_agencia || 'AGENCIA NO ESPECIFICADA'
  }

  function productosDe(p, productosMap) {
    if (p.detalles && p.detalles.length) {
      return p.detalles.map(d => ({
        cantidad: d.cantidad,
        nombre: d.nombre_producto || (productosMap && productosMap[d.producto_id]) || 'Producto',
      }))
    }
    return [{ cantidad: p.cantidad || 1, nombre: (productosMap && productosMap[p.producto_id]) || '—' }]
  }

  // Una etiqueta (HTML). `items` son los productos que caben en esta etiqueta.
  function htmlEtiqueta(p, items, totalUnidades, nEtiqueta, totalEtiquetas, asesor, assets) {
    const clase = items.length <= PRODUCTOS_LETRA_GRANDE ? 'grande' : 'chica'
    const lineas = items.map(i => `<div class="prod ${clase}">${esc(i.cantidad)} x ${esc(i.nombre)}</div>`).join('')
    const redes = REDES.map(r => `<li>${ICONOS[r.icono]}<span>${esc(r.texto)}</span></li>`).join('')
    const pagina = totalEtiquetas > 1 ? `<span class="pag">${nEtiqueta}/${totalEtiquetas}</span>` : ''
    return `
      <section class="etiqueta">
        <div class="cab">
          <img class="logo" src="${esc(assets.logo)}" alt="">
          <ul class="redes">${redes}</ul>
          <img class="qr" src="${esc(assets.qr)}" alt="">
        </div>
        <div class="cliente">
          <div class="rot">Cliente</div>
          <div class="nombre" style="font-size:${tamanoNombre(p.nombre_cliente)}pt">${esc(p.nombre_cliente)}</div>
          <div class="doc">DOC: ${esc(p.dni)} &nbsp;|&nbsp; TEL: ${esc(p.telefono)}</div>
        </div>
        <div class="destino">${esc(textoDestino(p))}</div>
        <div class="productos">
          <div class="prod-cab">Productos: <b>${esc(totalUnidades)}</b>${pagina}</div>
          ${lineas}
        </div>
        <div class="montos">
          <div class="resta"><span class="rot">Resta pagar</span><b>${esc(soles(p.resta_pagar))}</b></div>
          <div class="envio"><span class="rot">+ Costo de envío</span><b>${esc(soles(p.costo_envio))}</b></div>
        </div>
        <div class="detalle"><span class="rot">Detalle:</span> <b>${esc(p.detalle_observacion || '')}</b></div>
        <div class="pie">
          <i>¡Agradecemos su confianza, y que Dios los bendiga siempre!</i><br>
          Asesor: <b>${esc(asesor)}</b>
        </div>
      </section>`
  }

  // Etiquetas que necesita UNA copia del pedido (más de 6 productos continúan en otra etiqueta).
  function etiquetasPorPedido(p, productosMap = {}) {
    return Math.max(1, Math.ceil(productosDe(p, productosMap).length / PRODUCTOS_POR_ETIQUETA))
  }

  // Devuelve las etiquetas de los pedidos (omite los cancelados) y los conteos para confirmar.
  // Cada pedido puede traer `copias` (por defecto 1; 0 lo omite): se repite el juego completo de etiquetas.
  function construir(pedidos, { vendedoresMap = {}, productosMap = {}, assets }) {
    const validos = pedidos.filter(p => p.estado !== 'CANCELADO')
    const etiquetas = []
    let envios = 0
    for (const p of validos) {
      const copias = p.copias === undefined ? 1 : Math.max(0, parseInt(p.copias, 10) || 0)
      if (!copias) continue
      envios++
      const items = productosDe(p, productosMap)
      const totalUnidades = items.reduce((s, i) => s + (parseInt(i.cantidad, 10) || 0), 0)
      const total = etiquetasPorPedido(p, productosMap)
      const asesor = nombreAsesor(vendedoresMap[p.vendedor_id])
      for (let c = 0; c < copias; c++) {
        for (let n = 0; n < total; n++) {
          const parte = items.slice(n * PRODUCTOS_POR_ETIQUETA, (n + 1) * PRODUCTOS_POR_ETIQUETA)
          etiquetas.push(htmlEtiqueta(p, parte, totalUnidades, n + 1, total, asesor, assets))
        }
      }
    }
    return { etiquetas, envios, cancelados: pedidos.length - validos.length }
  }

  function documento(etiquetas) {
    return `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Etiquetas</title><style>${CSS}</style></head>
            <body>${etiquetas.join('')}</body></html>`
  }

  function cargarImagen(url) {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = () => reject(new Error('No se pudo cargar la imagen ' + url))
      img.src = url
    })
  }

  // La impresora es térmica (solo negro): el QR de TikTok trae puntos rojos y celestes que se
  // perderían o saldrían grises, así que todo lo que no sea blanco se pasa a negro.
  async function qrBlancoYNegro(url) {
    const img = await cargarImagen(url)
    const c = document.createElement('canvas')
    c.width = img.naturalWidth
    c.height = img.naturalHeight
    const ctx = c.getContext('2d')
    ctx.fillStyle = '#fff'
    ctx.fillRect(0, 0, c.width, c.height)
    ctx.drawImage(img, 0, 0)
    const datos = ctx.getImageData(0, 0, c.width, c.height)
    const px = datos.data
    for (let i = 0; i < px.length; i += 4) {
      const v = Math.min(px[i], px[i + 1], px[i + 2]) < 170 ? 0 : 255
      px[i] = px[i + 1] = px[i + 2] = v
      px[i + 3] = 255
    }
    ctx.putImageData(datos, 0, 0)
    return c.toDataURL('image/png')
  }

  let assetsCache = null
  async function assets() {
    if (!assetsCache) {
      const base = new URL('.', location.href)
      assetsCache = {
        logo: new URL('img/logo_verde.png', base).href,
        qr: await qrBlancoYNegro(new URL('img/qr_verde.png', base).href),
      }
    }
    return assetsCache
  }

  function esperarImagenes(doc) {
    const pendientes = [...doc.images].filter(i => !i.complete)
    return Promise.all(pendientes.map(i => new Promise(r => { i.onload = i.onerror = r })))
  }

  // Imprime en un iframe oculto: una etiqueta por página (100 x 100 mm).
  function imprimir(etiquetas) {
    return new Promise((resolve, reject) => {
      const f = document.createElement('iframe')
      f.style.cssText = 'position:fixed;right:0;bottom:0;width:0;height:0;border:0'
      f.onload = async () => {
        try {
          const w = f.contentWindow
          await esperarImagenes(w.document)
          const limpiar = () => { f.remove(); resolve() }
          w.onafterprint = limpiar
          setTimeout(limpiar, 5 * 60 * 1000)
          w.focus()
          w.print()
        } catch (e) { f.remove(); reject(e) }
      }
      f.srcdoc = documento(etiquetas)
      document.body.appendChild(f)
    })
  }

  return { construir, etiquetasPorPedido, documento, assets, imprimir, PRODUCTOS_POR_ETIQUETA }
})()
