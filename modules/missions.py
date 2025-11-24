import json
from datetime import datetime, timedelta
import random


class MissionManager:
    def __init__(self, memory_path="data/system_memory.json"):
        self.path = memory_path
        self.data = self.load_memory()

    # ----------------------------------------------------------
    # BASIC MEMORY OPERATIONS
    # ----------------------------------------------------------
    def load_memory(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_memory(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # ----------------------------------------------------------
    # INTERNAL UTILS
    # ----------------------------------------------------------
    def emotional_difficulty_modifier(self):
        emotion = self.data.get("emotion", {})
        stress = emotion.get("stress", 0)
        anxiety = emotion.get("anxiety", 0)
        energy = self.data["stats"].get("energy", 50)

        mod = 0
        if stress > 70: mod += 1
        if anxiety > 70: mod += 1
        if energy < 40: mod += 1
        return mod

    def calculate_difficulty(self, base, mission_type):
        """Compute final difficulty (1–5 range)."""
        diff = base

        # weekly and main quests are inherently harder
        if mission_type in ["weekly", "main_quest"]:
            diff += 1

        diff += self.emotional_difficulty_modifier()

        # clamp between 1 and 5
        return max(1, min(5, diff))

    def calculate_xp(self, difficulty):
        """XP scales with difficulty but is randomized."""
        return random.randint(5 * difficulty, 15 * difficulty)

    def calculate_dark_points(self, difficulty):
        """Dark Points scale with difficulty (1–3 per difficulty)."""
        return difficulty * random.randint(1, 3)

    # ----------------------------------------------------------
    # CREATE MISSION
    # ----------------------------------------------------------
    def create_mission(self, title, description, mission_type, base_difficulty, deadline_days=1):
        now = datetime.now()
        deadline = now + timedelta(days=deadline_days)

        difficulty = self.calculate_difficulty(base_difficulty, mission_type)
        reward_exp = self.calculate_xp(difficulty)
        dark_points = self.calculate_dark_points(difficulty)

        mission = {
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "reward_exp": reward_exp,
            "reward_dark": dark_points,
            "status": "pending",
            "created_at": now.strftime("%Y-%m-%d %H:%M"),
            "deadline": deadline.strftime("%Y-%m-%d %H:%M"),
            "mission_type": mission_type
        }

        self.data["missions"][mission_type].append(mission)
        self.save_memory()
        return mission

    # ----------------------------------------------------------
    # AUTO-GENERATED MISSIONS
    # ----------------------------------------------------------
    def generate_daily_missions(self):
        missions_list = []

        missions_list.append(self.create_mission(
            "Revisión Estratégica del Día",
            "Planifica tu día usando el sistema Isekai.",
            "daily",
            base_difficulty=1,
            deadline_days=1
        ))

        missions_list.append(self.create_mission(
            "Acción Profesional",
            "Avanzar en Mercor, CV o portafolio.",
            "daily",
            base_difficulty=2,
            deadline_days=1
        ))

        missions_list.append(self.create_mission(
            "Romper la Maldición",
            "Haz una microacción de avance.",
            "daily",
            base_difficulty=1,
            deadline_days=1
        ))

        # emotional dynamic missions
        anxiety = self.data["emotion"]["anxiety"]
        if anxiety > 60:
            missions_list.append(self.create_mission(
                "Calm Quest",
                "5 minutos de respiración consciente.",
                "daily",
                base_difficulty=1
            ))

        return missions_list

    def generate_weekly_missions(self):
        missions_list = []

        missions_list.append(self.create_mission(
            "Progreso en Mercor",
            "Aplicar a trabajos, mejorar perfil, enviar portafolio.",
            "weekly",
            base_difficulty=3,
            deadline_days=7
        ))

        missions_list.append(self.create_mission(
            "Avance Académico",
            "Tesis, lecturas o tareas del máster.",
            "weekly",
            base_difficulty=2,
            deadline_days=7
        ))

        missions_list.append(self.create_mission(
            "Mantenimiento del Mundo Exterior",
            "Acción de orden, finanzas o salud.",
            "weekly",
            base_difficulty=1,
            deadline_days=7
        ))

        return missions_list

    # ----------------------------------------------------------
    # COMPLETION
    # ----------------------------------------------------------
    def complete_mission(self, mission_type, index):
        mission = self.data["missions"][mission_type][index]
        mission["status"] = "completed"
        mission["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        # grant EXP
        from modules.stats import StatsManager
        sm = StatsManager(self.path)
        sm.add_exp(mission["reward_exp"])

        # grant dark points
        self.data["dark_points"] = self.data.get("dark_points", 0) + mission["reward_dark"]

        self.save_memory()
        return mission

    # ----------------------------------------------------------
    # FAIL HANDLING
    # ----------------------------------------------------------
    def fail_expired_missions(self):
        now = datetime.now()
        failed = []

        for mtype, missions in self.data["missions"].items():
            for m in missions:
                if m["status"] == "pending":
                    deadline = datetime.strptime(m["deadline"], "%Y-%m-%d %H:%M")
                    if now > deadline:
                        m["status"] = "failed"
                        failed.append(m)

        # punishment: emotional debuff
        if failed:
            from modules.stats import StatsManager
            sm = StatsManager(self.path)

            sm.add_effect(
                name="Frustración por Misiones Incompletas",
                effect_type="debuff",
                duration_hours=24,
                modifiers={"wisdom": -1, "charisma": -1},
                icon="debuff"
            )

        self.save_memory()
        return failed

    # ----------------------------------------------------------
    # CLEANUP
    # ----------------------------------------------------------
    def cleanup_missions(self):
        now = datetime.now()
        for mtype in self.data["missions"]:
            self.data["missions"][mtype] = [
                m for m in self.data["missions"][mtype]
                if (now - datetime.strptime(m["created_at"], "%Y-%m-%d %H:%M")).days < 30
            ]

        self.save_memory()
