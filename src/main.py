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
for idx, row in enumerate(PLANETS):
    pid, name, radius, size, speed, *_ = row
    angle = (idx * 47) % 360
    angles[pid] = angle
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

app.run()
