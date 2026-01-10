"""This module takes in some JSON files and loops through to gather IDs
of resources from Jamf Pro and then loops through and deletes the resources.
"""

from typing import Optional
from pathlib import Path
from datetime import datetime
import json
import logging

from jamfpy import Tenant
from .backup_manager import BackupManager
from .resource_registry import ResourceRegistry
from .models import DeletionResult, BatchResult, OperationStatus

logger = logging.getLogger(__name__)


class JamfResourceDeleter:
    """
    Class that will workout which resources need deleted and then delete them
    """

    def __init__(
        self,
        jamfpy_client: Tenant,
        backup_dir: Optional[str] = None,
        registry: Optional[ResourceRegistry] = None,
    ):
        """

        Args:
            jamfpy_client (Tenant): _description_
            backup_dir (Optional[str], optional): _description_. Defaults to None.
            registry (Optional[ResourceRegistry], optional): _description_. Defaults to None.
        """

        self.client = jamfpy_client
        self.backup_dir = backup_dir

        if backup_dir:
            backup_path = Path(backup_dir)
        else:
            backup_path = Path(__file__).parent / "backups"

        self.backup_manager = BackupManager(backup_path)

        self.registry = registry or ResourceRegistry()

    def delete_resource(
        self,
        resource_type: str,
        resource_id: int,
        resource_name: str = "Unknown",
        export: bool = False,
    ) -> DeletionResult:
        """Delete a single resource

        Args:
            resource_type (str): _description_
            resource_id (int): _description_
            resource_name (str, optional): _description_. Defaults to "Unknown".
            export (bool, optional): _description_. Defaults to False.

        Returns:
            DeletionResult: _description_
        """

        handler_class = self.registry.get_handler_class(resource_type)

        if not handler_class:
            logger.error("Unknown resource type: %s", resource_type)
            return DeletionResult(
                resource_type=resource_type,
                resource_id=resource_id,
                resource_name=resource_name,
                status=OperationStatus.FAILED,
                error_message=f"Unkown resource type: {resource_type}",
            )

        handler = handler_class(self.client)
        backup_data = None

        if export:
            backup_data = handler.get(resource_id)
            if backup_data:
                logger.info(
                    "Backed up %s %s (ID: %s)",
                    resource_type,
                    resource_name,
                    resource_id,
                )

        try:
            success = handler.delete(resource_id)

            if success:
                logger.info(
                    "Successfully deleted %s %s (ID: %s)",
                    resource_type,
                    resource_name,
                    resource_id,
                )
                return DeletionResult(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=resource_name,
                    status=OperationStatus.SUCCESS,
                    backup_data=backup_data,
                )
            else:
                logger.warning(
                    "Failed to delete %s %s (ID: %s)",
                    resource_type,
                    resource_name,
                    resource_id,
                )
                return DeletionResult(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=resource_name,
                    status=OperationStatus.FAILED,
                    error_message="Deletion returned false",
                )
        except Exception as e:
            logger.error(
                "Error deleting %s %s (ID: %s)",
                resource_type,
                resource_name,
                resource_id,
            )
            return DeletionResult(
                resource_type=resource_type,
                resource_id=resource_id,
                resource_name=resource_name,
                status=OperationStatus.FAILED,
                error_message=str(e),
                backup_data=backup_data,
            )

    def delete_from_json(
        self, json_file_path: Path, dry_run: bool = True, export: bool = False
    ) -> BatchResult:
        """Delete resources from a JSON file

        Args:
            json_file_path (Path): _description_
            dry_run (bool, optional): _description_. Defaults to True.
            export (bool, optional): _description_. Defaults to False.

        Returns:
            BatchResult: _description_
        """

        if not json_file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")

        with open(json_file_path, "r") as f:
            unused_resources = json.load(f)

        timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
        session_backups = {}
        results = []

        for resource_type, resource_list in unused_resources.items():
            logger.info("Processing %s...", resource_type)

            if export and not dry_run:
                session_backups[resource_type] = []

            for resource in resource_list:
                resource_id = resource.get("id")
                resource_name = resource.get("name")

                if dry_run:
                    logger.info(
                        "[DRY-RUN] Would delete %s:%s (ID: %s)",
                        resource_type,
                        resource_name,
                        resource_id,
                    )
                    if export:
                        logger.info("[DRY-RUN] Would backup configuration first")

                    results.append(
                        DeletionResult(
                            resource_type=resource_type,
                            resource_id=resource_id,
                            resource_name=resource_name,
                            status=OperationStatus.SKIPPED,
                        )
                    )
                else:
                    result = self.delete_resource(
                        resource_type=resource_type,
                        resource_id=resource_id,
                        resource_name=resource_name,
                        export=export,
                    )
                    results.append(result)

                    if export and result.backup_data:
                        session_backups[resource_type].append(
                            {
                                "id": resource_id,
                                "name": resource_name,
                                "configuration": result.backup_data,
                            }
                        )

        backup_path = None
        if export and not dry_run and session_backups:
            backup_path = self.backup_manager.save_backup(session_backups, timestamp)
            logger.info("Backup saved to: %s", backup_path)

        batch_result = BatchResult(
            total_processed=len(results),
            successful=sum(1 for r in results if r.status == OperationStatus.SUCCESS),
            failed=sum(1 for r in results if r.status == OperationStatus.FAILED),
            skipped=sum(1 for r in results if r.status == OperationStatus.SKIPPED),
            results=results,
            backup_path=backup_path,
        )

        return batch_result

    def list_backups(self) -> list:
        """List all backup files"""
        return self.backup_manager.list_backups()

    def restore_from_backup(self, backup_filename: str, dry_run: bool = True):
        """TO_DO WORK IN PROGRESS"""

        backup_path = self.backup_dir / backup_filename

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        with open(backup_path, "r") as f:
            backup_data = json.load(f)

        print(f"\n{'=' * 50}")
        print(f"Restoring from backup: {backup_filename}")
        print(f"{'=' * 50}")

        for resource_type, resources in backup_data.items():
            print(f"\nRestoring {resource_type}...")

            for resource in resources:
                resource_name = resource.get("name", "Unkown")
                # resource_config = resource.get("configuration")

            if dry_run:
                print(f"[DRY-RUN] Would restore {resource_type}: {resource_name}")
            else:
                print(f"Restoring {resource_type}: {resource_name}...")
                # TODO Add in logic here for restoring from file to Jamf Pro
                # Needs more thinking
                print("Restoration not implemented yet")
