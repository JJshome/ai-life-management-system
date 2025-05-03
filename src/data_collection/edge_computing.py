# -*- coding: utf-8 -*-
"""
Edge Computing Module

This module provides functionality for processing data at the edge (on local devices)
before transmitting it to the central system. This reduces bandwidth usage,
improves response time, and enhances privacy by processing sensitive data locally.
"""

import logging
import time
import json
import numpy as np
from typing import Dict, Any, List, Optional, Union, Callable
from threading import Thread, Lock
from queue import Queue, Empty

logger = logging.getLogger(__name__)


class EdgeProcessor:
    """Main class for edge computing functionality"""
    
    def __init__(self, device_id: str, processing_capacity: int = 100):
        self.device_id = device_id
        self.processing_capacity = processing_capacity  # Simulated capacity in operations per second
        self.processing_pipelines = {}
        self.data_queues = {}
        self.running = False
        self.processing_threads = {}
        self.locks = {}
        logger.info(f"Edge processor initialized for device {device_id} with capacity {processing_capacity}")
    
    def register_pipeline(self, data_type: str, pipeline_functions: List[Callable]) -> None:
        """Register a data processing pipeline for a specific data type"""
        self.processing_pipelines[data_type] = pipeline_functions
        self.data_queues[data_type] = Queue()
        self.locks[data_type] = Lock()
        logger.info(f"Registered edge processing pipeline for {data_type} with {len(pipeline_functions)} functions")
    
    def start(self) -> None:
        """Start all processing pipelines"""
        if self.running:
            logger.warning("Edge processor is already running")
            return
            
        self.running = True
        
        # Start a thread for each pipeline
        for data_type in self.processing_pipelines:
            self.processing_threads[data_type] = Thread(
                target=self._process_queue,
                args=(data_type,),
                daemon=True
            )
            self.processing_threads[data_type].start()
            logger.info(f"Started processing thread for {data_type}")
    
    def stop(self) -> None:
        """Stop all processing pipelines"""
        if not self.running:
            logger.warning("Edge processor is not running")
            return
            
        self.running = False
        
        # Wait for all threads to finish
        for data_type, thread in self.processing_threads.items():
            thread.join(timeout=2.0)  # Wait up to 2 seconds for thread to finish
            logger.info(f"Stopped processing thread for {data_type}")
        
        self.processing_threads = {}
    
    def process_data(self, data: Dict[str, Any], data_type: str) -> None:
        """Queue data for processing"""
        if data_type not in self.data_queues:
            logger.warning(f"No processing pipeline registered for {data_type}")
            return
            
        self.data_queues[data_type].put(data)
        logger.debug(f"Queued {data_type} data for processing")
    
    def process_data_synchronous(self, data: Dict[str, Any], data_type: str) -> Optional[Dict[str, Any]]:
        """Process data synchronously (blocking call)"""
        if data_type not in self.processing_pipelines:
            logger.warning(f"No processing pipeline registered for {data_type}")
            return None
            
        result = data.copy()
        
        with self.locks[data_type]:
            # Apply each function in the pipeline
            for func in self.processing_pipelines[data_type]:
                try:
                    result = func(result)
                except Exception as e:
                    logger.error(f"Error in edge processing pipeline for {data_type}: {e}")
                    return None
        
        logger.debug(f"Processed {data_type} data synchronously")
        return result
    
    def _process_queue(self, data_type: str) -> None:
        """Process data from the queue (runs in a separate thread)"""
        logger.info(f"Started queue processing for {data_type}")
        
        while self.running:
            try:
                # Get data from the queue with a timeout
                data = self.data_queues[data_type].get(timeout=1.0)
                
                # Process the data
                result = self.process_data_synchronous(data, data_type)
                
                # Handle the result (in a real system, this might send it to the cloud)
                if result:
                    logger.debug(f"Successfully processed {data_type} data")
                    # Simulate sending to cloud
                    self._send_to_cloud(result, data_type)
                
                # Mark the task as done
                self.data_queues[data_type].task_done()
                
            except Empty:
                # No data in the queue, just continue
                pass
            except Exception as e:
                logger.error(f"Error in queue processing for {data_type}: {e}")
    
    def _send_to_cloud(self, data: Dict[str, Any], data_type: str) -> None:
        """Simulate sending processed data to the cloud"""
        # In a real implementation, this would use appropriate protocol
        # to send data to the central system
        logger.debug(f"Would send {data_type} data to cloud: {data}")


# Example pipeline functions for different data types

def filter_redundant_sensor_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Filter out sensor readings that haven't changed significantly"""
    # This would use a proper state cache in a real implementation
    # Here we just simulate it
    return data


def compress_sensor_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Compress sensor data to reduce transmission size"""
    # In a real implementation, this would apply compression algorithms
    # Here we just simulate by removing some precision
    result = data.copy()
    
    for key, value in result.items():
        if isinstance(value, float):
            # Round to 2 decimal places to simulate compression
            result[key] = round(value, 2)
    
    return result


def encrypt_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Encrypt sensitive fields before transmission"""
    # In a real implementation, this would use proper encryption
    # Here we just simulate by marking the field as encrypted
    result = data.copy()
    
    sensitive_fields = ["health_data", "financial_data", "personal_info"]
    for field in sensitive_fields:
        if field in result:
            result[field] = f"ENCRYPTED_{result[field]}"
    
    return result


def aggregate_time_series(data_batch: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate time series data to reduce data volume"""
    # In a real implementation, this would aggregate readings over time
    # Here we just simulate by returning summary statistics
    if not data_batch:
        return {}
    
    # Identify numeric fields for aggregation
    first_item = data_batch[0]
    numeric_fields = [k for k, v in first_item.items() if isinstance(v, (int, float))]
    
    # Prepare result with metadata
    result = {
        "timestamp": time.time(),
        "count": len(data_batch),
        "aggregated": True
    }
    
    # Calculate aggregates for each numeric field
    for field in numeric_fields:
        values = [item.get(field) for item in data_batch if field in item]
        if values:
            result[f"{field}_min"] = min(values)
            result[f"{field}_max"] = max(values)
            result[f"{field}_avg"] = sum(values) / len(values)
            result[f"{field}_count"] = len(values)
    
    return result


# Edge AI specific components

class EdgeAI:
    """Provides edge AI functionality for local inference"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.model = None
        logger.info("Edge AI module initialized")
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str) -> bool:
        """Load an AI model for edge inference"""
        try:
            # In a real implementation, this would load an actual model
            # (e.g., TensorFlow Lite, ONNX Runtime, etc.)
            logger.info(f"Would load model from {model_path}")
            self.model_path = model_path
            self.model = "DUMMY_MODEL"  # Placeholder
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference on data using the loaded model"""
        if not self.model:
            raise ValueError("No model loaded")
        
        # In a real implementation, this would run actual inference
        # Here we just simulate by adding a prediction field
        result = data.copy()
        
        # Simulate different predictions based on data type
        if "heart_rate" in data:
            # Health prediction
            hr = data["heart_rate"]
            if hr > 100:
                result["stress_level_prediction"] = "high"
            elif hr > 70:
                result["stress_level_prediction"] = "medium"
            else:
                result["stress_level_prediction"] = "low"
                
        elif "amount" in data and data.get("type") == "expense":
            # Financial prediction
            amount = data["amount"]
            if amount > 1000:
                result["spending_category_prediction"] = "major_expense"
            elif amount > 100:
                result["spending_category_prediction"] = "regular_expense"
            else:
                result["spending_category_prediction"] = "minor_expense"
        
        # Add confidence score
        result["prediction_confidence"] = 0.85  # Simulated confidence
        result["prediction_timestamp"] = time.time()
        
        logger.debug(f"Made edge prediction: {result}")
        return result


# Factory function to create an edge processing system
def create_edge_processor(device_id: str) -> EdgeProcessor:
    """Create an edge processor with preconfigured pipelines"""
    processor = EdgeProcessor(device_id)
    
    # Register pipeline for health data
    processor.register_pipeline("health", [
        filter_redundant_sensor_data,
        encrypt_sensitive_data,
        compress_sensor_data
    ])
    
    # Register pipeline for financial data
    processor.register_pipeline("financial", [
        encrypt_sensitive_data,
        compress_sensor_data
    ])
    
    # Start the processor
    processor.start()
    
    return processor
