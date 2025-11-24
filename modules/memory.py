import json
import os
from datetime import datetime
from pathlib import Path


class MemoryManager:
    def __init__(self, memory_path="data/system_memory.json", backup_dir="data/backups/"):
        self.memory_path = memory_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------------------------
    # LOAD & SAVE MEMORY
    # ----------------------------------------------------------
    def load_memory(self):
        """Load main memory file."""
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_memory(self, data):
        """Save main memory file."""
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ----------------------------------------------------------
    # DAILY BACKUP SYSTEM
    # ----------------------------------------------------------
    def auto_backup(self):
        """Create a daily backup based on the date."""
        today = datetime.now().strftime("%Y-%m-%d")
        backup_path = self.backup_dir / f"{today}.json"

        # If backup already exists, skip
        if backup_path.exists():
            return "Backup for today already exists."

        # Create backup
        data = self.load_memory()

        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return f"Backup created: {backup_path}"

    # ----------------------------------------------------------
    # MANUAL BACKUP
    # ----------------------------------------------------------
    def manual_backup(self, name):
        """
        Create a backup with a custom name.
        Example: manual_backup('post_boss_victory')
        """
        safe_name = name.replace(" ", "_")
        backup_path = self.backup_dir / f"{safe_name}.json"

        data = self.load_memory()

        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return f"Manual backup created: {backup_path}"

    # ----------------------------------------------------------
    # RESTORE FROM BACKUP
    # ----------------------------------------------------------
    def restore_backup(self, filename):
        """Restore system state from a backup file."""
        backup_path = self.backup_dir / filename

        if not backup_path.exists():
            raise FileNotFoundError("Backup file doesn't exist.")

        with open(backup_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # overwrite main memory
        self.save_memory(data)
        return f"Restored system state from: {filename}"

    # ----------------------------------------------------------
    # EXPORT NARRATIVE (CHAPTER LOG)
    # ----------------------------------------------------------
    def export_day_as_chapter(self, date):
        """
        Export the memory of a given backup date as a narrative chapter.
        """
        backup_path = self.backup_dir / f"{date}.json"

        if not backup_path.exists():
            return "No backup exists for this date."

        with open(backup_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Build narrative
        chapter = f"📜 CAPÍTULO DEL {date}\n"
        chapter += "============================\n\n"

        # STATS
        stats = data.get("stats", {})
        chapter += "📊 ESTADÍSTICAS DEL PERSONAJE:\n"
        for k, v in stats.items():
            chapter += f"  - {k}: {v}\n"

        chapter += "\n🧠 ESTADO EMOCIONAL:\n"
        for k, v in data.get("emotion", {}).items():
            chapter += f"  - {k}: {v}\n"

        chapter += "\n🗺️ ESTADO DEL MUNDO:\n"
        for realm, info in data.get("world", {}).get("realms", {}).items():
            chapter += f"  - {realm.capitalize()}: progreso {info['progress']}%, reputación {info['reputation']}\n"

        chapter += "\n⚔️ BOSS DEL MES:\n"
        boss = data.get("bosses", {})
        if boss:
            chapter += f"  - {boss.get('name')} (Fase {boss.get('phase')}, HP actual: {boss.get('current_hp')})\n"
        else:
            chapter += "  - No había boss activo.\n"

        chapter += "\n📜 EVENTOS DEL DÍA:\n"
        for e in data.get("events", []):
            if e.get("date") == date:
                chapter += f"  - {e['type'].upper()}: {e['description']}\n"

        return chapter
