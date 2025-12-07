import os
import io
import base64
from PIL import Image
from typing import Dict, List, Optional, Tuple
from werkzeug.utils import secure_filename

from python.helpers.print_style import PrintStyle

class AttachmentManager:
  """Manages file attachments."""
  ALLOWED_EXTENSIONS = {
      'image': {'jpg', 'jpeg', 'png', 'bmp'},
      'code': {'py', 'js', 'sh', 'html', 'css'},
      'document': {'md', 'pdf', 'txt', 'csv', 'json'}
  }
  
  def __init__(self, work_dir: str):
      """Initializes an AttachmentManager.

      Args:
          work_dir: The directory to store attachments in.
      """
      self.work_dir = work_dir
      os.makedirs(work_dir, exist_ok=True)

  def is_allowed_file(self, filename: str) -> bool:
      """Checks if a file is allowed.

      Args:
          filename: The name of the file.

      Returns:
          True if the file is allowed, False otherwise.
      """
      ext = self.get_file_extension(filename)
      all_allowed = set().union(*self.ALLOWED_EXTENSIONS.values())
      return ext in all_allowed

  def get_file_type(self, filename: str) -> str:
      """Gets the type of a file.

      Args:
          filename: The name of the file.

      Returns:
          The type of the file.
      """
      ext = self.get_file_extension(filename)
      for file_type, extensions in self.ALLOWED_EXTENSIONS.items():
          if ext in extensions:
              return file_type
      return 'unknown'

  @staticmethod
  def get_file_extension(filename: str) -> str:
      """Gets the extension of a file.

      Args:
          filename: The name of the file.

      Returns:
          The extension of the file.
      """
      return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
  
  def validate_mime_type(self, file) -> bool:
      """Validates the MIME type of a file.

      Args:
          file: The file to validate.

      Returns:
          True if the MIME type is valid, False otherwise.
      """
      try:
          mime_type = file.content_type
          return mime_type.split('/')[0] in ['image', 'text', 'application']
      except AttributeError:
          return False

  def save_file(self, file, filename: str) -> Tuple[str, Dict]:
      """Saves a file and returns its path and metadata.

      Args:
          file: The file to save.
          filename: The name of the file.

      Returns:
          A tuple containing the path to the saved file and its metadata.
      """
      try:
          filename = secure_filename(filename)
          if not filename:
              raise ValueError("Invalid filename")
              
          file_path = os.path.join(self.work_dir, filename)
          
          file_type = self.get_file_type(filename)
          metadata = {
              'filename': filename,
              'type': file_type,
              'extension': self.get_file_extension(filename),
              'preview': None
          }
  
          # Save file
          file.save(file_path)
  
          # Generate preview for images
          if file_type == 'image':
              metadata['preview'] = self.generate_image_preview(file_path)
  
          return file_path, metadata
        
      except Exception as e:
          PrintStyle.error(f"Error saving file {filename}: {e}")
          return None, {} # type: ignore

  def generate_image_preview(self, image_path: str, max_size: int = 800) -> Optional[str]:
      """Generates a preview for an image.

      Args:
          image_path: The path to the image.
          max_size: The maximum size of the preview.

      Returns:
          A base64-encoded string of the preview, or None if an error
          occurred.
      """
      try:
          with Image.open(image_path) as img:
              # Convert image if needed
              if img.mode in ('RGBA', 'P'):
                  img = img.convert('RGB')
              
              # Resize for preview
              img.thumbnail((max_size, max_size))
              
              # Save to buffer
              buffer = io.BytesIO()
              img.save(buffer, format="JPEG", quality=70, optimize=True)
              
              # Convert to base64
              return base64.b64encode(buffer.getvalue()).decode('utf-8')
      except Exception as e:
          PrintStyle.error(f"Error generating preview for {image_path}: {e}")
          return None
      