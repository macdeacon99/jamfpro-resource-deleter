from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json


class BackupManager:
    """Handles backup operations of Jamf Resources"""

    def __init__(self, backup_dir: Path):
        self.backup_dir = backup_dir

        # What if it already exists?
        self.backup_dir.mkdir(parents=True, exist_ok=True)


    def save_backup(self, backup_data: Dict, timestamp: Optional[str]) -> str:
        """Save backup data to a JSON file"""

        # Consider using .timestamp for epoch. It's less readable but easier to handle, no format required.
        # Easier to match if you're just looking for matches etc.
        if timestamp is None:
            timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")

        backup_filename = f"backup_{timestamp}.json"
        backup_path = self.backup_dir / backup_filename

        # Have you verified this always appends correctly and makes the file if not?
        # what if you run the tool twice on the same dir? I'm not sure how right I am.
        with open(backup_path, "w") as f:
            json.dump(backup_data, f, indent=2)

        return str(backup_path)


    def list_backups(self) -> List[str]:
        """List all backup files in chronological order"""
        backup_files = sorted(self.backup_dir.glob("backup_*.json"), reverse=True)
        return [f.name for f in backup_files]


    def load_backup(self, backup_filename: str) -> Dict:
        """Load a backup file"""

        backup_path = self.backup_dir / backup_filename

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        with open(backup_path, "r") as f:
            return json.load(f)
