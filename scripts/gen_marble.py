import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

W, H = 1400, 700
rng = np.random.default_rng(7)

def fbm(shape, octaves=6, base=4.0, persistence=0.62, seed=0):
    """Fractal noise in [-1,1] via summed blurred white noise at multiple scales."""
    r = np.random.default_rng(seed)
    out = np.zeros(shape)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        sigma = (min(shape) / base) / (2 ** o)
        if sigma < 0.6: break
        n = gaussian_filter(r.standard_normal(shape), sigma)
        n /= (np.abs(n).max() + 1e-9)
        out += amp * n
        total += amp
        amp *= persistence
    return out / total

y, x = np.mgrid[0:H, 0:W].astype(float)
theta = np.deg2rad(-28)
u = x * np.cos(theta) + y * np.sin(theta)   # coordinate along the vein direction's normal

# --- primary veins: sin(u*f + turbulence) with sharp white peaks
t1 = fbm((H, W), octaves=8, base=2.0, seed=3)
v1 = np.sin(u * (2 * np.pi / 700) + t1 * 26.0)
vein1 = np.clip((v1 - 0.965) / 0.035, 0, 1) ** 0.8          # thin bright core
halo1 = np.clip((v1 - 0.75) / 0.25, 0, 1) ** 2.5 * 0.5    # translucent calcite zone beside it

# --- secondary finer veins, different angle
theta2 = np.deg2rad(-40)
u2 = x * np.cos(theta2) + y * np.sin(theta2)
t2 = fbm((H, W), octaves=8, base=3.0, seed=11)
v2 = np.sin(u2 * (2 * np.pi / 420) + t2 * 20.0)
vein2 = np.clip((v2 - 0.975) / 0.025, 0, 1) ** 0.8 * 0.55

# vein brightness fades along the length
fade1 = np.clip(fbm((H, W), octaves=3, base=2.0, seed=21) * 1.6 + 0.65, 0, 1)
fade2 = np.clip(fbm((H, W), octaves=3, base=3.0, seed=22) * 1.8 + 0.5, 0, 1)
vein1 *= fade1; halo1 *= fade1; vein2 *= fade2

# --- stone body: tonal patches with fairly hard edges, plus dark mineral zones
body = fbm((H, W), octaves=7, base=2.0, seed=5)
body = np.tanh(body * 2.2)                 # push toward hard-edged patches
dark = np.clip(-fbm((H, W), octaves=4, base=2.0, seed=9) * 2.0 - 0.3, 0, 1)

# --- colours
navy   = np.array([3, 22, 84])
blue   = np.array([10, 63, 181])
lblue  = np.array([56, 112, 224])
white  = np.array([240, 245, 255])
calc   = np.array([170, 195, 240])

img = blue + (lblue - blue) * np.clip(body, 0, 1)[..., None] + (navy - blue) * np.clip(-body, 0, 1)[..., None] * 0.9
img = img + (navy - img) * dark[..., None] * 0.6
img = img + (calc - img) * halo1[..., None]
img = img + (white - img) * np.clip(vein1 + vein2, 0, 1)[..., None]

# dark hairline beside the main veins
edge = np.clip((v1 - 0.92) / 0.045, 0, 1) * (1 - np.clip((v1 - 0.965) / 0.035, 0, 1)) * fade1
img = img + (navy - img) * edge[..., None] * 0.45

# crystalline grain + polished sheen
grain = rng.standard_normal((H, W)) * 4.0
img = img + grain[..., None]
sheen = np.clip((x / W + y / H) / 2, 0, 1)
img = img + (255 - img) * (0.10 * np.sin(sheen * np.pi))[..., None]

Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save("frontend/src/styles/marble.jpg", quality=88, optimize=True)
print("ok")
