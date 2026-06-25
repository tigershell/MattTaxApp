import datetime
import sqlite3
from pathlib import Path
from typing import Optional, List

from ..extensions import db


class BackupManager:
    """Creates and restores snapshots of the SQLite application database.

    Uses SQLite's online backup API, so a snapshot is consistent even if the
    app (or dev server) is running. Backups are timestamped files kept in the
    project's backups/ folder.

    Only supports SQLite (local development). A hosted Postgres database should
    use the provider's managed backups instead.
    """

    def __init__(self, backup_dir: Optional[Path] = None):
        self._backup_dir = Path(backup_dir) if backup_dir else Path.cwd() / "backups"

    def _db_path(self) -> Path:
        """Return the absolute path of the live SQLite database file.

        Reads the resolved engine URL (not the raw config string) so the path is
        correct regardless of how Flask-SQLAlchemy resolved a relative URI.
        Must be called within an application context.
        """
        url = db.engine.url
        if not url.drivername.startswith("sqlite"):
            raise RuntimeError("Backups are only supported for SQLite databases.")
        if not url.database:
            raise RuntimeError("Could not determine the SQLite database path.")
        return Path(url.database)

    def _snapshot(self, source: Path, dest: Path) -> None:
        """Copy `source` SQLite db into `dest` using the safe backup API."""
        src = sqlite3.connect(str(source))
        dst = sqlite3.connect(str(dest))
        try:
            with dst:
                src.backup(dst)
        finally:
            src.close()
            dst.close()

    def create_backup(self) -> Path:
        """Create a timestamped snapshot of the live database.

        Returns:
            The path to the new backup file.
        """
        live = self._db_path()
        if not live.exists():
            raise FileNotFoundError(f"Database not found: {live}")
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = self._backup_dir / f"taxidermatt_{stamp}.db"
        self._snapshot(live, dest)
        return dest

    def list_backups(self) -> List[Path]:
        """Return existing backup files, newest first."""
        if not self._backup_dir.exists():
            return []
        return sorted(self._backup_dir.glob("taxidermatt_*.db"), reverse=True)

    def restore(self, backup_file: str) -> Path:
        """Restore the database from a backup, snapshotting the current one first.

        The current live database is always backed up before being overwritten,
        so a restore can never lose your present data.

        Args:
            backup_file: A backup filename (looked up in backups/) or a full path.

        Returns:
            The path to the safety snapshot taken of the pre-restore database.
        """
        backup_path = Path(backup_file)
        if not backup_path.is_absolute():
            backup_path = self._backup_dir / backup_path
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        live = self._db_path()
        safety = self.create_backup()      # snapshot current DB before overwriting
        self._snapshot(backup_path, live)  # write the chosen backup into the live DB
        return safety
