#!/usr/bin/env python
"""
Seed a fictitious club so the demo runs end to end.

Creates (idempotently) "Club Andino Demo" in the SAME JSON org storage
the local API uses (.akitoi_data/orgs), imports a 5-member roster,
links the demo admin as owner, and prints everything the demo needs:
the admin token for the panel login and the card links.

Usage:
    python scripts/seed_demo_club.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from akitoi import OrganizationManager  # noqa: E402
from akitoi.core.roster import import_roster, parse_roster_file  # noqa: E402
from make_demo_token import DEMO_USER_ID, make_token  # noqa: E402

SLUG = "club-andino-demo"
FRONTEND = "http://localhost:3000"

ROSTER = """nombre,email,telefono,rol,estado,valid_until
Ana Pérez,ana@demo.akitoi,+51911222333,socio,vigente,2027-12-31
Luis Gómez,luis@demo.akitoi,+51922333444,directivo,vigente,2027-12-31
Rosa Díaz,rosa@demo.akitoi,,socio,vigente,2027-06-30
Carlos Ruiz,carlos@demo.akitoi,,socio,suspendido,2027-12-31
María Torres,maria@demo.akitoi,,socio,vencido,2025-12-31
"""


def main() -> None:
    manager = OrganizationManager()  # default storage: .akitoi_data/orgs

    org = manager.get_organization_by_slug(SLUG)
    if org is None:
        org = manager.create_organization(
            name="Club Andino Demo",
            owner_profile_id="demo-owner",
            slug=SLUG,
        )
        print(f"✔ Club creado: {org.name} ({org.id})")
    else:
        print(f"✔ Club ya existía: {org.name} ({org.id})")

    manager.add_admin(org.id, DEMO_USER_ID, role="owner")
    print(f"✔ Admin vinculado: {DEMO_USER_ID}")

    rows = parse_roster_file("padron-demo.csv", ROSTER.encode("utf-8"))
    log = import_roster(manager.storage, org.id, rows, filename="padron-demo.csv")
    print(
        f"✔ Padrón importado: {log.created} creados, {log.updated} "
        f"actualizados, {log.deactivated} bajas, {log.error_count} errores"
    )

    print("\n=== PARA LA DEMO ===")
    print(f"1) Panel admin:  {FRONTEND}/admin")
    print("2) Token de login (modo demo local, pégalo en el panel):\n")
    print(make_token())
    print("\n3) Carnets (VISTA 2):")
    for member in manager.list_members(org.id):
        card = manager.issue_card(member.id, FRONTEND)
        token = card["verify_url"].rsplit("/", 1)[-1]
        print(f"   {member.name:15s} -> {FRONTEND}/card/{token[:32]}…")
    print("\n(las URLs completas de carnet se emiten desde el panel con el botón Carnet)")


if __name__ == "__main__":
    main()
