"""Extract every decoded frame, preserving PTS; pages are for actual visual review.

Extraction is not review. Record viewed page numbers separately in the study log.
"""
import argparse
import json
from pathlib import Path

import av
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser()
parser.add_argument('video', type=Path)
parser.add_argument('start', type=float)
parser.add_argument('end', type=float)
parser.add_argument('output', type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
frames = []
page_images = []
with av.open(str(args.video)) as container:
    stream = container.streams.video[0]
    rate = str(stream.average_rate)
    container.seek(max(0, int(args.start / float(stream.time_base))), stream=stream)
    for frame in container.decode(stream):
        time = float(frame.time)
        if time < args.start - 1e-6:
            continue
        if time >= args.end - 1e-6:
            break
        name = f'{len(frames):04d}-{time:.6f}.png'
        im = frame.to_image()
        im.save(args.output / name)
        im.thumbnail((480, 270))
        frames.append({'time': time, 'image': name, 'page': len(frames) // 15 + 1})
        page_images.append(im)

for start in range(0, len(frames), 15):
    sheet = Image.new('RGB', (1440, 1500))
    draw = ImageDraw.Draw(sheet)
    for index in range(start, min(start + 15, len(frames))):
        col, row = (index - start) % 3, (index - start) // 3
        x, y = col * 480, row * 300
        sheet.paste(page_images[index], (x, y))
        draw.text((x + 8, y + 274), f"frame {index:03d} | {frames[index]['time']:.6f}s", fill='white')
    sheet.save(args.output / f'page-{start // 15 + 1:02d}.png')

(args.output / 'manifest.json').write_text(json.dumps({
    'video': str(args.video), 'start': args.start, 'end_exclusive': args.end,
    'source_average_rate': rate, 'sampling': 'every_decoded_frame',
    'frames': frames, 'pages': (len(frames) + 14) // 15,
    'review_status': 'extracted_not_yet_reviewed',
}, indent=2) + '\n')
print(args.output, len(frames), 'frames', (len(frames) + 14) // 15, 'pages')
