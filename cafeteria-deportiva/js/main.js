/* ============================================================
   KOS COFFEE SPORT — main.js  v4.1
   Navbar | Reveal | Parallax | Tienda tabs | WhatsApp
   ============================================================ */

/* ── WHATS-001: número centralizado ─────────────────────────── */
/* Cambiar solo aquí — se aplica en toda la página              */
const WHATSAPP_NUMBER = '542604331727'; /* TODO: confirmar número real */

/* ── Año actual en footer ────────────────────────────────────── */
const yearEl = document.querySelector('.footer__year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

/* ── Scroll reveal con IntersectionObserver ─────────────────── */
/* REGLA: no eliminar — animations.css depende de .is-visible   */
const revealEls = document.querySelectorAll(
  '.reveal, .reveal-left, .reveal-right, .reveal-up'
);
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12, rootMargin: '0px 0px -36px 0px' }
);
revealEls.forEach((el) => revealObserver.observe(el));

/* ── Smooth scroll para links de navegación ─────────────────── */
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (e) => {
    const href = link.getAttribute('href');
    if (href === '#') return; /* botones js-wa-product usan href="#" */
    const target = document.querySelector(href);
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      /* Cerrar menú mobile si está abierto */
      if (navMenu.classList.contains('is-open')) {
        navMenu.classList.remove('is-open');
        navBurger.classList.remove('is-open');
        navBurger.setAttribute('aria-expanded', 'false');
      }
    }
  });
});

/* ── Parallax con rAF ────────────────────────────────────────── */
const hero = document.querySelector('.hero');
let rafId;
if (hero) {
  window.addEventListener('scroll', () => {
    cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(() => {
      const scrollY = window.scrollY;
      if (scrollY < window.innerHeight) {
        hero.style.backgroundPositionY = `calc(40% + ${scrollY * 0.32}px)`;
      }
    });
  }, { passive: true });
}

/* ── Navbar: scrolled state + logo swap + burger ────────────── */
const navbar    = document.getElementById('navbar');
const navMenu   = document.getElementById('navMenu');
const navBurger = document.getElementById('navBurger');
const navLogo   = document.getElementById('navLogo');

const NAV_THRESHOLD = 60;

function updateNavbar() {
  if (window.scrollY > NAV_THRESHOLD) {
    navbar.classList.add('navbar--scrolled');
    /* LOGO-001: logo blanco sobre verde — CSS filter maneja esto */
    /* Si se necesita swap real de imagen, descomentar las líneas siguientes:
    if (navLogo) navLogo.src = navLogo.src.replace('logo-negro', 'logo-blanco');
    */
  } else {
    navbar.classList.remove('navbar--scrolled');
  }
}
window.addEventListener('scroll', updateNavbar, { passive: true });
updateNavbar(); /* ejecutar al cargar por si ya está scrolleada */

/* Hamburger toggle */
if (navBurger) {
  navBurger.addEventListener('click', () => {
    const isOpen = navMenu.classList.toggle('is-open');
    navBurger.classList.toggle('is-open', isOpen);
    navBurger.setAttribute('aria-expanded', String(isOpen));
  });
}

/* Cerrar menú al hacer click fuera */
document.addEventListener('click', (e) => {
  if (
    navMenu.classList.contains('is-open') &&
    !navbar.contains(e.target)
  ) {
    navMenu.classList.remove('is-open');
    navBurger.classList.remove('is-open');
    navBurger.setAttribute('aria-expanded', 'false');
  }
});

/* ── Tienda: tabs de filtro por categoría ───────────────────── */
/* SEC-002: lógica de la sección Tienda */
const tiendaTabs  = document.querySelectorAll('.tienda__tab');
const tiendaCards = document.querySelectorAll('.tienda__card');

tiendaTabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    /* Actualizar estado activo del tab */
    tiendaTabs.forEach((t) => {
      t.classList.remove('is-active');
      t.setAttribute('aria-selected', 'false');
    });
    tab.classList.add('is-active');
    tab.setAttribute('aria-selected', 'true');

    const filter = tab.dataset.filter;

    /* Limpiar estado expandido de todas las cards */
    tiendaCards.forEach((card) => card.classList.remove('tienda__card--expanded'));

    /* Filtrar cards */
    tiendaCards.forEach((card) => {
      if (filter === 'todos' || card.dataset.category === filter) {
        card.classList.remove('is-hidden');
      } else {
        card.classList.add('is-hidden');
      }
    });

    /* Vista expandida al filtrar por categoría específica:
       muestra las 3 imágenes del producto en columnas, no en carrusel */
    if (filter !== 'todos') {
      const matchingCard = document.querySelector(
        `.tienda__card[data-category="${filter}"]`
      );
      if (matchingCard) matchingCard.classList.add('tienda__card--expanded');
    }
  });
});

/* ── Carrusel de imágenes por producto en Tienda ────────────── */
document.querySelectorAll('.tienda__carousel').forEach((carousel) => {
  const track  = carousel.querySelector('.tienda__carousel-track');
  const dots   = carousel.querySelectorAll('.tienda__dot');
  const total  = track.querySelectorAll('img').length;
  let current  = 0;

  function goTo(idx) {
    current = (idx + total) % total;
    track.style.transform = `translateX(-${current * 100}%)`;
    dots.forEach((d, i) => d.classList.toggle('is-active', i === current));
  }

  carousel.querySelector('.js-carousel-prev')
    .addEventListener('click', () => goTo(current - 1));
  carousel.querySelector('.js-carousel-next')
    .addEventListener('click', () => goTo(current + 1));

  dots.forEach((dot) => {
    dot.addEventListener('click', () => goTo(Number(dot.dataset.dot)));
  });
});

/* ── WhatsApp: botones de producto con mensaje pre-cargado ──── */
/* WHATS-001: usa la constante centralizada WHATSAPP_NUMBER      */
document.querySelectorAll('.js-wa-product').forEach((btn) => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    const productName = btn.dataset.product || 'un producto';
    const msg = encodeURIComponent(
      `Hola KOS! 👋 Me interesa el siguiente producto:\n${productName}\n¿Podés darme más info y disponibilidad?`
    );
    const url = `https://wa.me/${WHATSAPP_NUMBER}?text=${msg}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  });
});