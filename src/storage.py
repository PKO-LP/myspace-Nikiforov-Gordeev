from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES_PATH = ROOT / 'data' / 'notes.txt'


def clean_note(text):
    return ' '.join(text.replace('|', ' ').split())


def load_notes(path=NOTES_PATH):
    if not path.exists():
        return {}
    notes = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if '|' not in line:
            continue
        planet_id, text = line.split('|', 1)
        planet_id = planet_id.strip()
        text = clean_note(text)
        if planet_id and text:
            notes[planet_id] = text
    return notes


def save_notes(notes, path=NOTES_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for planet_id, text in sorted(notes.items()):
        cleaned = clean_note(text)
        if planet_id and cleaned:
            lines.append(f'{planet_id}|{cleaned}')
    content = '\n'.join(lines) + ('\n' if lines else '')
    tmp_path = path.with_suffix('.tmp')
    tmp_path.write_text(content, encoding='utf-8')
    tmp_path.replace(path)
