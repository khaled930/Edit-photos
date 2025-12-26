from PIL import Image
import os

def compress_jpeg(input_path: str, output_path: str, quality: int):
    image = Image.open(input_path)

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.save(
        output_path,
        "JPEG",
        quality=quality,
        optimize=True
    )

    before_size = os.path.getsize(input_path)
    after_size = os.path.getsize(output_path)

    return {
        "before_kb": round(before_size / 1024, 2),
        "after_kb": round(after_size / 1024, 2),
        "ratio": round(before_size / after_size, 2)
    }
