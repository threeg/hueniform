# Detection layer

Image segmentation and colour clustering. Sits between matcher and services in the
dependency chain.

- **Allowed matcher imports:** only `matcher.taxonomy`, `matcher.colour`, `matcher.constants`
  (plus image/maths libs like PIL, numpy, sklearn). Enforced by import-linter.
- **Heavier gate:** `make test-model` (real rembg + KMeans over fixture photos) is DoD for
  detection-touching tickets.
- **Tests:** `backend/tests/detection/`

## Testing pattern: injected segmenter must return RGBA

Returning a plain RGB image from an injected segmenter causes the pipeline to convert it
to grayscale and treat the channel values as an alpha mask. For a dark-coloured image
(e.g. a red JPEG, which has low luminance ~80/255) this produces near-zero alpha coverage,
triggering the FR-27 fallback and setting `fallback_used = True`. Always return an RGBA
image with a fully-opaque (255) alpha channel from a passthrough segmenter:

```python
def _passthrough_segmenter(img: Image.Image) -> Image.Image:
    rgba = img.convert("RGBA")
    r, g, b, _a = rgba.split()
    opaque = Image.new("L", img.size, 255)
    return Image.merge("RGBA", (r, g, b, opaque))
```
