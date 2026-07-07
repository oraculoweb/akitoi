"""
Minimal mobile-first HTML page for a public hub.

Server-rendered, zero build step, self-contained (inline CSS/JS).
This is the MVP surface a visitor sees when scanning a QR or tapping
an NFC tag. It only exposes public data from the ContactCard plus
active links, and offers:
- "Guardar contacto" (.vcf -> native contact book)
- "Compartir" via the Web Share API (native share sheet on mobile)
- QR for re-sharing person-to-person
- The contact assistant form (intermediary messaging)
"""
from string import Template

from ..models.profile import Profile
from ..models.link import Link, LinkType

_BUTTON_RADIUS = {"rounded": "14px", "square": "4px", "pill": "999px"}

_PAGE = Template("""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$name · Akitoi</title>
<style>
*{box-sizing:border-box;margin:0}
body{font-family:$font;background:$bg;color:$text;display:flex;justify-content:center;min-height:100vh}
main{width:100%;max-width:430px;padding:28px 22px;text-align:center}
.logo{max-height:42px;margin:0 auto 6px;display:block}
.avatar{width:96px;height:96px;border-radius:50%;object-fit:cover;margin:10px auto;display:block;border:3px solid $primary}
h1{font-size:1.45rem;margin-top:6px}
.summary{opacity:.8;font-size:.95rem;margin:8px 0 20px}
.actions{display:flex;gap:10px;margin:16px 0}
.actions a,.actions button{flex:1;padding:12px;border-radius:$radius;border:2px solid $primary;background:transparent;color:$primary;font:inherit;font-weight:600;text-decoration:none;cursor:pointer}
.links a{display:block;margin:10px 0;padding:14px;border-radius:$radius;background:$primary;color:#fff;text-decoration:none;font-weight:600}
.qr{margin:20px auto 4px;width:160px;height:160px}
.qr-hint{font-size:.75rem;opacity:.55}
form{margin-top:24px;text-align:left;border-top:1px solid rgba(128,128,128,.25);padding-top:18px}
form strong{display:block;text-align:center;margin-bottom:8px}
input,textarea{width:100%;padding:11px;margin:5px 0;border:1px solid rgba(128,128,128,.4);border-radius:10px;font:inherit;background:transparent;color:inherit}
form button{width:100%;padding:13px;margin-top:6px;border:none;border-radius:$radius;background:$primary;color:#fff;font:inherit;font-weight:600;cursor:pointer}
.form-msg{font-size:.85rem;margin-top:8px;text-align:center}
.hp{position:absolute;left:-9999px}
footer{margin-top:28px;font-size:.75rem;opacity:.5}
</style>
</head>
<body>
<main>
$logo_html
$avatar_html
<h1>$name</h1>
<p class="summary">$summary</p>
<div class="actions">
  <a href="$vcf_url" download="$slug.vcf">&#128190; Guardar contacto</a>
  <button id="share-btn" type="button">&#128228; Compartir</button>
</div>
<nav class="links">
$links_html
</nav>
<img class="qr" src="$qr_url" alt="Código QR del perfil">
<p class="qr-hint">Escanea el QR para guardar este contacto</p>
<form id="contact-form" action="$contact_url" method="post">
  <strong>&#129302; Asistente de contacto</strong>
  <input name="sender_name" placeholder="Tu nombre" maxlength="80" required>
  <input name="sender_contact" placeholder="Tu email o teléfono" maxlength="120" required>
  <textarea name="message" rows="3" placeholder="Escribe tu mensaje" maxlength="500" required></textarea>
  <input class="hp" name="company" tabindex="-1" autocomplete="off">
  <button type="submit">Enviar al asistente</button>
  <p class="form-msg" id="form-msg"></p>
</form>
<footer>Creado con Akitoi · akitoi.bio</footer>
</main>
<script>
var shareBtn = document.getElementById('share-btn');
shareBtn.addEventListener('click', function () {
  if (navigator.share) {
    navigator.share({ title: document.title, url: location.href });
  } else {
    navigator.clipboard.writeText(location.href);
    shareBtn.textContent = '\\u2714 Enlace copiado';
  }
});
document.getElementById('contact-form').addEventListener('submit', function (e) {
  e.preventDefault();
  var form = e.target;
  var data = {};
  new FormData(form).forEach(function (v, k) { data[k] = v; });
  fetch(form.action, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then(function (r) {
    var msg = document.getElementById('form-msg');
    if (r.ok) { msg.textContent = '\\u2714 Mensaje enviado. Te responderán pronto.'; form.reset(); }
    else { msg.textContent = '\\u2716 No se pudo enviar. Inténtalo de nuevo.'; }
  });
});
</script>
</body>
</html>
""")


def resolve_link_target(link: Link) -> str:
    """Turn a link's raw value into a tappable href."""
    url = link.url
    if link.link_type == LinkType.WHATSAPP and not url.startswith("http"):
        return "https://wa.me/" + "".join(ch for ch in url if ch.isdigit())
    if link.link_type == LinkType.EMAIL and "@" in url and not url.startswith("mailto:"):
        return f"mailto:{url}"
    return url


def render_profile_page(profile: Profile, summary: str, path_prefix: str) -> str:
    """
    Render the mobile hub page for a published profile.

    Args:
        profile: The profile to render (must be published)
        summary: Privacy-filtered short summary (from ContactCard)
        path_prefix: URL prefix for the mobile endpoints (e.g. "/m/slug")
    """
    theme = profile.theme
    links_html = "\n".join(
        '<a href="{href}" rel="noopener">{icon} {title}</a>'.format(
            href=_html_escape_attr(resolve_link_target(link)),
            icon=link.icon or "",
            title=_html_escape(link.title),
        )
        for link in profile.get_active_links()
    )

    avatar_html = (
        f'<img class="avatar" src="{_html_escape_attr(profile.profile_image_url)}" alt="Foto de {_html_escape(profile.name)}">'
        if profile.profile_image_url
        else ""
    )
    logo_html = (
        f'<img class="logo" src="{_html_escape_attr(profile.logo_url)}" alt="Logo">'
        if profile.logo_url
        else ""
    )

    return _PAGE.substitute(
        name=_html_escape(profile.name),
        slug=profile.slug,
        summary=_html_escape(summary),
        font=theme.font_family,
        bg=theme.background_color,
        text=theme.text_color,
        primary=theme.primary_color,
        radius=_BUTTON_RADIUS.get(theme.button_style, "14px"),
        links_html=links_html,
        avatar_html=avatar_html,
        logo_html=logo_html,
        vcf_url=f"{path_prefix}/vcard",
        qr_url=f"{path_prefix}/qr.svg",
        contact_url=f"{path_prefix}/contact",
    )


def _html_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _html_escape_attr(value: str) -> str:
    return _html_escape(value).replace('"', "&quot;")
