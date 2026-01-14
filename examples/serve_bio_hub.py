"""
Simple web server to demonstrate the Akitoi Bio Hub in HTML.

This script loads a profile from storage and serves it as an HTML page.
"""

import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

import akitoi
from akitoi import ProfileManager


class BioHubHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the bio hub."""

    profile_manager = ProfileManager()
    template_path = Path(__file__).parent / "bio_hub_template.html"

    def do_GET(self):
        """Handle GET requests."""
        # Parse the path
        path = self.path.strip('/')

        # Root path - list all profiles
        if not path or path == 'index.html':
            self.serve_index()
        # Profile path
        else:
            # Remove .html extension if present
            slug = path.replace('.html', '')
            self.serve_profile(slug)

    def serve_index(self):
        """Serve an index page with all profiles."""
        profiles = self.profile_manager.list_profiles()
        published_profiles = [p for p in profiles if p.is_published]

        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Akitoi Bio Hub - Profiles</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Inter', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 40px 20px;
                }
                .container {
                    max-width: 900px;
                    width: 100%;
                }
                .header {
                    text-align: center;
                    color: white;
                    margin-bottom: 48px;
                }
                .header h1 {
                    font-size: 48px;
                    margin-bottom: 12px;
                    font-weight: 700;
                }
                .header p {
                    font-size: 18px;
                    opacity: 0.9;
                }
                .profiles-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                    gap: 24px;
                }
                .profile-card {
                    background: white;
                    border-radius: 20px;
                    padding: 32px;
                    text-decoration: none;
                    color: #1e293b;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                }
                .profile-card:hover {
                    transform: translateY(-8px);
                    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
                }
                .profile-card h2 {
                    font-size: 24px;
                    margin-bottom: 8px;
                    font-weight: 600;
                }
                .profile-card .bio {
                    font-size: 14px;
                    color: #64748b;
                    margin-bottom: 16px;
                    line-height: 1.5;
                }
                .profile-card .stats {
                    display: flex;
                    gap: 16px;
                    padding-top: 16px;
                    border-top: 1px solid #e2e8f0;
                }
                .profile-card .stat {
                    flex: 1;
                    text-align: center;
                }
                .profile-card .stat-value {
                    font-size: 20px;
                    font-weight: 700;
                    color: #667eea;
                }
                .profile-card .stat-label {
                    font-size: 11px;
                    color: #94a3b8;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                .empty-state {
                    background: white;
                    border-radius: 20px;
                    padding: 64px 32px;
                    text-align: center;
                    color: #64748b;
                }
                .empty-state h2 {
                    font-size: 24px;
                    margin-bottom: 12px;
                    color: #1e293b;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌟 Akitoi Bio Hub</h1>
                    <p>Your professional contact hub in one place</p>
                </div>
        """

        if published_profiles:
            html += '<div class="profiles-grid">'
            for profile in published_profiles:
                html += f"""
                <a href="/{profile.slug}" class="profile-card">
                    <h2>{profile.name}</h2>
                    <p class="bio">{profile.bio or 'No bio available'}</p>
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-value">{profile.views}</div>
                            <div class="stat-label">Views</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{profile.get_total_clicks()}</div>
                            <div class="stat-label">Clicks</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">{len(profile.links)}</div>
                            <div class="stat-label">Links</div>
                        </div>
                    </div>
                </a>
                """
            html += '</div>'
        else:
            html += """
            <div class="empty-state">
                <h2>No Profiles Yet</h2>
                <p>Run the basic_usage.py example to create your first profile!</p>
            </div>
            """

        html += """
            </div>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_profile(self, slug: str):
        """Serve a profile page."""
        # Get profile by slug
        profile = self.profile_manager.get_profile_by_slug(slug)

        if not profile:
            self.send_error(404, f"Profile not found: {slug}")
            return

        if not profile.is_published:
            self.send_error(403, "Profile is not published")
            return

        # Record view
        self.profile_manager.record_view(slug)

        # Load template
        with open(self.template_path, 'r') as f:
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

        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        """Custom log message format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=8000):
    """Run the web server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, BioHubHandler)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   🌟 Akitoi Bio Hub Server is running!                  ║
║                                                          ║
║   Open your browser and visit:                          ║
║   → http://localhost:{port}                               ║
║                                                          ║
║   Press Ctrl+C to stop the server                       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped.")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()
