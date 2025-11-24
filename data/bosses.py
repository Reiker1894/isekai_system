import json
from datetime import datetime, timedelta
import random


class BossManager:
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
    # BOSS DEFINITIONS
    # ----------------------------------------------------------
    def define_bosses(self):
        """
        Bosses come with 3 phases. Each phase has HP and modifiers.
        """
        return {
            "Beso de la Bruja": {
                "type": "emotional",
                "phases": [
                    {
                        "phase": 1,
                        "name": "Susurro de Parálisis",
                        "hp": 40,
                        "debuff": {"strength": -1},
                        "attack_description": "Invoca dudas y micro-parálisis.",
                        "mission_objective": "Completar una acción pequeña cuando te sientas bloqueado."
                    },
                    {
                        "phase": 2,
                        "name": "Sombras de Auto-Sabotaje",
                        "hp": 60,
                        "debuff": {"wisdom": -1, "dexterity": -1},
                        "attack_description": "Genera pensamientos negativos sobre tu avance.",
                        "mission_objective": "Terminar una micro-tarea en menos de 15 minutos."
                    },
                    {
                        "phase": 3,
                        "name": "Juicio Interno",
                        "hp": 80,
                        "debuff": {"charisma": -1, "luck": -1},
                        "attack_description": "Bloqueo emocional crítico.",
                        "mission_objective": "Realizar un acto de auto-rescate (escribir, salir, mover cuerpo, etc.)."
                    }
                ]
            },

            "Dragón de las Finanzas": {
                "type": "economic",
                "phases": [
                    {
                        "phase": 1,
                        "name": "Gasto Impulsivo",
                        "hp": 50,
                        "debuff": {"wisdom": -1},
                        "attack_description": "Tienta a tomar malas decisiones financieras.",
                        "mission_objective": "Revisar gastos del día."
                    },
                    {
                        "phase": 2,
                        "name": "Niebla de la Deuda",
                        "hp": 70,
                        "debuff": {"clarity": -1},
                        "attack_description": "Te hace sentir perdido en lo económico.",
                        "mission_objective": "Actualizar tu hoja de control financiero."
                    },
                    {
                        "phase": 3,
                        "name": "Furia del Mercado",
                        "hp": 100,
                        "debuff": {"luck": -2},
                        "attack_description": "Provoca impulsos de riesgo y ansiedad.",
                        "mission_objective": "No operar trading durante 24 horas."
                    }
                ]
            }
        }

    # ----------------------------------------------------------
    # CURRENT BOSS STATE
    # ----------------------------------------------------------
    def get_current_boss(self):
        return self.data.get("bosses", {})

    # ----------------------------------------------------------
    # START A BOSS BATTLE FOR THE MONTH
    # ----------------------------------------------------------
    def start_boss_battle(self, boss_name):
        bosses = self.define_bosses()

        if boss_name not in bosses:
            raise Exception("Boss does not exist.")

        self.data["bosses"] = {
            "name": boss_name,
            "phase": 1,
            "current_hp": bosses[boss_name]["phases"][0]["hp"],
            "total_phases": 3,
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "expires": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        }

        self.save_memory()
        return self.data["bosses"]

    # ----------------------------------------------------------
    # BOSS ATTACK (BASED ON EMOTION)
    # ----------------------------------------------------------
    def boss_attack(self):
        """Boss reacts to your emotional state."""
        boss_state = self.get_current_boss()
        if not boss_state:
            return None

        bosses = self.define_bosses()
        boss = bosses[boss_state["name"]]

        phase_index = boss_state["phase"] - 1
        phase = boss["phases"][phase_index]

        emotion = self.data.get("emotion", {})
        anxiety = emotion.get("anxiety", 0)
        fatigue = emotion.get("fatigue", 0)
        stress = emotion.get("stress", 0)

        # Boss attacks harder based on emotional vulnerability
        trigger_chance = (anxiety + fatigue + stress) / 3

        if trigger_chance > 50:
            # Apply debuff to stats
            from modules.stats import StatsManager
            sm = StatsManager(self.path)
            sm.add_effect(
                name=f"Ataque de {phase['name']}",
                duration_days=1,
                modifiers=phase["debuff"]
            )
            return f"⚠ {phase['attack_description']} (Ataque activado)"

        return "El boss observó… no atacó."

    # ----------------------------------------------------------
    # PLAYER DAMAGES THE BOSS
    # ----------------------------------------------------------
    def damage_boss(self, amount):
        boss_state = self.get_current_boss()
        if not boss_state:
            return None

        boss_state["current_hp"] -= amount

        # Phase cleared?
        if boss_state["current_hp"] <= 0:
            boss_state["phase"] += 1

            if boss_state["phase"] > boss_state["total_phases"]:
                # Victory!
                self.apply_victory_rewards()
                boss_state["defeated"] = True
                boss_state["current_hp"] = 0
            else:
                bosses = self.define_bosses()
                next_hp = bosses[boss_state["name"]]["phases"][boss_state["phase"] - 1]["hp"]
                boss_state["current_hp"] = next_hp

        self.save_memory()
        return boss_state

    # ----------------------------------------------------------
    # REWARDS FOR DEFEATING THE BOSS
    # ----------------------------------------------------------
    def apply_victory_rewards(self):
        """Boss defeat rewards."""
        from modules.stats import StatsManager
        sm = StatsManager(self.path)

        # Big rewards
        sm.add_exp(300)
        sm.add_effect(
            name="Victoria Heroica",
            duration_days=5,
            modifiers={"wisdom": +2, "charisma": +1}
        )

        return "🎉 Boss derrotado. Obtuviste grandes recompensas."

