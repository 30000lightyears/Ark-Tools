import contextlib
import json
import time
from pathlib import Path
from typing import Any

import UnityPy
from natsort import natsorted
from UnityPy.classes import MonoBehaviour, Sprite, Texture2D


class ArkMediaUnPacker:
    def __init__(self, input_file: str | bytes, output_path: str = "out/"):
        self.env = UnityPy.load(input_file)

        self.output_path = Path(output_path) / f"unpack_{int(time.time())}"

        if not self.output_path.exists():
            self.output_path.mkdir(parents=True)

        self.result = {
            "output_path": self.output_path,
            "type_cnt": 0,
            "pics": {"full": [], "face": [], "full_alpha": [], "face_alpha": []},
            "pos_info": [],
        }

    def save_Texture2D(self, data: Texture2D):
        """保存素材图片（立绘差分的原始和遮罩图片、CG、插图等）

        Args:
            data (_type_): Texture2D
        """

        if not self.output_path.exists():
            self.output_path.mkdir()

        if data.m_Width != 0:
            pic_type = 1
            if data.m_Name.startswith("avg"):
                img_path = self.output_path / "full"
            else:
                img_path = self.output_path / "face"
                pic_type = 0

            if not img_path.exists():
                img_path.mkdir()

            out_file = img_path / f"{data.m_Name}.png"

            try:
                data.image.save(out_file)

                if pic_type:
                    if not out_file.name.endswith("[alpha].png"):
                        self.result["pics"]["full"].append(out_file.name)
                        self.result["type_cnt"] += 1
                    else:
                        self.result["pics"]["full_alpha"].append(
                            out_file.name.replace("[alpha].png", "")
                        )
                else:
                    if not out_file.name.endswith("[alpha].png"):
                        self.result["pics"]["face"].append(out_file.name)
                    else:
                        self.result["pics"]["face_alpha"].append(
                            out_file.name.replace("[alpha].png", "")
                        )

            except Exception:
                pass

    def save_Sprite(self, data: Sprite):
        """保存Sprite图片

        Args:
            data (_type_): Sprite
        """

        if not self.output_path.exists():
            self.output_path.mkdir()

        if data.m_Name.startswith("avg"):
            img_path = self.output_path / "full"

            if not img_path.exists():
                img_path.mkdir()

            out_file = img_path / f"{data.m_Name}_sprite.png"

            with contextlib.suppress(Exception):
                data.image.save(out_file)

    def get_pos_info(self, mono: MonoBehaviour):
        """获取差分图像的变形参数

        Args:
            mono (_type_): MonoBehaviour
        """

        if spriteGroups := mono.object_reader.read_typetree().get("spriteGroups"):
            for p in spriteGroups:
                self.result["pos_info"].append(
                    {
                        "face_size_x": int(p["faceSize"]["x"]),
                        "face_size_y": int(p["faceSize"]["y"]),
                        "face_pos_x": int(p["facePos"]["x"]),
                        "face_pos_y": int(p["facePos"]["y"]),
                    }
                )

    methods = {
        "Texture2D": save_Texture2D,
        "MonoBehaviour": get_pos_info,
        "Sprite": save_Sprite,
    }

    def export_avg_chararts(self) -> dict[str, Any]:
        """获取剧情立绘差分的原始图片、遮罩图片和差分图像的变形参数

        Returns:
            Dict[str, Any]: _description_
        """
        for obj in self.env.objects:
            func = self.methods.get(obj.type.name)

            if not func:
                # print('Unknown type:' + type_name)
                continue

            assert func
            func(self, obj.read())

        self.result["pics"]["face_alpha"] = natsorted(self.result["pics"]["face_alpha"])
        return self.result