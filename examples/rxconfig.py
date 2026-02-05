"""Reflex config for the demo app."""
import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="demo_app",
    plugins=[SitemapPlugin()],
)
