import json
import random
from datetime import datetime


class WorldManager:
    def __init__(self, memory_path="data/system_memory.json"):
        self.path = memory_path
        self.data = self.load_memory()

    # ----------------------------------------------------------
    # LOAD / SAVE MEMORY
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
    # REINOS DEL MUNDO
    # ----------------------------------------------------------
    def initialize_world(self):
        """Creates world structure if it doesn't exist."""
        if "world" not in self.data:
            self.data["world"] = {
                "realms": {
                    "work": {"progress": 10, "reputation": 5, "difficulty": 2},
                    "politics": {"progress": 5, "reputation": 2, "difficulty": 3},
                    "startup": {"progress": 0, "reputation": 0, "difficulty": 4},
                    "academia": {"progress": 15, "reputation": 8, "difficulty": 2},
                    "finance": {"progress": 10, "reputation": 3, "difficulty": 4},
                    "health": {"progress": 5, "reputation": 1, "difficulty": 3},
                    "family": {"progress": 5, "reputation": 3, "difficulty": 3}
                }
            }
        self.save_memory()

    # ----------------------------------------------------------
    # REAL EVENTS (YOU INPUT THEM)
    # ----------------------------------------------------------
    def register_real_event(self, category, description, intensity=1):
        """
        category: work, family, finance, emotions, politics...
        intensity: 1 = leve, 2 = medio, 3 = fuerte
        """
        event = {
            "type": "real_event",
            "category": category,
            "description": description,
            "intensity": intensity,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        if "events" not in self.data:
            self.data["events"] = []

        self.data["events"].append(event)

        # Apply emotional impact
        self.apply_real_event_impact(event)

        self.save_memory()
        return event

    def apply_real_event_impact(self, event):
        """
        Events influence: stats, boss aggression, realm difficulty, emotions.
        """
        emotion = self.data.get("emotion", {})

        intensity = event["intensity"]

        # Emotional categories
        if event["category"] == "family":
            emotion["stress"] += 10 * intensity
            emotion["anxiety"] += 5 * intensity

        if event["category"] == "work":
            emotion["stress"] += 7 * intensity

        if event["category"] == "finance":
            emotion["anxiety"] += 12 * intensity

        if event["category"] == "emotions":
            emotion["fatigue"] += 8 * intensity

        # Cap values between 0 and 100
        for key in emotion:
            emotion[key] = max(0, min(emotion[key], 100))

        self.data["emotion"] = emotion

        # Notify boss
        self.signal_boss(event)

    # ----------------------------------------------------------
    # SIGNAL BOSS ON REAL EVENTS
    # ----------------------------------------------------------
    def signal_boss(self, event):
        """
        Boss escalates aggression depending on real-world events.
        """
        boss_state = self.data.get("bosses", {})
        if not boss_state:
            return

        from modules.bosses import BossManager
        bm = BossManager(self.path)
        bm.boss_attack()  # triggers emotional-based debuff

    # ----------------------------------------------------------
    # WORLD RANDOM EVENTS (SOFT)
    # ----------------------------------------------------------
    def generate_random_world_event(self):
        """
        These events are harmless and thematic, only affect stats slightly.
        """

        events = [
            {
                "name": "Claridad Fugaz",
                "effect": {"clarity": +10},
                "description": "Tu mente se siente más ligera por unos momentos."
            },
            {
                "name": "Viento de Productividad",
                "effect": {"motivation": +15},
                "description": "Un impulso repentino te anima a avanzar hoy."
            },
            {
                "name": "Sombra de Duda",
                "effect": {"motivation": -10},
                "description": "Un pensamiento pasajero reduce tu iniciativa."
            },
            {
                "name": "Calma Interior",
                "effect": {"anxiety": -12},
                "description": "Una sensación protectora te envuelve."
            },
            {
                "name": "Presagio del Mundo",
                "effect": {"luck": +1},
                "description": "Algo pequeño te sale bien sin explicación."
            }
        ]

        chosen = random.choice(events)

        # apply effect
        emotion = self.data.get("emotion", {})
        for key, val in chosen["effect"].items():
            if key in emotion:
                emotion[key] = min(100, max(0, emotion[key] + val))

        self.data["emotion"] = emotion

        # log event
        if "events" not in self.data:
            self.data["events"] = []

        self.data["events"].append({
            "type": "random_world",
            "name": chosen["name"],
            "description": chosen["description"],
            "date": datetime.now().strftime("%Y-%m-%d")
        })

        self.save_memory()
        return chosen

