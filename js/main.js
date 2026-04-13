/* ── Nav toggle ───────────────────────────────────── */
const navToggle = document.getElementById('nav-toggle');
const navLinks  = document.getElementById('nav-links');

if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
  });
}

// Close nav on link click (mobile)
document.querySelectorAll('.nav-links a').forEach(link => {
  link.addEventListener('click', () => navLinks?.classList.remove('open'));
});

// Mobile dropdown toggle
document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
  toggle.addEventListener('click', () => {
    if (window.innerWidth <= 768) {
      toggle.closest('.has-dropdown').classList.toggle('open');
      const isOpen = toggle.closest('.has-dropdown').classList.contains('open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    }
  });
});

/* ── Active nav link ──────────────────────────────── */
const currentPage = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav-links a').forEach(link => {
  if (link.getAttribute('href') === currentPage) {
    link.classList.add('active');
  }
});

/* ── FAQ accordion ────────────────────────────────── */
document.querySelectorAll('.accordion-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const body = btn.nextElementSibling;
    if (!body) return;
    const isOpen = btn.classList.contains('open');
    // Close all
    document.querySelectorAll('.accordion-btn').forEach(b => {
      b.classList.remove('open');
      b.nextElementSibling?.classList.remove('open');
    });
    // Open clicked (unless it was already open)
    if (!isOpen) {
      btn.classList.add('open');
      body.classList.add('open');
    }
  });
});

/* ── Scroll fade-in ───────────────────────────────── */
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
