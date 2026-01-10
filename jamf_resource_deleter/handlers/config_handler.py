from typing import Optional, Dict
from base import ResourceHandler
from requests import HTTPError

class ComputerConfigProfileHandler(ResourceHandler):
    resource_name = "macOS Configuration Profile"

    def delete(self, resource_id: int) -> bool:
        return self.client.classic.configuration_profiles.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.configuration_profiles.get_by_id(resource_id).json()
        except HTTPError as e:
            print(f"Could not retrieve {self.resource_name} {resource_id}: {e}")
            return None
