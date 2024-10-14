import os

import torch
from mcelery.cos import download_cos_file, get_local_path, upload_cos_file
from mcelery.infer import celery_app, register_infer_tasks

from srt import transcribe, fix_srt


@celery_app.task(lazy=False, name="srt_infer", queue="srt_infer", autoretry_for=(Exception,), default_retry_delay=10)
def srt_infer_task(audio_cos: str, text: str, output_cos: str) -> str:
    """
    根据音频文件生成字幕服务
    :param audio_cos: 音频文件 COS key
    :param text: 文本，原始文案，通过提供原始文案可以使asr结果更准确。请确保文案与音频内容一致
    :param output_cos: 输出的字幕文件 COS key
    :return: output_cos
    """
    audio_path = download_cos_file(audio_cos)

    srt = transcribe(str(audio_path))

    if os.getenv("EMPTY_CACHE"):
        torch.cuda.empty_cache()

    if text != "":
        fix_srt(srt, text)

    output_path = get_local_path(output_cos)
    with output_path.open("w", encoding="utf-8") as f:
        f.write("\n\n".join(map(str, srt)))
    upload_cos_file(output_cos)
    return output_cos


register_infer_tasks()
