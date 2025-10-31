#!/usr/bin/env python3
"""
Lasercut Manager - Main Flask Application
A lightweight Digital Asset Management system for lasercut templates.
"""

import os
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from scanner import FileScanner
from models import db, Asset, Tag

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Ensure database directory exists
    db_dir = Path('app/db')
    db_dir.mkdir(parents=True, exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{db_dir.absolute()}/data.sqlite'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")
    
    # Initialize file scanner
    scanner = FileScanner()
    
    @app.route('/')
    def index():
        """Main page showing all assets with optional tag filtering."""
        tag_filter = request.args.get('tag', '')
        
        query = Asset.query
        if tag_filter:
            query = query.filter(Asset.tags.any(Tag.name.ilike(f'%{tag_filter}%')))
        
        assets = query.order_by(Asset.created_at.desc()).all()
        all_tags = Tag.query.order_by(Tag.name).all()
        
        return render_template('index.html', 
                             assets=assets, 
                             all_tags=all_tags, 
                             current_tag=tag_filter)
    
    @app.route('/scan')
    def scan_files():
        """Trigger file scanning and thumbnail generation."""
        try:
            scanned_count = scanner.scan_directory()
            return jsonify({
                'success': True, 
                'message': f'Scanned {scanned_count} files',
                'count': scanned_count
            })
        except Exception as e:
            logger.error(f"Error during scanning: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/assets')
    def api_assets():
        """REST API endpoint for assets with optional tag filtering."""
        tag_filter = request.args.get('tag', '')
        
        query = Asset.query
        if tag_filter:
            query = query.filter(Asset.tags.any(Tag.name.ilike(f'%{tag_filter}%')))
        
        assets = query.order_by(Asset.created_at.desc()).all()
        
        return jsonify([{
            'id': asset.id,
            'filename': asset.filename,
            'file_path': asset.file_path,
            'file_type': asset.file_type,
            'thumbnail_path': asset.thumbnail_path,
            'tags': [tag.name for tag in asset.tags],
            'created_at': asset.created_at.isoformat(),
            'file_size': asset.file_size
        } for asset in assets])
    
    @app.route('/api/tags')
    def api_tags():
        """REST API endpoint for all tags."""
        tags = Tag.query.order_by(Tag.name).all()
        return jsonify([{'id': tag.id, 'name': tag.name} for tag in tags])
    
    @app.route('/add_tag', methods=['POST'])
    def add_tag():
        """Add a tag to an asset."""
        try:
            data = request.get_json()
            asset_id = data.get('asset_id')
            tag_name = data.get('tag_name', '').strip()
            
            if not asset_id or not tag_name:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            asset = Asset.query.get_or_404(asset_id)
            
            # Find or create tag
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            
            # Add tag to asset if not already present
            if tag not in asset.tags:
                asset.tags.append(tag)
                db.session.commit()
                logger.info(f"Added tag '{tag_name}' to asset {asset.filename}")
            
            return jsonify({'success': True, 'message': 'Tag added successfully'})
            
        except Exception as e:
            logger.error(f"Error adding tag: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/remove_tag', methods=['POST'])
    def remove_tag():
        """Remove a tag from an asset."""
        try:
            data = request.get_json()
            asset_id = data.get('asset_id')
            tag_id = data.get('tag_id')
            
            if not asset_id or not tag_id:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            asset = Asset.query.get_or_404(asset_id)
            tag = Tag.query.get_or_404(tag_id)
            
            if tag in asset.tags:
                asset.tags.remove(tag)
                db.session.commit()
                logger.info(f"Removed tag '{tag.name}' from asset {asset.filename}")
            
            return jsonify({'success': True, 'message': 'Tag removed successfully'})
            
        except Exception as e:
            logger.error(f"Error removing tag: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8080, debug=True)
