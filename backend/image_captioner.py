"""
image_captioner.py
调用 MiniMax M2.5 Vision API 为图片生成中文描述（Caption）。

设计原则：
- 直接使用 minimax_client（原始 openai.OpenAI 实例），不经过 FallbackLLMClient。
  因为 SiliconFlow fallback 不支持 Vision，图片描述只能走 MiniMax。
- 失败时返回 ""，不抛异常，调用方自行决定是否跳过该图片块。
"""

import base64
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_CAPTION_PROMPT = (
    "请用中文详细描述这张图片的内容，包括：图中的主要元素、结构关系、标注文字（如有）。"
    "如果这是技术图纸或示意图，请重点描述其结构和功能。"
    "描述要准确、详尽，以便用于文档检索。"
)


def describe_image(client, model: str, image_path: str,
                   context_text: str = "", extra_prompt: str = "",
                   max_tokens: int = 512) -> str:
    """
    将本地图片转为 base64，调用 MiniMax M2.5 Vision API 生成中文描述。

    Args:
        client: MiniMax 的 openai.OpenAI 实例（minimax_client）
        model:  MiniMax 模型名称（如 "MiniMax-M2.5"）
        image_path: 图片绝对路径
        context_text: 图片周边的文字（如图注、标题），可提升描述质量
        extra_prompt: 自定义主提示词；非空时替换默认的 _CAPTION_PROMPT

    Returns:
        图片的中文描述字符串；失败时返回 ""
    """
    path = Path(image_path)
    if not path.exists():
        logger.warning(f"图片文件不存在: {image_path}")
        return ""

    # 读取并编码图片
    try:
        image_bytes = path.read_bytes()
        b64_str = base64.b64encode(image_bytes).decode("utf-8")
    except Exception as e:
        logger.warning(f"读取图片失败 {image_path}: {e}")
        return ""

    # 根据文件后缀决定 MIME 类型
    suffix = path.suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg", ".webp": "image/webp"}
    mime = mime_map.get(suffix, "image/png")

    # 构建 prompt（附加上下文文字有助于提升描述质量）
    prompt = extra_prompt if extra_prompt else _CAPTION_PROMPT
    if context_text:
        prompt += f"\n\n图片周边文字参考：{context_text}"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64_str}"}
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        caption = response.choices[0].message.content.strip()
        return caption
    except Exception as e:
        logger.warning(f"Vision API 调用失败 {image_path}: {e}")
        return ""
