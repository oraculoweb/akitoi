"""
Generate a standalone HTML demo of the Akitoi Bio Hub.

This script loads a profile from storage and creates a standalone HTML file.
"""

import json
from pathlib import Path

import akitoi
from akitoi import ProfileManager


def generate_html_demo(slug: str, output_path: str = "demo_bio_hub.html"):
    """Generate a standalone HTML demo for a profile."""
    # Initialize manager
    manager = ProfileManager()

    # Get profile
    profile = manager.get_profile_by_slug(slug)

    if not profile:
        print(f"Error: Profile '{slug}' not found")
        return False

    # Load template
    template_path = Path(__file__).parent / "bio_hub_template.html"
    with open(template_path, 'r') as f:
        template = f.read()

    # Prepare profile data
    profile_json = json.dumps({
        'name': profile.name,
        'bio': profile.bio,
        'slug': profile.slug,
        'profile_image_url': profile.profile_image_url,
        'logo_url': profile.logo_url,
        'links': [
            {
                'title': link.title,
                'url': link.url,
                'link_type': link.link_type.value,
                'icon': link.icon,
                'is_active': link.is_active,
                'clicks': link.clicks,
            }
            for link in profile.links
        ],
        'views': profile.views,
    })

    # Replace template variables
    html = template
    html = html.replace('{{name}}', profile.name)
    html = html.replace('{{bio}}', profile.bio or '')
    html = html.replace('{{background_color}}', profile.theme.background_color)
    html = html.replace('{{primary_color}}', profile.theme.primary_color)
    html = html.replace('{{text_color}}', profile.theme.text_color)
    html = html.replace('{{views}}', str(profile.views))
    html = html.replace('{{total_clicks}}', str(profile.get_total_clicks()))
    html = html.replace('{{link_count}}', str(len(profile.links)))
    html = html.replace('{{PROFILE_DATA}}', profile_json)

    # Write to file
    output_file = Path(__file__).parent / output_path
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"✓ HTML demo generated successfully!")
    print(f"  File: {output_file}")
    print(f"\n  Profile: {profile.name}")
    print(f"  Slug: {profile.slug}")
    print(f"  Links: {len(profile.links)}")
    print(f"  Views: {profile.views}")
    print(f"\n  To view: Open {output_file} in your web browser")

    return True


if __name__ == "__main__":
    # Generate demo for juan-tello-4 profile
    generate_html_demo("juan-tello-4", "juan_tello_bio_hub.html")