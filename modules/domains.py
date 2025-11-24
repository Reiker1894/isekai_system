import json
from datetime import datetime


class DomainManager:
    def __init__(self, memory_path="data/system_memory.json"):
        self.path = memory_path
        self.data = self.load_memory()

    # -------------------------------------------------------
    # BASIC MEMORY OPERATIONS
    # -------------------------------------------------------
    def load_memory(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_memory(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # -------------------------------------------------------
    # ADD EXP TO DOMAIN
    # -------------------------------------------------------
    def add_exp(self, domain, amount):
        """Adds EXP to a domain and manages level ups and unlocks."""
        d = self.data["domains"][domain]

        d["exp"] += amount

        leveled_up = False
        unlocked = None

        while d["exp"] >= d["exp_to_next"]:
            d["exp"] -= d["exp_to_next"]
            d["level"] += 1
            d["exp_to_next"] = int(d["exp_to_next"] * 1.35)

            leveled_up = True
            unlocked = self.check_milestone(domain)

        self.save_memory()

        return {
            "leveled_up": leveled_up,
            "new_level": d["level"],
            "unlocked": unlocked
        }

    # -------------------------------------------------------
    # CHECK IF DOMAIN HAS COMPLETED ANY MILESTONE
    # -------------------------------------------------------
    def check_milestone(self, domain):
        d = self.data["domains"][domain]
        level = d["level"]

        milestones = d.get("milestones", {})
        unlocked = d.get("unlocked", [])

        str_level = str(level)

        if str_level in milestones and str_level not in unlocked:
            event = milestones[str_level]
            d["unlocked"].append(str_level)

            # Add log entry
            self.data["logs"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "entry": f"[DOMINIO] {d['name']} alcanzó el hito: {event}"
            })

            # Update map
            self.update_map(domain, event)

            self.save_memory()

            return event

        return None

    # -------------------------------------------------------
    # MAP UPDATE WHEN UNLOCKING MILESTONES
    # -------------------------------------------------------
    def update_map(self, domain, event_name):
        """Marks areas as active/discovered when unlocking new levels."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        if "map" not in self.data:
            self.data["map"] = {
                "active_zones": [],
                "discovered_zones": [],
                "last_update": now
            }

        zone_name = f"{domain}_lvl_{event_name}"

        if zone_name not in self.data["map"]["discovered_zones"]:
            self.data["map"]["discovered_zones"].append(zone_name)

        if zone_name not in self.data["map"]["active_zones"]:
            self.data["map"]["active_zones"].append(zone_name)

        self.data["map"]["last_update"] = now
        self.save_memory()

    # -------------------------------------------------------
    # ASSIGN EXP AFTER MISSION COMPLETION
    # -------------------------------------------------------
    def reward_from_mission(self, mission):
        """Grants domain EXP based on mission difficulty and domain."""
        domain = mission.get("domain")
        difficulty = mission.get("difficulty", 1)

        if domain is None:
            return None

        # EXP scaling based on difficulty
        domain_exp = int(15 * difficulty)

        return self.add_exp(domain, domain_exp)

    # -------------------------------------------------------
    # WEEKLY MILESTONES (COMPLETE)
    # -------------------------------------------------------
    def complete_weekly_objective(self, domain, index):
        try:
            obj = self.data["domains"][domain]["weekly_dynamic_milestones"][index]
            obj["completed"] = True

            # Reward domain EXP
            self.add_exp(domain, 20)

            # Log entry
            self.data["logs"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "entry": f"Objetivo semanal completado en {domain}: {obj['task']}"
            })

            self.save_memory()
            return True
        except:
            return False

    # -------------------------------------------------------
    # CLEAN WEEKLY MILESTONES
    # -------------------------------------------------------
    def clear_weekly(self):
        """Resets weekly tasks for a fresh weekly cycle."""
        for domain_key in self.data["domains"]:
            self.data["domains"][domain_key]["weekly_dynamic_milestones"] = []

        self.data["logs"].append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "entry": "Reset semanal de objetivos dinámicos."
        })

        self.save_memory()
        return True
