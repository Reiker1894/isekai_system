import json
from datetime import datetime, timedelta
import random

class CurseManager:
    def __init__(self, memory_path="data/system_memory.json"):
        self.path = memory_path
        self.data = self.load_memory()

    # ----------------------------------------------------
    # BASE MEMORY OPS
    # ----------------------------------------------------
    def load_memory(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_memory(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # ----------------------------------------------------
    # HELPERS
    # ----------------------------------------------------
    def now(self):
        return datetime.now()

    def hours_since(self, timestamp):
        if timestamp is None:
            return 999
        try:
            prev = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
            delta = self.now() - prev
            return delta.total_seconds() / 3600
        except:
            return 999

    # ----------------------------------------------------
    # CHECK COOLDOWN
    # ----------------------------------------------------
    def can_trigger(self):
        curse = self.data["curse"]
        cooldown = curse.get("cooldown_hours", 12)
        last = curse.get("last_trigger")

        return self.hours_since(last) >= cooldown

    # ----------------------------------------------------
    # MAIN TRIGGER
    # ----------------------------------------------------
    def trigger_curse(self, source="auto"):
        """
        Activa la maldición del Beso de la Bruja.
        Aumenta intensidad, aplica debuff y registra en logs.
        """

        curse = self.data.get("curse", {})
        curse["active"] = True

        # Intensidad escala 1–5
        curse["intensity"] = min(curse.get("intensity", 1) + 1, 5)

        # Marcar tiempo del trigger
        curse["last_trigger"] = self.now().strftime("%Y-%m-%d %H:%M")

        # Registrar
        self.log_event(f"🔥 Maldición activada ({source}). Intensidad: {curse['intensity']}")

        # Aplicar efecto debuff
        self.apply_curse_effect(curse["intensity"])

        self.data["curse"] = curse
        self.save_memory()

        return curse

    # ----------------------------------------------------
    # APPLY STATS EFFECTS
    # ----------------------------------------------------
    def apply_curse_effect(self, intensity):
        """
        Aplica efectos negativos basados en la intensidad.
        """

        from modules.stats import StatsManager
        sm = StatsManager(self.path)

        # tabla de debuffs
        debuffs = {
            1: {"clarity": -3},
            2: {"clarity": -6, "motivation": -4},
            3: {"clarity": -8, "motivation": -6, "wisdom": -1},
            4: {"anxiety": +10, "clarity": -12, "wisdom": -1},
            5: {"anxiety": +20, "clarity": -18, "wisdom": -2, "charisma": -1},
        }

        mods = debuffs.get(intensity, {})

        # Aplicar a emoción directamente
        emotion = self.data.get("emotion", {})
        for stat, val in mods.items():
            emotion[stat] = max(0, min(100, emotion.get(stat, 50) + val))

        self.data["emotion"] = emotion
        self.save_memory()

        # Además: aplicar debuff temporal (24h)
        sm.add_effect(
            name=f"Beso de la Bruja (Nivel {intensity})",
            effect_type="debuff",
            duration_hours=24,
            modifiers=self.convert_to_stat_mods(intensity),
            icon="curse"
        )

    def convert_to_stat_mods(self, intensity):
        """
        Traduce intensidad a penalizaciones de stats numéricos.
        """
        if intensity == 1:
            return {"wisdom": -1}
        elif intensity == 2:
            return {"wisdom": -1, "charisma": -1}
        elif intensity == 3:
            return {"wisdom": -2, "charisma": -1}
        elif intensity == 4:
            return {"wisdom": -2, "charisma": -1, "dexterity": -1}
        else:  # intensidad 5
            return {"wisdom": -3, "charisma": -2, "dexterity": -1}

    # ----------------------------------------------------
    # AUTO CHECK (random chance)
    # ----------------------------------------------------
    def try_auto_trigger(self):
        """
        Activa la maldición de forma automática si:
        - está en cooldown
        - las emociones están débiles
        - RNG lo permite (solo leveling vibe)
        """

        if not self.can_trigger():
            return False

        emotion = self.data.get("emotion", {})
        stress = emotion.get("stress", 50)
        fatigue = emotion.get("fatigue", 40)
        anxiety = emotion.get("anxiety", 40)

        # riesgo base según estado emocional
        risk = 0
        risk += (stress > 60) * 20
        risk += (anxiety > 60) * 20
        risk += (fatigue > 60) * 20

        # Mínimo siempre existe un 5% de probabilidad
        chance = max(5, min(75, risk))

        roll = random.randint(1, 100)

        if roll <= chance:
            self.trigger_curse("auto-RNG")
            return True
        
        return False

    # ----------------------------------------------------
    # MANUAL CONTROL
    # ----------------------------------------------------
    def force_trigger(self):
        """Activa la maldición manualmente desde admin."""
        return self.trigger_curse("manual")

    def dispel(self):
        """
        Apaga la maldición completamente.
        Reinicia intensidad al nivel 1.
        """

        curse = self.data["curse"]
        curse["active"] = False
        curse["intensity"] = 1

        self.log_event("✨ Maldición dispersada manualmente.")
        self.data["curse"] = curse
        self.save_memory()

    # ----------------------------------------------------
    # LOGGING
    # ----------------------------------------------------
    def log_event(self, text):
        log = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "entry": text
        }
        self.data["logs"].append(log)
        self.save_memory()
