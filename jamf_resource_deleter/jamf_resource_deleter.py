"""This module takes in some JSON files and loops through to gather IDs
of resources from Jamf Pro and then loops through and deletes the resources.
"""

from typing import Dict, Callable
from pathlib import Path
import json
import jamfpy
from requests import HTTPError


class JamfResourceDeleter:
    """
    Class that will workout which resources need deleted and then delete them
    """

    def __init__(self, jamfpy_client):
        """Initialise the JamfResourceDeleter object

        Args:
            jamfpy_client (jamfpy.Tenant object): Pass a JamfPy instance to this method
        """
        self.jamfpy_client: jamfpy.Tenant = jamfpy_client

        self.resource_handlers: Dict[str, Callable] = {
            "unusedComputerGroups": self._delete_computer_group,
            "unusedMacApps": self._delete_apps,
            "unusedMobileDeviceApps": self._delete_apps,
            "unusedPackages": self._delete_packages,
            "unusedPolicies": self._delete_policies,
            "unusedComputerProfiles": self._delete_profiles,
            "unusedScripts": self._delete_scripts,
            "unusedComputerEAs": self._delete_computer_extension_attributes,
            "unusedRestrictedSoftware": self._delete_restricted_software,
        }

    def _delete_computer_group(self, resource_id: int) -> bool:
        """Delete a computer group by ID"""
        a = self.jamfpy_client.classic.computer_groups.get_by_id(resource_id)
        print(a)
        return self.jamfpy_client.classic.computer_groups.delete_by_id(resource_id)

    def _delete_apps(self, resource_id: int) -> bool:
        """Delete a mac app by ID"""
        return self.jamfpy_client.pro.app_installers.delete(resource_id)

    def _delete_packages(self, resource_id: int) -> bool:
        """Delete a package by ID"""
        return self.jamfpy_client.classic.packages.delete_by_id(resource_id)

    def _delete_policies(self, resource_id: int) -> bool:
        """Delete a policy by ID"""
        return self.jamfpy_client.classic.policies.delete_by_id(resource_id)

    def _delete_profiles(self, resource_id: int) -> bool:
        """Delete a profile by ID"""
        return self.jamfpy_client.classic.configuration_profiles.delete_by_id(
            resource_id
        )

    def _delete_scripts(self, resource_id: int) -> bool:
        """Delete a script by ID"""
        return self.jamfpy_client.classic.scripts.delete_by_id(resource_id)

    def _delete_computer_extension_attributes(self, resource_id: int) -> bool:
        """Delete an extension attribute by ID"""
        return self.jamfpy_client.classic.computer_extension_attributes.delete_by_id(
            resource_id
        )

    def _delete_restricted_software(self, resource_id: int) -> bool:
        """Delete a restricted software by ID"""
        return self.jamfpy_client.classic.restricted_software.delete_by_id(resource_id)

    def delete_resource(self, resource_type: str, resource_id: int) -> bool:
        """
        This method will determin what the resource type is and then delete the resources of that type.

        :param self: Passing the current instance
        :param resource_type: A string of which resource type it is
        :type resource_type: str
        :param resource_id: The ID of the resource being deleted
        :type resource_id: int
        :return: Returns True or False if resource was deleted
        :rtype: bool
        """

        handler = self.resource_handlers.get(resource_type)

        if not handler:
            raise ValueError(f"Unknown resource type: {resource_type}")

        try:
            return handler(resource_id)
        except HTTPError as e:
            print(f"Error deleting {resource_type} with ID: {resource_id}: {e}")
            return False

    def delete_from_json(self, json_file_path: Path, dry_run: bool = True):
        """This method will take a file path of a JSON file and loop through each
        resouce and get the ID, then attempt to delete that resource

        Args:
            json_file_path (Path): File path of the JSON file
            dry_run (bool, optional): This will determine if the method should delete the resource, or just test. Defaults to True.
        """
        with open(json_file_path, "r") as f:
            unused_resources = json.load(f)

        for resource_type, resource_list in unused_resources.items():
            print(f"\nProcessing {resource_type}...")

            for resource in resource_list:
                resource_id = resource.get("id")
                resource_name = resource.get("name", "Unknown")

                if dry_run:
                    print(
                        f" [DRY-RUN] Would delete {resource_type}: {resource_name} (ID: {resource_id})"
                    )
                else:
                    print(
                        f"Deleting {resource_type}: {resource_name} (ID: {resource_id})"
                    )
                    success = self.delete_resource(resource_type, resource_id)
                    print("Successfully Deleted" if success else "Failed to delete")
