"""Optional full art rebuild inside Blender 5.2; not required to play.
Open this file in Blender's text editor and Run Script. Creates new ASHFALL scenes
alongside existing user scenes. Exports into this project's public/assets directory.
The existing ASHFALL .blend/GLBs in this project are intentionally regenerated.
"""
from pathlib import Path
ROOT=str(Path(__file__).resolve().parent.parent)
scope={'ROOT':ROOT}
for name in ['01_asset_foundation.py','02_characters.py','03_animation_weapons.py','04_environment.py','05_scene_review.py','06_review_lighting.py','07_ground_finish.py','08_surface_normals.py']:
    path=Path(ROOT)/'blender'/name
    exec(compile(path.read_text(),str(path),'exec'),scope)
print('ASHFALL workshop rebuilt:',ROOT)
