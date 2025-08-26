"""
Caching strategies for the PII anonymizer module.
Implements the Strategy pattern for different caching approaches.
"""

import threading
from typing import Optional, Any


class ThreadSafeLRUCache:
    """Thread-safe LRU cache implementation"""
    
    def __init__(self, maxsize: int = 1000):
        self._cache = {}
        self._lock = threading.RLock()
        self.maxsize = maxsize
        self._access_order = []
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._access_order.remove(key)
                self._access_order.append(key)
                return self._cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self._cache:
                self._access_order.remove(key)
            elif len(self._cache) >= self.maxsize:
                # Remove least recently used
                oldest = self._access_order.pop(0)
                del self._cache[oldest]
            
            self._cache[key] = value
            self._access_order.append(key)
    
    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._access_order.clear()


class NoCacheStrategy:
    """No-op cache for when caching is disabled"""
    
    def get(self, key: str) -> Optional[Any]:
        return None
    
    def set(self, key: str, value: Any) -> None:
        pass
    
    def clear(self) -> None:
        pass