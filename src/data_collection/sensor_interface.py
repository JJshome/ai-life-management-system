# -*- coding: utf-8 -*-
"""
Sensor Interface Module

This module provides interfaces for various sensor technologies including:
- Wearable devices
- Ear-insert sensors for electrochemical impedance measurement
- Environmental sensors
- Other health monitoring devices
"""

import logging
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class SensorBase(ABC):
    """Base class for all sensor interfaces"""
    
    def __init__(self, sensor_id: str, description: str):
        self.sensor_id = sensor_id
        self.description = description
        self.connected = False
        self.last_reading_time = None
        logger.info(f"Initialized sensor: {sensor_id} - {description}")
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the sensor"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the sensor"""
        pass
    
    @abstractmethod
    def read_data(self) -> Dict[str, Any]:
        """Read data from the sensor"""
        pass
    
    def is_connected(self) -> bool:
        """Check if the sensor is connected"""
        return self.connected


class EarInsertSensor(SensorBase):
    """Interface for ear-insert sensors that measure electrochemical impedance"""
    
    def __init__(self, sensor_id: str, frequency_range: List[float]):
        super().__init__(sensor_id, "Ear-insert electrochemical impedance sensor")
        self.frequency_range = frequency_range
        self.current_frequency = frequency_range[0]
        logger.info(f"Ear-insert sensor initialized with frequency range: {frequency_range}")
    
    def connect(self) -> bool:
        """Connect to the ear-insert sensor"""
        # This would contain real connection logic in production
        logger.info(f"Connecting to ear-insert sensor {self.sensor_id}")
        self.connected = True
        return self.connected
    
    def disconnect(self) -> bool:
        """Disconnect from the ear-insert sensor"""
        # This would contain real disconnection logic in production
        logger.info(f"Disconnecting from ear-insert sensor {self.sensor_id}")
        self.connected = False
        return not self.connected
    
    def read_data(self) -> Dict[str, Any]:
        """Read electrochemical impedance data from the sensor"""
        if not self.connected:
            raise ConnectionError("Sensor is not connected")
        
        # In a real implementation, this would read actual sensor data
        # Here we simulate data collection
        reading = {
            "timestamp": time.time(),
            "sensor_id": self.sensor_id,
            "frequency": self.current_frequency,
            "impedance": 1000.0 + (self.current_frequency * 0.01),  # Simulated impedance value
            "phase": 45.0,  # Simulated phase value
            "temperature": 36.8,  # Simulated body temperature
        }
        
        self.last_reading_time = reading["timestamp"]
        logger.debug(f"Read data from ear-insert sensor: {reading}")
        return reading
    
    def set_frequency(self, frequency: float) -> None:
        """Set the measurement frequency"""
        if frequency not in self.frequency_range:
            raise ValueError(f"Frequency {frequency} is outside the supported range")
        
        self.current_frequency = frequency
        logger.info(f"Set ear-insert sensor frequency to {frequency} Hz")
    
    def scan_frequency_range(self) -> List[Dict[str, Any]]:
        """Perform a frequency scan across the entire range"""
        if not self.connected:
            raise ConnectionError("Sensor is not connected")
        
        results = []
        for freq in self.frequency_range:
            self.set_frequency(freq)
            reading = self.read_data()
            results.append(reading)
        
        return results


class WearableSensor(SensorBase):
    """Interface for wearable health monitoring devices"""
    
    def __init__(self, sensor_id: str, sensor_type: str, capabilities: List[str]):
        super().__init__(sensor_id, f"Wearable {sensor_type} sensor")
        self.sensor_type = sensor_type
        self.capabilities = capabilities
        logger.info(f"Wearable sensor initialized with capabilities: {capabilities}")
    
    def connect(self) -> bool:
        """Connect to the wearable sensor"""
        # This would contain real connection logic in production
        logger.info(f"Connecting to wearable sensor {self.sensor_id}")
        self.connected = True
        return self.connected
    
    def disconnect(self) -> bool:
        """Disconnect from the wearable sensor"""
        # This would contain real disconnection logic in production
        logger.info(f"Disconnecting from wearable sensor {self.sensor_id}")
        self.connected = False
        return not self.connected
    
    def read_data(self) -> Dict[str, Any]:
        """Read health data from the wearable sensor"""
        if not self.connected:
            raise ConnectionError("Sensor is not connected")
        
        # In a real implementation, this would read actual sensor data
        # Here we simulate data collection
        reading = {
            "timestamp": time.time(),
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type,
        }
        
        # Add readings based on sensor capabilities
        if "heart_rate" in self.capabilities:
            reading["heart_rate"] = 72  # Simulated heart rate
        
        if "blood_pressure" in self.capabilities:
            reading["blood_pressure"] = {"systolic": 120, "diastolic": 80}  # Simulated BP
        
        if "blood_glucose" in self.capabilities:
            reading["blood_glucose"] = 5.5  # Simulated blood glucose level
        
        if "temperature" in self.capabilities:
            reading["temperature"] = 36.6  # Simulated body temperature
        
        if "activity" in self.capabilities:
            reading["steps"] = 8500  # Simulated step count
            reading["active_minutes"] = 35  # Simulated active minutes
        
        if "sleep" in self.capabilities:
            reading["sleep_quality"] = 85  # Simulated sleep quality score
            reading["deep_sleep_minutes"] = 120  # Simulated deep sleep duration
        
        self.last_reading_time = reading["timestamp"]
        logger.debug(f"Read data from wearable sensor: {reading}")
        return reading


class SensorInterface:
    """Main interface class for managing multiple sensors"""
    
    def __init__(self):
        self.sensors = {}
        logger.info("Sensor interface initialized")
    
    def add_sensor(self, sensor: SensorBase) -> None:
        """Add a sensor to the interface"""
        self.sensors[sensor.sensor_id] = sensor
        logger.info(f"Added sensor {sensor.sensor_id} to interface")
    
    def remove_sensor(self, sensor_id: str) -> bool:
        """Remove a sensor from the interface"""
        if sensor_id in self.sensors:
            del self.sensors[sensor_id]
            logger.info(f"Removed sensor {sensor_id} from interface")
            return True
        return False
    
    def connect_all(self) -> Dict[str, bool]:
        """Connect to all sensors"""
        results = {}
        for sensor_id, sensor in self.sensors.items():
            try:
                results[sensor_id] = sensor.connect()
            except Exception as e:
                logger.error(f"Error connecting to sensor {sensor_id}: {e}")
                results[sensor_id] = False
        return results
    
    def disconnect_all(self) -> Dict[str, bool]:
        """Disconnect from all sensors"""
        results = {}
        for sensor_id, sensor in self.sensors.items():
            try:
                results[sensor_id] = sensor.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting from sensor {sensor_id}: {e}")
                results[sensor_id] = False
        return results
    
    def read_all_data(self) -> Dict[str, Any]:
        """Read data from all connected sensors"""
        results = {}
        for sensor_id, sensor in self.sensors.items():
            if sensor.is_connected():
                try:
                    results[sensor_id] = sensor.read_data()
                except Exception as e:
                    logger.error(f"Error reading data from sensor {sensor_id}: {e}")
                    results[sensor_id] = {}
        return results
    
    def get_sensor(self, sensor_id: str) -> Optional[SensorBase]:
        """Get a specific sensor by ID"""
        return self.sensors.get(sensor_id)
    
    def get_sensors_by_type(self, sensor_type: str) -> List[SensorBase]:
        """Get all sensors of a specific type"""
        return [sensor for sensor in self.sensors.values() 
                if sensor.description.lower().find(sensor_type.lower()) >= 0]
