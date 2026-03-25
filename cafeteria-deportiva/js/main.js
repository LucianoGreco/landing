/* ============================================================
   KOS COFFEE CORNER — main.js
   F1: FRONT-001 navbar | FRONT-009 rAF parallax | FRONT-017 año
   ============================================================ */

/* ── Año actual en footer ────────────────────────────────────── */
const yearEl = document.querySelector('.footer__year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

/* ── Scroll reveal con IntersectionObserver ─────────────────── */
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
  { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
);

revealEls.forEach((el) => revealObserver.observe(el));

/* ── Smooth scroll para links de navegación ─────────────────── */
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (e) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      /* Cerrar menú mobile si está abierto */
      navMenu.classList.remove('is-open');
      navBurger.classList.remove('is-open');
      navBurger.setAttribute('aria-expanded', 'false');
    }
  });
});

/* ── Parallax con rAF ────────────────────────────────────────── */
/* FRONT-009: cancelAnimationFrame evita acumulación de callbacks */
const hero = document.querySelector('.hero');
let rafId;

if (hero) {
  window.addEventListener('scroll', () => {
    cancelAnimationFrame(rafId);
    rafId = requestAnimationFrame(() => {
      const scrollY = window.scrollY;
      if (scrollY < window.innerHeight) {
        hero.style.backgroundPositionY = `calc(50% + ${scrollY * 0.35}px)`;
      }
    });
  }, { passive: true });
}

/* ── Navbar: clase scrolled + burger ────────────────────────── */
/* FRONT-001 */
const navbar    = document.getElementById('navbar');
const navMenu   = document.getElementById('navMenu');
const navBurger = document.getElementById('navBurger');

/* Opacidad al hacer scroll */
const navScrollThreshold = 60;

window.addEventListener('scroll', () => {
  if (window.scrollY > navScrollThreshold) {
    navbar.classList.add('navbar--scrolled');
  } else {
    navbar.classList.remove('navbar--scrolled');
  }
}, { passive: true });

/* Correr al cargar por si la página ya está scrolleada */
if (window.scrollY > navScrollThreshold) {
  navbar.classList.add('navbar--scrolled');
}

/* Hamburger toggle */
if (navBurger) {
  navBurger.addEventListener('click', () => {
    const isOpen = navMenu.classList.toggle('is-open');
    navBurger.classList.toggle('is-open', isOpen);
    navBurger.setAttribute('aria-expanded', isOpen);
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