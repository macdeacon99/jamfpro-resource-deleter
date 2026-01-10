from base import ResourceHandler

# TODO - Need to test this and make sure that I can 
# delete all app types and that I can not export them.

class MacAppsHandler(ResourceHandler):
    resource_name = "Mac App"

    def delete(self, resource_id: int) -> bool:
        return self.client.pro.app_installers.delete(resource_id)