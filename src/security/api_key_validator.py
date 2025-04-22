import re
from datetime import datetime
from typing import List


class APIKeyValidator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.permissions = [] 
        self.uuid_part = None 
        self.expiration_date = None
    
    def validate_api_key(self) -> bool:
        if self._is_format_valid():
            self._extract_parts()
            if self._is_uuid_valid() and self._is_permissions_valid() and self._is_not_expired():
                return True
        return False
    
    def _is_format_valid(self) -> bool:
        pattern = r"^([a-zA-Z0-9]{8})-([a-zA-Z,-]+)-(\d{4}-\d{2}-\d{2})$"
        return bool(re.match(pattern, self.api_key))
    
    def _extract_parts(self) -> None:
        pattern = r"^([a-zA-Z0-9]{8})-([a-zA-Z,]+)-(\d{4}-\d{2}-\d{2})$"
        match = re.match(pattern, self.api_key)
        if match:
            self.uuid_part = match.group(1)
            self.permissions = match.group(2).split(',')
            self.expiration_date = datetime.strptime(match.group(3), "%Y-%m-%d").date()
        
    def _is_uuid_valid(self) -> bool:
        return len(self.uuid_part) == 8 and self.uuid_part.isalnum()
    
    def _is_permissions_valid(self) -> bool:
        valid_permissions = {"standard", "admin"}
        return all(permission in valid_permissions for permission in self.permissions)
    
    def _is_not_expired(self) -> bool:
        return self.expiration_date >= datetime.now().date()

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions
