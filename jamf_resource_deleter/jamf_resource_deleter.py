"""This module takes in some JSON files and loops through to gather IDs
of resources from Jamf Pro and then loops through and deletes the resources.
"""

from datetime import datetime
from typing import Dict, Callable, Optional
from pathlib import Path
import json
from jamfpy import Tenant
from requests import HTTPError


class JamfResourceDeleter:
    """
    Class that will workout which resources need deleted and then delete them
    """

    def __init__(self, jamfpy_client: Tenant, backup_dir: Optional[str] = None):
        """Initialise the JamfResourceDeleter object

        Args:
            jamfpy_client (jamfpy.Tenant object): Pass a JamfPy instance to this method
        """
        self.script_dir = Path(__file__).parent

        if backup_dir:
            self.backup_dir = Path(backup_dir)
        else:
            self.backup_dir = self.script_dir / "backups"

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.jamfpy_client = jamfpy_client

        self.resource_handlers: Dict[str, Dict[str, Callable]] = {
            "unusedComputers": {
                "delete": self._delete_computers,
                "get": self._get_computers,
            },
            "unusedComputerGroups": {
                "delete": self._delete_computer_group,
                "get": self._get_computer_groups,
            },
            "unusedMacApps": {
                "delete": self._delete_apps, 
                "get": self._get_apps
            },
            "unusedMobileDeviceApps": {
                "delete": self._delete_apps,
                "get": self._get_apps,
            },
            "unusedPackages": {
                "delete": self._delete_packages,
                "get": self._get_packages,
            },
            "unusedPolicies": {
                "delete": self._delete_policies,
                "get": self._get_policies,
            },
            "unusedComputerProfiles": {
                "delete": self._delete_profiles,
                "get": self._get_profiles,
            },
            "unusedScripts": {"delete": self._delete_scripts, "get": self._get_scripts},
            "unusedComputerEAs": {
                "delete": self._delete_computer_extension_attributes,
                "get": self._get_computer_extension_attributes,
            },
            "unusedRestrictedSoftware": {
                "delete": self._delete_restricted_software,
                "get": self._get_restricted_software,
            },
        }

    # Deletion methods
    def _delete_computers(self, resource_id: int) -> bool:
        """Export and delete computer by ID"""
        return self.jamfpy_client.classic.computers.delete_by_id(resource_id)

    def _delete_computer_group(self, resource_id: int) -> bool:
        """Delete a computer group by ID"""
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



    # Get Methods
    def _get_computers(self, resource_id: int) -> Optional[Dict]:
        """Get computer configuration by ID"""
        try:
            return self.jamfpy_client.classic.computers.get_by_id(resource_id)
        except HTTPError as e:
            print(f"Could not retrieve computer {resource_id}: {e}")
            return None

    def _get_computer_groups(self, resource_id: int) -> Optional[Dict]:
        """Get computer group configuration by ID"""
        try:
            return self.jamfpy_client.classic.computer_groups.get_by_id(resource_id)
        except HTTPError as e:
            print(f"Could not retrieve computer group {resource_id}: {e}")
            return None

    def _get_apps(self, resource_id: int) -> Optional[Dict]:
        """Get apps configuration by ID"""
        print(f"App Installers cannot be exported - App Installed {resource_id} not exported")
        return None
    
    def _get_packages(self, resource_id: int) -> Optional[Dict]:
        """Get packages by ID"""
        try:
            return self.jamfpy_client.classic.packages.get_by_id(resource_id)
        except HTTPError as e:
            print(f"Could not retrieve package {resource_id}: {e}")
            return None
        
    def _get_policies(self, resource_id: int) -> Optional[Dict]:
        """Get policy by ID"""
        try:
            return self.jamfpy_client.classic.policies.get_by_id(resource_id)
        except HTTPError as e:
            print(f"Could not retrieve policy {resource_id}: {e}")
            return None
        
    def _get_profiles(self, resource_id: int) -> Optional[Dict]:
        """Get Profile config by ID"""
        try:
            return self.jamfpy_client.classic.configuration_profiles.get_by_id(resource_id)
        except HTTPError as e:
            print(f"Could not retrieve profile {resource_id}: {e}")
            return None
        
    def _get_scripts(self, resource_id: int) -> Optional[Dict]:
        """Get script by ID"""
        try:
            return self.jamfpy_client.classic.scripts.get_by_id(resource_id)
        except HTTPError as e:
            print(f"Could not retrieve script {resource_id}: {e}")
            return None
        
    def _get_computer_extension_attributes(self, resource_id: int) -> Optional[Dict]:
        """Get Computer Extension Attribute by ID"""
        try:
            return self.jamfpy_client.classic.computer_extension_attributes.get_by_id(resource_id)
        except HTTPError as e:
            print(f"Could not retrieve Extension Attribute {resource_id}: {e}")
            return None
        
    def _get_restricted_software(self, resource_id: int) -> Optional[Dict]:
        """Get restricted software by ID"""
        try:
            return self.jamfpy_client.classic.restricted_software.get_by_id(resource_id)
        except HTTPError as e:
            print(f"Could not retrieve restricted software {resource_id}: {e}")
            return None


    def export_resource(self, resource_type: str, resource_id: int) -> Optional[Dict]:
        """_summary_

        Args:
            resource_type (str): _description_
            resource_id (int): _description_

        Returns:
            Optional[Dict]: _description_
        """
        handler = self.resource_handlers.get(resource_type, {}).get('get')

        if not handler:
            print(f"No export handler for resource type: {resource_type}")
            return None
        
        try:
            return handler(resource_id)
        except Exception as e:
            print(f"Error exporting {resource_type} ID {resource_id}: {e}")
            return None
        
    def save_backup(self, backup_data: Dict, timestamp: str) -> str:
        """_summary_

        Args:
            backup_data (Dict): _description_
            timestamp (str): _description_

        Returns:
            str: _description_
        """
        backup_filename = f"backup_{timestamp}.json"
        backup_path = self.backup_dir / backup_filename
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2)

        return str(backup_path)



    def delete_resource(self, resource_type: str, resource_id: int, export: bool = False) -> tuple[bool, Optional[Dict]]:
        """_summary_

        Args:
            resource_type (str): _description_
            resource_id (int): _description_
            export (bool, optional): _description_. Defaults to False.

        Raises:
            ValueError: _description_

        Returns:
            tuple[bool, Optional[Dict]]: _description_
        """

        backup_data = None

        if export:
            backup_data = self.export_resource(resource_type, resource_id)
            if backup_data:
                print("Backed up configuration")


        handler = self.resource_handlers.get(resource_type, {}).get('delete')

        if not handler:
            raise ValueError(f"Unknown resource type: {resource_type}")

        try:
            success = handler(resource_id)
            return success, backup_data
        except HTTPError as e:
            print(f"Error deleting {resource_type} with ID: {resource_id}: {e}")
            return False, backup_data

    def delete_from_json(self, json_file_path: Path, dry_run: bool = True, export: bool = False):
        """This method will take a file path of a JSON file and loop through each
        resouce and get the ID, then attempt to delete that resource

        Args:
            json_file_path (Path): File path of the JSON file
            dry_run (bool, optional): This will determine if the method should delete the resource, or just test. Defaults to True.
        """

        if not json_file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")
        
        with open(json_file_path, "r") as f:
            unused_resources = json.load(f)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        session_backups = {}


        for resource_type, resource_list in unused_resources.items():
            print(f"\nProcessing {resource_type}...")

            if export and not dry_run:
                session_backups[resource_type] = []

            for resource in resource_list:
                resource_id = resource.get("id")
                resource_name = resource.get("name", "Unknown")

                if dry_run:
                    print(
                        f" [DRY-RUN] Would delete {resource_type}: {resource_name} (ID: {resource_id})"
                    )
                    if export:
                            print("[DRY-RUN] Would backup configuration first")
                else:
                    print(
                        f"Deleting {resource_type}: {resource_name} (ID: {resource_id})"
                    )
                    success, backup_data = self.delete_resource(
                        resource_type=resource_type,
                        resource_id=resource_id,
                        export=export
                    )

                    if success:
                        print("Sucessfully deleted")

                        if export and backup_data:
                            session_backups[resource_type].append({
                                'id': resource_id,
                                'name': resource_name,
                                'configuration': backup_data
                            })
                    else:
                        print("Failed to delete")

                if export and not dry_run and session_backups:
                    backup_path = self.save_backup(session_backups, timestamp)
                    print(f"Backup saved to: {backup_path}")

    def list_backups(self) -> list:
        """List all backup files"""
        backup_files = sorted(self.backup_dir.glob("backup_*.json"), reverse=True)
        return [f.name for f in backup_files]
    
    def restore_from_backup(self, backup_filename: str, dry_run: bool = True):
        """TO_DO WORK IN PROGRESS"""

        backup_path = self.backup_dir / backup_filename

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        with open(backup_path, 'r') as f:
            backup_data = json.load(f)

        print(f"\n{'=' * 50}")
        print(f"Restoring from backup: {backup_filename}")
        print(f"{'=' * 50}")

        for resource_type, resources in backup_data.items():
            print(f"\nRestoring {resource_type}...")

            for resource in resources:
                resource_name = resource.get("name", "Unkown")
                resource_config = resource.get("configuration")

            if dry_run:
                print(f"[DRY-RUN] Would restore {resource_type}: {resource_name}")
            else:
                print(f"Restoring {resource_type}: {resource_name}...")
                # TODO Add in logic here for restoring from file to Jamf Pro
                # Needs more thinking
                print("Restoration not implemented yet")
