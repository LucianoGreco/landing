const config = window.APP_CONFIG;

document.querySelector('.hero__title').textContent = config.hero.title;
document.querySelector('.hero__sub').textContent = config.hero.subtitle;

document.querySelector('.fab-whatsapp').href =
  `https://wa.me/${config.contact.whatsapp}`;

const menuContainer = document.querySelector('.menu-grid');

menuContainer.innerHTML = config.menu.map(item => `
  <div class="menu-card">
    <h3>${item.name}</h3>
    <p>${item.description}</p>
    <span>$${item.price}</span>
  </div>
`).join('');
