from pathlib import Path
from PIL import Image, UnidentifiedImageError
import numpy as np
import matplotlib.pyplot as plt
INPUT_PATH = Path("images/source.jpg")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
def load_image(path: Path) -> tuple[Image.Image, str]:
    if not path.is_file():
        raise FileNotFoundError(
            f"файл изображения не найден по пути {path.resolve()}"
        )
    try:
        with Image.open(path) as img:
            img.load()
            original_format = img.format
            return img.convert("RGB"), original_format
    except UnidentifiedImageError:
        raise ValueError(
            f"файл '{path.name}' не является поддерживаемым "
            f"изображением (JPEG/PNG)"
        )


def change_brightness(image_array: np.ndarray, delta: int) -> np.ndarray:
    if not isinstance(delta, (int, float)):
        raise ValueError("delta должен быть числом")
    temp = image_array.astype(np.int16) + delta
    temp = np.clip(temp, 0, 255)
    return temp.astype(np.uint8)
def resize_keep_aspect(image: Image.Image, new_width: int) -> Image.Image:
    if not isinstance(new_width, int) or new_width <= 0:
        raise ValueError(
            f"Ошибка: new_width должен быть положительным целым числом, "
            f"получено: {new_width}"
        )
    
    old_width, old_height = image.size
    new_height = max(1, round(old_height * new_width / old_width))
    return image.resize(
        (new_width, new_height),
        resample=Image.Resampling.LANCZOS
    )
def to_grayscale_numpy(image_array: np.ndarray) -> np.ndarray:
    if len(image_array.shape) != 3 or image_array.shape[2] != 3:
        raise ValueError("Ожидается RGB-массив формы (H, W, 3)")
    r = image_array[:, :, 0].astype(np.float32)
    g = image_array[:, :, 1].astype(np.float32)
    b = image_array[:, :, 2].astype(np.float32)
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    return gray.astype(np.uint8)
def process_region(
    image_array: np.ndarray,
    x1: int, y1: int, x2: int, y2: int
) -> np.ndarray:
    h, w, _ = image_array.shape
    if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
        raise ValueError(
            f"координаты ({x1},{y1})-({x2},{y2}) выходят за пределы "
            f"изображения ({w}x{h})"
        )
    if x1 >= x2 or y1 >= y2:
        raise ValueError(
            f"некорректные координаты области: "
            f"x1({x1})>=x2({x2}) или y1({y1})>=y2({y2})"
        )
    result = image_array.copy()
    region = result[y1:y2, x1:x2]
    gray_region = to_grayscale_numpy(region)
    result[y1:y2, x1:x2] = np.stack([gray_region] * 3, axis=-1)
    return result
def save_result(image, filename: str) -> Path:
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    path = OUTPUT_DIR / filename
    image.save(path)
    print(f"сохранено: {path}")
    return path
def main():
    image, img_format = load_image(INPUT_PATH)
    img_array = np.asarray(image)
    
    print(f"\n1. Имя файла: {INPUT_PATH.name}")
    print(f"2. Формат: {img_format}")
    print(f"3. Размер (Pillow): {image.size}")
    print(f"4. Цветовой режим: {image.mode}")
    print(f"5. Ширина: {image.width} px, Высота: {image.height} px")
    print(f"6. Альфа-канал: {'Есть' if image.mode == 'RGBA' else 'Нет'}")
    
    print(f"\n7. Shape (NumPy): {img_array.shape}")
    print(f"8. Dtype: {img_array.dtype}")
    print(f"9. Мин/Макс: {img_array.min()} / {img_array.max()}")
    print(f"10. Количество каналов: {img_array.shape[2]}")
    
    print(f"\n11. Значения RGB для трёх пикселей:")
    print(f"    [0, 0]: {img_array[0, 0]}")
    print(f"    [10, 10]: {img_array[10, 10]}")
    print(f"    [50, 50]: {img_array[50, 50]}")
    
    print(f"\n12. Различие image.size и array.shape:")
    print(f"    image.size  = {image.size} → (Ширина, Высота) = (X, Y)")
    print(f"    array.shape = {img_array.shape} → (Высота, Ширина, Каналы) = (Y, X, C)")
    print(f"    В NumPy сначала идут строки (Y), потом столбцы (X).")
    r_channel = img_array[:, :, 0]
    g_channel = img_array[:, :, 1]
    b_channel = img_array[:, :, 2]
    
    print(f"\nКрасный канал:")
    print(f"   Мин: {r_channel.min()}, Макс: {r_channel.max()}, "
          f"Среднее: {r_channel.mean():.2f}")
    
    print(f"\nЗелёный канал:")
    print(f"   Мин: {g_channel.min()}, Макс: {g_channel.max()}, "
          f"Среднее: {g_channel.mean():.2f}")
    
    print(f"\nСиний канал:")
    print(f"   Мин: {b_channel.min()}, Макс: {b_channel.max()}, "
          f"Среднее: {b_channel.mean():.2f}")
    r_img = np.zeros_like(img_array)
    r_img[:, :, 0] = r_channel
    save_result(r_img, "red_channel.png")
    
    g_img = np.zeros_like(img_array)
    g_img[:, :, 1] = g_channel
    save_result(g_img, "green_channel.png")
    
    b_img = np.zeros_like(img_array)
    b_img[:, :, 2] = b_channel
    save_result(b_img, "blue_channel.png") 
    darker = change_brightness(img_array, -50)
    brighter = change_brightness(img_array, 50)
    
    print(f"\nЗатемнённое (delta=-50): мин={darker.min()}, макс={darker.max()}")
    print(f"Осветлённое (delta=+50): мин={brighter.min()}, макс={brighter.max()}")
    
    save_result(darker, "darker.png")
    save_result(brighter, "brighter.png")
    w, h = image.size
    resized_50 = image.resize(
        (w // 2, h // 2),
        resample=Image.Resampling.LANCZOS
    )
    save_result(resized_50, "resized_50.png")
    resized_150 = image.resize(
        (int(w * 1.5), int(h * 1.5)),
        resample=Image.Resampling.LANCZOS
    )
    save_result(resized_150, "resized_150.png")
    resized_custom = resize_keep_aspect(image, 400)
    save_result(resized_custom, "resized_custom.png")
    print(f"reshape() просто перераспределяет пиксели и изображение искажается")
    print(f"resize() с ресэмплингом (LANCZOS) интерполирует пиксели")
    print(f"сохраняя качество.")
    try:
        image.rotate("abc")
    except TypeError:
        print("ошибка: некорректный тип угла")
    rotated_45 = image.rotate(
        45,
        resample=Image.Resampling.BICUBIC,
        expand=True,
        fillcolor=(255, 255, 255)
    )
    save_result(rotated_45, "rotated_45.png")
    rotated_90 = image.rotate(90, expand=True)
    rotated_custom = image.rotate(
        30,
        resample=Image.Resampling.BICUBIC,
        expand=True,
        fillcolor=(0, 0, 0)
    )
    save_result(rotated_custom, "rotated_custom.png")
    rot_no_expand = image.rotate(45, expand=False)
    rot_with_expand = image.rotate(45, expand=True)
    print(f"\nРазмер с expand=False: {rot_no_expand.size}")
    print(f"Размер с expand=True:  {rot_with_expand.size}")
    print(f"expand=False: холст остаётся прежним, углы обрезаются.")
    print(f"expand=True: холст расширяется, чтобы всё изображение поместилось.")
    gray_pillow = image.convert("L")
    save_result(gray_pillow, "grayscale_pillow.png")
    gray_numpy = to_grayscale_numpy(img_array)
    save_result(gray_numpy, "grayscale_numpy.png")
    
    print(f"глаз воспринимает цвета неравномерно:")
    print(f"зелёный кажется самым ярким, синий — самым тёмным")
    print(f"формула Y=0.299R+0.587G+0.114B учитывает эту особенность")
    x1, y1 = w // 4, h // 4
    x2, y2 = w * 3 // 4, h * 3 // 4
    print(f"Область: ({x1},{y1}) — ({x2},{y2})")
    
    region_processed = process_region(img_array, x1, y1, x2, y2)
    save_result(region_processed, "region_processed.png")
    try:
        process_region(img_array, -10, 0, 100, 100)
    except ValueError as e:
        print(f"ошибка координат: {e}")
    
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    
    items = [
        (image, "Исходное"),
        (resized_50, "Уменьшенное (50%)"),
        (rotated_45, "Поворот 45°"),
        (gray_pillow, "Grayscale (Pillow)"),
        (Image.fromarray(brighter), "Яркость +50"),
        (Image.fromarray(region_processed), "Область")
    ]
    
    for ax, (img, title) in zip(axes.flat, items):
        cmap = "gray" if img.mode == "L" else None
        ax.imshow(img, cmap=cmap)
        ax.set_title(title, fontsize=12)
        ax.axis("off")
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "result.png", dpi=100)
    plt.close()
    print(f"Сохранено: {OUTPUT_DIR / 'result.png'}")
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n ошибка: {e}")