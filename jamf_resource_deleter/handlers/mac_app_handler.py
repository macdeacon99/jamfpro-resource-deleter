from typing import Dict
from .base import ResourceHandler


class MacAppsHandler(ResourceHandler):
    resource_name = "Mac App"

    def delete(self, resource_id: int) -> bool:
        return self.client.pro.app_installers.delete(resource_id)

    # Cannot retrieve or re-create macapps so not being implemented
    def get(self, resource_id: int):
        pass

    def create(self, resource_config: Dict):
        pass
