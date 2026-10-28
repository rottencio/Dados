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
# main.py
# Aplicación de dados para Dungeons & Dragons
# Versión: 0.0


__version__ = "0.0"

from datetime import datetime
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

from dice_logic import (
    MAX_ABS_MODIFIER,
    MAX_DICE,
    DiceExpressionError,
    roll_dice,
)


BG = (0.075, 0.085, 0.12, 1)
PANEL = (0.13, 0.15, 0.20, 1)
ACCENT = (0.65, 0.42, 0.20, 1)
TEXT = (0.94, 0.92, 0.87, 1)
MUTED = (0.72, 0.74, 0.78, 1)


def make_button(text, callback, *, height=48, background=ACCENT):
    button = Button(
        text=text,
        size_hint_y=None,
        height=dp(height),
        background_normal="",
        background_color=background,
        color=TEXT,
        font_size="16sp",
    )
    button.bind(on_release=callback)
    return button


class DiceApp(App):
    def build(self):
        self.title = "Dados de D&D"
        self.history = []
        self.dice_count = 1
        self.dice_sides = 20
        self.modifier = 0

        root = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10),
        )
        root.bind(size=self._set_background)
        with root.canvas.before:
            from kivy.graphics import Color, Rectangle
            self._bg_color = Color(*BG)
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
        self._set_background(root, root.size)

        title = Label(
            text="[b]DADOS DE ROL[/b]",
            markup=True,
            font_size="25sp",
            color=TEXT,
            size_hint_y=None,
            height=dp(42),
        )
        root.add_widget(title)

        self.expression = TextInput(
            text="1d20",
            multiline=False,
            readonly=True,
            size_hint_y=None,
            height=dp(50),
            font_size="20sp",
            background_normal="",
            background_active="",
            background_color=PANEL,
            foreground_color=TEXT,
            cursor_color=TEXT,
            padding=(dp(12), dp(13)),
        )
        root.add_widget(self.expression)

        count_row = BoxLayout(size_hint_y=None, height=dp(43), spacing=dp(6))
        count_row.add_widget(Label(
            text="Dados",
            color=TEXT,
            font_size="16sp",
            size_hint_x=1,
        ))
        self.count_controls = [
            make_button("-", lambda _button: self._change_count(-1), height=43),
        ]
        self.count_label = Label(
            text="1",
            color=TEXT,
            font_size="18sp",
            size_hint_x=0.6,
        )
        self.count_controls.append(
            make_button("+", lambda _button: self._change_count(1), height=43)
        )
        count_row.add_widget(self.count_controls[0])
        count_row.add_widget(self.count_label)
        count_row.add_widget(self.count_controls[1])
        root.add_widget(count_row)

        modifier_row = BoxLayout(size_hint_y=None, height=dp(43), spacing=dp(6))
        modifier_row.add_widget(Label(
            text="Modificador",
            color=TEXT,
            font_size="16sp",
            size_hint_x=1,
        ))
        self.modifier_controls = [
            make_button("-", lambda _button: self._change_modifier(-1), height=43),
        ]
        self.modifier_label = Label(
            text="0",
            color=TEXT,
            font_size="18sp",
            size_hint_x=0.6,
        )
        self.modifier_controls.append(
            make_button("+", lambda _button: self._change_modifier(1), height=43)
        )
        modifier_row.add_widget(self.modifier_controls[0])
        modifier_row.add_widget(self.modifier_label)
        modifier_row.add_widget(self.modifier_controls[1])
        root.add_widget(modifier_row)

        quick_row = BoxLayout(size_hint_y=None, height=dp(43), spacing=dp(5))
        self.side_buttons = []
        for sides in (4, 6, 8, 10, 12, 20, 100):
            button = make_button(
                f"d{sides}",
                lambda _button, s=sides: self._set_sides(s),
                height=43,
                background=PANEL,
            )
            self.side_buttons.append(button)
            quick_row.add_widget(button)
        root.add_widget(quick_row)

        options = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
        self.keep_spinner = Spinner(
            text="Todos",
            values=("Todos", "3 mayores", "3 menores"),
            size_hint_x=1,
            background_normal="",
            background_color=PANEL,
            color=TEXT,
            font_size="14sp",
        )
        self.mode_spinner = Spinner(
            text="Normal",
            values=("Normal", "Ventaja", "Desventaja"),
            size_hint_x=1,
            background_normal="",
            background_color=PANEL,
            color=TEXT,
            font_size="14sp",
        )
        options.add_widget(self.keep_spinner)
        options.add_widget(self.mode_spinner)
        root.add_widget(options)

        self.roll_button = make_button("TIRAR DADOS", self._roll, height=54)
        root.add_widget(self.roll_button)

        self.result_label = Label(
            text="Introduce una tirada y pulsa TIRAR DADOS.",
            color=TEXT,
            font_size="18sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(92),
        )
        self.result_label.bind(size=lambda obj, size: setattr(obj, "text_size", size))
        root.add_widget(self.result_label)

        history_title = Label(
            text="[b]Historial de esta sesión[/b]",
            markup=True,
            color=TEXT,
            font_size="17sp",
            size_hint_y=None,
            height=dp(30),
        )
        root.add_widget(history_title)

        scroll = ScrollView()
        self.history_label = Label(
            text="Todavía no hay tiradas.",
            color=MUTED,
            font_size="14sp",
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        self.history_label.bind(
            texture_size=lambda obj, size: setattr(obj, "height", size[1] + dp(12))
        )
        self.history_label.bind(
            width=lambda obj, width: setattr(obj, "text_size", (width, None))
        )
        scroll.add_widget(self.history_label)
        root.add_widget(scroll)

        root.add_widget(make_button(
            "BORRAR HISTORIAL",
            self._clear_history,
            height=42,
            background=PANEL,
        ))
        return root

    def _set_background(self, widget, size):
        if hasattr(self, "_bg_rect"):
            self._bg_rect.pos = widget.pos
            self._bg_rect.size = size

    def _update_expression(self):
        expression = f"{self.dice_count}d{self.dice_sides}"
        if self.modifier > 0:
            expression += f"+{self.modifier}"
        elif self.modifier < 0:
            expression += str(self.modifier)
        self.expression.text = expression

    def _change_count(self, change):
        self.dice_count = max(1, min(MAX_DICE, self.dice_count + change))
        self.count_label.text = str(self.dice_count)
        self._update_expression()

    def _change_modifier(self, change):
        self.modifier = max(
            -MAX_ABS_MODIFIER,
            min(MAX_ABS_MODIFIER, self.modifier + change),
        )
        self.modifier_label.text = str(self.modifier)
        self._update_expression()

    def _set_sides(self, sides):
        self.dice_sides = sides
        self._update_expression()

    def _roll(self, *_args):
        keep_map = {
            "Todos": "all",
            "3 mayores": "highest",
            "3 menores": "lowest",
        }
        mode_map = {
            "Normal": "normal",
            "Ventaja": "advantage",
            "Desventaja": "disadvantage",
        }
        keep = keep_map[self.keep_spinner.text]
        advantage = mode_map[self.mode_spinner.text]
        expression = self.expression.text
        self._set_controls_disabled(True)
        self.roll_button.text = "TIRANDO..."
        self._animation_tick = 0
        self._roll_animation = Clock.schedule_interval(self._animate_roll, 0.09)
        Clock.schedule_once(
            lambda _dt: self._complete_roll(expression, keep, advantage),
            1.2,
        )

    def _set_controls_disabled(self, disabled):
        for control in (
            *self.count_controls,
            *self.modifier_controls,
            *self.side_buttons,
            self.keep_spinner,
            self.mode_spinner,
            self.roll_button,
        ):
            control.disabled = disabled

    def _animate_roll(self, _dt):
        self._animation_tick += 1
        count = self.dice_count * (2 if self.mode_spinner.text != "Normal" else 1)
        visible_count = min(count, 8)
        values = "  ".join(
            str(random.randint(1, self.dice_sides))
            for _ in range(visible_count)
        )
        if count > visible_count:
            values += "  ..."
        dots = "." * (self._animation_tick % 3 + 1)
        self.result_label.markup = False
        self.result_label.text = f"Lanzando{dots}\n{values}"

    def _complete_roll(self, expression, keep, advantage):
        self._roll_animation.cancel()
        try:
            result = roll_dice(expression, keep=keep, advantage=advantage)
        except (DiceExpressionError, ValueError) as exc:
            self.result_label.markup = True
            self.result_label.text = f"[color=ff7777]Error: {exc}[/color]"
        else:
            self.result_label.markup = False
            self.result_label.text = (
                f"{result.total}\n{result.expression}\n{result.description}"
            )
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.history.insert(
                0,
                f"{timestamp}  |  {result.expression} = {result.total}\n"
                f"    {result.description}",
            )
            self._refresh_history()
        finally:
            self.roll_button.text = "TIRAR DADOS"
            self._set_controls_disabled(False)

    def _refresh_history(self):
        self.history_label.text = "\n\n".join(self.history) or "Todavía no hay tiradas."

    def _clear_history(self, *_args):
        self.history.clear()
        self._refresh_history()
        self.result_label.text = "Historial borrado."


if __name__ == "__main__":
    DiceApp().run()
