import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import login_required

from ..logic.backup_manager import BackupManager

backup_bp = Blueprint("backup", __name__)


def _human_size(num: float) -> str:
    """Format a byte count as a human-readable size."""
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.0f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"


def _list_backups():
    """Return display info for existing backups, newest first."""
    files = []
    for p in BackupManager().list_backups():
        stat = p.stat()
        files.append({
            "name": p.name,
            "size": _human_size(stat.st_size),
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%d %b %Y, %H:%M"),
        })
    return files


@backup_bp.route("/backup")
@login_required
def index():
    """Backup & restore page."""
    return render_template("backup/index.html", backups=_list_backups())


@backup_bp.route("/backup/download")
@login_required
def download_new():
    """Create a fresh snapshot and download it straight away.

    A copy is also kept on the machine in backups/, so one click gives you both
    a local backup and a downloaded file you can store anywhere (e.g. cloud).
    """
    dest = BackupManager().create_backup()
    return send_file(dest, as_attachment=True, download_name=dest.name)


@backup_bp.route("/backup/download/<path:filename>")
@login_required
def download_existing(filename: str):
    """Download a previously created backup by name."""
    match = next((p for p in BackupManager().list_backups() if p.name == filename), None)
    if not match:
        abort(404)
    return send_file(match, as_attachment=True, download_name=match.name)


@backup_bp.route("/backup/restore", methods=["POST"])
@login_required
def restore():
    """Restore the database from a chosen backup (current data snapshotted first)."""
    filename = request.form.get("filename", "")
    mgr = BackupManager()
    if not any(p.name == filename for p in mgr.list_backups()):
        flash("Backup not found.", "error")
        return redirect(url_for("backup.index"))
    safety = mgr.restore(filename)
    flash(
        f"Database restored from {filename}. Your previous data was saved as "
        f"{safety.name} — restore that if you need to undo this."
    )
    return redirect(url_for("backup.index"))
