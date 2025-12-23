"""
Basic usage example for Akitoi platform.

This example demonstrates how to create a bio hub profile,
add contact links, and retrieve analytics.
"""

import akitoi
from akitoi import ProfileManager, Link, LinkType, Theme, URLShortener


def main():
    """Run basic usage example."""
    print("=== Akitoi Bio Hub Example ===\n")

    # Initialize manager
    manager = ProfileManager()

    # Create a custom theme
    theme = Theme(
        primary_color="#6366f1",
        background_color="#f8fafc",
        text_color="#1e293b",
        button_style="pill"
    )

    # Create profile
    print("Creating profile...")
    profile = manager.create_profile(
        name="Maria Garcia",
        bio="Digital Marketing Expert | Content Creator | Tech Enthusiast",
        theme=theme
    )
    print(f"✓ Profile created with slug: {profile.slug}")
    print(f"  Profile ID: {profile.id}\n")

    # Add contact links
    print("Adding contact links...")
    links = [
        Link(
            title="Chat on WhatsApp",
            url="+34612345678",
            link_type=LinkType.WHATSAPP
        ),
        Link(
            title="Send me an email",
            url="maria@example.com",
            link_type=LinkType.EMAIL
        ),
        Link(
            title="LinkedIn Profile",
            url="https://linkedin.com/in/mariagarcia",
            link_type=LinkType.LINKEDIN
        ),
        Link(
            title="Portfolio Website",
            url="https://mariagarcia.com",
            link_type=LinkType.WEBSITE
        ),
        Link(
            title="Twitter/X",
            url="https://x.com/mariagarcia",
            link_type=LinkType.TWITTER
        ),
        Link(
            title="AI Assistant",
            url="https://chat.example.com/maria-ai",
            link_type=LinkType.AI_AGENT
        ),
    ]

    for link in links:
        manager.add_link(profile.id, link)
        print(f"  ✓ Added: {link.title}")

    print()

    # Publish profile
    print("Publishing profile...")
    manager.publish_profile(profile.id)
    print("✓ Profile is now public\n")

    # Generate URLs
    print("Generating URLs...")
    shortener = URLShortener(base_url="https://akitoi.bio")

    profile_url = shortener.get_profile_url(profile.slug)
    short_url = shortener.get_short_url(profile.slug)

    print(f"  Profile URL: {profile_url}")
    print(f"  Short URL: {short_url}\n")

    # Simulate user interactions
    print("Simulating user interactions...")
    manager.record_view(profile.slug)
    manager.record_view(profile.slug)
    manager.record_view(profile.slug)

    manager.record_link_click(profile.slug, 0)  # WhatsApp
    manager.record_link_click(profile.slug, 0)  # WhatsApp
    manager.record_link_click(profile.slug, 2)  # LinkedIn

    print("✓ Recorded 3 views and 3 link clicks\n")

    # Display analytics
    print("=== Analytics ===")
    updated_profile = manager.get_profile_by_slug(profile.slug)

    print(f"Profile: {updated_profile.name}")
    print(f"Views: {updated_profile.views}")
    print(f"Total link clicks: {updated_profile.get_total_clicks()}")
    print(f"\nLink breakdown:")

    for i, link in enumerate(updated_profile.links):
        print(f"  {i+1}. {link.title}: {link.clicks} clicks")

    print("\n=== Profile Summary ===")
    print(f"Name: {updated_profile.name}")
    print(f"Slug: {updated_profile.slug}")
    print(f"Bio: {updated_profile.bio}")
    print(f"Published: {updated_profile.is_published}")
    print(f"Links: {len(updated_profile.links)}")
    print(f"Theme: {updated_profile.theme.primary_color}")
    print(f"Created: {updated_profile.created_at.strftime('%Y-%m-%d %H:%M')}")

    print("\n✓ Example completed successfully!")


if __name__ == "__main__":
    main()
