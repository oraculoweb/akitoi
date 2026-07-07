"""
Crear tu propio perfil personalizado de Akitoi

Instrucciones:
1. Edita los datos entre las líneas marcadas con 👇
2. Guarda el archivo
3. Ejecuta: python3 examples/crear_mi_perfil.py
4. Inicia el servidor: python3 examples/serve_bio_hub.py
5. Abre: http://localhost:8000
"""

from akitoi import ProfileManager, Link, LinkType, Theme


def main():
    # Inicializar manager
    manager = ProfileManager()

    # ============================================================
    # 👇 PERSONALIZA ESTOS DATOS 👇
    # ============================================================

    # Tu información personal
    TU_NOMBRE = "Juan Tello"
    TU_BIO = "Desarrollador Full Stack | Emprendedor Digital | Tech Enthusiast"

    # Tus enlaces de contacto (deja en blanco "" los que no uses)
    TU_WHATSAPP = "+521234567890"  # Formato: +52 para México, +34 para España
    TU_EMAIL = "juantello@email.com"
    TU_LINKEDIN = "https://linkedin.com/in/juantello"
    TU_GITHUB = "https://github.com/juantello"
    TU_TWITTER = "https://twitter.com/juantello"
    TU_WEBSITE = "https://juantello.com"
    TU_INSTAGRAM = "https://instagram.com/juantello"

    # Tu tema de colores (elige uno o personaliza)
    # Opciones: "#6366f1" (Índigo), "#10b981" (Verde), "#f59e0b" (Naranja)
    #           "#ef4444" (Rojo), "#8b5cf6" (Morado), "#06b6d4" (Cyan)
    COLOR_PRINCIPAL = "#6366f1"
    COLOR_FONDO = "#f8fafc"
    COLOR_TEXTO = "#1e293b"

    # ============================================================
    # 👆 HASTA AQUÍ 👆
    # ============================================================

    # Crear tema
    mi_tema = Theme(
        primary_color=COLOR_PRINCIPAL,
        background_color=COLOR_FONDO,
        text_color=COLOR_TEXTO,
        button_style="pill"
    )

    # Crear perfil
    print("\n" + "="*60)
    print("🌟 Creando tu perfil de Akitoi Bio Hub")
    print("="*60 + "\n")

    perfil = manager.create_profile(
        name=TU_NOMBRE,
        bio=TU_BIO,
        theme=mi_tema
    )

    print(f"✅ Perfil creado exitosamente!")
    print(f"   Nombre: {perfil.name}")
    print(f"   Slug: {perfil.slug}")
    print(f"   ID: {perfil.id}\n")

    # Agregar enlaces (solo los que tengas configurados)
    print("📱 Agregando enlaces de contacto...\n")

    enlaces_agregados = 0

    if TU_WHATSAPP:
        manager.add_link(perfil.id, Link(
            title="Contáctame por WhatsApp",
            url=TU_WHATSAPP,
            link_type=LinkType.WHATSAPP
        ))
        print(f"   ✓ WhatsApp: {TU_WHATSAPP}")
        enlaces_agregados += 1

    if TU_EMAIL:
        manager.add_link(perfil.id, Link(
            title="Envíame un email",
            url=TU_EMAIL,
            link_type=LinkType.EMAIL
        ))
        print(f"   ✓ Email: {TU_EMAIL}")
        enlaces_agregados += 1

    if TU_LINKEDIN:
        manager.add_link(perfil.id, Link(
            title="Conéctemos en LinkedIn",
            url=TU_LINKEDIN,
            link_type=LinkType.LINKEDIN
        ))
        print(f"   ✓ LinkedIn: {TU_LINKEDIN}")
        enlaces_agregados += 1

    if TU_GITHUB:
        manager.add_link(perfil.id, Link(
            title="Mis proyectos en GitHub",
            url=TU_GITHUB,
            link_type=LinkType.GITHUB
        ))
        print(f"   ✓ GitHub: {TU_GITHUB}")
        enlaces_agregados += 1

    if TU_TWITTER:
        manager.add_link(perfil.id, Link(
            title="Sígueme en Twitter",
            url=TU_TWITTER,
            link_type=LinkType.TWITTER
        ))
        print(f"   ✓ Twitter: {TU_TWITTER}")
        enlaces_agregados += 1

    if TU_WEBSITE:
        manager.add_link(perfil.id, Link(
            title="Visita mi sitio web",
            url=TU_WEBSITE,
            link_type=LinkType.WEBSITE
        ))
        print(f"   ✓ Website: {TU_WEBSITE}")
        enlaces_agregados += 1

    if TU_INSTAGRAM:
        manager.add_link(perfil.id, Link(
            title="Sígueme en Instagram",
            url=TU_INSTAGRAM,
            link_type=LinkType.INSTAGRAM
        ))
        print(f"   ✓ Instagram: {TU_INSTAGRAM}")
        enlaces_agregados += 1

    # Publicar perfil
    manager.publish_profile(perfil.id)

    print(f"\n✅ Total de enlaces agregados: {enlaces_agregados}")
    print(f"✅ Perfil publicado exitosamente!\n")

    print("="*60)
    print("🚀 Siguiente paso:")
    print("="*60)
    print(f"\n1. Ejecuta el servidor:")
    print(f"   python3 examples/serve_bio_hub.py\n")
    print(f"2. Abre tu navegador en:")
    print(f"   http://localhost:8000/{perfil.slug}\n")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
