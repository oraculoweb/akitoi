"""
Mi perfil personalizado de Akitoi
"""

from akitoi import ProfileManager, Link, LinkType, Theme

def main():
    # Inicializar manager
    manager = ProfileManager()

    # Crear tu tema personalizado
    mi_tema = Theme(
        primary_color="#10b981",      # Color verde (cámbialo al que quieras)
        background_color="#ffffff",    # Fondo blanco
        text_color="#111827",         # Texto oscuro
        button_style="pill"           # Estilo de botones
    )

    # Crear tu perfil CON TUS DATOS
    perfil = manager.create_profile(
        name="Juan Tello",  # 👈 TU NOMBRE
        bio="AI Educador| Emprendedor | Creador de Contenidos",  # 👈 TU BIO
        theme=mi_tema
    )
    
    print(f"✓ Perfil creado: {perfil.slug}")
    print(f"  ID: {perfil.id}\n")

    # Agregar TUS enlaces
    print("Agregando enlaces...")
    
    manager.add_link(perfil.id, Link(
        title="Contáctame por WhatsApp",
        url="+51996780986",  # 👈 TU NÚMERO (formato internacional)
        link_type=LinkType.WHATSAPP
    ))
    
    manager.add_link(perfil.id, Link(
        title="Envíame un email",
        url="juan@lafabricaw.com",  # 👈 TU EMAIL
        link_type=LinkType.EMAIL
    ))
    
    manager.add_link(perfil.id, Link(
        title="LinkedIn",
        url="https://www.linkedin.com/in/jftello",  # 👈 TU LINKEDIN
        link_type=LinkType.LINKEDIN
    ))

    manager.add_link(perfil.id, Link(
        title="Ai Facil academy",
        url="https://aprendeaifacil.com",  # 👈 TU SITIO WEB
        link_type=LinkType.WEBSITE
    ))

    manager.add_link(perfil.id, Link(
        title="Youtube AI Facil",
        url="https://www.youtube.com/@aifacil",  # 👈 TU YOUTUBE
        link_type=LinkType.YOUTUBE
    ))

    manager.add_link(perfil.id, Link(
        title="WhatsApp canal AI Facil",
        url="https://whatsapp.com/channel/0029Va1SG9Y5kg7BvYQcGA3g",  # 👈 AI Facil WhatsApp
        link_type=LinkType.WHATSAPP
    ))

    manager.add_link(perfil.id, Link(
        title="TikTok",
        url="https://www.tiktok.com/@oraculowebtok",  # 👈 TU TIKTOK
        link_type=LinkType.TIKTOK
    ))

    manager.add_link(perfil.id, Link(
        title="X",
        url="https://x.com/oraculoweb",  # 👈 TU X
        link_type=LinkType.TWITTER
    ))

    # Publicar el perfil
    manager.publish_profile(perfil.id)
    print("\n✓ Perfil publicado exitosamente!")
    print(f"  Accede en: http://localhost:8000/{perfil.slug}")

if __name__ == "__main__":
    main()
