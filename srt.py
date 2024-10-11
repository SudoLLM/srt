import difflib
from dataclasses import dataclass
from typing import List

import unicodedata
import whisper


@dataclass
class Srt:
    id: int
    start: float
    end: float
    text: str

    def __str__(self):
        def format_time(v: float) -> str:
            hours, remainder = divmod(v, 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = (seconds - int(seconds)) * 1000
            return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03}"

        return f"{self.id + 1}\n{format_time(self.start)} --> {format_time(self.end)}\n{self.text.strip()}"


def transcribe(audio_path: str, model_size: str = "small") -> List[Srt]:
    """
    Transcribe an audio file using Whisper
    :param audio_path: audio file path
    :param model_size: "tiny", "base", "small", "medium", "large-v2"
    :return:
    """
    model = whisper.load_model(model_size, download_root="models")
    result = model.transcribe(audio_path, initial_prompt="输出中文简体")
    return [Srt(id=s["id"], start=s["start"], end=s["end"], text=s["text"]) for s in result["segments"]]


def gen_tokens(text, replace_punctuation: bool = False) -> List[str]:
    """
    将文本分割, 英文单词为一个 token, 每个汉字为一个 token
    :param replace_punctuation: 是否将标点符号保留为单个空格
    :param text: 文本
    :return: token list
    """
    tokens, cur_word = [], []

    def append_word():
        if cur_word:
            tokens.append("".join(cur_word))
            cur_word.clear()

    for char in text:
        category = unicodedata.category(char)
        if (
            # Nd/Nl/No
            category[0] == "N"
            # 中日韩统一汉字: https://www.unicode.org/charts/PDF/U4E00.pdf
            or "\u4E00" <= char <= "\u9FFF"
            # 平假名: https://www.unicode.org/charts/PDF/U3040.pdf
            or "\u3040" <= char <= "\u309F"
            # 片假名: https://www.unicode.org/charts/PDF/U30A0.pdf
            or "\u30A0" <= char <= "\u30FF"
        ):
            append_word()
            tokens.append(char)
        # Lu/Ll/Lt/Lm/Lo
        elif category[0] == "L":
            cur_word.append(char)
        # Pc/Pd/Ps/Pe/Pi/Pf/Sm/Sc/Sk/So
        elif (replace_punctuation and category[0] in ("P", "S")) or char.isspace():
            append_word()
            if not tokens or not tokens[-1].isspace():
                tokens.append(" ")
    append_word()
    return tokens


def fix_srt(srt: List[Srt], prompt: str):
    tokens = gen_tokens(prompt, replace_punctuation=True)

    for s in srt:
        s_tokens = gen_tokens(s.text)

        idx, pl = len(s_tokens), 3
        while pl > 0 and idx < len(tokens):
            if not tokens[idx].isspace():
                pl -= 1
            idx += 1

        # 只关注最后一个比较, 前面的直接用 prompt 替换 srt
        cruncher = difflib.SequenceMatcher(None, s_tokens, tokens[:idx])
        opcode = None
        for opcode in cruncher.get_opcodes():
            continue
        assert opcode is not None

        tag, i1, i2, j1, j2 = opcode
        if tag == "replace" or tag == "insert":
            # replace 最多替换已有的长度
            if tag == "replace":
                j2 = j1 + i2 - i1
            # 最多截取到空格的部分
            j = j1
            while j < j2 and not tokens[j].isspace():
                j += 1
            # 保守点, 如果没有遇到标点, 放弃
            j2 = j1 if tag == "insert" and j == j2 else j
        s.text = "".join(tokens[:j2])

        while j2 < len(tokens) and tokens[j2] in (".", " "):
            j2 += 1
        tokens = tokens[j2:]
