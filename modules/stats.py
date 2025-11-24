import json
from datetime import datetime, timedelta


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
    # CORE STAT RETRIEVAL
    # ----------------------------------------------------------
    def base_stats(self):
        """Return base (unmodified) stats."""
        return self.data.get("stats", {})

    # ----------------------------------------------------------
    # EMOTION IMPACT ON STATS
    # ----------------------------------------------------------
    def emotional_modifiers(self):
        """
        Create temporary modifiers based on emotional state.
        These are not saved as base stats, only used in 'final_stats'.
        """
        emotion = self.data.get("emotion", {})
        mods = {
            "strength": 0,
            "intelligence": 0,
            "wisdom": 0,
            "charisma": 0,
            "dexterity": 0,
            "luck": 0
        }

        stress = emotion.get("stress", 0)
        anxiety = emotion.get("anxiety", 0)
        motivation = emotion.get("motivation", 0)
        clarity = emotion.get("clarity", 0)
        fatigue = emotion.get("fatigue", 0)

        # NEGATIVE EMOTIONAL EFFECTS (DEBUFFS)
        if anxiety > 70:
            mods["dexterity"] -= 1
        if stress > 75:
            mods["charisma"] -= 1
        if fatigue > 60:
            mods["strength"] -= 2
        if clarity < 30:
            mods["wisdom"] -= 1
        if motivation < 25:
            mods["luck"] -= 1

        # POSITIVE EMOTIONAL EFFECTS (BUFFS)
        if motivation > 80:
            mods["wisdom"] += 1
        if clarity > 75:
            mods["intelligence"] += 1
        if motivation > 90:
            mods["charisma"] += 1
        if stress < 30 and clarity > 60:
            mods["dexterity"] += 1

        return mods

    # ----------------------------------------------------------
    # BUFFS & DEBUFFS SYSTEM
    # ----------------------------------------------------------
    def active_effects(self):
        """Returns list of buffs/debuffs and removes expired ones."""
        effects = self.data.get("effects", [])

        today = datetime.now().date()
        cleaned_effects = []

        for e in effects:
            end_date = datetime.strptime(e["end_date"], "%Y-%m-%d").date()
            if end_date >= today:
                cleaned_effects.append(e)

        self.data["effects"] = cleaned_effects
        self.save_memory()
        return cleaned_effects

    def apply_effect_modifiers(self):
        """Apply buffs/debuffs from temporary effects."""
        effects = self.active_effects()
        mods = {
            "strength": 0,
            "intelligence": 0,
            "wisdom": 0,
            "charisma": 0,
            "dexterity": 0,
            "luck": 0,
        }

        for e in effects:
            for stat, value in e["modifiers"].items():
                mods[stat] += value

        return mods

    def add_effect(self, name, duration_days, modifiers):
        """Adds a buff or debuff lasting multiple days."""
        today = datetime.now().date()
        end_date = today + timedelta(days=duration_days)

        effect = {
            "name": name,
            "modifiers": modifiers,
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }

        if "effects" not in self.data:
            self.data["effects"] = []

        self.data["effects"].append(effect)
        self.save_memory()
        return effect

    # ----------------------------------------------------------
    # FINAL STATS (BASE + EMOTION + EFFECTS)
    # ----------------------------------------------------------
    def final_stats(self):
        """Calculate real stats used by the player today."""
        base = self.base_stats()
        emotion_mods = self.emotional_modifiers()
        effect_mods = self.apply_effect_modifiers()

        final_stats = {}

        for stat, value in base.items():
            if stat in ["level", "exp", "exp_to_next_level", "energy", "max_energy"]:
                final_stats[stat] = value
            else:
                final_stats[stat] = value + emotion_mods.get(stat, 0) + effect_mods.get(stat, 0)

        return final_stats

    # ----------------------------------------------------------
    # XP SYSTEM & LEVELING
    # ----------------------------------------------------------
    def add_exp(self, amount):
        stats = self.data["stats"]
        stats["exp"] += amount

        # Level up logic
        while stats["exp"] >= stats["exp_to_next_level"]:
            stats["exp"] -= stats["exp_to_next_level"]
            stats["level"] += 1
            stats["exp_to_next_level"] = int(stats["exp_to_next_level"] * 1.25)

            # Stat upgrade reward
            stats["strength"] += 1
            stats["wisdom"] += 1

            print(f"🎉 LEVEL UP! You are now Level {stats['level']}")

        self.save_memory()

    # ----------------------------------------------------------
    # ENERGY SYSTEM
    # ----------------------------------------------------------
    def change_energy(self, amount):
        stats = self.data["stats"]
        stats["energy"] = max(0, min(stats["energy"] + amount, stats["max_energy"]))
        self.save_memory()
