"""
Model Manager - Quản lý nhiều models cho multi-course support
Manages multiple ModelLoader instances with caching and lazy loading
"""
from pathlib import Path
from typing import Dict, Optional
from threading import Lock

from .loader import ModelLoader


class ModelManager:
    """
    Manager for multiple course models
    
    Features:
    - Lazy loading: Load models only when needed
    - Caching: Keep loaded models in memory
    - Thread-safe: Safe for concurrent requests
    """
    
    def __init__(self, default_course_id: Optional[int] = None):
        """
        Initialize model manager
        
        Args:
            default_course_id: Default course ID to preload (optional)
        """
        self._loaders: Dict[int, ModelLoader] = {}
        self._lock = Lock()
        self.default_course_id = default_course_id
        
        # Preload default course if specified
        if default_course_id is not None:
            self.get_loader(default_course_id, verbose=True)
    
    def get_loader(self, course_id: int, verbose: bool = False) -> ModelLoader:
        """
        Get ModelLoader for a specific course (lazy load if not cached)
        
        Args:
            course_id: Course ID
            verbose: Print loading messages
            
        Returns:
            ModelLoader instance for the course
        """
        with self._lock:
            # Check cache first
            if course_id in self._loaders:
                if verbose:
                    print(f"✓ Using cached model for course {course_id}")
                return self._loaders[course_id]
            
            # Create and load new loader
            if verbose:
                print(f"📦 Loading model for course {course_id}...")
            
            loader = ModelLoader(course_id=course_id)
            loader.load_all(verbose=verbose)
            
            # Cache it
            self._loaders[course_id] = loader
            
            if verbose:
                print(f"✓ Model for course {course_id} loaded and cached")
            
            return loader
    
    def unload(self, course_id: int):
        """
        Unload and remove a model from cache
        
        Args:
            course_id: Course ID to unload
        """
        with self._lock:
            if course_id in self._loaders:
                del self._loaders[course_id]
                print(f"✓ Unloaded model for course {course_id}")
    
    def unload_all(self):
        """Unload all cached models"""
        with self._lock:
            self._loaders.clear()
            print("✓ All models unloaded")
    
    def list_loaded_courses(self) -> list:
        """Get list of currently loaded course IDs"""
        with self._lock:
            return list(self._loaders.keys())
    
    def is_loaded(self, course_id: int) -> bool:
        """Check if a course model is loaded"""
        with self._lock:
            return course_id in self._loaders

