# Subtitle Word Frequency

Compute word frequencies from `.srt` and `.ass` subtitle files.

## Features
- Supports SRT and ASS subtitles
- Auto-generates a CSV output name
- GUI file pickers on GNOME (via `zenity`), with Tk fallback

## Requirements
- Python 3
- Optional (GNOME GUI): `zenity`
- Optional (Tk fallback GUI): `python3-tk`

Install GUI helpers on Ubuntu:

```bash
sudo apt install zenity python3-tk
```

## Usage

## Quick start
Clone and run the GUI right away:

```bash
git clone https://github.com/injust90/subtitle-word-frequency.git
cd subtitle-word-frequency
python3 word_frequency.py
```

## Install with pipx
If you want a global command without managing a venv manually:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install git+https://github.com/injust90/subtitle-word-frequency.git
```

Then run:

```bash
subtitle-word-frequency
```

### GUI (recommended)
Launch without arguments to open file pickers:

```bash
python3 word_frequency.py
```

### CLI
Provide an input file and (optionally) an output file or directory:

```bash
python3 word_frequency.py /path/to/subtitles.srt
python3 word_frequency.py /path/to/subtitles.ass /path/to/output.csv
python3 word_frequency.py /path/to/subtitles.ass /path/to/output_dir/
```

The output file is named like:

```
<subtitle_stem>_word_frequency.csv
```

## Desktop launcher
A starter launcher is included at [WordFrequency.desktop](WordFrequency.desktop).
For a one-command install on Linux, run:

```bash
./install_launcher.sh
```

This creates a launcher in `~/.local/share/applications` using your current Python and icon path.

Manual option: update the `Exec` and `Icon` paths in the template, then make it executable:

```bash
chmod +x WordFrequency.desktop
```

## Output
CSV with two columns:

```
word,count
```

## License
MIT
