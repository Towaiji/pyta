from __future__ import annotations

from typing import TYPE_CHECKING

from .core import NewMessage, PythonTaReporter
from .node_printers import LineType

if TYPE_CHECKING:
    from pylint.lint import PyLinter


class PlainReporter(PythonTaReporter):
    """Plain text reporter."""

    name = "pyta-plain"

    OUTPUT_FILENAME = "pyta_report.txt"

    # Rendering constants
    _SPACE = " "
    _BREAK = "\n"
    _COLOURING = {}
    code_err_title = "=== Code errors/forbidden usage (fix: high priority) ==="
    style_err_title = "=== Style/convention errors (fix: before submission) ==="
    no_err_message = "No problems detected, good job!" + _BREAK * 2
    no_snippet = "No code to display for this message." + _BREAK * 2

    def print_messages(self, level: str = "all") -> None:
        """Print messages for the current file.

        If level == 'all', both errors and style errors are displayed. Otherwise,
        only errors are displayed.
        """
        error_msgs, style_msgs = self.group_messages(self.messages[self.current_file])

        result = "PyTA Report for: " + self._colourify("bold", self.current_file) + self._BREAK
        result += self._generate_report_date_time() + self._BREAK
        result += self._colourify("code-heading", self.code_err_title + self._BREAK)
        messages_result = self._colour_messages_by_type(error_msgs)
        if messages_result:
            result += messages_result
        else:
            result += self.no_err_message

        if level == "all":
            result += self._colourify("style-heading", self.style_err_title + self._BREAK)
            messages_result = self._colour_messages_by_type(style_msgs)
            if messages_result:
                result += messages_result
            else:
                result += self.no_err_message

        self.writeln(result)
        self.out.flush()

    def _colour_messages_by_type(self, messages: dict[str, list[NewMessage]]) -> str:
        """
        Return string of properly formatted members of the messages dict
        (error or style) indicated by style.
        """
        max_messages = self.linter.config.pyta_number_of_messages

        result = ""
        for msg_id in messages:
            result += self._colourify("bold", msg_id)
            result += self._colourify("bold", " ({})  ".format(messages[msg_id][0].symbol))
            result += "Number of occurrences: {}.".format(len(messages[msg_id]))
            if (
                max_messages != 0
                and max_messages != float("inf")
                and max_messages < len(messages[msg_id])
            ):
                result += " (First {} shown).".format(max_messages)
            result += self._BREAK

            for i, msg in enumerate(messages[msg_id]):
                if max_messages != 0 and i == max_messages:
                    break

                # Use only explanation, without redundant accessory information
                msg_truncated = msg.msg.split("\n")[0]
                result += 2 * self._SPACE
                result += (
                    self._colourify("bold", "[Line {}] {}".format(msg.line, msg_truncated))
                    + self._BREAK
                )

                result += msg.snippet
                result += self._BREAK

        return result

    def _add_line(self, lineno: int, linetype: LineType, slice_: slice, text: str = "") -> str:
        """Format given source code line as specified and return as str.

        Called by _build_snippet, relies on _colourify.
        """
        lineno_spaces = self._PRE_LINE_NUM_SPACES + self._NUM_LENGTH_SPACES + self._AFTER_NUM_SPACES
        snippet_so_far = super()._add_line(lineno, linetype, slice_, text)
        if linetype == LineType.ERROR:
            start = slice_.start or 0
            prespace = (
                lineno_spaces + start
            ) * self._SPACE  # number 7 for prespaces included for adding line number
            snippet_so_far += self._overline_helper(text[slice_], prespace)

        elif linetype == LineType.DOCSTRING:
            prespace = (lineno_spaces + len(text) - len(text.lstrip(" "))) * self._SPACE
            snippet_so_far += self._overline_helper(text.lstrip(" "), prespace)

        return snippet_so_far

    def _overline_helper(self, text: str, prespace: str) -> str:
        """
        Helper method _add_line. Adds the Unicode U+203E (the overline character "‾") under any
        part that is highlighted as ERROR. Returns the corresponding snippet as a result.
        """
        overline = "‾" * len(text)
        return prespace + overline + self._BREAK


def register(linter: PyLinter):
    linter.register_reporter(PlainReporter)
