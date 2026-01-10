from typing import Optional, Dict
from base import ResourceHandler
from requests import HTTPError

class ComputerGroupHandler(ResourceHandler):
    resource_name = "Computer Group"

    def delete(self, resource_id: int) -> bool:
        return self.client.classic.computer_groups.delete_by_id(resource_id)

    def get(self, resource_id: int) -> Optional[Dict]:
        try:
            return self.client.classic.computer_groups.get_by_id(resource_id).json()
        except HTTPError as e:
            print(f"Could not retrieve {self.resource_name} {resource_id}: {e}")
            return None
