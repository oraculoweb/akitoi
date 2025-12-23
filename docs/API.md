# Akitoi API Documentation

## Overview

Akitoi provides a simple, pythonic API for creating and managing bio hub profiles.

## Quick Start

```python
import akitoi

# Create a profile
profile = akitoi.create_profile(
    name="John Doe",
    slug="johndoe",  # Optional: auto-generated if not provided
    bio="Software Developer & Tech Enthusiast"
)

# Add links
from akitoi import Link, LinkType

whatsapp = Link(
    title="Chat on WhatsApp",
    url="+34123456789",
    link_type=LinkType.WHATSAPP
)

# Get ProfileManager for advanced operations
manager = akitoi.ProfileManager()
manager.add_link(profile.id, whatsapp)

# Retrieve profile
retrieved = akitoi.get_profile("johndoe")
```

## Core Classes

### Profile

Represents a bio hub profile.

**Attributes:**
- `id` (str): Unique identifier
- `slug` (str): URL-friendly identifier
- `name` (str): Display name
- `bio` (str): Biography text
- `profile_image_url` (str, optional): URL to profile image
- `logo_url` (str, optional): URL to logo
- `theme` (Theme): Visual theme configuration
- `links` (List[Link]): Contact links
- `is_published` (bool): Publication status
- `views` (int): Total profile views
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

**Methods:**
- `add_link(link)`: Add a link to the profile
- `remove_link(index)`: Remove a link by index
- `increment_views()`: Increment view counter
- `publish()`: Make profile public
- `unpublish()`: Make profile private
- `to_dict()`: Export to dictionary
- `from_dict(data)`: Import from dictionary

### Link

Represents a contact link.

**Attributes:**
- `title` (str): Display title
- `url` (str): URL or contact information
- `link_type` (LinkType): Type of link
- `icon` (str, optional): Icon/emoji
- `is_active` (bool): Visibility status
- `position` (int): Display order
- `clicks` (int): Click counter

**Link Types:**
- `WHATSAPP`: WhatsApp chat link
- `EMAIL`: Email address
- `WEBSITE`: Website URL
- `LINKEDIN`: LinkedIn profile
- `TWITTER`: Twitter/X profile
- `INSTAGRAM`: Instagram profile
- `FACEBOOK`: Facebook profile
- `GITHUB`: GitHub profile
- `YOUTUBE`: YouTube channel
- `TIKTOK`: TikTok profile
- `LLM_PROFILE`: LLM user profile
- `AI_AGENT`: AI Agent link
- `CUSTOM`: Custom link

**Methods:**
- `increment_clicks()`: Increment click counter
- `to_dict()`: Export to dictionary
- `from_dict(data)`: Import from dictionary

### Theme

Visual theme configuration.

**Attributes:**
- `primary_color` (str): Primary color (hex)
- `background_color` (str): Background color (hex)
- `text_color` (str): Text color (hex)
- `button_style` (str): Button style ('rounded', 'square', 'pill')
- `font_family` (str): Font family

**Methods:**
- `to_dict()`: Export to dictionary
- `from_dict(data)`: Import from dictionary

## ProfileManager

Main interface for profile operations.

### Creating Profiles

```python
from akitoi import ProfileManager, Theme

manager = ProfileManager()

# Basic profile
profile = manager.create_profile(
    name="Jane Doe",
    slug="janedoe",
    bio="Product Manager"
)

# With custom theme
theme = Theme(
    primary_color="#ff6b6b",
    background_color="#1a1a2e",
    text_color="#eaeaea"
)

profile = manager.create_profile(
    name="Tech Company",
    bio="Innovative solutions",
    theme=theme,
    logo_url="https://example.com/logo.png"
)
```

### Retrieving Profiles

```python
# By ID
profile = manager.get_profile(profile_id)

# By slug
profile = manager.get_profile_by_slug("janedoe")

# List all profiles
profiles = manager.list_profiles()
```

### Updating Profiles

```python
# Update basic info
manager.update_profile(
    profile_id,
    name="Jane Smith",
    bio="Senior Product Manager"
)

# Update theme
new_theme = Theme(primary_color="#007bff")
manager.update_theme(profile_id, new_theme)
```

### Managing Links

```python
from akitoi import Link, LinkType

# Add link
email_link = Link(
    title="Email Me",
    url="jane@example.com",
    link_type=LinkType.EMAIL
)
manager.add_link(profile_id, email_link)

# Remove link (by index)
manager.remove_link(profile_id, 0)
```

### Publishing

```python
# Publish profile (make public)
manager.publish_profile(profile_id)

# Unpublish profile (make private)
manager.unpublish_profile(profile_id)
```

### Analytics

```python
# Record profile view
manager.record_view(slug)

# Record link click
manager.record_link_click(slug, link_index)

# Get analytics
profile = manager.get_profile_by_slug(slug)
print(f"Views: {profile.views}")
print(f"Total clicks: {profile.get_total_clicks()}")

for link in profile.links:
    print(f"{link.title}: {link.clicks} clicks")
```

## URLShortener

Utilities for URL shortening and QR code generation.

```python
from akitoi import URLShortener

shortener = URLShortener(base_url="https://akitoi.bio")

# Get profile URL
url = shortener.get_profile_url("johndoe")
# Returns: https://akitoi.bio/johndoe

# Get short URL
short_url = shortener.get_short_url("johndoe")
# Returns: https://akitoi.bio/s/abc123

# Generate QR code data
qr_data = shortener.generate_qr_data("johndoe")

# Create WhatsApp URL
whatsapp_url = URLShortener.create_whatsapp_url(
    phone="+34123456789",
    message="Hello from Akitoi!"
)

# Create email URL
email_url = URLShortener.create_email_url(
    email="contact@example.com",
    subject="Contact from Akitoi",
    body="Hi there!"
)
```

## Complete Example

```python
import akitoi
from akitoi import ProfileManager, Link, LinkType, Theme

# Initialize manager
manager = ProfileManager()

# Create profile with custom theme
theme = Theme(
    primary_color="#6366f1",
    background_color="#ffffff",
    button_style="pill"
)

profile = manager.create_profile(
    name="Alex Rodriguez",
    slug="alexrod",
    bio="Digital Marketing Expert | Content Creator",
    profile_image_url="https://example.com/alex.jpg",
    theme=theme
)

# Add contact links
links = [
    Link(
        title="📱 WhatsApp",
        url="+34612345678",
        link_type=LinkType.WHATSAPP
    ),
    Link(
        title="✉️ Email",
        url="alex@example.com",
        link_type=LinkType.EMAIL
    ),
    Link(
        title="💼 LinkedIn",
        url="https://linkedin.com/in/alexrod",
        link_type=LinkType.LINKEDIN
    ),
    Link(
        title="🌐 Portfolio",
        url="https://alexrodriguez.com",
        link_type=LinkType.WEBSITE
    ),
    Link(
        title="🤖 AI Assistant",
        url="https://chat.example.com/alexai",
        link_type=LinkType.AI_AGENT
    ),
]

for link in links:
    manager.add_link(profile.id, link)

# Publish profile
manager.publish_profile(profile.id)

# Generate URLs
from akitoi import URLShortener
shortener = URLShortener()

profile_url = shortener.get_profile_url(profile.slug)
print(f"Profile URL: {profile_url}")

# Simulate user interaction
manager.record_view(profile.slug)
manager.record_link_click(profile.slug, 0)  # WhatsApp click

# Get analytics
updated_profile = manager.get_profile_by_slug(profile.slug)
print(f"Views: {updated_profile.views}")
print(f"Total link clicks: {updated_profile.get_total_clicks()}")
```

## Storage

By default, Akitoi uses JSON file storage. You can specify a custom storage path:

```python
from akitoi.storage.json_storage import JSONStorage

storage = JSONStorage(storage_path="./my_data")
manager = ProfileManager(storage=storage)
```

## Validation

Akitoi includes built-in validators:

```python
from akitoi.utils.validators import (
    validate_slug,
    validate_email,
    validate_url,
    validate_whatsapp,
    sanitize_slug
)

# Validate slug
is_valid = validate_slug("john-doe")  # True

# Sanitize user input
clean_slug = sanitize_slug("John Doe!")  # "john-doe"

# Validate email
is_valid_email = validate_email("user@example.com")  # True
```

## Error Handling

```python
try:
    profile = manager.create_profile(name="Test", slug="invalid slug!")
except ValueError as e:
    print(f"Invalid input: {e}")

try:
    profile = manager.create_profile(name="Test", slug="existing-slug")
except ValueError as e:
    print(f"Slug already exists: {e}")
```

## Best Practices

1. **Use auto-generated slugs** when possible to avoid conflicts
2. **Validate user input** before creating profiles
3. **Sanitize slugs** from user-provided names
4. **Publish profiles** only after adding content
5. **Track analytics** to understand user engagement
6. **Use appropriate link types** for better UX and icons
7. **Keep themes consistent** with brand identity

## Next Steps

- [Setup Guide](../README.md#installation)
- [Contributing Guide](CONTRIBUTING.md)
- [Examples](../examples/)
