# Akitoi Bio Hub - HTML Demo

This directory contains a complete HTML demonstration of the Akitoi Bio Hub platform.

## 📁 Files

### `maria_garcia_bio_hub.html`
**Ready-to-use standalone demo** - Just open this file in any web browser!

This is a complete, working example of a bio hub page with:
- Modern, responsive design
- 6 contact links (WhatsApp, Email, LinkedIn, Website, Twitter, AI Assistant)
- Analytics stats display
- Smooth animations and hover effects
- Custom indigo theme

### `bio_hub_template.html`
The master template used to generate bio hub pages. Contains:
- Responsive CSS styling
- JavaScript for dynamic rendering
- Template variables ({{name}}, {{bio}}, etc.)
- Animation and interaction logic

### `serve_bio_hub.py`
Python HTTP server to demonstrate the full platform:
```bash
python examples/serve_bio_hub.py
```
Then visit: http://localhost:8000

Features:
- Index page listing all profiles
- Individual profile pages by slug
- Automatic view tracking
- Profile data loaded from storage

### `generate_html_demo.py`
Utility script to create standalone HTML demos:
```bash
python examples/generate_html_demo.py
```
Generates a shareable HTML file from any profile in storage.

## 🚀 Quick Start

### Option 1: View the Demo (Easiest)
Simply open `maria_garcia_bio_hub.html` in your web browser.

### Option 2: Run the Web Server
```bash
# Install the package first
pip install -e .

# Create sample data (if not already done)
python examples/basic_usage.py

# Start the server
python examples/serve_bio_hub.py

# Open browser to http://localhost:8000
```

### Option 3: Generate Your Own
```bash
# Create a profile first
python examples/basic_usage.py

# Generate HTML demo
python examples/generate_html_demo.py

# Open the generated HTML file
```

## 🎨 Features Demonstrated

### Design
- ✅ Modern, clean interface
- ✅ Responsive layout (mobile, tablet, desktop)
- ✅ Custom theming (colors, fonts)
- ✅ Smooth animations and transitions
- ✅ Professional typography (Inter font)

### Functionality
- ✅ Dynamic link rendering
- ✅ WhatsApp click-to-chat integration
- ✅ Email mailto links
- ✅ Social media links
- ✅ Analytics stats display
- ✅ Click tracking (console logging)

### User Experience
- ✅ Fast loading
- ✅ No dependencies (standalone HTML)
- ✅ Accessible design
- ✅ Touch-friendly buttons
- ✅ Hover effects and visual feedback

## 📱 Sample Profile: Maria Garcia

The demo showcases a complete bio hub for "Maria Garcia":
- **Name**: Maria Garcia
- **Bio**: Digital Marketing Expert | Content Creator | Tech Enthusiast
- **Theme**: Indigo (#6366f1) with light background
- **Links**: 6 professional contact methods

## 🛠️ Customization

To create your own bio hub:

1. **Create a profile** using the Python API:
```python
from akitoi import ProfileManager, Theme, Link, LinkType

manager = ProfileManager()
profile = manager.create_profile(
    name="Your Name",
    bio="Your bio here",
    theme=Theme(primary_color="#6366f1")
)

manager.add_link(profile.id, Link(
    title="Contact Me",
    url="your-url",
    link_type=LinkType.WHATSAPP
))
```

2. **Generate HTML**:
```bash
python examples/generate_html_demo.py
```

3. **Share** the generated HTML file!

## 🌐 Browser Compatibility

The HTML demo works in all modern browsers:
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 📊 What's Tracked

The demo includes basic analytics:
- **Views**: Number of times the page is visited
- **Clicks**: Number of times links are clicked
- **Links**: Total number of contact links

In production, these would be tracked server-side.

## 🎯 Next Steps

Want to build your own Akitoi platform? Check out:
- `../README.md` - Main project documentation
- `basic_usage.py` - API usage examples
- `../src/akitoi/` - Core platform code

---

**Tip**: You can deploy `maria_garcia_bio_hub.html` to any static hosting service (GitHub Pages, Netlify, Vercel) and it will work immediately - no server needed!