# -*- coding: utf-8 -*-
"""
External API Connector Module

This module provides interfaces to connect with external data sources including:
- Medical record systems
- Financial institutions
- Social media platforms
- Health and fitness apps
- Environment monitoring systems
"""

import logging
import time
import json
import hashlib
import hmac
import base64
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Tuple

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors"""
    pass


class AuthenticationError(APIError):
    """Authentication related errors"""
    pass


class ConnectionError(APIError):
    """Connection related errors"""
    pass


class DataError(APIError):
    """Data processing errors"""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded errors"""
    pass


class ExternalAPIBase(ABC):
    """Base class for all external API connectors"""
    
    def __init__(self, api_name: str, api_base_url: str):
        self.api_name = api_name
        self.api_base_url = api_base_url
        self.authenticated = False
        self.auth_token = None
        self.last_request_time = None
        self.rate_limit_remaining = None
        logger.info(f"Initialized external API connector: {api_name}")
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the external API"""
        pass
    
    @abstractmethod
    def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data from the external API"""
        pass
    
    @abstractmethod
    def post_data(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Post data to the external API"""
        pass
    
    def is_authenticated(self) -> bool:
        """Check if authenticated with the API"""
        return self.authenticated
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and check for errors"""
        self.last_request_time = time.time()
        
        # Update rate limit info if available
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        
        # Check for errors
        if response.status_code == 401:
            self.authenticated = False
            raise AuthenticationError(f"Authentication failed: {response.text}")
        
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After', '60')
            raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds")
        
        if response.status_code >= 400:
            raise APIError(f"API error: {response.status_code} - {response.text}")
        
        # Parse JSON response
        try:
            return response.json()
        except ValueError:
            raise DataError(f"Failed to parse JSON response: {response.text}")


class MedicalRecordAPI(ExternalAPIBase):
    """Connector for medical record systems using FHIR standard"""
    
    def __init__(self, api_base_url: str, client_id: str, client_secret: str):
        super().__init__("Medical Record API (FHIR)", api_base_url)
        self.client_id = client_id
        self.client_secret = client_secret
        logger.info("Medical Record API connector initialized")
    
    def authenticate(self) -> bool:
        """Authenticate with OAuth 2.0"""
        try:
            auth_endpoint = f"{self.api_base_url}/auth/token"
            response = requests.post(
                auth_endpoint,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )
            
            auth_data = self._handle_response(response)
            self.auth_token = auth_data.get("access_token")
            
            if not self.auth_token:
                raise AuthenticationError("No access token received")
            
            self.authenticated = True
            logger.info("Successfully authenticated with Medical Record API")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self.authenticated = False
            return False
    
    def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data from the FHIR API"""
        if not self.is_authenticated():
            if not self.authenticate():
                raise AuthenticationError("Cannot proceed without authentication")
        
        try:
            url = f"{self.api_base_url}/{endpoint}"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = requests.get(url, headers=headers, params=params)
            return self._handle_response(response)
            
        except Exception as e:
            logger.error(f"Error getting data from {endpoint}: {e}")
            raise
    
    def post_data(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Post data to the FHIR API"""
        if not self.is_authenticated():
            if not self.authenticate():
                raise AuthenticationError("Cannot proceed without authentication")
        
        try:
            url = f"{self.api_base_url}/{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/fhir+json"
            }
            
            response = requests.post(url, headers=headers, json=data)
            return self._handle_response(response)
            
        except Exception as e:
            logger.error(f"Error posting data to {endpoint}: {e}")
            raise
    
    def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Get patient data by ID"""
        return self.get_data(f"Patient/{patient_id}")
    
    def get_patient_observations(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get patient observations (measurements, lab results, etc.)"""
        response = self.get_data("Observation", {"patient": patient_id})
        return response.get("entry", [])
    
    def get_patient_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get patient conditions (diagnoses)"""
        response = self.get_data("Condition", {"patient": patient_id})
        return response.get("entry", [])
    
    def get_patient_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get patient medications"""
        response = self.get_data("MedicationRequest", {"patient": patient_id})
        return response.get("entry", [])


class FinancialAPI(ExternalAPIBase):
    """Connector for financial institutions using Open Banking standards"""
    
    def __init__(self, api_base_url: str, api_key: str, api_secret: str):
        super().__init__("Financial API (Open Banking)", api_base_url)
        self.api_key = api_key
        self.api_secret = api_secret
        logger.info("Financial API connector initialized")
    
    def authenticate(self) -> bool:
        """Authenticate with the financial API"""
        try:
            timestamp = str(int(time.time()))
            signature_data = f"{self.api_key}:{timestamp}"
            signature = hmac.new(
                self.api_secret.encode(),
                signature_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            auth_endpoint = f"{self.api_base_url}/auth"
            headers = {
                "X-API-Key": self.api_key,
                "X-Timestamp": timestamp,
                "X-Signature": signature
            }
            
            response = requests.post(auth_endpoint, headers=headers)
            auth_data = self._handle_response(response)
            self.auth_token = auth_data.get("access_token")
            
            if not self.auth_token:
                raise AuthenticationError("No access token received")
            
            self.authenticated = True
            logger.info("Successfully authenticated with Financial API")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self.authenticated = False
            return False
    
    def get_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get data from the financial API"""
        if not self.is_authenticated():
            if not self.authenticate():
                raise AuthenticationError("Cannot proceed without authentication")
        
        try:
            url = f"{self.api_base_url}/{endpoint}"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = requests.get(url, headers=headers, params=params)
            return self._handle_response(response)
            
        except Exception as e:
            logger.error(f"Error getting data from {endpoint}: {e}")
            raise
    
    def post_data(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Post data to the financial API"""
        if not self.is_authenticated():
            if not self.authenticate():
                raise AuthenticationError("Cannot proceed without authentication")
        
        try:
            url = f"{self.api_base_url}/{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, headers=headers, json=data)
            return self._handle_response(response)
            
        except Exception as e:
            logger.error(f"Error posting data to {endpoint}: {e}")
            raise
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get all accounts"""
        response = self.get_data("accounts")
        return response.get("accounts", [])
    
    def get_transactions(self, account_id: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get transactions for an account"""
        params = {"account_id": account_id}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        response = self.get_data("transactions", params)
        return response.get("transactions", [])
    
    def get_balance(self, account_id: str) -> Dict[str, Any]:
        """Get current balance for an account"""
        response = self.get_data(f"accounts/{account_id}/balance")
        return response.get("balance", {})


class ExternalAPIConnector:
    """Main manager class for all external API connections"""
    
    def __init__(self):
        self.api_connectors = {}
        logger.info("External API connector manager initialized")
    
    def add_connector(self, connector_id: str, connector: ExternalAPIBase) -> None:
        """Add a new API connector"""
        self.api_connectors[connector_id] = connector
        logger.info(f"Added API connector: {connector_id}")
    
    def remove_connector(self, connector_id: str) -> bool:
        """Remove an API connector"""
        if connector_id in self.api_connectors:
            del self.api_connectors[connector_id]
            logger.info(f"Removed API connector: {connector_id}")
            return True
        return False
    
    def get_connector(self, connector_id: str) -> Optional[ExternalAPIBase]:
        """Get a specific API connector by ID"""
        return self.api_connectors.get(connector_id)
    
    def authenticate_all(self) -> Dict[str, bool]:
        """Authenticate all API connectors"""
        results = {}
        for connector_id, connector in self.api_connectors.items():
            try:
                results[connector_id] = connector.authenticate()
            except Exception as e:
                logger.error(f"Error authenticating connector {connector_id}: {e}")
                results[connector_id] = False
        return results
    
    def get_all_data(self, endpoint_map: Dict[str, str], params_map: Dict[str, Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get data from multiple APIs at once"""
        if params_map is None:
            params_map = {}
            
        results = {}
        for connector_id, endpoint in endpoint_map.items():
            connector = self.get_connector(connector_id)
            if not connector:
                logger.warning(f"Connector {connector_id} not found")
                continue
                
            try:
                params = params_map.get(connector_id, {})
                results[connector_id] = connector.get_data(endpoint, params)
            except Exception as e:
                logger.error(f"Error getting data from {connector_id}: {e}")
                results[connector_id] = {"error": str(e)}
                
        return results
