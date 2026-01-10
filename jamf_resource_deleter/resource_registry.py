from typing import Dict, Type
from .handlers import (
    ResourceHandler,
    ComputerAttributeHandler,
    ComputerConfigProfileHandler,
    ComputerGroupHandler,
    ComputerHandler,
    ScriptHandler,
    PackageHandler,
    PolicyHandler,
    RestrictedSoftwareHandler,
    MacAppsHandler,
)


class ResourceRegistry:
    """Central Registry for resource type mappings"""

    def __init__(self):
        self._handlers: Dict[str, Type[ResourceHandler]] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register all default resource handlers"""
        self.register("unusedComputers", ComputerHandler)
        self.register("unusedComputerGroups", ComputerGroupHandler)
        self.register("unusedMacApps", MacAppsHandler)
        self.register("unusedMobileDeviceApps", MacAppsHandler)
        self.register("unusedPackages", PackageHandler)
        self.register("unusedPolicies", PolicyHandler)
        self.register("unusedComputerProfiles", ComputerConfigProfileHandler)
        self.register("unusedScripts", ScriptHandler)
        self.register("unusedComputerEAs", ComputerAttributeHandler)
        self.register("unusedRestrictedSoftware", RestrictedSoftwareHandler)

    def register(self, resource_type: str, handler_class: Type[ResourceHandler]):
        """Register a handler for a resource type"""
        self._handlers[resource_type] = handler_class

    def get_handler_class(self, resource_type: str) -> Type[ResourceHandler]:
        """Get the handler class for a resource type"""
        return self._handlers.get(resource_type)

    def is_registered(self, resource_type: str) -> bool:
        """Check if a resource type is registered"""
        return resource_type in self._handlers
