# Design Spec: thefriendshipclass.com → GitHub Pages

**Date:** 2026-04-13
**Original site:** https://thefriendshipclass.com/
**Target:** Static GitHub Pages site (plain HTML/CSS/JS)

---

## Context

The current site runs on WordPress with Elementor, WooCommerce, and The Events Calendar plugin. The goal is to recreate it as a static GitHub Pages site — same visual design, same content, same branding — eliminating the WordPress hosting cost and maintenance overhead. Dynamic features (payments, events, contact form) are replaced with lightweight third-party services.

---

## Tech Stack

| Concern | Choice | Reason |
|---|---|---|
| Hosting | GitHub Pages | Free, no server maintenance |
| Framework | Plain HTML/CSS/JS | No build tools, editable in any text editor |
| Fonts | Google Fonts CDN | Playfair Display + Nunito Sans (matches original exactly) |
| Events | Luma or Eventbrite embed | Paste one embed code; events managed externally |
| Contact form | Formspree | Free tier (50/mo); emails go to evolve.with.moni@gmail.com |
| Payments | External links | Stripe Payment Links or Gumroad; no backend needed |
| Images | `images/` folder | Exported from WordPress media library |
| Domain | github.io URL initially | Custom domain (thefriendshipclass.com) via CNAME later |

---

## Typography — Must Match Original

```css
/* Load in every page <head> */
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Nunito+Sans:wght@400;600;700&display=swap" rel="stylesheet">
```

| Use | Font | Weights |
|---|---|---|
| All headings (h1–h4) | Playfair Display | 700, 900 |
| Subheadings, section labels | Playfair Display | 400 |
| Body text, paragraphs | Nunito Sans | 400, 600 |
| Buttons, nav, labels | Nunito Sans | 600, 700 |

---

## Color Palette

| Token | Value | Use |
|---|---|---|
| `--bg` | `#1d1d22` | Page background |
| `--bg-alt` | `#111116` | Alternate section background |
| `--bg-card` | `#1d1d22` | Card backgrounds |
| `--gold` | `#d4af37` | Primary accent, headings, borders |
| `--gold-light` | `#efbe4a` | Hover states, highlights |
| `--text` | `#ffffff` | Primary text |
| `--text-muted` | `#b0b0b0` | Secondary text |
| `--footer-bg` | `#0a0a0d` | Footer background |

---

## File Structure

```
evolveWithMoni/                  ← GitHub repo root
├── index.html                   ← Home
├── about.html                   ← About Moni
├── friendship-class.html        ← Winning In Friendship (5-week class)
├── accountability.html          ← True Accountability Program
├── events.html                  ← Events (Luma/Eventbrite embed)
├── networking.html              ← Networking page
├── packages.html                ← Pricing & Packages
├── testimonials.html            ← Testimonials
├── faq.html                     ← FAQ
├── contact.html                 ← Contact (Formspree form)
├── privacy-policy.html          ← Privacy Policy
├── css/
│   ├── style.css                ← All styles (variables, layout, components)
│   └── animations.css           ← Scroll fade-in and reveal effects
├── js/
│   └── main.js                  ← Nav toggle, FAQ accordion, scroll animations
├── images/                      ← All photos exported from WordPress
│   ├── hero-moni.jpg
│   ├── group-photo.jpg
│   └── ...
├── CNAME                        ← (empty for now; add custom domain later)
└── docs/
    └── superpowers/specs/       ← This file
```

---

## Navigation (shared across all pages)

Sticky top nav, dark background, gold logo text.

```
[✦ Evolve With Moni]    Home  About  Classes ▾  Events  Networking  Packages  Contact
                                       ↓
                              Winning In Friendship
                              True Accountability Program
```

- Hamburger menu on mobile (JS toggle)
- Active page highlighted in gold
- Smooth scroll only on single-page anchors (not used here — separate pages)

---

## Pages

### index.html — Home

Sections in order:
1. **Hero** — full-width, dark bg, Moni photo, tagline ("Your Space for Social Growth and Self-development"), 2 CTA buttons (Join the Journey, Learn More)
2. **About teaser** — 2-column: Moni photo left, bio excerpt right, link to about.html
3. **Featured Offerings** — 3 cards: Winning In Friendship, True Accountability Program, Networking Events
4. **Testimonials strip** — 2–3 quotes, static or CSS auto-scroll
5. **Upcoming Events** — Luma/Eventbrite embed or manual event cards linking to registration
6. **Email/Newsletter CTA** — banner with email input for newsletter signup (separate from contact form; use a Mailchimp embed form or simple Formspree endpoint)
7. **Footer** — nav links, Instagram (@winning.in.friendship), Threads (@winning.in.friendship), evolve.with.moni@gmail.com, Privacy Policy

### about.html — About

- Full Moni bio: "a lover of people, invigorating events, inspiring quotes, dancing & ice cream"
- Speaking background, women's development focus
- Photo of Moni
- Social links (Instagram, Threads)

### friendship-class.html — Winning In Friendship

- Heading: "Winning In Friendship: Make Reliable Friends as an Adult"
- What you'll learn
- 5-week curriculum breakdown
- Group photo (Moni + 8 participants, balloon arch)
- Enrollment CTA button → external payment link (Stripe/Gumroad)

### accountability.html — True Accountability Program

- "Where goals stop living in your head…and start showing up in your life"
- Program structure and community component
- Next cycle start date (kept current manually)
- Join CTA → external payment link

### events.html — Events

- Intro: "Monthly uplifting gatherings designed to inspire, encourage, and build meaningful community"
- **Luma or Eventbrite embed** (single `<iframe>` or `<script>` embed code)
- Past event photo gallery (images from WordPress)

### networking.html — Networking

- Women's connection events description
- Monthly gathering details
- Photo of women in conversation
- Event signup CTA

### packages.html — Packages & Pricing

- R.A.R.E. Friendship Solution branding
- Price cards for each package (content from original /packages/ page)
- "Join the Journey Here!" buttons → external payment links

### testimonials.html — Testimonials

- Grid of testimonial quote cards
- Gold border styling
- Participant names

### faq.html — FAQ

- Accordion-style Q&A
- JS expand/collapse (no library; ~15 lines of vanilla JS)

### contact.html — Contact

- Name, Email, Message fields
- **Formspree** action endpoint (`https://formspree.io/f/XXXXX`) — placeholder; real ID obtained after signing up at formspree.io with evolve.with.moni@gmail.com
- evolve.with.moni@gmail.com displayed as a fallback
- Instagram and Threads links

---

## Shared CSS Architecture (`css/style.css`)

```css
/* 1. CSS custom properties (all tokens at top) */
:root { --bg: #1d1d22; --gold: #d4af37; ... }

/* 2. Reset + base */
/* 3. Typography (Playfair Display headings, Nunito Sans body) */
/* 4. Nav (sticky, mobile hamburger) */
/* 5. Hero section */
/* 6. Cards */
/* 7. Buttons (gold filled, gold outline) */
/* 8. Footer */
/* 9. Utility classes (.gold-text, .section-label, etc.) */
/* 10. Responsive breakpoints (mobile-first) */
```

`css/animations.css` — fade-in on scroll using `IntersectionObserver` (no library).

---

## JavaScript (`js/main.js`)

Three responsibilities only:
1. **Mobile nav toggle** — hamburger open/close
2. **FAQ accordion** — expand/collapse answer panels
3. **Scroll animations** — `IntersectionObserver` adds `.visible` class to elements with `.fade-in`

No external JS libraries. No jQuery.

---

## Deployment

1. Create GitHub repo (e.g. `drishtiwali/evolveWithMoni` or `username/username.github.io`)
2. Push all files to `main` branch
3. GitHub repo Settings → Pages → Source: `main` branch, root `/`
4. Site live at `https://username.github.io/evolveWithMoni/` (or root if named `username.github.io`)
5. Later: add `CNAME` file with `thefriendshipclass.com`, update DNS at domain registrar

---

## Build Script (`build.py`)

Zero-dependency Python 3 script at the repo root. Fetches page content from the WordPress REST API and regenerates the main content area of each HTML file.

### Usage

```bash
python3 build.py                   # sync all mapped pages
python3 build.py --list-slugs      # print all slugs from the API (dry run, no writes)
python3 build.py --page about      # sync one page by slug
```

### How it works

1. Fetches `https://thefriendshipclass.com/wp-json/wp/v2/pages?per_page=100`
2. Matches each page slug to a local HTML file via `SLUG_MAP`
3. Strips Elementor scaffolding from `content.rendered` (`data-elementor-*` attrs, `elementor-*` class tokens)
4. Rewrites internal `thefriendshipclass.com/*` links to local `.html` paths via `LINK_MAP`
5. Replaces the block between `</nav>` and `<footer class="site-footer">` in each file
6. Reports `✓` (updated), `–` (unmapped slug), `✗` (missing file), `⚠` (anchor not found)

### Slug map (confirmed against live site)

| WordPress slug | Local file |
|---|---|
| `home` | `index.html` |
| `about` | `about.html` |
| `winning-in-friendship-class` | `friendship-class.html` |
| `true-accountability-program-community` | `accountability.html` |
| `events` | `events.html` |
| `networking` | `networking.html` |
| `packages` | `packages.html` |
| `testimonials` | `testimonials.html` |
| `frequently-asked-questions` | `faq.html` |
| `contact` | `contact.html` |
| `privacy-policy` | `privacy-policy.html` |

### Adding a new page

1. Add the new WP slug → HTML filename to `SLUG_MAP` in `build.py`
2. Add the WP URL → local filename to `LINK_MAP` if it links internally
3. Create the HTML file with the standard nav + `<footer class="site-footer">` structure
4. Run `python3 build.py --page <slug>`

### Limitations

- Elementor CSS is not included — some layout differences from the live site are expected; fix with minimal overrides in `css/style.css`
- Images load cross-origin from `thefriendshipclass.com`; to host locally, download them and update `src` attributes
- WooCommerce/PHP-rendered pages are not synced (they are out of scope)

---

## Out of Scope

- WooCommerce cart/checkout/my-account pages (replaced by external payment links)
- WordPress-specific pages: products/, products-2/, course-info/, course-info-2/, about1/ (duplicates/WP artifacts)
- Server-side logic of any kind
- CMS or admin interface (content edits = editing HTML files directly)
