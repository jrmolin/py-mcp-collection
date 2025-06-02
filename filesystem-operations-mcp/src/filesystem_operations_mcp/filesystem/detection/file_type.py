import mimetypes

from magika import Magika


def init_magika() -> Magika:
    m = Magika()

    mime_types = mimetypes.MimeTypes()
    mime_types.add_type("application/yaml", ".yaml")
    mime_types.add_type("application/yaml", ".yml")

    return m
