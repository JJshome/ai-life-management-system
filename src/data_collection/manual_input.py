# -*- coding: utf-8 -*-
"""
Manual Input Handler Module

This module manages the collection of data that must be input manually by users,
such as lifestyle information, medical history, food intake, and more.
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class HealthRecord:
    """Health record data structure"""
    record_id: str
    timestamp: float = field(default_factory=time.time)
    record_type: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealthRecord':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class LifestyleRecord:
    """Lifestyle record data structure"""
    record_id: str
    timestamp: float = field(default_factory=time.time)
    record_type: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LifestyleRecord':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class FinancialRecord:
    """Financial record data structure"""
    record_id: str
    timestamp: float = field(default_factory=time.time)
    record_type: str = ""
    amount: float = 0.0
    currency: str = "USD"
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FinancialRecord':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class SocialRecord:
    """Social activity record data structure"""
    record_id: str
    timestamp: float = field(default_factory=time.time)
    record_type: str = ""
    participants: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialRecord':
        """Create from dictionary"""
        return cls(**data)


class ManualInputHandler:
    """Handler for all manually input data"""
    
    def __init__(self, user_id: str, storage_path: Optional[str] = None):
        self.user_id = user_id
        self.storage_path = storage_path
        self.health_records = []
        self.lifestyle_records = []
        self.financial_records = []
        self.social_records = []
        logger.info(f"Manual input handler initialized for user {user_id}")
    
    def add_health_record(self, record_type: str, details: Dict[str, Any]) -> HealthRecord:
        """Add a new health record"""
        record_id = f"health_{self.user_id}_{int(time.time())}"
        record = HealthRecord(record_id=record_id, record_type=record_type, details=details)
        self.health_records.append(record)
        logger.info(f"Added health record {record_id} for user {self.user_id}")
        self._save_records()
        return record
    
    def add_lifestyle_record(self, record_type: str, details: Dict[str, Any]) -> LifestyleRecord:
        """Add a new lifestyle record"""
        record_id = f"lifestyle_{self.user_id}_{int(time.time())}"
        record = LifestyleRecord(record_id=record_id, record_type=record_type, details=details)
        self.lifestyle_records.append(record)
        logger.info(f"Added lifestyle record {record_id} for user {self.user_id}")
        self._save_records()
        return record
    
    def add_financial_record(self, record_type: str, amount: float, 
                             currency: str = "USD", details: Dict[str, Any] = None) -> FinancialRecord:
        """Add a new financial record"""
        record_id = f"financial_{self.user_id}_{int(time.time())}"
        if details is None:
            details = {}
        record = FinancialRecord(
            record_id=record_id, 
            record_type=record_type, 
            amount=amount,
            currency=currency,
            details=details
        )
        self.financial_records.append(record)
        logger.info(f"Added financial record {record_id} for user {self.user_id}")
        self._save_records()
        return record
    
    def add_social_record(self, record_type: str, participants: List[str], 
                          details: Dict[str, Any] = None) -> SocialRecord:
        """Add a new social activity record"""
        record_id = f"social_{self.user_id}_{int(time.time())}"
        if details is None:
            details = {}
        record = SocialRecord(
            record_id=record_id, 
            record_type=record_type, 
            participants=participants,
            details=details
        )
        self.social_records.append(record)
        logger.info(f"Added social record {record_id} for user {self.user_id}")
        self._save_records()
        return record
    
    def get_health_records(self, start_time: Optional[float] = None, 
                          end_time: Optional[float] = None,
                          record_type: Optional[str] = None) -> List[HealthRecord]:
        """Get health records within a time range and/or of a specific type"""
        filtered_records = self.health_records
        
        if start_time is not None:
            filtered_records = [r for r in filtered_records if r.timestamp >= start_time]
        
        if end_time is not None:
            filtered_records = [r for r in filtered_records if r.timestamp <= end_time]
        
        if record_type is not None:
            filtered_records = [r for r in filtered_records if r.record_type == record_type]
        
        return filtered_records
    
    def get_lifestyle_records(self, start_time: Optional[float] = None, 
                             end_time: Optional[float] = None,
                             record_type: Optional[str] = None) -> List[LifestyleRecord]:
        """Get lifestyle records within a time range and/or of a specific type"""
        filtered_records = self.lifestyle_records
        
        if start_time is not None:
            filtered_records = [r for r in filtered_records if r.timestamp >= start_time]
        
        if end_time is not None:
            filtered_records = [r for r in filtered_records if r.timestamp <= end_time]
        
        if record_type is not None:
            filtered_records = [r for r in filtered_records if r.record_type == record_type]
        
        return filtered_records
    
    def get_financial_records(self, start_time: Optional[float] = None, 
                             end_time: Optional[float] = None,
                             record_type: Optional[str] = None) -> List[FinancialRecord]:
        """Get financial records within a time range and/or of a specific type"""
        filtered_records = self.financial_records
        
        if start_time is not None:
            filtered_records = [r for r in filtered_records if r.timestamp >= start_time]
        
        if end_time is not None:
            filtered_records = [r for r in filtered_records if r.timestamp <= end_time]
        
        if record_type is not None:
            filtered_records = [r for r in filtered_records if r.record_type == record_type]
        
        return filtered_records
    
    def get_social_records(self, start_time: Optional[float] = None, 
                          end_time: Optional[float] = None,
                          record_type: Optional[str] = None) -> List[SocialRecord]:
        """Get social activity records within a time range and/or of a specific type"""
        filtered_records = self.social_records
        
        if start_time is not None:
            filtered_records = [r for r in filtered_records if r.timestamp >= start_time]
        
        if end_time is not None:
            filtered_records = [r for r in filtered_records if r.timestamp <= end_time]
        
        if record_type is not None:
            filtered_records = [r for r in filtered_records if r.record_type == record_type]
        
        return filtered_records
    
    def _save_records(self) -> None:
        """Save records to storage"""
        if self.storage_path is None:
            logger.warning("No storage path specified, records will not be persisted")
            return
        
        try:
            # In a real implementation, this would save to a database or file system
            # Here we just log that it would be saved
            logger.info(f"Would save records for user {self.user_id} to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving records: {e}")
    
    def load_records(self) -> None:
        """Load records from storage"""
        if self.storage_path is None:
            logger.warning("No storage path specified, no records to load")
            return
        
        try:
            # In a real implementation, this would load from a database or file system
            # Here we just log that it would be loaded
            logger.info(f"Would load records for user {self.user_id} from {self.storage_path}")
        except Exception as e:
            logger.error(f"Error loading records: {e}")
