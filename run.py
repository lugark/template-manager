#!/usr/bin/env python3
"""
Run script for the Lasercut Manager application.
"""

import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_dir))

if __name__ == '__main__':
    from main import create_app
    
    app = create_app()
    print("🧩 Lasercut Manager starting...")
    print("📁 Data directory: data/")
    print("🖼️  Thumbnails directory: app/static/thumbnails/")
    print("🌐 Web interface: http://localhost:8080")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=8081, debug=True)
