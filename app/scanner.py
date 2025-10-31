"""
File scanner and thumbnail generator for the Lasercut Manager.
Scans the /data directory for supported file types and generates thumbnails.
"""

import os
import logging
from pathlib import Path
from PIL import Image
import cairosvg
from pdf2image import convert_from_path
import zipfile
from models import db, Asset, Tag

logger = logging.getLogger(__name__)

class FileScanner:
    """Handles file scanning and thumbnail generation."""
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.zip', '.svg', '.pdf', '.png', '.jpg', '.jpeg'}
    
    def __init__(self, data_dir='data', thumbnails_dir='app/static/thumbnails'):
        """
        Initialize the file scanner.
        
        Args:
            data_dir: Directory to scan for files
            thumbnails_dir: Directory to store generated thumbnails
        """
        self.data_dir = Path(data_dir)
        self.thumbnails_dir = Path(thumbnails_dir)
        
        # Ensure thumbnails directory exists
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FileScanner initialized - Data dir: {self.data_dir}, Thumbnails dir: {self.thumbnails_dir}")
    
    def scan_directory(self):
        """
        Scan the data directory for supported files and update the database.
        
        Returns:
            int: Number of files processed
        """
        if not self.data_dir.exists():
            logger.error(f"Data directory {self.data_dir} does not exist")
            return 0
        
        processed_count = 0
        
        try:
            # Get all files in the data directory recursively
            for file_path in self.data_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    try:
                        self._process_file(file_path)
                        processed_count += 1
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {e}")
                        continue
            
            logger.info(f"Scan completed. Processed {processed_count} files")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error during directory scan: {e}")
            return processed_count
    
    def _process_file(self, file_path):
        """
        Process a single file: check if it exists in DB, generate thumbnail if needed.
        
        Args:
            file_path: Path to the file to process
        """
        # Convert to relative path for storage
        relative_path = file_path.relative_to(self.data_dir)
        file_path_str = str(relative_path)
        
        # Check if file already exists in database
        existing_asset = Asset.query.filter_by(file_path=file_path_str).first()
        
        if existing_asset:
            # Update file size and modification time if needed
            file_size = file_path.stat().st_size
            if existing_asset.file_size != file_size:
                existing_asset.file_size = file_size
                existing_asset.updated_at = db.func.now()
                db.session.commit()
                logger.info(f"Updated file size for {file_path_str}")
            return
        
        # Create new asset record
        file_type = file_path.suffix.lower()
        file_size = file_path.stat().st_size
        
        # Generate thumbnail
        thumbnail_path = self._generate_thumbnail(file_path)
        
        # Create asset record
        asset = Asset(
            filename=file_path.name,
            file_path=file_path_str,
            file_type=file_type,
            file_size=file_size,
            thumbnail_path=thumbnail_path
        )
        
        db.session.add(asset)
        db.session.commit()
        
        logger.info(f"Added new asset: {file_path_str}")
    
    def _generate_thumbnail(self, file_path):
        """
        Generate a thumbnail for the given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Relative path to the generated thumbnail, or None if generation failed
        """
        try:
            # Check for existing preview files first
            preview_files = ['preview.jpg', 'preview.png', 'preview.jpeg']
            for preview_file in preview_files:
                preview_path = file_path.parent / preview_file
                if preview_path.exists():
                    # Copy existing preview to thumbnails directory
                    thumbnail_name = f"{file_path.stem}_preview{preview_path.suffix}"
                    thumbnail_path = self.thumbnails_dir / thumbnail_name
                    
                    # Copy the file
                    import shutil
                    shutil.copy2(preview_path, thumbnail_path)
                    
                    logger.info(f"Used existing preview for {file_path.name}")
                    return f"thumbnails/{thumbnail_name}"
            
            # Generate thumbnail based on file type
            thumbnail_name = f"{file_path.stem}_thumb.png"
            thumbnail_path = self.thumbnails_dir / thumbnail_name
            
            if file_path.suffix.lower() == '.svg':
                self._generate_svg_thumbnail(file_path, thumbnail_path)
            elif file_path.suffix.lower() == '.pdf':
                self._generate_pdf_thumbnail(file_path, thumbnail_path)
            elif file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                self._generate_image_thumbnail(file_path, thumbnail_path)
            elif file_path.suffix.lower() == '.zip':
                self._generate_zip_thumbnail(file_path, thumbnail_path)
            else:
                logger.warning(f"No thumbnail generation method for {file_path.suffix}")
                return None
            
            if thumbnail_path.exists():
                logger.info(f"Generated thumbnail for {file_path.name}")
                return f"thumbnails/{thumbnail_name}"
            else:
                logger.warning(f"Failed to generate thumbnail for {file_path.name}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating thumbnail for {file_path}: {e}")
            return None
    
    def _generate_svg_thumbnail(self, svg_path, output_path):
        """Generate PNG thumbnail from SVG file."""
        try:
            cairosvg.svg2png(url=str(svg_path), write_to=str(output_path), output_width=300)
        except Exception as e:
            logger.error(f"Error converting SVG {svg_path}: {e}")
    
    def _generate_pdf_thumbnail(self, pdf_path, output_path):
        """Generate PNG thumbnail from PDF file."""
        try:
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
            if images:
                # Resize to max 300px width while maintaining aspect ratio
                img = images[0]
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(output_path, 'PNG')
        except Exception as e:
            logger.error(f"Error converting PDF {pdf_path}: {e}")
    
    def _generate_image_thumbnail(self, image_path, output_path):
        """Generate thumbnail from image file."""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize to max 300px width while maintaining aspect ratio
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(output_path, 'PNG')
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
    
    def _generate_zip_thumbnail(self, zip_path, output_path):
        """Generate thumbnail for ZIP file by looking for preview images inside."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                # Look for preview images in the ZIP
                preview_files = ['preview.jpg', 'preview.png', 'preview.jpeg', 'thumbnail.png', 'thumb.jpg']
                
                for file_info in zip_file.filelist:
                    if file_info.filename.lower() in preview_files:
                        # Extract and use the preview image
                        with zip_file.open(file_info) as preview_data:
                            with Image.open(preview_data) as img:
                                if img.mode in ('RGBA', 'LA', 'P'):
                                    img = img.convert('RGB')
                                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                                img.save(output_path, 'PNG')
                                return
                
                # If no preview found, create a generic ZIP icon
                self._create_zip_icon(output_path)
                
        except Exception as e:
            logger.error(f"Error processing ZIP {zip_path}: {e}")
    
    def _create_zip_icon(self, output_path):
        """Create a generic ZIP file icon."""
        try:
            # Create a simple ZIP icon
            img = Image.new('RGB', (300, 300), color='lightblue')
            # This is a placeholder - in a real implementation, you might want to
            # create a more sophisticated icon or use an existing icon file
            img.save(output_path, 'PNG')
        except Exception as e:
            logger.error(f"Error creating ZIP icon: {e}")
