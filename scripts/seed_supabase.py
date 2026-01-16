#!/usr/bin/env python3
"""
Script para insertar datos de prueba en Supabase.

Este script crea el perfil de Juan Tello con todos sus enlaces,
usando como referencia el archivo examples/Juan-Tello.py

Uso:
    python3 scripts/seed_supabase.py
"""
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

from sqlalchemy.orm import Session
from src.akitoi.database import SessionLocal, ProfileDB, LinkDB
from src.akitoi.database.utils import get_profile_by_slug


def create_juan_tello_profile(db: Session) -> ProfileDB:
    """
    Crea el perfil de Juan Tello con todos sus datos.

    Args:
        db: Sesión de base de datos

    Returns:
        ProfileDB: El perfil creado
    """
    print("📝 Creando perfil de Juan Tello...")

    # Verificar si el perfil ya existe
    existing_profile = get_profile_by_slug(db, "juan-tello")
    if existing_profile:
        print(f"⚠️  El perfil 'juan-tello' ya existe (ID: {existing_profile.id})")
        print("   Eliminando perfil existente para recrearlo...")
        db.delete(existing_profile)
        db.commit()

    # Generar ID único
    profile_id = str(uuid.uuid4())

    # Crear perfil con tema personalizado
    profile = ProfileDB(
        id=profile_id,
        name="Juan Tello",
        slug="juan-tello",
        bio="AI Educador | Emprendedor | Creador de Contenidos",
        profile_image_url="https://avatars.githubusercontent.com/u/1234567",  # Placeholder
        logo_url=None,
        theme={
            "primary_color": "#10b981",       # Verde
            "background_color": "#ffffff",     # Blanco
            "text_color": "#111827",          # Texto oscuro
            "font_family": "Inter, sans-serif"
        },
        is_published=True,  # Publicado desde el inicio
        view_count=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    print(f"✅ Perfil creado exitosamente!")
    print(f"   ID: {profile.id}")
    print(f"   Slug: {profile.slug}")
    print(f"   Nombre: {profile.name}")
    print()

    return profile


def add_links_to_profile(db: Session, profile_id: str) -> list[LinkDB]:
    """
    Agrega todos los enlaces al perfil de Juan Tello.

    Args:
        db: Sesión de base de datos
        profile_id: ID del perfil

    Returns:
        list[LinkDB]: Lista de enlaces creados
    """
    print("🔗 Agregando enlaces al perfil...")

    # Definir todos los enlaces en orden
    links_data = [
        {
            "type": "whatsapp",
            "url": "https://wa.me/51996780986",
            "label": "Contáctame por WhatsApp",
            "icon": "whatsapp",
            "order": 1
        },
        {
            "type": "email",
            "url": "mailto:juan@lafabricaw.com",
            "label": "Envíame un email",
            "icon": "email",
            "order": 2
        },
        {
            "type": "linkedin",
            "url": "https://www.linkedin.com/in/jftello",
            "label": "LinkedIn",
            "icon": "linkedin",
            "order": 3
        },
        {
            "type": "website",
            "url": "https://aprendeaifacil.com",
            "label": "AI Fácil Academy",
            "icon": "website",
            "order": 4
        },
        {
            "type": "youtube",
            "url": "https://www.youtube.com/@aifacil",
            "label": "YouTube AI Fácil",
            "icon": "youtube",
            "order": 5
        },
        {
            "type": "whatsapp",
            "url": "https://whatsapp.com/channel/0029Va1SG9Y5kg7BvYQcGA3g",
            "label": "Canal WhatsApp AI Fácil",
            "icon": "whatsapp",
            "order": 6
        },
        {
            "type": "tiktok",
            "url": "https://www.tiktok.com/@oraculowebtok",
            "label": "TikTok",
            "icon": "tiktok",
            "order": 7
        },
        {
            "type": "twitter",
            "url": "https://x.com/oraculoweb",
            "label": "X (Twitter)",
            "icon": "twitter",
            "order": 8
        }
    ]

    created_links = []

    for link_data in links_data:
        link = LinkDB(
            id=str(uuid.uuid4()),
            profile_id=profile_id,
            type=link_data["type"],
            url=link_data["url"],
            label=link_data["label"],
            icon=link_data["icon"],
            order=link_data["order"],
            click_count=0,
            created_at=datetime.utcnow()
        )
        db.add(link)
        created_links.append(link)
        print(f"   ✓ {link.label} ({link.type})")

    db.commit()

    print()
    print(f"✅ {len(created_links)} enlaces agregados exitosamente!")
    print()

    return created_links


def print_summary(profile: ProfileDB, links: list[LinkDB]):
    """
    Imprime un resumen del perfil creado.

    Args:
        profile: Perfil creado
        links: Lista de enlaces creados
    """
    print("=" * 60)
    print("📊 RESUMEN DEL PERFIL CREADO")
    print("=" * 60)
    print()
    print(f"👤 Perfil:")
    print(f"   Nombre:       {profile.name}")
    print(f"   Slug:         {profile.slug}")
    print(f"   Bio:          {profile.bio}")
    print(f"   Publicado:    {'Sí' if profile.is_published else 'No'}")
    print(f"   ID:           {profile.id}")
    print()
    print(f"🔗 Enlaces ({len(links)}):")
    for i, link in enumerate(links, 1):
        print(f"   {i}. {link.label}")
        print(f"      Tipo: {link.type}")
        print(f"      URL:  {link.url}")
    print()
    print("🎨 Tema:")
    print(f"   Color primario:  {profile.theme['primary_color']}")
    print(f"   Color de fondo:  {profile.theme['background_color']}")
    print(f"   Color de texto:  {profile.theme['text_color']}")
    print()
    print("=" * 60)
    print("✅ Datos insertados exitosamente en Supabase!")
    print("=" * 60)
    print()
    print("🌐 Próximos pasos:")
    print("   1. Ve a https://app.supabase.com")
    print("   2. Abre tu proyecto 'akitoi'")
    print("   3. Click en 'Table Editor'")
    print("   4. Revisa las tablas 'profiles' y 'links'")
    print()
    print("🚀 Para ver el perfil en la API:")
    print("   1. Ejecuta: ./scripts/run_dev.sh")
    print("   2. Visita: http://localhost:8000/docs")
    print(f"   3. Prueba: GET /api/v1/profiles/{profile.slug}")
    print()


def verify_connection():
    """Verifica la conexión a Supabase antes de empezar."""
    print("🔌 Verificando conexión a Supabase...")

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL no está configurada")
        print("   Asegúrate de tener el archivo .env configurado")
        sys.exit(1)

    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Conexión exitosa a PostgreSQL")
            print(f"   Version: {version.split(',')[0]}")
            print()
    except Exception as e:
        print(f"❌ ERROR: No se pudo conectar a Supabase")
        print(f"   {e}")
        sys.exit(1)


def main():
    """Función principal del script."""
    print()
    print("=" * 60)
    print("🚀 SEED SUPABASE - Insertar Datos de Prueba")
    print("=" * 60)
    print()

    # Verificar conexión
    verify_connection()

    # Crear sesión de base de datos
    db = SessionLocal()

    try:
        # Crear perfil
        profile = create_juan_tello_profile(db)

        # Agregar enlaces
        links = add_links_to_profile(db, profile.id)

        # Imprimir resumen
        print_summary(profile, links)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    main()
