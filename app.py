import io
import hashlib
import zipfile
import math
from typing import Dict, List, Tuple, Optional

import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageChops

# ═══════════════════════════════════════════════════════════════════
# 🔐 SECURITY SETTINGS
# ═══════════════════════════════════════════════════════════════════
APP_PASSWORD = "KDPGIFT2026"
BRAND_NAME = "KDPEasy Studio"
TOOL_NAME = "AI Humanizer"
WELCOME_MESSAGE = "Welcome, VIP Creator!"
# ═══════════════════════════════════════════════════════════════════

MAX_UPLOAD = 30
MAX_INPUT_LONG_EDGE = 2400
PREVIEW_LONG_EDGE = 700

# All numeric presets are "base" values (intensity slider 1.0 = default).
# Ranges are documented next to each key.
PRESETS: Dict[str, Dict] = {
    "🎨 Watercolor Storybook": {
        # Softens AI polish, adds paper texture, gentle warmth.
        "grain": 5,          # 0-30 (film noise)
        "warmth": 4,         # -20 (cool) to +20 (warm)
        "saturation": 0.88,  # 1.0 = unchanged, <1 desaturate
        "brightness": 1.02,  # 1.0 = unchanged
        "contrast": 0.96,    # 1.0 = unchanged
        "texture": 0.28,     # 0-1 paper overlay opacity
        "vignette": 0.06,    # 0-1 corner darkening
        "blur": 0.5,         # 0-3 sigma (very light)
        "sepia": 0.05,       # 0-1 sepia mix
    },
    "📜 Vintage Warm": {
        # Golden-age storybook look. Sepia + grain + vignette.
        "grain": 16,
        "warmth": 14,
        "saturation": 0.9,
        "brightness": 0.99,
        "contrast": 1.06,
        "texture": 0.22,
        "vignette": 0.22,
        "blur": 0.3,
        "sepia": 0.18,
    },
    "🖼️ Handcrafted Illustration": {
        # Universal all-round. Slight grain + touch of warmth.
        "grain": 9,
        "warmth": 5,
        "saturation": 0.94,
        "brightness": 1.0,
        "contrast": 1.02,
        "texture": 0.18,
        "vignette": 0.08,
        "blur": 0.3,
        "sepia": 0.03,
    },
    "✏️ Pastel Drawing": {
        # Muted, dreamy, chalk-on-paper feel. Best for gentle scenes.
        "grain": 7,
        "warmth": -3,
        "saturation": 0.75,
        "brightness": 1.06,
        "contrast": 0.92,
        "texture": 0.36,
        "vignette": 0.04,
        "blur": 1.1,
        "sepia": 0.0,
    },
}

st.set_page_config(
    page_title=f"{BRAND_NAME} — {TOOL_NAME}",
    page_icon="🎨",
    layout="wide",
)

CUSTOM_CSS = """
<style>
    .main > div { padding-top: 2rem; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf3 100%); }
    .block-container { max-width: 1300px; }
    h1 { color: #1f2937; font-weight: 700; }
    h2, h3 { color: #1f2937; }
    .stButton>button {
        background-color: #4f46e5;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover { background-color: #4338ca; color: white; }
    .stDownloadButton>button {
        background-color: #10b981;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        font-weight: 700;
    }
    .stDownloadButton>button:hover { background-color: #059669; color: white; }
    div[data-testid="stFileUploader"] {
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        border: 2px dashed #cbd5e1;
    }
    .info-card {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #4f46e5;
        margin-bottom: 1rem;
    }
    .gift-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1rem 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin-bottom: 1rem;
        color: #78350f;
    }
    .login-card {
        background: white;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        max-width: 480px;
        margin: 3rem auto;
        text-align: center;
    }
    .login-card h2 { color: #1f2937; margin-bottom: 0.5rem; }
    .login-card .brand {
        color: #4f46e5;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
    .preview-box {
        background: white;
        padding: 0.8rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 🔐 Password gate
# ═══════════════════════════════════════════════════════════════════
def check_password() -> bool:
    if st.session_state.get("auth_ok"):
        return True

    st.markdown(
        f"""
        <div class="login-card">
            <div class="brand">{BRAND_NAME} · 🎁 Free VIP Gift</div>
            <h2>🎨 {TOOL_NAME}</h2>
            <p style="color:#6b7280;margin-bottom:1.5rem;">
                Enter your VIP password to continue.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        pw = st.text_input("Password", type="password",
                           label_visibility="collapsed",
                           placeholder="Enter password…")
        ok = st.form_submit_button("🔓 Unlock", use_container_width=True)

    if ok:
        if pw == APP_PASSWORD:
            st.session_state.auth_ok = True
            st.rerun()
        else:
            st.error("❌ Wrong password. Please try again.")
    return False


if not check_password():
    st.stop()


# ═══════════════════════════════════════════════════════════════════
# 🎨 Image processing helpers — all Pillow / numpy, no external service
# ═══════════════════════════════════════════════════════════════════
def to_rgb(img: Image.Image, bg: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
    """Ensure image is RGB (compositing transparency onto a solid bg)."""
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        base = Image.new("RGB", img.size, bg)
        img = img.convert("RGBA")
        base.paste(img, mask=img.split()[-1])
        return base
    return img.convert("RGB")


def shrink_if_huge(img: Image.Image, max_edge: int = MAX_INPUT_LONG_EDGE) -> Image.Image:
    w, h = img.size
    long_edge = max(w, h)
    if long_edge <= max_edge:
        return img
    scale = max_edge / long_edge
    return img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)


def apply_warmth(img: Image.Image, warmth: float) -> Image.Image:
    """Positive warmth = boost R, dampen B. Negative = cool."""
    if abs(warmth) < 0.5:
        return img
    arr = np.asarray(img, dtype=np.int16)
    shift = warmth / 20.0  # normalized -1..+1
    r_delta = int(shift * 22)
    b_delta = int(-shift * 20)
    arr[:, :, 0] = np.clip(arr[:, :, 0] + r_delta, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] + b_delta, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def apply_sepia(img: Image.Image, strength: float) -> Image.Image:
    """Blend a sepia-toned version at `strength` (0..1)."""
    if strength <= 0.01:
        return img
    arr = np.asarray(img, dtype=np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    tr = 0.393 * r + 0.769 * g + 0.189 * b
    tg = 0.349 * r + 0.686 * g + 0.168 * b
    tb = 0.272 * r + 0.534 * g + 0.131 * b
    sepia = np.stack([tr, tg, tb], axis=-1)
    sepia = np.clip(sepia, 0, 255)
    blended = arr * (1 - strength) + sepia * strength
    return Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), "RGB")


def apply_saturation(img: Image.Image, factor: float) -> Image.Image:
    if abs(factor - 1.0) < 0.01:
        return img
    return ImageEnhance.Color(img).enhance(factor)


def apply_brightness(img: Image.Image, factor: float) -> Image.Image:
    if abs(factor - 1.0) < 0.01:
        return img
    return ImageEnhance.Brightness(img).enhance(factor)


def apply_contrast(img: Image.Image, factor: float) -> Image.Image:
    if abs(factor - 1.0) < 0.01:
        return img
    return ImageEnhance.Contrast(img).enhance(factor)


def apply_blur(img: Image.Image, sigma: float) -> Image.Image:
    if sigma <= 0.05:
        return img
    return img.filter(ImageFilter.GaussianBlur(radius=sigma))


def add_grain(img: Image.Image, intensity: float, seed_bytes: bytes) -> Image.Image:
    """Add film-like noise. `intensity` roughly 0-30."""
    if intensity <= 0.5:
        return img
    w, h = img.size
    seed = int.from_bytes(seed_bytes[:4], "little") if seed_bytes else 12345
    rng = np.random.default_rng(seed)
    # Luminance noise (single channel) applied to all channels — feels filmic.
    noise = rng.normal(0, intensity, (h, w)).astype(np.float32)
    noise = np.clip(noise, -intensity * 3, intensity * 3)
    arr = np.asarray(img, dtype=np.float32)
    for c in range(3):
        arr[..., c] += noise
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def make_paper_texture(w: int, h: int, seed_bytes: bytes) -> Image.Image:
    """Generate a deterministic subtle paper texture from noise + blur."""
    seed = int.from_bytes(seed_bytes[:4], "little") if seed_bytes else 42
    rng = np.random.default_rng(seed)
    # Base off-white paper with per-pixel micro-noise
    noise = rng.normal(0, 12, (h, w)).astype(np.float32)
    base_val = 240 + noise
    base_val = np.clip(base_val, 210, 255)
    tex = np.stack([base_val, base_val * 0.995, base_val * 0.985], axis=-1)
    img = Image.fromarray(np.clip(tex, 0, 255).astype(np.uint8), "RGB")
    # Light blur so noise reads as fibers, not pixels
    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    return img


def apply_paper_texture(img: Image.Image, opacity: float,
                        seed_bytes: bytes) -> Image.Image:
    if opacity <= 0.01:
        return img
    w, h = img.size
    tex = make_paper_texture(w, h, seed_bytes)
    # Multiply blend (Pillow's "multiply" via ImageChops) then blend back
    multiplied = ImageChops.multiply(img, tex)
    return Image.blend(img, multiplied, opacity)


def apply_vignette(img: Image.Image, strength: float) -> Image.Image:
    """Darken corners with a radial gradient. `strength` 0..1."""
    if strength <= 0.01:
        return img
    w, h = img.size
    xs = np.linspace(-1, 1, w, dtype=np.float32)
    ys = np.linspace(-1, 1, h, dtype=np.float32)
    x, y = np.meshgrid(xs, ys)
    dist = np.sqrt(x ** 2 + y ** 2) / math.sqrt(2)  # 0 at center, 1 at corner
    mask = 1 - np.clip(dist ** 2 * strength * 1.6, 0, strength)
    mask = mask[..., None]  # (h,w,1)
    arr = np.asarray(img, dtype=np.float32) * mask
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def apply_preset(img: Image.Image, preset: Dict, intensity: float,
                 warmth_override: Optional[float], grain_override: Optional[float],
                 texture_override: Optional[float],
                 image_bytes: bytes) -> Image.Image:
    """Run every effect in sequence. `intensity` scales grain/texture/vignette/sepia."""
    img = to_rgb(img)
    img = shrink_if_huge(img)
    seed = hashlib.md5(image_bytes).digest()

    # Base preset values, scaled by intensity where it makes sense
    grain = grain_override if grain_override is not None else preset["grain"]
    grain = grain * intensity
    texture = texture_override if texture_override is not None else preset["texture"]
    texture = texture * intensity
    vignette = preset["vignette"] * intensity
    sepia = preset["sepia"] * intensity
    warmth = warmth_override if warmth_override is not None else preset["warmth"]

    saturation = 1.0 + (preset["saturation"] - 1.0) * intensity
    brightness = 1.0 + (preset["brightness"] - 1.0) * intensity
    contrast = 1.0 + (preset["contrast"] - 1.0) * intensity
    blur = preset["blur"] * intensity

    # Order matters — colour first, then texture/grain overlays, then vignette
    img = apply_warmth(img, warmth)
    img = apply_saturation(img, saturation)
    img = apply_brightness(img, brightness)
    img = apply_contrast(img, contrast)
    img = apply_sepia(img, sepia)
    img = apply_blur(img, blur)
    img = apply_paper_texture(img, texture, seed)
    img = add_grain(img, grain, seed)
    img = apply_vignette(img, vignette)
    return img


@st.cache_data(show_spinner=False, max_entries=60)
def humanize_cached(image_bytes: bytes, preset_name: str, intensity: float,
                    warmth: float, grain: float, texture: float,
                    _v: int = 1) -> bytes:
    preset = PRESETS[preset_name]
    img = Image.open(io.BytesIO(image_bytes))
    out = apply_preset(img, preset, intensity, warmth, grain, texture,
                       image_bytes)
    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def make_preview(png_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(png_bytes))
    w, h = img.size
    long_edge = max(w, h)
    if long_edge > PREVIEW_LONG_EDGE:
        scale = PREVIEW_LONG_EDGE / long_edge
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=85)
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════
# Header + logout
# ═══════════════════════════════════════════════════════════════════
hl, hr = st.columns([5, 1])
with hl:
    st.markdown(
        f"<h1>🎨 {TOOL_NAME}  "
        f"<span style='color:#f59e0b;font-size:1rem;'>🎁 VIP gift</span></h1>"
        f"<p style='color:#6b7280;margin-top:-0.5rem;'>"
        f"{BRAND_NAME} — {WELCOME_MESSAGE}</p>",
        unsafe_allow_html=True,
    )
with hr:
    st.write("")
    if st.button("Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🎨 Style preset")
    preset_name = st.selectbox(
        "Pick a look",
        list(PRESETS.keys()),
        index=2,   # Handcrafted Illustration — safest default
        label_visibility="collapsed",
        help="Each preset applies a curated combination of "
             "warmth, grain, texture, and colour grading.",
    )
    preset = PRESETS[preset_name]

    st.caption(
        {
            "🎨 Watercolor Storybook": "Soft, paper-textured, gentle warmth. "
            "Best for storybook & bedtime scenes.",
            "📜 Vintage Warm": "Golden-age storybook feel. Sepia hint + "
            "grain + subtle vignette.",
            "🖼️ Handcrafted Illustration": "Universal light touch. Works for "
            "covers, interiors, character portraits.",
            "✏️ Pastel Drawing": "Muted, dreamy, chalk-on-paper. Great for "
            "gentle scenes and children's books.",
        }[preset_name]
    )

    st.markdown("### 🎚️ Fine-tune")
    intensity = st.slider(
        "Overall intensity",
        0.3, 1.6, 1.0, 0.05,
        help="Scales the preset up or down. 1.0 = preset default.",
    )

    st.markdown("**Advanced overrides**")
    use_advanced = st.checkbox("Show advanced sliders", value=False)

    if use_advanced:
        warmth = st.slider(
            "Warmth (cool ← → warm)",
            -20, 20, int(preset["warmth"]), 1,
        )
        grain = st.slider(
            "Grain amount",
            0, 30, int(preset["grain"]), 1,
        )
        texture = st.slider(
            "Paper texture opacity",
            0.0, 1.0, float(preset["texture"]), 0.02,
        )
    else:
        warmth = None
        grain = None
        texture = None

    st.markdown("---")
    st.markdown(
        '<div class="info-card" style="font-size:0.85rem;">'
        "💡 <b>Tip:</b> Same preset + slider values apply to every image in "
        "the batch. This is what keeps your cover and interior pages "
        "visually consistent."
        "</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════
# Upload
# ═══════════════════════════════════════════════════════════════════
st.markdown("### 1️⃣ Upload your AI images")

uploaded = st.file_uploader(
    "Drop up to 30 images at once — cover + all interior pages together. "
    "Same style will be applied to every image for consistent look.",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
)

if not uploaded:
    st.info("👆 Drop your AI-generated images to get started.")
    st.markdown(
        '<div class="gift-card">'
        "🎁 <b>This is a free VIP gift from KDPEasy Studio.</b><br>"
        "Amazon buyers are getting sharper at spotting AI art. "
        "This tool takes any AI-generated image (ChatGPT, Midjourney, "
        "DALL-E, Leonardo…) and adds the tiny imperfections that make "
        "it read as handcrafted — grain, paper texture, warmth, colour "
        "grading, and subtle vignette."
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

if len(uploaded) > MAX_UPLOAD:
    st.warning(
        f"⚠️ You uploaded {len(uploaded)} images. Only the first "
        f"{MAX_UPLOAD} will be processed."
    )
    uploaded = uploaded[:MAX_UPLOAD]

# Store bytes so we don't re-read the widget every rerun
files: List[Dict] = []
for f in uploaded:
    files.append({"name": f.name, "bytes": f.getvalue()})

N = len(files)
first = files[0]


# ═══════════════════════════════════════════════════════════════════
# Live preview on first image
# ═══════════════════════════════════════════════════════════════════
st.markdown("### 2️⃣ Live preview")

pcol1, pcol2 = st.columns(2)

# Original
with pcol1:
    st.markdown("**Original**")
    st.markdown('<div class="preview-box">', unsafe_allow_html=True)
    st.image(first["bytes"], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption(f"📎 {first['name']}")

# Humanized preview
with pcol2:
    st.markdown(f"**After — {preset_name}**")
    try:
        preview_png = humanize_cached(
            first["bytes"], preset_name, float(intensity),
            float(warmth) if warmth is not None else float(preset["warmth"]),
            float(grain) if grain is not None else float(preset["grain"]),
            float(texture) if texture is not None else float(preset["texture"]),
        )
        preview_jpg = make_preview(preview_png)
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.image(preview_jpg, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.caption(f"Intensity {intensity:.2f}  •  "
                   f"Warmth {int(warmth) if warmth is not None else int(preset['warmth'])}  •  "
                   f"Grain {int(grain) if grain is not None else int(preset['grain'])}  •  "
                   f"Texture {(texture if texture is not None else preset['texture']):.2f}")
    except Exception as e:
        st.error(f"Preview error: {e}")


# ═══════════════════════════════════════════════════════════════════
# Batch export
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(f"### 3️⃣ Humanize all {N} image{'s' if N > 1 else ''}")

ex1, ex2 = st.columns([1, 2])
with ex1:
    go = st.button(f"🎨 Humanize & download ZIP",
                   use_container_width=True)
with ex2:
    st.caption(
        f"Same style + slider values applied to every image → "
        f"cover + interior stay visually consistent."
    )

if go:
    progress = st.progress(0.0, text="Humanizing images…")
    try:
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w",
                              compression=zipfile.ZIP_DEFLATED) as zf:
            for i, item in enumerate(files):
                png = humanize_cached(
                    item["bytes"], preset_name, float(intensity),
                    float(warmth) if warmth is not None else float(preset["warmth"]),
                    float(grain) if grain is not None else float(preset["grain"]),
                    float(texture) if texture is not None else float(preset["texture"]),
                )
                base = item["name"].rsplit(".", 1)[0]
                zf.writestr(f"{base}-humanized.png", png)
                progress.progress((i + 1) / N,
                                  text=f"Humanizing… {i+1}/{N}")
        zip_bytes = zip_buf.getvalue()
        progress.progress(1.0, text="Done!")
        size_mb = len(zip_bytes) / (1024 * 1024)
        st.success(
            f"✅ {N} image{'s' if N > 1 else ''} humanized  •  "
            f"{size_mb:.1f} MB ZIP ready."
        )
        st.download_button(
            label=f"⬇️ Download humanized-images.zip",
            data=zip_bytes,
            file_name="humanized-images.zip",
            mime="application/zip",
            use_container_width=True,
        )

        st.markdown(
            '<div class="gift-card" style="margin-top:1rem;">'
            "✨ <b>Enjoyed this free tool?</b> "
            "If you publish picture books or coloring books on KDP, "
            "our full Suite has more waiting for you — AI Upscaler, "
            "Story Composer, PDF Builder, and Background Remover. "
            "Reach us at <b>daodinhthe1989@gmail.com</b>."
            "</div>",
            unsafe_allow_html=True,
        )
    except Exception as e:
        progress.empty()
        st.error(f"❌ Could not humanize: {e}")


# ═══════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;color:#9ca3af;font-size:0.85rem;'>"
    f"{BRAND_NAME} — {TOOL_NAME} 🎁  •  "
    f"Made with ❤️ for KDP & Etsy creators"
    f"</div>",
    unsafe_allow_html=True,
)
