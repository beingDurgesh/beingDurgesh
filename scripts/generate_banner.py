
"""
Generate stipple-art hero banner SVGs for beingDurgesh's GitHub profile.
Creates dark.svg and light.svg with animated dot-matrix artwork
that loops: profile pic → developer icon → Python logo → profile pic.
"""

import random
import sys
import os

# Check for Pillow
try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
except ImportError:
    print("Installing Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

# ── CONFIG ──
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_SOURCE_PATH = os.path.join(OUTPUT_DIR, "profile-source.png")
CANVAS_W, CANVAS_H = 320, 360  # Higher-resolution stipple canvas
DOT_DENSITY = 10000  # Dense enough to preserve facial and logo details
NUM_LAYERS = 12  # Number of animation layers for fade-in
ANIM_DUR = "0.9s"

# ── DOWNLOAD / CREATE SOURCE IMAGES ──

def load_profile_image():
    """Load the checked-in portrait source used for the hero animation."""
    if not os.path.exists(PROFILE_SOURCE_PATH):
        raise FileNotFoundError(
            f"Profile source is missing: {PROFILE_SOURCE_PATH}. "
            "Add profile-source.png before generating the banner."
        )
    return Image.open(PROFILE_SOURCE_PATH).convert("RGB")


def create_profile_stipple_source(image):
    """Turn the portrait into bold line art so dots form a readable face."""
    target_ratio = CANVAS_W / CANVAS_H
    width, height = image.size
    source_ratio = width / height

    if source_ratio > target_ratio:
        crop_width = round(height * target_ratio)
        crop_left = (width - crop_width) // 2
        image = image.crop((crop_left, 0, crop_left + crop_width, height))
    else:
        crop_height = round(width / target_ratio)
        crop_top = max(0, (height - crop_height) // 3)
        image = image.crop((0, crop_top, width, crop_top + crop_height))

    grayscale = ImageOps.grayscale(image)
    grayscale = ImageEnhance.Contrast(grayscale).enhance(1.6)
    edges = grayscale.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.autocontrast(edges, cutoff=2)

    # FIND_EDGES creates light strokes on black; invert it because the dot
    # sampler uses darkness as density. MinFilter gently thickens the lines.
    return ImageOps.invert(edges).filter(ImageFilter.MinFilter(3))

def create_dev_icon(size=400):
    """Load the user's dev logo and prep it for stipple art."""
    icon_path = os.path.join(OUTPUT_DIR, "dev-icon-source.png")
    if not os.path.exists(icon_path):
        return Image.new("L", (size, size), 255)
        
    img = Image.open(icon_path).convert("RGBA")
    
    # Create white background and composite
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, (0, 0), img)
    
    # Convert to grayscale
    img = bg.convert("L")
    
    # Resize to fit within size bounds
    img.thumbnail((size, size), Image.LANCZOS)
    
    # Center on white canvas
    final_img = Image.new("L", (size, size), 255)
    offset = ((size - img.width) // 2, (size - img.height) // 2)
    final_img.paste(img, offset)
    
    # Enhance contrast
    final_img = ImageEnhance.Contrast(final_img).enhance(2.0)
    
    return final_img

def create_python_icon(size=400):
    """Load the user's python logo and prep it for stipple art."""
    icon_path = os.path.join(OUTPUT_DIR, "python-icon-source.png")
    if not os.path.exists(icon_path):
        return Image.new("L", (size, size), 255)
        
    img = Image.open(icon_path).convert("RGBA")
    
    # Create white background and composite
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, (0, 0), img)
    
    # Convert to grayscale
    img = bg.convert("L")
    
    # Resize to fit within size bounds
    img.thumbnail((size, size), Image.LANCZOS)
    
    # Center on white canvas
    final_img = Image.new("L", (size, size), 255)
    offset = ((size - img.width) // 2, (size - img.height) // 2)
    final_img.paste(img, offset)
    
    # Enhance contrast
    final_img = ImageEnhance.Contrast(final_img).enhance(2.0)
    
    return final_img


def image_to_stipple_points(img, canvas_w, canvas_h, num_dots):
    """Convert a grayscale image to stipple dot positions using weighted random sampling."""
    # Resize image to canvas size
    img = img.convert("L")
    img = img.resize((canvas_w, canvas_h), Image.LANCZOS)
    
    pixels = img.load()
    
    # Build probability map: darker = higher probability
    weights = []
    coords = []
    for y in range(canvas_h):
        for x in range(canvas_w):
            darkness = 255 - pixels[x, y]
            if darkness > 20:  # Skip very light pixels
                weights.append(darkness)
                coords.append((x, y))
    
    if not weights:
        return []
    
    # Normalize weights
    total = sum(weights)
    probs = [w / total for w in weights]
    
    # Weighted random sampling
    random.seed(42)  # Reproducible
    chosen_indices = random.choices(range(len(coords)), weights=probs, k=num_dots)
    
    # Deduplicate and collect
    seen = set()
    points = []
    for idx in chosen_indices:
        pt = coords[idx]
        if pt not in seen:
            seen.add(pt)
            points.append(pt)
    
    return points


def points_to_svg_path(points):
    """Convert list of (x,y) points to compact SVG path with 1x1 rects."""
    if not points:
        return ""
    
    # Sort by y then x for RLE optimization
    points.sort(key=lambda p: (p[1], p[0]))
    
    parts = []
    i = 0
    while i < len(points):
        x, y = points[i]
        # Check for horizontal run
        run = 1
        while i + run < len(points) and points[i + run][1] == y and points[i + run][0] == x + run:
            run += 1
        
        if run > 1:
            parts.append(f"M{x} {y}h{run}v1h-{run}z")
        else:
            parts.append(f"M{x} {y}h1v1h-1z")
        i += run
    
    return "".join(parts)


def split_into_layers(points, num_layers):
    """Split points into layers for progressive reveal animation."""
    random.seed(123)
    shuffled = list(points)
    random.shuffle(shuffled)
    
    layers = [[] for _ in range(num_layers)]
    for i, pt in enumerate(shuffled):
        layers[i % num_layers].append(pt)
    
    return layers


def build_stipple_group(points, num_layers, base_delay=0.20, fill_color="#00FF41",
                        anim_dur="0.9s", visibility_begin=None, visibility_end=None):
    """Build SVG group with layered stipple animation."""
    layers = split_into_layers(points, num_layers)
    
    lines = []
    
    # Wrapper group with visibility control if needed
    if visibility_begin is not None and visibility_end is not None:
        lines.append(f'<g>')
        # Show at visibility_begin, hide at visibility_end
        lines.append(f'<set attributeName="opacity" to="1" begin="{visibility_begin}s"/>')
        lines.append(f'<set attributeName="opacity" to="0" begin="{visibility_end}s"/>')
    elif visibility_begin is not None:
        lines.append(f'<g opacity="0">')
        lines.append(f'<set attributeName="opacity" to="1" begin="{visibility_begin}s"/>')
    else:
        lines.append('<g>')
    
    for i, layer in enumerate(layers):
        delay = base_delay + i * 0.03
        path_d = points_to_svg_path(layer)
        if not path_d:
            continue
        lines.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;1" '
            f'dur="{anim_dur}" begin="{delay:.2f}s" fill="freeze" '
            f'calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/>'
            f'<path d="{path_d}"/></g>'
        )
    
    lines.append('</g>')
    return "\n".join(lines)


def build_morphing_stipple(images_data, canvas_w, canvas_h, num_dots, num_layers,
                           fill_color, cycle_duration=4.0):
    """
    Build multiple stipple groups that cycle through images.
    Each image shows for cycle_duration seconds, then fades to next.
    """
    all_groups = []
    num_images = len(images_data)
    total_cycle = cycle_duration * num_images
    
    for idx, (img, label) in enumerate(images_data):
        points = image_to_stipple_points(img, canvas_w, canvas_h, num_dots)
        
        # Calculate visibility timing
        show_start = idx * cycle_duration
        show_end = show_start + cycle_duration
        
        # Create SVG group with visibility animation
        layers = split_into_layers(points, num_layers)
        
        lines = []
        lines.append(f'<!-- {label} -->')
        
        # Every shape uses the same repeating timeline. The final portrait is
        # intentional: it lets the animation return to the profile image before
        # the next loop begins.
        fade_duration = 0.55
        if idx == 0:
            key_times = f"0;{(show_end - fade_duration) / total_cycle:.4f};{show_end / total_cycle:.4f};1"
            values = "1;1;0;0"
        elif idx == num_images - 1:
            key_times = f"0;{(show_start - fade_duration) / total_cycle:.4f};{show_start / total_cycle:.4f};1"
            values = "0;0;1;1"
        else:
            key_times = (
                f"0;{(show_start - fade_duration) / total_cycle:.4f};{show_start / total_cycle:.4f};"
                f"{(show_end - fade_duration) / total_cycle:.4f};{show_end / total_cycle:.4f};1"
            )
            values = "0;0;1;1;0;0"

        lines.append(f'<g fill="{fill_color}" shape-rendering="crispEdges" opacity="0">')
        lines.append(
            f'<animate attributeName="opacity" values="{values}" keyTimes="{key_times}" '
            f'dur="{total_cycle:.1f}s" repeatCount="indefinite"/>'
        )

        for i, layer in enumerate(layers):
            base_start = (show_start - fade_duration) if idx > 0 else 0.0
            delay = base_start + 0.20 + (i * 0.03)
            fraction = 0.75 / total_cycle
            
            path_d = points_to_svg_path(layer)
            if not path_d:
                continue
            lines.append(
                f'<g opacity="0"><animate attributeName="opacity" values="0;1;1" '
                f'dur="{total_cycle:.1f}s" begin="{delay:.2f}s" repeatCount="indefinite" '
                f'calcMode="spline" keyTimes="0;{fraction:.4f};1" keySplines=".4 0 .2 1; 0 0 1 1"/>'
                f'<path d="{path_d}"/></g>'
            )
        lines.append('</g>')
        
        all_groups.append("\n".join(lines))
    
    return "\n".join(all_groups)


def generate_svg(theme="dark"):
    """Generate the complete hero banner SVG."""
    
    is_dark = theme == "dark"
    
    # Theme colors
    if is_dark:
        bg_primary = "#030B07"
        bg_panel = "#07130B"
        bg_titlebar = "#08100D"
        border_subtle = "rgba(110,231,183,0.16)"
        accent = "#4ADE80"
        accent_secondary = "#16A34A"
        text_primary = "#ECFDF5"
        text_secondary = "#A7F3D0"
        text_muted = "rgba(167,243,208,0.32)"
        dot_color = "#86EFAC"
        dot_border_color = "#34D399"
        label_prefix_color = "#6EE7B7"
        panel_border = "rgba(52,211,153,0.38)"
        gradient_stops = ['#4ADE80', '#10B981', '#86EFAC']
    else:
        bg_primary = "#F2FBF5"
        bg_panel = "#FFFFFF"
        bg_titlebar = "#E8F8EE"
        border_subtle = "rgba(6,95,70,0.14)"
        accent = "#059669"
        accent_secondary = "#047857"
        text_primary = "#052E1C"
        text_secondary = "#047857"
        text_muted = "rgba(6,95,70,0.26)"
        dot_color = "#16A34A"
        dot_border_color = "#059669"
        label_prefix_color = "#047857"
        panel_border = "rgba(5,150,105,0.32)"
        gradient_stops = ['#059669', '#10B981', '#22C55E']
    
    # ── Download/create images ──
    print(f"[{theme}] Loading and tracing profile picture...")
    profile_img = create_profile_stipple_source(load_profile_image())
    
    print(f"[{theme}] Creating icon images...")
    dev_img = create_dev_icon(400)
    python_img = create_python_icon(400)
    
    # ── Generate stipple art ──
    print(f"[{theme}] Generating stipple art (this may take a moment)...")
    images_data = [
        (profile_img, "Profile Picture"),
        (dev_img, "Developer Icon"),
        (python_img, "Python Logo"),
        (profile_img, "Profile Picture (Loop Return)"),
    ]
    
    stipple_svg = build_morphing_stipple(
        images_data, CANVAS_W, CANVAS_H, DOT_DENSITY, NUM_LAYERS,
        fill_color=dot_color, cycle_duration=4.0
    )
    stipple_scale_x = 372 / CANVAS_W
    stipple_scale_y = 492 / CANVAS_H
    
    # ── Build SYSTEM.INFO text lines ──
    info_lines = [
        ("Subject", "Durgesh Shukla"),
        ("Role", "Data Analyst"),
        ("Origin", " Mumbai "),
        ("Certification", "Complete Machine Learning &amp; Data Science Course"),
        ("Status", "Building + Learning + Shipping"),
        ("ToolChain", "Python, R, Jupyter, Pandas, NumPy, Scikit-Learn, TensorFlow, PyTorch, SQL"),
    ]
    
    core_lines = [
          ("Core.Lang", "Python, R, SQL"),
          ("Core.Analytics", "Pandas, NumPy, Jupyter"),
          ("Core.ML", "Scikit-Learn, TensorFlow, PyTorch"),
          ("Core.Database", "PostgreSQL, MongoDB, Supabase"),
          ("Core.Infra", "Docker, Git, MLflow, Kubernetes"),
    ]
    
    contact_lines = [
        ("Grid.Mail", "durgeshshukla964@gmail.com"),
        ("Grid.Twitter", "Durgesh964"),
        ("Grid.GitHub", "@beingDurgesh"),
        ("Grid.Instagram", "n0twotuthink"),
    ]
    
    def make_info_text(x, y, label, value, delay, total_width=655):
        dots_count = max(10, 65 - len(label) - len(value))
        dots = "." * dots_count
        return (
            f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" '
            f'begin="{delay:.2f}s" fill="freeze"/><animateTransform attributeName="transform" '
            f'type="translate" values="-8 0;0 0" dur="0.4s" begin="{delay:.2f}s" fill="freeze"/>'
            f'<text x="{x}" y="{y}" font-size="14" textLength="{total_width}" '
            f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
            f'<tspan fill="{label_prefix_color}">{label} </tspan>'
            f'<tspan fill="{text_muted}">{dots}</tspan>'
            f'<tspan fill="{text_primary}" font-weight="600"> {value}</tspan>'
            f'</text></g>'
        )
    
    def make_section_line(x, y, label, delay, total_width=655):
        dashes = "-" * (72 - len(label))
        return (
            f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" '
            f'begin="{delay:.2f}s" fill="freeze"/>'
            f'<text x="{x}" y="{y}" font-size="14" textLength="{total_width}" '
            f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
            f'<tspan fill="{text_secondary}">- {label} </tspan>'
            f'<tspan fill="{text_muted}">{dashes}</tspan>'
            f'</text></g>'
        )
    
    # Build text SVG
    text_x = 470
    text_y_start = 120
    line_height = 23
    text_svgs = []
    delay = 0.70
    
    # SYSTEM.INFO header
    text_svgs.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" '
        f'begin="{delay:.2f}s" fill="freeze"/>'
        f'<text x="{text_x}" y="82" font-size="18" font-weight="700" fill="{accent}">'
        f'SYSTEM.INFO</text>'
        f'<circle cx="1115" cy="77" r="4" fill="#EF4444"><animate attributeName="opacity" '
        f'values="1;0.3;1" dur="2s" repeatCount="indefinite"/></circle>'
        f'<text x="1125" y="82" font-size="11" font-weight="600" fill="#EF4444"> LIVE</text>'
        f'</g>'
    )
    delay += 0.12
    
    # Email badge
    text_svgs.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" '
        f'begin="{delay:.2f}s" fill="freeze"/>'
        f'<rect x="{text_x}" y="94" width="220" height="22" rx="3" fill="none" stroke="{accent}" opacity="0.6"/>'
        f'<text x="{text_x + 8}" y="110" font-size="12" fill="{text_primary}">durgeshshukla964@gmail.com</text>'
        f'</g>'
    )
    delay += 0.20
    
    # Info lines
    y = text_y_start + 20
    for label, value in info_lines:
        text_svgs.append(make_info_text(text_x, y, label, value, delay))
        y += line_height
        delay += 0.12
    
    y += 8  # Gap before core section
    
    for label, value in core_lines:
        text_svgs.append(make_info_text(text_x, y, label, value, delay))
        y += line_height
        delay += 0.12
    
    y += 8  # Gap before contact section
    text_svgs.append(make_section_line(text_x, y, "Contact", delay))
    y += line_height
    delay += 0.12
    
    for label, value in contact_lines:
        text_svgs.append(make_info_text(text_x, y, label, value, delay))
        y += line_height
        delay += 0.12
    
    # Bottom prompt
    y += 8
    text_svgs.append(
        f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" '
        f'begin="{delay:.2f}s" fill="freeze"/>'
        f'<text x="{text_x}" y="{y}" font-size="14" fill="{text_secondary}">'
        f'&#9656; More about me &amp; projects below in README &#8595; '
        f'<tspan fill="{accent}">&#9608;'
        f'<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>'
        f'</tspan></text></g>'
    )
    
    text_block = "\n".join(text_svgs)
    
    # ── Assemble full SVG ──
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Md Kasif - profile.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{gradient_stops[0]}"><animate attributeName="stop-color" values="{gradient_stops[0]};{gradient_stops[1]};{gradient_stops[2]};{gradient_stops[0]}" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="0.5" stop-color="{gradient_stops[1]}"><animate attributeName="stop-color" values="{gradient_stops[1]};{gradient_stops[2]};{gradient_stops[0]};{gradient_stops[1]}" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="1" stop-color="{gradient_stops[2]}"><animate attributeName="stop-color" values="{gradient_stops[2]};{gradient_stops[0]};{gradient_stops[1]};{gradient_stops[2]}" dur="10s" repeatCount="indefinite"/></stop>
    </linearGradient>
<linearGradient id="asciiGrad" x1="0" y1="0" x2="0" y2="520" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{accent}"/>
      <stop offset="0.45" stop-color="{accent_secondary}"/>
      <stop offset="1" stop-color="{accent}"/>
      <animateTransform attributeName="gradientTransform" type="translate" values="0 -120; 0 120; 0 -120" dur="9s" repeatCount="indefinite"/>
    </linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{bg_panel}"/><stop offset="1" stop-color="{bg_primary}"/></linearGradient>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
</defs>
<rect x="2" y="2" width="1176" height="606" rx="18" fill="{bg_primary}"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>
<rect x="2" y="2" width="1176" height="46" fill="{bg_titlebar}"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="{border_subtle}"/>
<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>
<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="{text_secondary}">beingDurgesh@github: ~/profile — ./system.live</text>
<text x="38" y="74" font-size="10" letter-spacing="3" fill="{text_secondary}" opacity="0.7">VISUAL.MAP</text>
<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="{dot_border_color}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>
<rect x="36" y="84" width="400" height="492" rx="10" fill="{bg_panel}" stroke="{panel_border}"/>
<g transform="translate(50,86) scale({stipple_scale_x:.4f},{stipple_scale_y:.4f})" fill="{dot_color}" shape-rendering="crispEdges">
{stipple_svg}
</g>
{text_block}
</g>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>
</svg>'''
    
    return svg


# ── MAIN ──
if __name__ == "__main__":
    print("=" * 60)
    print("Generating hero banner SVGs for beingDurgesh")
    print("=" * 60)
    
    for theme in ["dark", "light"]:
        print(f"\n--- Generating {theme}.svg ---")
        svg_content = generate_svg(theme)
        
        output_path = os.path.join(OUTPUT_DIR, f"{theme}.svg")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        file_size = os.path.getsize(output_path)
        print(f"✅ Written {output_path} ({file_size:,} bytes)")
    
    print("\n" + "=" * 60)
    print("Done! Both dark.svg and light.svg have been generated.")
    print("=" * 60)
