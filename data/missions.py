import json
from datetime import datetime, timedelta


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
    # CREATE MISSION OBJECTS
    # ----------------------------------------------------------
    def create_mission(self, title, description, mission_type, difficulty, reward_exp, deadline_days=1):
        """
        mission_type: daily / weekly / side / main
        difficulty: 1 = easy, 2 = medium, 3 = hard, 4 = elite
        """
        now = datetime.now()
        deadline = now + timedelta(days=deadline_days)

        mission = {
            "title": title,
            "description": description,
            "difficulty": difficulty,
            "reward_exp": reward_exp,
            "status": "pending",
            "created_at": now.strftime("%Y-%m-%d %H:%M"),
            "deadline": deadline.strftime("%Y-%m-%d %H:%M"),
            "mission_type": mission_type
        }

        self.data["missions"][mission_type].append(mission)
        self.save_memory()
        return mission

    # ----------------------------------------------------------
    # DAILY / WEEKLY MISSIONS GENERATION (AUTO)
    # ----------------------------------------------------------
    def generate_daily_missions(self):
        """Auto-generates 3–5 missions depending on energy and emotion."""
        energy = self.data["stats"]["energy"]
        emotion = self.data["emotion"]
        missions = []

        # Base mission set
        missions.append(self.create_mission(
            "Revisión Estratégica del Día",
            "Planifica tu día usando tu sistema Isekai.",
            "daily",
            1,
            20,
            deadline_days=1
        ))

        missions.append(self.create_mission(
            "Acción de Avance Profesional",
            "Enviar CV, aplicar a Mercor o avanzar en tu portafolio.",
            "daily",
            2,
            35,
            deadline_days=1
        ))

        missions.append(self.create_mission(
            "Micro-gesto contra el Beso de la Bruja",
            "Realiza una microacción de ruptura cuando sientas parálisis.",
            "daily",
            1,
            25,
            deadline_days=1
        ))

        # If energy is high → add bonus missions
        if energy > 65:
            missions.append(self.create_mission(
                "Estudio Intensivo",
                "30–60 minutos de lectura o estudio técnico.",
                "daily",
                2,
                40
            ))

        # If anxiety is high → assign lighter mission
        if emotion.get("anxiety", 0) > 60:
            missions.append(self.create_mission(
                "Calm Quest",
                "5 minutos de respiración o descanso consciente.",
                "daily",
                1,
                10
            ))

        return missions

    def generate_weekly_missions(self):
        """Auto-generate weekly missions with deadlines (7 days)."""
        missions = []

        missions.append(self.create_mission(
            "Progreso en Mercor",
            "Aplicar a 5 trabajos, mejorar perfil, o enviar portafolio.",
            "weekly",
            3,
            120,
            deadline_days=7
        ))

        missions.append(self.create_mission(
            "Avance Académico",
            "Trabajar en tesis, lecturas o tareas del máster.",
            "weekly",
            2,
            80,
            deadline_days=7
        ))

        missions.append(self.create_mission(
            "Mantenimiento del Mundo Exterior",
            "Realizar una acción que mejore tu vida (orden, finanzas, salud).",
            "weekly",
            1,
            50,
            deadline_days=7
        ))

        return missions

    # ----------------------------------------------------------
    # MISSION COMPLETION OR FAILURE
    # ----------------------------------------------------------
    def complete_mission(self, mission_type, index):
        mission = self.data["missions"][mission_type][index]
        mission["status"] = "completed"
        mission["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        # give EXP
        from modules.stats import StatsManager
        sm = StatsManager(self.path)
        sm.add_exp(mission["reward_exp"])

        self.save_memory()
        return mission

    def fail_expired_missions(self):
        """Automatically mark expired missions as failed, apply debuffs."""
        now = datetime.now()
        failed = []

        for mission_type, missions in self.data["missions"].items():
            for m in missions:
                if m["status"] == "pending":
                    deadline = datetime.strptime(m["deadline"], "%Y-%m-%d %H:%M")
                    if now > deadline:
                        m["status"] = "failed"
                        failed.append(m)

        # Apply emotional debuff (failure penalty)
        if failed:
            from modules.stats import StatsManager
            sm = StatsManager(self.path)

            sm.add_effect(
                name="Frustración por Misiones Incompletas",
                duration_days=2,
                modifiers={"wisdom": -1, "charisma": -1}
            )

        self.save_memory()
        return failed

    # ----------------------------------------------------------
    # CLEANUP COMPLETED / FAILED MISSIONS
    # ----------------------------------------------------------
    def cleanup_missions(self):
        """Remove missions older than 30 days for cleanliness."""
        now = datetime.now()
        for mtype in self.data["missions"]:
            self.data["missions"][mtype] = [
                m for m in self.data["missions"][mtype]
                if (now - datetime.strptime(m["created_at"], "%Y-%m-%d %H:%M")).days < 30
            ]
        self.save_memory()

