from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance, ImageFont
import subprocess

TEMP_PATH = Path("data/img")


def upscale(save_path: Path):
    print("进行超分处理...")
    tool_path = "./tools/realcugan/realcugan-ncnn-vulkan.exe"
    # -m models-pro
    cmd = f"{tool_path} -m models-nose -n 0 -i {save_path.absolute()} -o {save_path.absolute()}"
    process = subprocess.Popen(
        cmd.split(" "), stdout=subprocess.PIPE, universal_newlines=True
    )
    # 实时读取stdout
    assert process.stdout
    for line in process.stdout:
        print(line, end="")
    # 等待命令执行完毕
    process.wait()
    print("处理完成.")
    return Image.open(save_path)


def get_center(img_a: tuple[int, int], img_b: tuple[int, int], offset=(0, 0)):
    """获取可以使 img_b 在 img_a 中居中的 img_b 左上角坐标

    Args:
        img_a (tuple[int,int]): img_a 的大小
        img_b (tuple[int,int]): img_b 的大小
        offset (tuple, optional): 偏移量. Defaults to (0, 0).
    """
    return (
        (img_a[0] - img_b[0]) // 2 + offset[0],
        (img_a[1] - img_b[1]) // 2 + offset[1],
    )


def get_mask(
    img_size: tuple[int, int],
    xy_list: list[tuple[int, int, int, int]],
    offset: tuple[int, int] = (0, 0),
    radius: int = 12,
):
    """获取裁剪蒙版图层

    Args:
        img_size (tuple[int,int]): 原始图像的尺寸
        pos (tuple[int,int,int,int]): 蒙版四角坐标
        r (int, optional): 蒙版圆角半径.
    """
    alpha = Image.new("L", img_size)
    draw = ImageDraw.Draw(alpha)
    for xy in xy_list:
        pos = (
            xy[0] + offset[0],
            xy[1] + offset[1],
            xy[2] + offset[0],
            xy[3] + offset[1],
        )

        draw.rounded_rectangle(pos, fill=255, radius=radius)

    return alpha


# def get_shadow(
#     img_size: tuple[int, int], xy_list: list[tuple[int, int, int, int]], shadow_size, offset, radius
# ):
#     """
#     获取 shadow 蒙版图层
#     """
#     shadow = get_mask(img_size, xy_list, offset,radius)
#     return shadow.filter(ImageFilter.GaussianBlur(shadow_size))


def draw_card(
    input_img,
    xy_list: list[tuple[int, int, int, int]],
    offset: tuple[int, int] = (0, 0),
    radius: int = 12,
    blur_radius=30,
    color: str = "white",
    brightness: int = 230,
    shadow_size: int = 5,
    blur_bg=0,
):
    """绘制高斯模糊的圆角矩形

    Args:
        input_img (Image): 输入图片
        xy_list (List[Tuple[int, int, int, int]]): 需要绘制矩形的坐标(x1,y1,x2,y2)列表
        offset (Tuple[int, int], optional): 整体偏移量 (x, y). Defaults to (0, 0).
        radius (int, optional): 圆角半径. Defaults to 15.
        blur_radius (int, optional): 模糊半径. Defaults to 30.
        color (str, optional): 颜色（黑/白）. Defaults to 'white'.
        brightness (int, optional): 亮度. Defaults to 210.
        m (int, optional): _description_. Defaults to 1.

    """

    base_img = input_img.copy()
    base_img = base_img.filter(ImageFilter.GaussianBlur(blur_bg))

    # 阴影层
    shadow_alpha = get_mask(base_img.size, xy_list, (offset[0], offset[1] + 5), radius)
    shadow_alpha = shadow_alpha.filter(ImageFilter.GaussianBlur(shadow_size))
    shadow_layer = ImageEnhance.Brightness(base_img).enhance(0.8)
    base_img.paste(shadow_layer, mask=shadow_alpha)

    # 模糊层
    blur_layer = base_img.copy()
    # 加一层变亮/变暗
    blur_layer.paste(
        Image.new("RGBA", base_img.size, color),
        mask=Image.new("L", base_img.size, brightness),
    )
    blur_layer = blur_layer.filter(ImageFilter.GaussianBlur(blur_radius))
    # 加一点噪声
    blur_layer.paste(
        Image.effect_noise(base_img.size, 30), mask=Image.new("L", base_img.size, 5)
    )
    blur_mask = get_mask((blur_layer.width, blur_layer.height), xy_list, offset, radius)
    # blur_mask = blur_mask.resize(blur_layer.size, resample=Image.LANCZOS)
    base_img.paste(blur_layer, mask=blur_mask)
    # 画边框
    outline_color = "#c7c8d6"
    if color == "black":
        outline_color = "#121417"
    n = Image.new("RGBA", (base_img.width, base_img.height))
    draw = ImageDraw.Draw(n)
    for xy in xy_list:
        pos = (
            xy[0] + offset[0],
            xy[1] + offset[1],
            xy[2] + offset[0],
            xy[3] + offset[1],
        )
        draw.rounded_rectangle(pos, outline=outline_color, width=1, radius=radius)
    base_img.alpha_composite(n.resize(base_img.size, resample=Image.LANCZOS))
    return base_img


class MiSansFont:
    font_path = "resources/fonts/"

    @classmethod
    def Bold(cls, size):
        return ImageFont.truetype(f"{cls.font_path}MiSans-Bold.ttf", size)

    @classmethod
    def Demibold(cls, size):
        return ImageFont.truetype(f"{cls.font_path}MiSans-Demibold.ttf", size)

    @classmethod
    def Semibold(cls, size):
        return ImageFont.truetype(f"{cls.font_path}MiSans-Semibold.ttf", size)

    @classmethod
    def Regular(cls, size):
        return ImageFont.truetype(f"{cls.font_path}MiSans-Regular.ttf", size)
