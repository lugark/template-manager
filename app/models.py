"""
SQLAlchemy models for the Lasercut Manager application.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship

db = SQLAlchemy()

# Association table for many-to-many relationship between assets and tags
asset_tags = Table(
    'asset_tags',
    db.Model.metadata,
    Column('asset_id', Integer, ForeignKey('assets.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Asset(db.Model):
    """Model representing a file asset in the system."""
    
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False, unique=True)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, default=0)
    thumbnail_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Many-to-many relationship with tags
    tags = relationship('Tag', secondary=asset_tags, back_populates='assets')
    
    def __repr__(self):
        return f'<Asset {self.filename}>'
    
    def to_dict(self):
        """Convert asset to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'thumbnail_path': self.thumbnail_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': [tag.name for tag in self.tags]
        }

class Tag(db.Model):
    """Model representing a tag for categorizing assets."""
    
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Many-to-many relationship with assets
    assets = relationship('Asset', secondary=asset_tags, back_populates='tags')
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
    def to_dict(self):
        """Convert tag to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'asset_count': len(self.assets)
        }
