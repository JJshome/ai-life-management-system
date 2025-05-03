# -*- coding: utf-8 -*-
"""
Main Data Collection Module

This module integrates all components of the data collection system and provides
a unified interface for collecting, processing, and storing data from various sources.
"""

import logging
import time
import json
import threading
from typing import Dict, Any, List, Optional

from .sensor_interface import SensorInterface, EarInsertSensor, WearableSensor
from .manual_input import ManualInputHandler
from .external_api import ExternalAPIConnector, MedicalRecordAPI, FinancialAPI
from .data_preprocessor import create_data_preprocessor
from .edge_computing import create_edge_processor, EdgeAI

logger = logging.getLogger(__name__)


class DataCollectionModule:
    """Main class for the Data Collection Module (110)"""
    
    def __init__(self, user_id: str, config: Dict[str, Any] = None):
        """Initialize the Data Collection Module with all components"""
        self.user_id = user_id
        self.config = config or {}
        self.running = False
        self.collection_thread = None
        
        # Initialize all submodules
        self._initialize_components()
        
        logger.info(f"Data Collection Module initialized for user {user_id}")
    
    def _initialize_components(self):
        """Initialize all component modules"""
        # Sensor interface for physical sensors
        self.sensor_interface = SensorInterface()
        
        # Manual input handler for user-entered data
        storage_path = self.config.get("storage_path", None)
        self.manual_input = ManualInputHandler(self.user_id, storage_path)
        
        # External API connector for third-party data
        self.api_connector = ExternalAPIConnector()
        
        # Data preprocessors
        self.preprocessors = create_data_preprocessor()
        
        # Edge processor for local data processing
        device_id = self.config.get("device_id", f"device_{self.user_id}")
        self.edge_processor = create_edge_processor(device_id)
        
        # Edge AI for local inference
        model_path = self.config.get("edge_model_path", None)
        self.edge_ai = EdgeAI(model_path)
    
    def setup_sensors(self) -> None:
        """Set up sensors based on configuration"""
        sensors_config = self.config.get("sensors", {})
        
        # Set up ear-insert sensors for electrochemical impedance
        if "ear_insert" in sensors_config:
            for sensor_config in sensors_config["ear_insert"]:
                sensor_id = sensor_config.get("id", f"ear_{int(time.time())}")
                frequency_range = sensor_config.get("frequency_range", [100.0, 200.0, 300.0, 400.0, 500.0])
                sensor = EarInsertSensor(sensor_id, frequency_range)
                self.sensor_interface.add_sensor(sensor)
        
        # Set up wearable sensors
        if "wearable" in sensors_config:
            for sensor_config in sensors_config["wearable"]:
                sensor_id = sensor_config.get("id", f"wearable_{int(time.time())}")
                sensor_type = sensor_config.get("type", "health")
                capabilities = sensor_config.get("capabilities", ["heart_rate", "activity"])
                sensor = WearableSensor(sensor_id, sensor_type, capabilities)
                self.sensor_interface.add_sensor(sensor)
    
    def setup_external_apis(self) -> None:
        """Set up external API connections based on configuration"""
        apis_config = self.config.get("external_apis", {})
        
        # Set up medical record API
        if "medical" in apis_config:
            med_config = apis_config["medical"]
            medical_api = MedicalRecordAPI(
                med_config.get("base_url", "https://api.example.com/fhir"),
                med_config.get("client_id", ""),
                med_config.get("client_secret", "")
            )
            self.api_connector.add_connector("medical", medical_api)
        
        # Set up financial API
        if "financial" in apis_config:
            fin_config = apis_config["financial"]
            financial_api = FinancialAPI(
                fin_config.get("base_url", "https://api.example.com/banking"),
                fin_config.get("api_key", ""),
                fin_config.get("api_secret", "")
            )
            self.api_connector.add_connector("financial", financial_api)
    
    def start(self) -> bool:
        """Start the data collection process"""
        if self.running:
            logger.warning("Data collection is already running")
            return False
        
        try:
            # Connect to all sensors
            connect_results = self.sensor_interface.connect_all()
            logger.info(f"Sensor connection results: {connect_results}")
            
            # Authenticate with all external APIs
            auth_results = self.api_connector.authenticate_all()
            logger.info(f"API authentication results: {auth_results}")
            
            # Start continuous data collection in a separate thread
            self.running = True
            self.collection_thread = threading.Thread(
                target=self._collection_loop,
                daemon=True
            )
            self.collection_thread.start()
            
            logger.info("Data collection started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting data collection: {e}")
            self.running = False
            return False
    
    def stop(self) -> bool:
        """Stop the data collection process"""
        if not self.running:
            logger.warning("Data collection is not running")
            return False
        
        try:
            # Stop the collection thread
            self.running = False
            if self.collection_thread:
                self.collection_thread.join(timeout=5.0)
            
            # Disconnect from all sensors
            disconnect_results = self.sensor_interface.disconnect_all()
            logger.info(f"Sensor disconnection results: {disconnect_results}")
            
            # Stop edge processor
            self.edge_processor.stop()
            
            logger.info("Data collection stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping data collection: {e}")
            return False
    
    def _collection_loop(self) -> None:
        """Continuous data collection loop running in a separate thread"""
        logger.info("Starting data collection loop")
        
        collection_interval = self.config.get("collection_interval", 60)  # seconds
        
        while self.running:
            try:
                # Collect sensor data
                sensor_data = self.sensor_interface.read_all_data()
                
                # Process sensor data through edge processor
                for sensor_id, data in sensor_data.items():
                    sensor_type = data.get("sensor_type", "unknown")
                    if sensor_type in ["health", "activity", "environment"]:
                        self.edge_processor.process_data(data, "health")
                
                # Collect data from external APIs at less frequent intervals
                api_interval = self.config.get("api_collection_interval", 3600)  # 1 hour
                current_time = time.time()
                
                if hasattr(self, 'last_api_collection_time'):
                    time_since_last = current_time - self.last_api_collection_time
                    if time_since_last >= api_interval:
                        self._collect_external_api_data()
                        self.last_api_collection_time = current_time
                else:
                    # First run
                    self._collect_external_api_data()
                    self.last_api_collection_time = current_time
                
                # Sleep until next collection interval
                time.sleep(collection_interval)
                
            except Exception as e:
                logger.error(f"Error in data collection loop: {e}")
                # Continue the loop even after an error
                time.sleep(collection_interval)
    
    def _collect_external_api_data(self) -> None:
        """Collect data from external APIs"""
        logger.info("Collecting data from external APIs")
        
        try:
            # Define endpoints and parameters for each API
            endpoint_map = {}
            params_map = {}
            
            # Medical API endpoints
            if self.api_connector.get_connector("medical"):
                endpoint_map["medical"] = "Patient/$everything"
                params_map["medical"] = {"_id": self.user_id}
            
            # Financial API endpoints
            if self.api_connector.get_connector("financial"):
                endpoint_map["financial"] = "accounts/transactions"
                one_month_ago = int(time.time()) - (30 * 24 * 60 * 60)
                params_map["financial"] = {"start_date": one_month_ago}
            
            # Get data from all APIs
            if endpoint_map:
                api_data = self.api_connector.get_all_data(endpoint_map, params_map)
                
                # Process API data
                for api_id, data in api_data.items():
                    if "error" in data:
                        logger.error(f"Error getting data from {api_id}: {data['error']}")
                        continue
                    
                    # Preprocess data based on type
                    if api_id == "medical":
                        preprocessed_data = self.preprocessors["health"].preprocess_batch(
                            data.get("entry", [])
                        )
                        # Further processing or storage would go here
                        
                    elif api_id == "financial":
                        preprocessed_data = self.preprocessors["financial"].preprocess_batch(
                            data.get("transactions", [])
                        )
                        # Further processing or storage would go here
            
        except Exception as e:
            logger.error(f"Error collecting external API data: {e}")
    
    def add_manual_health_data(self, record_type: str, details: Dict[str, Any]) -> bool:
        """Add manually entered health data"""
        try:
            record = self.manual_input.add_health_record(record_type, details)
            
            # Preprocess the data
            preprocessed_data = self.preprocessors["health"].preprocess(record.to_dict())
            
            # Process through edge AI if appropriate
            if self.edge_ai.model:
                ai_processed = self.edge_ai.predict(preprocessed_data)
                # Further processing or storage would go here
            
            logger.info(f"Successfully added manual health data of type {record_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding manual health data: {e}")
            return False
    
    def add_manual_lifestyle_data(self, record_type: str, details: Dict[str, Any]) -> bool:
        """Add manually entered lifestyle data"""
        try:
            record = self.manual_input.add_lifestyle_record(record_type, details)
            logger.info(f"Successfully added manual lifestyle data of type {record_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding manual lifestyle data: {e}")
            return False
    
    def add_manual_financial_data(self, record_type: str, amount: float, 
                                 currency: str = "USD", details: Dict[str, Any] = None) -> bool:
        """Add manually entered financial data"""
        try:
            record = self.manual_input.add_financial_record(record_type, amount, currency, details)
            
            # Preprocess the data
            preprocessed_data = self.preprocessors["financial"].preprocess(record.to_dict())
            
            logger.info(f"Successfully added manual financial data of type {record_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding manual financial data: {e}")
            return False
    
    def add_manual_social_data(self, record_type: str, participants: List[str], 
                              details: Dict[str, Any] = None) -> bool:
        """Add manually entered social activity data"""
        try:
            record = self.manual_input.add_social_record(record_type, participants, details)
            logger.info(f"Successfully added manual social data of type {record_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding manual social data: {e}")
            return False
    
    def get_health_records(self, start_time: Optional[float] = None, 
                          end_time: Optional[float] = None,
                          record_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get health records within a time range and/or of a specific type"""
        records = self.manual_input.get_health_records(start_time, end_time, record_type)
        return [record.to_dict() for record in records]
    
    def get_lifestyle_records(self, start_time: Optional[float] = None, 
                             end_time: Optional[float] = None,
                             record_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get lifestyle records within a time range and/or of a specific type"""
        records = self.manual_input.get_lifestyle_records(start_time, end_time, record_type)
        return [record.to_dict() for record in records]
    
    def get_financial_records(self, start_time: Optional[float] = None, 
                             end_time: Optional[float] = None,
                             record_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get financial records within a time range and/or of a specific type"""
        records = self.manual_input.get_financial_records(start_time, end_time, record_type)
        return [record.to_dict() for record in records]
    
    def get_social_records(self, start_time: Optional[float] = None, 
                          end_time: Optional[float] = None,
                          record_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get social activity records within a time range and/or of a specific type"""
        records = self.manual_input.get_social_records(start_time, end_time, record_type)
        return [record.to_dict() for record in records]


# Create a data collection module with example configuration
def create_data_collection_module(user_id: str) -> DataCollectionModule:
    """Create a data collection module with default configuration"""
    config = {
        "storage_path": f"data/{user_id}",
        "device_id": f"device_{user_id}",
        "collection_interval": 60,  # seconds
        "api_collection_interval": 3600,  # 1 hour
        "sensors": {
            "ear_insert": [
                {
                    "id": "ear_sensor_1",
                    "frequency_range": [100.0, 200.0, 500.0, 1000.0, 2000.0, 5000.0]
                }
            ],
            "wearable": [
                {
                    "id": "wrist_sensor_1",
                    "type": "health",
                    "capabilities": ["heart_rate", "blood_pressure", "temperature", "activity"]
                },
                {
                    "id": "chest_sensor_1",
                    "type": "health",
                    "capabilities": ["heart_rate", "respiration_rate", "ecg"]
                }
            ]
        },
        "external_apis": {
            "medical": {
                "base_url": "https://api.example.com/fhir",
                "client_id": "sample_client_id",
                "client_secret": "sample_client_secret"
            },
            "financial": {
                "base_url": "https://api.example.com/banking",
                "api_key": "sample_api_key",
                "api_secret": "sample_api_secret"
            }
        }
    }
    
    # Create module and set up components
    module = DataCollectionModule(user_id, config)
    module.setup_sensors()
    module.setup_external_apis()
    
    return module


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create a data collection module
    dcm = create_data_collection_module("user123")
    
    # Start data collection
    dcm.start()
    
    try:
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop data collection on keyboard interrupt
        dcm.stop()
