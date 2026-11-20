from panda3d.core import loadPrcFileData
loadPrcFileData('', 'load-display pandadx9')
loadPrcFileData('', 'win-size 1280 720')

from pathlib import Path
from ursina import *
from motion import clamp_zoom, orbit_position, step_angle
from planet_data import FACTS, IDS, PLANETS
from storage import load_notes, save_notes

ROOT = Path(__file__).resolve().parent.parent
TEX_DIR = ROOT / 'assets' / 'textures'


def tex(name):
    return load_texture(str(TEX_DIR / f'{name}.png'))


app = Ursina(title='MySpace', borderless=False)
window.color = color.rgb(6, 9, 18)

camera.position = (0, 28, -36)
camera.rotation_x = 38

sun = Entity(
    model='sphere',
    scale=2.4,
    texture=tex('sun'),
    unlit=True,
    collider='sphere',
)
sun_halo = Entity(
    model='sphere',
    scale=2.85,
    color=color.rgba(255, 195, 70, 55),
    unlit=True,
)

planets = {}
angles = {}
planet_meta = {}
for idx, row in enumerate(PLANETS):
    pid, name, radius, size, speed, diameter, dist, period = row
    angle = (idx * 47) % 360
    angles[pid] = angle
    planet_meta[pid] = {
        'name': name,
        'radius': radius,
        'speed': speed,
        'diameter': diameter,
        'dist': dist,
        'period': period,
        'fact': FACTS[idx],
    }
    ent = Entity(
        model='sphere',
        scale=size,
        texture=tex(pid),
        unlit=True,
        position=orbit_position(radius, angle),
        collider='sphere',
    )
    planets[pid] = ent

    pts = [orbit_position(radius, a) for a in range(0, 361, 4)]
    Entity(
        model=Mesh(vertices=pts, mode='line', thickness=1),
        color=color.rgba(120, 145, 200, 70),
        unlit=True,
    )

    if pid == 'saturn':
        Entity(
            parent=ent,
            model=Circle(resolution=48, mode='line', thickness=3),
            rotation_x=70,
            scale=1.9,
            color=color.rgba(235, 215, 170, 180),
            unlit=True,
        )

state = {
    'paused': False,
    'speed_mult': 1.0,
    'zoom': 1.0,
    'yaw': 0.0,
    'pitch': 38.0,
    'selected': 'earth',
}
notes = load_notes()

# Верхняя панель управления
# Боковая карточка планеты
panel = Entity(
    parent=camera.ui,
    model='quad',
    scale=(0.52, 0.68),
    position=(0.58, 0.02),
    color=color.rgba(220, 230, 245, 240),
)
title_txt = Text(parent=camera.ui, text='', position=(0.35, 0.31), scale=1.35, color=color.rgb(15, 35, 95))
info_txt = Text(parent=camera.ui, text='', position=(0.35, 0.24), scale=0.88, color=color.black)
note_label = Text(parent=camera.ui, text='Заметка о планете:', position=(0.35, -0.05), scale=0.88, color=color.dark_gray)
note_field = InputField(parent=camera.ui, position=(0.58, -0.13), scale=(0.46, 0.06))
status_txt = Text(parent=camera.ui, text='', position=(0.35, -0.26), scale=0.82, color=color.rgb(0, 120, 40))

title_txt = Text(parent=camera.ui, text='', position=(0.35, 0.31), scale=1.35, color=color.gold)
info_txt = Text(parent=camera.ui, text='', position=(0.35, 0.24), scale=0.88, color=color.white)
note_label = Text(parent=camera.ui, text='Заметка о планете:', position=(0.35, -0.05), scale=0.88, color=color.light_gray)
note_field = InputField(parent=camera.ui, position=(0.58, -0.13), scale=(0.46, 0.06))
status_txt = Text(parent=camera.ui, text='', position=(0.35, -0.26), scale=0.82, color=color.lime)


def select_planet(pid):
    state['selected'] = pid
    meta = planet_meta[pid]
    title_txt.text = meta['name']
    info_txt.text = (
        f"Диаметр: {meta['diameter']} км\n"
        f"Расстояние от Солнца: {meta['dist']} млн км\n"
        f"Период обращения: {meta['period']}\n\n"
        f"Факт: {meta['fact']}"
    )
    note_field.text = notes.get(pid, '')
    status_txt.text = ''


def save_current_note():
    pid = state['selected']
    text = note_field.text.strip()
    if text:
        notes[pid] = text
    else:
        notes.pop(pid, None)
    save_notes(notes)
    status_txt.text = 'Заметка сохранена!'


save_btn = Button(
    parent=camera.ui,
    text='Сохранить заметку',
    position=(0.58, -0.21),
    scale=(0.32, 0.05),
    color=color.azure,
    on_click=save_current_note,
)

for pid, ent in planets.items():
    ent.on_click = lambda p=pid: select_planet(p)

select_planet('earth')


def update_camera():
    dist = 45.0 * state['zoom']
    rad_yaw = math.radians(state['yaw'])
    rad_pitch = math.radians(state['pitch'])
    camera.x = dist * math.cos(rad_pitch) * math.sin(rad_yaw)
    camera.y = dist * math.sin(rad_pitch)
    camera.z = -dist * math.cos(rad_pitch) * math.cos(rad_yaw)
    camera.look_at((0, 0, 0))


update_camera()


def input(key):
    if note_field.active:
        if key == 'enter':
            save_current_note()
        return
    if key == 'space':
        state['paused'] = not state['paused']
    elif key == 'r':
        state['zoom'] = 1.0
        state['yaw'] = 0.0
        state['pitch'] = 38.0
        update_camera()
    elif key == 'scroll up':
        state['zoom'] = clamp_zoom(state['zoom'] - 0.1)
        update_camera()
    elif key == 'scroll down':
        state['zoom'] = clamp_zoom(state['zoom'] + 0.1)
        update_camera()


def update():
    sun.rotation_y += 12 * time.dt
    for pid, meta in planet_meta.items():
        angles[pid] = step_angle(angles[pid], meta['speed'] * state['speed_mult'], time.dt, state['paused'])
        planets[pid].position = orbit_position(meta['radius'], angles[pid])
        planets[pid].rotation_y += 35 * time.dt

    if held_keys['right mouse']:
        state['yaw'] += mouse.velocity[0] * 120
        state['pitch'] = max(10.0, min(85.0, state['pitch'] - mouse.velocity[1] * 120))
        update_camera()


app.run()
