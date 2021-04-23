import traceback
import re
from utils.logger import logger


class CrawlerProp():

    REDUNDANT_RE = [
        r'，外交部[\s\S]*(說明|如下(:|：))',
    ]

    REDUNDANT = [
        "有關",
        "外交部嚴正聲明並強烈譴責說明如下：",
        "外交部澄清如下：",
        "外交部澄清說明如下：",
        "外交部特澄清說明如下：",
        "外交部特此澄清說明如下：",
        "外交部再度鄭重澄清說明如下：",
        "外交部嚴正澄清此為錯誤消息",
        "外交部澄清說明如下",
        "外交部深表遺憾",
        "外交部說明如下：",
        "對於若干",
        "勿轉傳",
        "針對",
        "關於網路謠傳",
        "網路謠傳",
        "網路流傳",
        "網路上流傳",
        "關於媒體報導",
        "外交部嚴正澄清如下：",
        "聽說",
        "疾管署：假的",
        "應該如何辨別？",
        "應該如何辨別?",
        "請問是否屬實？",
        "請問是否屬實?",
        "真的是這樣嗎?",
        "真的是這樣嗎？",
        "請問這是真的嗎？",
        "請問這是真的嗎?",
        "請問是真的嗎？",
        "這是真的嗎?",
        "這是真的嗎？",
        "這是真的嗎",
        "是真的嗎?",
        "是真的嗎？",
        "是真的嗎",
        "是嗎",
        "嗎",
        "「",
        "」",
        "?",
        "？"
    ]


crawlerProp = CrawlerProp()


def remove_redundant_word(sentence):
    try:
        for re_str in crawlerProp.REDUNDANT_RE:
            sentence = re.sub(re_str, "", sentence)

        for word in crawlerProp.REDUNDANT:
            sentence = sentence.replace(word, "")

        if sentence.startswith("，"):
            sentence = sentence[1:]

        for i in range(3):
            sentence = sentence.strip()
            if sentence.endswith("，"):
                sentence = sentence[:-1]

        return sentence

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None
