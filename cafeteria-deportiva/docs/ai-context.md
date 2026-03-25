# Proyecto

Landing page estática — KOS Coffee Corner (cafetería deportiva)

# Stack

- HTML5 semántico
- CSS modular (styles.css + animations.css)
- Vanilla JS (main.js)
- Sin frameworks, sin build tools

# Estructura de archivos

```
cafeteria-deportiva/
  assets/images/        → imágenes (hero-bg.jpg, about.jpg, menu-item-*.*, gallery/*)
  css/
    styles.css          → estilos principales
    animations.css      → keyframes + clases reveal
  js/
    main.js             → navbar, scroll reveal, parallax, smooth scroll
  index.html            → estructura completa
```

# Convenciones CSS

- BEM: bloque__elemento--modificador
- Variables CSS en :root
- Clases de animación: .reveal / .reveal-left / .reveal-right / .reveal-up
- JS activa .is-visible via IntersectionObserver

# Convenciones JS

- Sin jQuery, sin librerías
- IntersectionObserver para scroll reveal
- rAF (requestAnimationFrame) para parallax
- Event delegation donde sea posible

# Convenciones HTML

- Secciones con IDs: #inicio, #menu, #nosotros, #galeria, #contacto
- section-tag + section-title en cada sección
- Imágenes con width/height/loading="lazy"
- ARIA labels en elementos interactivos

# Reglas estrictas

- No agregar dependencias externas
- No romper animaciones existentes (.reveal-* deben seguir funcionando)
- Mantener BEM en clases nuevas
- CSS nuevo va en styles.css (no inline)
- JS nuevo va en main.js

# TODOs activos en el proyecto

- FRONT-007: reemplazar datos de contacto con datos reales del cliente
  - Dirección: "Av. Ejemplo 123, Ciudad Real"
  - Teléfono: "11 1234-5678"
  - WhatsApp FAB: wa.me/5411123456789
  - Horario completo pendiente

# Output esperado

- Solo código
- Sin explicaciones
- Listo para copiar y pegar