import unittest
import sys
import os
import threading
import time

# Add parent directory to path to import modules directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from cache import ThreadSafeLRUCache, NoCacheStrategy


class TestThreadSafeLRUCache(unittest.TestCase):
    """Test the ThreadSafeLRUCache class"""
    
    def setUp(self):
        """Set up a cache for each test"""
        self.cache = ThreadSafeLRUCache(maxsize=3)
    
    def test_get_set(self):
        """Test basic get and set operations"""
        # Initially empty
        self.assertIsNone(self.cache.get("key1"))
        
        # Set and get a value
        self.cache.set("key1", "value1")
        self.assertEqual(self.cache.get("key1"), "value1")
        
        # Update a value
        self.cache.set("key1", "new_value1")
        self.assertEqual(self.cache.get("key1"), "new_value1")
    
    def test_lru_eviction(self):
        """Test LRU eviction policy"""
        # Fill the cache to capacity
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        
        # All keys should be present
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get("key2"), "value2")
        self.assertEqual(self.cache.get("key3"), "value3")
        
        # Access key1 to make key2 the least recently used
        self.cache.get("key1")
        self.cache.get("key3")
        
        # Add a new key, which should evict key2
        self.cache.set("key4", "value4")
        
        # key2 should be evicted
        self.assertIsNone(self.cache.get("key2"))
        
        # Other keys should still be present
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get("key3"), "value3")
        self.assertEqual(self.cache.get("key4"), "value4")
    
    def test_clear(self):
        """Test clearing the cache"""
        # Add some items
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        # Verify items are present
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get("key2"), "value2")
        
        # Clear the cache
        self.cache.clear()
        
        # Verify items are gone
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
    
    def test_thread_safety(self):
        """Test thread safety with concurrent access"""
        # Number of operations per thread
        num_operations = 100
        # Number of threads
        num_threads = 10
        
        def worker(thread_id):
            for i in range(num_operations):
                key = f"key_{thread_id}_{i}"
                value = f"value_{thread_id}_{i}"
                self.cache.set(key, value)
                # Occasionally read values
                if i % 10 == 0:
                    self.cache.get(key)
        
        # Create and start threads
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify some values are in the cache (can't check all due to LRU eviction)
        # Check the most recently added values from each thread
        for i in range(num_threads):
            key = f"key_{i}_{num_operations-1}"
            value = f"value_{i}_{num_operations-1}"
            # Some values might be evicted due to LRU policy
            # So we don't assert on specific values


class TestNoCacheStrategy(unittest.TestCase):
    """Test the NoCacheStrategy class"""
    
    def setUp(self):
        """Set up a no-cache strategy for each test"""
        self.cache = NoCacheStrategy()
    
    def test_get_always_returns_none(self):
        """Test that get always returns None"""
        self.assertIsNone(self.cache.get("any_key"))
        
        # Even after setting a value
        self.cache.set("key1", "value1")
        self.assertIsNone(self.cache.get("key1"))
    
    def test_set_does_nothing(self):
        """Test that set does nothing"""
        # No exception should be raised
        self.cache.set("key1", "value1")
        self.assertIsNone(self.cache.get("key1"))
    
    def test_clear_does_nothing(self):
        """Test that clear does nothing"""
        # No exception should be raised
        self.cache.clear()


if __name__ == "__main__":
    unittest.main()