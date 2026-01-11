"""This module takes in some JSON files and loops through to gather IDs
of resources from Jamf Pro and then loops through and deletes the resources.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json
import logging
from requests import Response, RequestException

from jamfpy import Tenant
from .backup_manager import BackupManager
from .resource_registry import ResourceRegistry
from .models import OperationResult, BatchResult, OperationStatus

logger = logging.getLogger(__name__)


class JamfResourceDeleter:
    """
    Class that will workout which resources need deleted and then delete them
    """

    def __init__(
        self,
        jamfpy_client: Tenant,
        backup_dir: Optional[Path] = None,
        registry: Optional[ResourceRegistry] = None,
        configure_logging: bool = True,
    ):
        """

        Args:
            jamfpy_client (Tenant): _description_
            backup_dir (Optional[str], optional): _description_. Defaults to None.
            registry (Optional[ResourceRegistry], optional): _description_. Defaults to None.
        """

        if configure_logging:
            root_logger = logging.getLogger()
            if not root_logger.handlers:
                logging.basicConfig(
                    level=logging.INFO, format="%(levelname)s - %(message)s"
                )

        self.logger = logging.getLogger(__name__)

        self.client = jamfpy_client
        self.backup_dir = backup_dir

        if backup_dir:
            self.backup_path = Path(backup_dir)
        else:
            self.backup_path = Path.cwd() / "backups"

        self.backup_manager = BackupManager(self.backup_path)

        self.registry = registry or ResourceRegistry()

    def delete_resource(
        self,
        resource_type: str,
        resource_id: int,
        resource_name: str = "Unknown",
        export: bool = False,
    ) -> OperationResult:
        """Delete a single resource

        Args:
            resource_type (str): _description_
            resource_id (int): _description_
            resource_name (str, optional): _description_. Defaults to "Unknown".
            export (bool, optional): _description_. Defaults to False.

        Returns:
            OperationResult: _description_
        """

        handler_class = self.registry.get_handler_class(resource_type)

        if not handler_class:
            logger.error("Unknown resource type: %s", resource_type)
            return OperationResult(
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
            success: Response = handler.delete(resource_id)

            if success:
                logger.info(
                    "Successfully deleted %s %s (ID: %s)",
                    resource_type,
                    resource_name,
                    resource_id,
                )
                return OperationResult(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=resource_name,
                    status=OperationStatus.SUCCESS,
                    backup_data=backup_data,
                )
            else:
                logger.warning(
                    "Failed to delete %s %s (ID: %s): %s",
                    resource_type,
                    resource_name,
                    resource_id,
                    success.text,
                )
                return OperationResult(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=resource_name,
                    status=OperationStatus.FAILED,
                    error_message=success.text,
                )
        except RequestException as e:
            logger.error(
                "Error deleting %s %s (ID: %s): %s",
                resource_type,
                resource_name,
                resource_id,
                e,
            )
            return OperationResult(
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
        session_backups: Dict[str, list[Dict[str, Any]]] = {}
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
                        "[DRY-RUN] Would delete %s: %s (ID: %s)",
                        resource_type,
                        resource_name,
                        resource_id,
                    )
                    if export:
                        logger.info("[DRY-RUN] Would backup configuration first")

                    results.append(
                        OperationResult(
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

    def restore_from_backup(
        self, backup_filename: str, dry_run: bool = True
    ) -> Optional[BatchResult]:
        """This will restore resources from backup file"""

        backup_path = self.backup_path / backup_filename

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        with open(backup_path, "r") as f:
            backup_data = json.load(f)

        print(f"\n{'=' * 50}")
        print(f"Restoring from backup: {backup_filename}")
        print(f"{'=' * 50}")

        results = []

        for resource_type, resources in backup_data.items():
            handler_class = self.registry.get_handler_class(resource_type)

            if not handler_class:
                logger.error("Unknown resource type: %s", resource_type)
                return None

            handler = handler_class(self.client)

            logger.info("\nRestoring %s...", resource_type)

            for resource in resources:
                resource_name = resource.get("name", "Unkown")
                resource_config = resource.get("configuration")

                if dry_run:
                    logger.info(
                        "[DRY-RUN] Would restore %s: %s", resource_type, resource_name
                    )
                else:
                    logger.info("Restoring %s: %s", resource_type, resource_name)
                    try:
                        success, status_code = handler.create(resource_config)

                        if success:
                            logger.info(
                                "Successfully re-created %s %s: %s",
                                resource_type,
                                resource_name,
                                status_code,
                            )
                            results.append(
                                OperationResult(
                                    resource_type=resource_type,
                                    resource_name=resource_name,
                                    resource_id=0,
                                    status=OperationStatus.SUCCESS,
                                )
                            )
                        else:
                            logger.warning(
                                "Failed to re-create %s %s: %s",
                                resource_type,
                                resource_name,
                                status_code,
                            )
                            results.append(
                                OperationResult(
                                    resource_type=resource_type,
                                    resource_name=resource_name,
                                    resource_id=0,
                                    status=OperationStatus.FAILED,
                                    error_message=status_code,
                                )
                            )
                    except Exception as e:
                        logger.error(
                            "Error re-creating %s %s: %s",
                            resource_type,
                            resource_name,
                            e,
                        )
                print({"=" * 50})

            batch_result = BatchResult(
                total_processed=len(results),
                successful=sum(
                    1 for r in results if r.status == OperationStatus.SUCCESS
                ),
                failed=sum(1 for r in results if r.status == OperationStatus.FAILED),
                skipped=sum(1 for r in results if r.status == OperationStatus.SKIPPED),
                results=results,
                backup_path=backup_path,
            )

        return batch_result
