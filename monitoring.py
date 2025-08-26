"""
Performance monitoring and utilities for PII processing.
Tracks metrics and provides performance analysis capabilities.
"""

import time
from typing import Dict, List, Any

from core import ProcessingResult


class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
    
    def record_processing(self, result: ProcessingResult):
        """Record processing metrics"""
        self.metrics.append({
            "timestamp": time.time(),
            "processing_time": result.processing_time,
            "text_length": result.metadata.get("text_length", 0),
            "entities_found": result.total_entities,
            "cache_hits": result.cache_hits
        })
    
    def get_average_performance(self) -> Dict[str, float]:
        """Get average performance metrics"""
        if not self.metrics:
            return {}
        
        total_time = sum(m["processing_time"] for m in self.metrics)
        total_length = sum(m["text_length"] for m in self.metrics)
        
        return {
            "avg_processing_time": total_time / len(self.metrics),
            "chars_per_second": total_length / total_time if total_time > 0 else 0,
            "avg_entities_per_text": sum(m["entities_found"] for m in self.metrics) / len(self.metrics)
        }
    
    def clear_metrics(self):
        """Clear all recorded metrics"""
        self.metrics.clear()
    
    def get_total_processed(self) -> int:
        """Get total number of texts processed"""
        return len(self.metrics)
    
    def get_total_entities_found(self) -> int:
        """Get total number of entities found across all processing"""
        return sum(m["entities_found"] for m in self.metrics)