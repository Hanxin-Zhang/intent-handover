"""Generate a vector overview from the current bundled CPU demo selections."""
from pathlib import Path
import argparse,re
from intent_handover.report import svg_scene
from intent_handover.demos import build_scene
from intent_handover.core import select_grasp
from intent_handover.geometry import moved,gripper_boxes
parser=argparse.ArgumentParser(description='Render the bundled FS selections as a README SVG')
parser.add_argument('--output',type=Path,default=Path('docs/media/cpu-selection.svg'))
args=parser.parse_args()
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="520" viewBox="0 0 1400 520"><rect width="1400" height="520" rx="20" fill="#0d1724"/><style>text{font-family:DejaVu Sans,Arial,sans-serif}.title{fill:#fff;font-size:30px;font-weight:700}.label{fill:#aebdd0;font-size:17px}.name{fill:#fff;font-size:23px;font-weight:700}.meta{fill:#70dfcc;font-size:16px}</style><text class="title" x="28" y="48">Three objects. One selection workflow.</text><text class="label" x="28" y="81">Bundled CPU demos  /  Full Strategy</text>']
for i,name in enumerate(('hammer','screwdriver','bottle')):
 scene=build_scene(name);r=select_grasp(scene,'FS');selected=r['selected']
 boxes=scene['object']['boxes']+scene['receiving_hand']['boxes']+[moved(b,selected['T_object_gripper']) for b in gripper_boxes(selected['width_m'])]
 colors=['#aebdd0']*len(scene['object']['boxes'])+['#f3be75']*len(scene['receiving_hand']['boxes'])+['#70dfcc']*3
 visual=svg_scene(boxes,colors)
 visual=re.sub(r'<svg[^>]*>', '<svg x="0" y="53" width="428" height="282" viewBox="0 0 540 410">',visual)
 x=28+i*455
 parts += [f'<g transform="translate({x},108)"><rect width="434" height="344" rx="12" fill="#162537"/><text class="name" x="20" y="36">{name.title()}</text>',visual,f'<text class="meta" x="20" y="322">Selected aperture  /  {selected["width_m"]*1000:.0f} mm</text></g>']
parts+=['<circle cx="37" cy="487" r="5" fill="#aebdd0"/><text class="label" x="50" y="493">Object geometry</text><circle cx="317" cy="487" r="5" fill="#f3be75"/><text class="label" x="330" y="493">Receiving hand</text><circle cx="587" cy="487" r="5" fill="#70dfcc"/><text class="label" x="600" y="493">Selected gripper</text><text class="label" x="1090" y="493">NumPy · CPU · local HTML</text></svg>']
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(''.join(parts))
