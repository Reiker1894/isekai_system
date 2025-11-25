import json
import os
from datetime import datetime, timedelta

class HabitsManager:

    def __init__(self, habits_path="data/habits.json", system_path="data/system_memory.json"):
        self.habits_path = habits_path
        self.system_path = system_path
        self.habits = self.load_json(habits_path)
        self.system = self.load_json(system_path)

    # ---------------------------------------------------------
    # JSON HANDLING
    # ---------------------------------------------------------
    def load_json(self, path):
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ---------------------------------------------------------
    # ACCESSORS
    # ---------------------------------------------------------
    def get_definitions(self):
        return self.habits.get("definitions", [])

    def get_daily_log(self):
        return self.habits.get("daily_log", {})

    def get_streaks(self):
        return self.habits.get("streaks", {})

    # ---------------------------------------------------------
    # REGISTER DAILY HABIT COMPLETION
    # ---------------------------------------------------------
    def toggle_habit(self, habit_id, date_str):
        """
        Marca o desmarca un hábito como hecho para una fecha.
        date_str debe ser "YYYY-MM-DD".
        """

        if "daily_log" not in self.habits:
            self.habits["daily_log"] = {}

        if date_str not in self.habits["daily_log"]:
            self.habits["daily_log"][date_str] = {}

        # Toggle
        prev = self.habits["daily_log"][date_str].get(habit_id, False)
        self.habits["daily_log"][date_str][habit_id] = not prev

        self.update_streak(habit_id)

        # Si se completó hoy, aplicar efectos
        if not prev:
            self.apply_habit_effect(habit_id)

        self.save_json(self.habits_path, self.habits)

        return self.habits["daily_log"][date_str][habit_id]

    # ---------------------------------------------------------
    # APPLY HABIT EFFECTS → to stats/emotion/domains
    # ---------------------------------------------------------
    def apply_habit_effect(self, habit_id):
        """
        Efectos de hábitos hacia:
        - stats (energy, intelligence, etc.)
        - emotion (fatigue, clarity…)
        - domains (academia, consulting…)
        """

        definitions = self.get_definitions()
        habit = next((h for h in definitions if h["id"] == habit_id), None)
        if not habit:
            return

        effects = habit.get("effects", {})

        # Stats directos
        stats = self.system.get("stats", {})
        emotion = self.system.get("emotion", {})
        domains = self.system.get("domains", {})

        for key, value in effects.items():

            # ---------- Stats ----------
            if key in stats:
                stats[key] += value
            
            # ---------- Emotion ----------
            elif key in emotion:
                emotion[key] += value
            
            # ---------- Domains ----------
            elif key == "domains":
                for d_key, d_value in value.items():
                    if d_key in domains:
                        domains[d_key]["exp"] += d_value

                        # Level-up de domains
                        if domains[d_key]["exp"] >= domains[d_key]["exp_to_next"]:
                            domains[d_key]["exp"] = 0
                            domains[d_key]["level"] += 1
                            domains[d_key]["exp_to_next"] = int(domains[d_key]["exp_to_next"] * 1.35)

        # Save system
        self.system["stats"] = stats
        self.system["emotion"] = emotion
        self.system["domains"] = domains
        self.save_json(self.system_path, self.system)

    # ---------------------------------------------------------
    # STREAK SYSTEM
    # ---------------------------------------------------------
    def update_streak(self, habit_id):
        """
        Actualiza el streak del hábito, revisando si se completó
        el día anterior.
        Cada 7 días seguidos → 25 Dark Points
        """

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        log = self.get_daily_log()
        streaks = self.get_streaks()

        streak = streaks.get(habit_id, 0)

        # Si el hábito se completó hoy
        if today in log and log[today].get(habit_id, False):

            # Si también se completó ayer → streak +1
            if yesterday in log and log[yesterday].get(habit_id, False):
                streak += 1
            else:
                streak = 1  # nuevo streak

            # Bonus de Dark Points por 7 días
            if streak >= 7:
                self.give_dark_points_bonus()
                streak = 0  # reset después de recompensa

        else:
            streak = 0  # streak roto

        streaks[habit_id] = streak
        self.habits["streaks"] = streaks
        self.save_json(self.habits_path, self.habits)

    # ---------------------------------------------------------
    # GIVE DARK POINTS
    # ---------------------------------------------------------
    def give_dark_points_bonus(self):
        """
        Otorga +25 Dark Points al completar 7 días seguidos.
        """
        dp = self.system.get("dark_points", 0)
        dp += self.habits.get("streak_bonus_dark_points", 25)
        self.system["dark_points"] = dp
        self.save_json(self.system_path, self.system)

    # ---------------------------------------------------------
    # WEEKLY SUMMARY (for charts)
    # ---------------------------------------------------------
    def get_week_summary(self, week_start_date):
        """
        Retorna datos para graficar la semana entera.
        week_start_date debe ser datetime.
        """
        log = self.get_daily_log()
        summary = []

        for i in range(7):
            day = (week_start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            daily_count = 0

            if day in log:
                for h_id, done in log[day].items():
                    if done:
                        daily_count += 1

            summary.append(daily_count)

        return summary

