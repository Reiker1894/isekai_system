import json
import random
from datetime import datetime, timedelta


class DynamicMilestones:
    def __init__(self, memory_path="data/system_memory.json"):
        self.path = memory_path
        self.data = self.load_memory()

    # --------------------------------------------
    # BASIC MEMORY OPERATIONS
    # --------------------------------------------
    def load_memory(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_memory(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # --------------------------------------------
    # WEEKLY MILESTONE GENERATION LOGIC
    # --------------------------------------------
    def get_candidates(self, domain):
        """Return context-aware milestone candidates based on domain."""

        emotion = self.data.get("emotion", {})
        stress = emotion.get("stress", 40)
        anxiety = emotion.get("anxiety", 40)
        motivation = emotion.get("motivation", 60)

        # POLÍTICA
        if domain == "politics":
            base = [
                "Leer análisis de coyuntura nacional",
                "Enviar un mensaje profesional a un contacto político",
                "Actualizar tu agenda de networking político",
                "Leer un informe del BID o CAF",
                "Escribir 3 líneas de opinión política"
            ]
            if motivation > 70:
                base.append("Buscar un nuevo contacto político")
            if stress < 40:
                base.append("Analizar un discurso político reciente")
            return base

        # ACADEMIA
        if domain == "academia":
            base = [
                "Leer 5 páginas de un artículo del máster",
                "Corregir 1 párrafo de tu tesis",
                "Repasar una fórmula o modelo",
                "Hacer 30 minutos de estudio suave",
                "Organizar tus archivos académicos"
            ]
            if anxiety < 40:
                base.append("Resolver un ejercicio académico")
            return base

        # CONSULTORÍA
        if domain == "consulting":
            base = [
                "Enviar 1 aplicación en Mercor",
                "Actualizar 1 línea del CV",
                "Mejorar tu bio profesional",
                "Crear una métrica para tu portafolio",
                "Revisar oportunidades laborales"
            ]
            if motivation > 60:
                base.append("Elegir un proyecto para portafolio")
            return base

        # FINANZAS
        if domain == "finance":
            base = [
                "Ahorrar 20.000 pesos hoy",
                "Registrar gastos del día",
                "Revisar tu presupuesto semanal",
                "Eliminar un gasto innecesario",
                "Actualizar tu control financiero"
            ]
            if stress > 50:
                base.append("Evitar compras impulsivas")
            return base

        # FAMILIA
        if domain == "family":
            base = [
                "Enviar un mensaje amable a tu mamá",
                "Hablar 5 minutos con tu papá",
                "Preguntar por el día de tu familia",
                "Proponer un plan sencillo del fin de semana",
                "Agradecer algo pequeño hoy"
            ]
            if motivation > 55:
                base.append("Proponer mejorar la comunicación con 1 familiar")
            return base

        return []

    # --------------------------------------------
    # GENERATE WEEKLY OBJECTIVES
    # --------------------------------------------
    def generate_weekly_milestones(self):
        """Generate new random milestones for each domain."""
        now = datetime.now().strftime("%Y-%m-%d")

        for domain_key, domain_data in self.data["domains"].items():

            candidates = self.get_candidates(domain_key)
            if not candidates:
                continue

            # choose 2–3 objectives randomly
            selected = random.sample(candidates, k=min(3, len(candidates)))

            self.data["domains"][domain_key]["weekly_dynamic_milestones"] = [
                {
                    "task": s,
                    "completed": False,
                    "generated_at": now
                }
                for s in selected
            ]

        self.save_memory()
        return True

    # --------------------------------------------
    # MARK ONE AS COMPLETED
    # --------------------------------------------
    def complete_weekly(self, domain, index):
        try:
            self.data["domains"][domain]["weekly_dynamic_milestones"][index]["completed"] = True
            self.save_memory()
            return True
        except:
            return False
