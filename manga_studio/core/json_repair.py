"""Utilitaire de réparation ciblée pour les sorties JSON malformées générées par LLM."""

import json
import re
from typing import Any, Dict, Optional


class JSONRepairHelper:
    """Tente de réparer les erreurs de syntaxe JSON fréquentes des modèles LLM."""

    @staticmethod
    def extract_and_parse(raw_text: str) -> Dict[str, Any]:
        """Tente de parser le texte en JSON, avec application de réparations progressives."""
        cleaned = raw_text.strip()

        # 1. Suppression des blocs Markdown ```json ... ```
        if "```" in cleaned:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
            if match:
                cleaned = match.group(1).strip()

        # 2. Essai direct
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # 3. Réparation des virgules traînantes (trailing commas)
        repaired = re.sub(r",\s*([\]}])", r"\1", cleaned)

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

        # 4. Détection et complétion d'accolades ou crochets manquants
        repaired = JSONRepairHelper._balance_delimiters(repaired)

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

        # 5. Extraction par regex du premier bloc { ... }
        match_obj = re.search(r"(\{[\s\S]*\})", repaired)
        if match_obj:
            try:
                return json.loads(match_obj.group(1))
            except json.JSONDecodeError:
                balanced_obj = JSONRepairHelper._balance_delimiters(match_obj.group(1))
                return json.loads(balanced_obj)

        raise ValueError(f"Impossible de réparer le JSON fourni : {raw_text[:200]}...")

    @staticmethod
    def _balance_delimiters(text: str) -> str:
        """Équilibre les accolades et crochets ouverts non fermés en respectant la pile d'imbrication."""
        result = text.rstrip()
        if result.endswith(","):
            result = result[:-1]

        # Pile des délimiteurs ouverts
        stack = []
        in_string = False
        escape = False

        for char in result:
            if char == '"' and not escape:
                in_string = not in_string
            elif not in_string:
                if char in ("{", "["):
                    stack.append(char)
                elif char == "}" and stack and stack[-1] == "{":
                    stack.pop()
                elif char == "]" and stack and stack[-1] == "[":
                    stack.pop()
            escape = (char == "\\" and not escape)

        # Fermeture des délimiteurs dans l'ordre inverse
        while stack:
            opener = stack.pop()
            if opener == "{":
                result += "}"
            elif opener == "[":
                result += "]"

        return result
