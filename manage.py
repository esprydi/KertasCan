#!/usr/bin/env python
import os
import sys

# === MONKEYPATCH UNTUK PYTHON-BIDI (Fix EasyOCR on Python 3.13) ===
import bidi
try:
    from bidi import algorithm
    if not hasattr(bidi, 'get_display'):
        bidi.get_display = algorithm.get_display
except ImportError:
    pass
# ==================================================================

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kertascan_project.settings')
    try:
        # pyrefly: ignore [missing-import]
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # DEFAULT PORT SETTING
    # Jika Anda ingin mengubah port default secara permanen, ganti '8000' di bawah:
    if len(sys.argv) == 2 and sys.argv[1] == 'runserver':
        sys.argv.append('8000') 
        
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
