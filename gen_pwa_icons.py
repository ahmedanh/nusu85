"""Generate PWA icons for SHAMEL using PIL/Pillow."""
import os, sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    os.system(f"{sys.executable} -m pip install pillow -q")
    from PIL import Image, ImageDraw, ImageFont

ICONS_DIR = os.path.join(os.path.dirname(__file__),
                         'attendance', 'static', 'pwa', 'icons')
os.makedirs(ICONS_DIR, exist_ok=True)

SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

NAVY  = (30,  58, 95)
GOLD  = (201, 168, 76)
WHITE = (255, 255, 255)


def make_icon(size):
    img  = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle
    margin = int(size * .04)
    draw.ellipse([margin, margin, size-margin, size-margin], fill=NAVY)

    # Gold ring
    ring_w = max(2, int(size * .03))
    draw.ellipse(
        [margin+ring_w, margin+ring_w, size-margin-ring_w, size-margin-ring_w],
        outline=GOLD, width=ring_w
    )

    # "S" letter in center
    center = size // 2
    fs = int(size * .42)
    try:
        font = ImageFont.truetype("arial.ttf", fs)
    except Exception:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fs)
        except Exception:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), "S", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(
        (center - tw // 2, center - th // 2 - bbox[1]),
        "S", fill=GOLD, font=font
    )

    return img


for sz in SIZES:
    icon = make_icon(sz)
    path = os.path.join(ICONS_DIR, f'icon-{sz}.png')
    icon.save(path, 'PNG')
    print(f'  ✓ icon-{sz}.png')

# Placeholder screenshots (solid colour)
for name, w, h in [('screenshot-wide', 1280, 720), ('screenshot-mobile', 390, 844)]:
    img  = Image.new('RGB', (w, h), NAVY)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, w, 8], fill=GOLD)
    path = os.path.join(ICONS_DIR, f'{name}.png')
    img.save(path, 'PNG')
    print(f'  ✓ {name}.png')

print('\nAll PWA icons generated.')
