import json
from datetime import datetime, timedelta
import random


class StatsManager:
    def __init__(self, memory_path="data/system_memory.json"):
        self.path = memory_path
        self.data = self.load_memory()

    # ----------------------------------------------------------
    # BASIC FILE OPERATIONS
    # ----------------------------------------------------------
    def load_memory(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠ No memory file found. Creating a new one.")
            return {}

    def save_memory(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # ----------------------------------------------------------
    # BASE STATS
    # ----------------------------------------------------------
    def base_stats(self):
        return self.data.get("stats", {})

    # ----------------------------------------------------------
    # EMOTIONAL MODIFIERS
    # ----------------------------------------------------------
    def emotional_modifiers(self):
        emotion = self.data.get("emotion", {})
        mods = {
            "strength": 0, "intelligence": 0, "wisdom": 0,
            "charisma": 0, "dexterity": 0, "luck": 0
        }

        stress = emotion.get("stress", 0)
        anxiety = emotion.get("anxiety", 0)
        motivation = emotion.get("motivation", 0)
        clarity = emotion.get("clarity", 0)
        fatigue = emotion.get("fatigue", 0)

        # NEGATIVE STATES
        if anxiety > 65: mods["wisdom"] -= 1
        if stress > 70: mods["charisma"] -= 1
        if fatigue > 60: mods["strength"] -= 1
        if clarity < 30: mods["intelligence"] -= 1
        if motivation < 25: mods["luck"] -= 1

        # POSITIVE STATES
        if motivation > 80: mods["wisdom"] += 1
        if clarity > 75: mods["intelligence"] += 1
        if stress < 30 and clarity > 60: mods["dexterity"] += 1

        return mods

    # ----------------------------------------------------------
    # EFFECT (BUFF/DEBUFF) SYSTEM
    # ----------------------------------------------------------
    def active_effects(self):
        """Return effects that haven't expired; remove expired ones."""
        effects = self.data.get("effects", [])
        now = datetime.now()

        cleaned = []
        for e in effects:
            expiry = datetime.strptime(e["expires_at"], "%Y-%m-%d %H:%M")
            if expiry > now:
                cleaned.append(e)

        self.data["effects"] = cleaned
        self.save_memory()
        return cleaned

    def apply_effect_modifiers(self):
        effects = self.active_effects()

        mods = {
            "strength": 0, "intelligence": 0, "wisdom": 0,
            "charisma": 0, "dexterity": 0, "luck": 0
        }

        for e in effects:
            for stat, value in e.get("modifiers", {}).items():
                mods[stat] += value

        return mods

    def add_effect(self, name, effect_type, duration_hours, modifiers, icon="default"):
        now = datetime.now()
        expiry = now + timedelta(hours=duration_hours)

        effect = {
            "name": name,
            "type": effect_type,   # buff | debuff
            "start_at": now.strftime("%Y-%m-%d %H:%M"),
            "expires_at": expiry.strftime("%Y-%m-%d %H:%M"),
            "modifiers": modifiers,
            "icon": icon
        }

        if "effects" not in self.data:
            self.data["effects"] = []

        self.data["effects"].append(effect)
        self.save_memory()
        return effect

    # ----------------------------------------------------------
    # CURSE SYSTEM — "BESO DE LA BRUJA"
    # ----------------------------------------------------------
    def curse_engine(self):
        """Latent curse activation + intensity scaling."""
        curse = self.data.get("curse", {})
        emotion = self.data.get("emotion", {})

        stress = emotion.get("stress", 0)
        anxiety = emotion.get("anxiety", 0)
        fatigue = emotion.get("fatigue", 0)

        now = datetime.now()

        # check cooldown
        last = curse.get("last_trigger")
        if last:
            last_time = datetime.strptime(last, "%Y-%m-%d %H:%M")
            cd_hours = curse.get("cooldown_hours", 12)
            if now - last_time < timedelta(hours=cd_hours):
                return  # still on cooldown

        # probability of activation = based on emotional stressors
        probability = 0

        if stress > 70: probability += 30
        if anxiety > 70: probability += 30
        if fatigue > 60: probability += 15
        if stress > 80 or anxiety > 80: probability += 40

        # roll
        roll = random.randint(1, 100)

        if roll <= probability:
            self.trigger_curse()
            curse["last_trigger"] = now.strftime("%Y-%m-%d %H:%M")
            self.save_memory()

    def trigger_curse(self):
        """Activate the Beso de la Bruja debuff."""
        intensity = random.choice([1, 2, 3, 4])

        modifiers = {
            1: {"energy": -10, "motivation": -5, "clarity": -5},
            2: {"energy": -15, "motivation": -8, "clarity": -7},
            3: {"energy": -20, "motivation": -10, "clarity": -10},
            4: {"energy": -25, "motivation": -15, "clarity": -12}
        }[intensity]

        # convert them into stat modifiers
        stat_mods = {
            "wisdom": -(2 if intensity >= 2 else 1),
            "charisma": -1,
            "intelligence": -1 if intensity >= 3 else 0
        }

        self.add_effect(
            "Beso de la Bruja",
            "debuff",
            duration_hours=random.randint(12, 48),
            modifiers=stat_mods,
            icon="curse"
        )

        # apply raw emotion hits
        emo = self.data["emotion"]
        emo["motivation"] = max(0, emo["motivation"] + modifiers["motivation"])
        emo["clarity"] = max(0, emo["clarity"] + modifiers["clarity"])
        emo["fatigue"] = min(100, emo["fatigue"] + intensity * 5)

        self.data["curse"]["active"] = True
        self.data["curse"]["intensity"] = intensity
        self.save_memory()

    # ----------------------------------------------------------
    # FINAL STATS = BASE + EMOTION MODS + EFFECT MODS
    # ----------------------------------------------------------
    def final_stats(self):
        base = self.base_stats()
        emo = self.emotional_modifiers()
        eff = self.apply_effect_modifiers()

        final = {}
        for stat, value in base.items():
            if stat in ["level", "exp", "exp_to_next_level", "energy", "max_energy"]:
                final[stat] = value
            else:
                final[stat] = value + emo.get(stat, 0) + eff.get(stat, 0)

        return final
