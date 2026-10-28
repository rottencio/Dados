# Dados
# Copyright (C) 2026 rottencio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# dice_logic.py
# Aplicación de dados para Dungeons & Dragons
# Versión: 0.0

"""Lógica independiente de la interfaz para tiradas de dados de D&D.

No depende de Kivy, por lo que puede probarse con pytest en cualquier entorno
Python compatible.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
import re
from typing import Callable


class DiceExpressionError(ValueError):
    """La expresión de dados no es válida o excede los límites permitidos."""


@dataclass(frozen=True)
class RollResult:
    expression: str
    rolls: tuple[int, ...]
    kept_rolls: tuple[int, ...]
    modifier: int
    total: int
    description: str


# Límites defensivos para evitar entradas accidentales o abusivas.
MAX_DICE = 100
MAX_SIDES = 1000
MAX_ABS_MODIFIER = 100_000

_EXPRESSION_RE = re.compile(
    r"^\s*(?:(\d{1,3})\s*)?[dD]\s*(\d{1,4})"
    r"(?:\s*([+-])\s*(\d{1,6}))?\s*$"
)


def roll_dice(
    expression: str,
    *,
    keep: str = "all",
    advantage: str = "normal",
    rng: Callable[[int, int], int] = random.randint,
) -> RollResult:
    """Evalúa expresiones simples como 2d6+3, sin usar eval().

    keep: 'all', 'highest' o 'lowest'. Para highest/lowest se conservan
    los dados necesarios para sumar tres resultados si hay cuatro o más;
    para cantidades menores, conserva todos.
    advantage: 'normal', 'advantage' o 'disadvantage'. Solo se aplica a 1d20
    (con o sin modificador) y requiere keep='all'.
    rng se inyecta para poder probar los límites de forma determinista.
    """
    if not isinstance(expression, str):
        raise DiceExpressionError("La tirada debe ser una expresión de texto.")

    match = _EXPRESSION_RE.fullmatch(expression)
    if not match:
        raise DiceExpressionError(
            "Formato no válido. Usa, por ejemplo, 1d20, 2d6+3 o 1d20-2."
        )

    count_text, sides_text, sign, modifier_text = match.groups()
    count = int(count_text) if count_text is not None else 1
    sides = int(sides_text)
    modifier = int(modifier_text or 0)
    if sign == "-":
        modifier = -modifier

    if count < 1 or count > MAX_DICE:
        raise DiceExpressionError(f"La cantidad de dados debe estar entre 1 y {MAX_DICE}.")
    if sides < 2 or sides > MAX_SIDES:
        raise DiceExpressionError(f"Las caras deben estar entre 2 y {MAX_SIDES}.")
    if abs(modifier) > MAX_ABS_MODIFIER:
        raise DiceExpressionError(
            f"El modificador no puede superar {MAX_ABS_MODIFIER} en valor absoluto."
        )
    if keep not in {"all", "highest", "lowest"}:
        raise DiceExpressionError("Selección de dados no reconocida.")
    if advantage not in {"normal", "advantage", "disadvantage"}:
        raise DiceExpressionError("Modo de ventaja no reconocido.")
    if advantage != "normal" and (count != 1 or sides != 20 or keep != "all"):
        raise DiceExpressionError(
            "Ventaja y desventaja solo están disponibles para una tirada de 1d20 "
            "sin selección de dados."
        )

    actual_count = 2 if advantage != "normal" else count
    rolls = tuple(rng(1, sides) for _ in range(actual_count))
    if any(not isinstance(value, int) or not 1 <= value <= sides for value in rolls):
        raise ValueError("El generador de números produjo un resultado fuera de rango.")

    if advantage == "advantage":
        kept = (max(rolls),)
        mode_label = "con ventaja"
    elif advantage == "disadvantage":
        kept = (min(rolls),)
        mode_label = "con desventaja"
    elif keep in {"highest", "lowest"} and count >= 4:
        # Regla habitual de creación de características: 4d6, descartar el menor.
        selected = sorted(rolls, reverse=(keep == "highest"))[:3]
        kept = tuple(selected)
        mode_label = " (3 mayores)" if keep == "highest" else " (3 menores)"
    else:
        kept = rolls
        mode_label = ""

    total = sum(kept) + modifier
    canonical = f"{count}d{sides}"
    if modifier > 0:
        canonical += f"+{modifier}"
    elif modifier < 0:
        canonical += str(modifier)
    if advantage != "normal":
        canonical += f" ({mode_label.strip()})"
    elif mode_label:
        canonical += mode_label

    detail = ", ".join(str(value) for value in rolls)
    if len(kept) != len(rolls):
        detail += " → se suman " + ", ".join(str(value) for value in kept)
    if modifier:
        detail += f" {'+' if modifier > 0 else '−'} {abs(modifier)}"
    return RollResult(
        expression=canonical,
        rolls=rolls,
        kept_rolls=kept,
        modifier=modifier,
        total=total,
        description=detail,
    )
