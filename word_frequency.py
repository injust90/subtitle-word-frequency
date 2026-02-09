#!/usr/bin/env python3
"""Compute word frequencies from an SRT or ASS subtitle file."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

# Match SRT timecode lines (e.g., 00:01:23,456 --> 00:01:25,789).
TIME_CODE_RE = re.compile(r"^\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}")
# Match ASS override tags like {\pos(0,0)}.
ASS_OVERRIDE_RE = re.compile(r"\{.*?\}")
# Replace punctuation with whitespace so words split cleanly.
PUNCT_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)
# Strip common bidi control marks that can appear in subtitle files.
BIDI_MARKS = str.maketrans({
    "\u200e": "",
    "\u200f": "",
    "\u202a": "",
    "\u202b": "",
    "\u202c": "",
    "\u202d": "",
    "\u202e": "",
    "\ufeff": "",
})


def normalize_line(line: str) -> str:
    """Lowercase and remove punctuation (including apostrophes)."""
    cleaned = line.translate(BIDI_MARKS).lower()
    cleaned = PUNCT_RE.sub(" ", cleaned)
    return cleaned


def iter_srt_lines(srt_path: Path) -> list[str]:
    """Extract subtitle text lines from an SRT file."""
    lines: list[str] = []
    with srt_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            # Skip numeric index lines in SRT blocks.
            if line.isdigit():
                continue
            # Skip timecode lines; only keep subtitle text.
            if TIME_CODE_RE.match(line):
                continue
            lines.append(line)
    return lines


def iter_ass_lines(ass_path: Path) -> list[str]:
    """Extract subtitle text from ASS Dialogue lines, handling format metadata."""
    lines: list[str] = []
    text_index = None
    field_count = None
    with ass_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("Format:"):
                # Capture column order so we can extract the Text field reliably.
                fields = [field.strip() for field in line.split(":", 1)[1].split(",")]
                field_count = len(fields)
                if "Text" in fields:
                    text_index = fields.index("Text")
                continue
            if line.startswith("Dialogue:"):
                payload = line.split(":", 1)[1].lstrip()
                if field_count:
                    # Split into the declared number of fields; Text may contain commas.
                    parts = payload.split(",", field_count - 1)
                    if text_index is not None and text_index < len(parts):
                        text = parts[text_index]
                    else:
                        text = parts[-1]
                else:
                    # Default ASS format has 10 fields; text is last.
                    parts = payload.split(",", 9)
                    text = parts[-1]
                # Remove ASS override tags and replace explicit line breaks.
                text = ASS_OVERRIDE_RE.sub("", text)
                text = text.replace("\\N", " ").replace("\\n", " ").replace("\\h", " ")
                lines.append(text)
    return lines


def iter_subtitle_lines(sub_path: Path) -> list[str]:
    """Dispatch to the correct parser based on file extension."""
    suffix = sub_path.suffix.lower()
    if suffix == ".ass":
        return iter_ass_lines(sub_path)
    # Default to SRT parsing for all other extensions.
    return iter_srt_lines(sub_path)


def count_words(lines: list[str]) -> Counter[str]:
    """Count word occurrences across normalized subtitle lines."""
    counts: Counter[str] = Counter()
    for line in lines:
        normalized = normalize_line(line)
        # Split on whitespace after normalization.
        for word in normalized.split():
            counts[word] += 1
    return counts


def write_csv(counts: Counter[str], output_path: Path) -> None:
    """Write word counts to a CSV file in a stable, sorted order."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Sort by frequency (desc), then alphabetically for stable output.
    sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["word", "count"])
        writer.writerows(sorted_items)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for input and output paths."""
    parser = argparse.ArgumentParser(description="Compute word frequencies from an SRT or ASS file.")
    parser.add_argument("input", nargs="?", type=Path, help="Path to .srt or .ass file")
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        help="Optional output CSV path or output directory",
    )
    return parser.parse_args()


def main() -> None:
    """Run the word-frequency pipeline."""
    args = parse_args()
    if not args.input:
        run_gui()
        return

    input_path = args.input
    if not input_path.exists() or not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = build_output_path(input_path, args.output)
    lines = iter_subtitle_lines(input_path)
    counts = count_words(lines)
    write_csv(counts, output_path)


def build_output_path(input_path: Path, output: Path | None) -> Path:
    """Build the output CSV path from an optional file or directory."""
    default_name = f"{input_path.stem}_word_frequency.csv"
    if output is None:
        return input_path.with_name(default_name)
    if output.exists() and output.is_dir():
        return output / default_name
    if output.suffix.lower() == ".csv":
        return output
    return output / default_name


def run_gui() -> None:
    """Show file picker dialogs and run the word-frequency pipeline."""
    if shutil.which("zenity"):
        input_path = run_zenity_file_picker()
        if not input_path:
            return
        output_dir = run_zenity_dir_picker(Path(input_path).parent)
        if not output_dir:
            output_dir = str(Path(input_path).parent)

        input_path = Path(input_path)
        output_path = build_output_path(input_path, Path(output_dir))
        lines = iter_subtitle_lines(input_path)
        counts = count_words(lines)
        write_csv(counts, output_path)
        run_zenity_info(f"Saved: {output_path}")
        return

    root = Tk()
    root.withdraw()
    root.update_idletasks()
    pointer_x = root.winfo_pointerx()
    pointer_y = root.winfo_pointery()
    root.geometry(f"200x50+{pointer_x + 10}+{pointer_y + 10}")
    root.attributes("-topmost", True)
    root.deiconify()
    root.update()
    root.withdraw()
    input_path = filedialog.askopenfilename(
        title="Select subtitle file",
        filetypes=[("Subtitle files", "*.srt *.ass"), ("All files", "*")],
        parent=root,
    )
    if not input_path:
        return
    output_dir = filedialog.askdirectory(
        title="Select output folder",
        initialdir=str(Path(input_path).parent),
        parent=root,
    )
    if not output_dir:
        output_dir = str(Path(input_path).parent)

    input_path = Path(input_path)
    output_path = build_output_path(input_path, Path(output_dir))
    lines = iter_subtitle_lines(input_path)
    counts = count_words(lines)
    write_csv(counts, output_path)
    messagebox.showinfo("Word Frequency", f"Saved: {output_path}")


def run_zenity_file_picker() -> str:
    """Open a GNOME file picker for subtitle files and return the path."""
    result = subprocess.run(
        [
            "zenity",
            "--file-selection",
            "--title=Select subtitle file",
            "--file-filter=*.srt *.ass",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def run_zenity_dir_picker(initial_dir: Path) -> str:
    """Open a GNOME folder picker and return the selected directory."""
    result = subprocess.run(
        [
            "zenity",
            "--file-selection",
            "--directory",
            "--title=Select output folder",
            f"--filename={initial_dir}/",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def run_zenity_info(message: str) -> None:
    """Show a GNOME info dialog with the result message."""
    subprocess.run(
        ["zenity", "--info", f"--text={message}"],
        check=False,
        capture_output=True,
        text=True,
    )


if __name__ == "__main__":
    main()
