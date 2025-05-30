from langdetect import detect, detect_langs
from langdetect import DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
# 保证结果稳定
DetectorFactory.seed = 0

class LanguageMapper:
    def __init__(self):
        self.language_to_code = {
            "英语": "en",
            "法语": "fr",
            "德语": "de",
            "西班牙语": "es",
            "中文": "zh-cn",
            "日语": "ja",
            "俄语": "ru",
            # 你可以继续添加更多语言
        }
        # 反转字典，代码查名称
        self.code_to_language = {v: k for k, v in self.language_to_code.items()}


    def get_code(self, language_name):
        """根据语言名称返回语言代码，找不到返回 None"""
        return self.language_to_code.get(language_name)

    def get_language(self, code):
        """根据语言代码返回语言名称，找不到返回 None"""
        return self.code_to_language.get(code)

    def detect_language(self, text):
        """根据语言返回语言语种，找不到返回 无法识别语言"""
        try:
            lang_code = detect(text)
            return self.code_to_language.get(lang_code, lang_code)
        except LangDetectException:
            return "无法识别语言"


if __name__ == "__main__":
    # 使用示例
    mapper = LanguageMapper()
    print(mapper.get_code("中文"))    # 输出: zh-cn
    print(mapper.get_language("en"))  # 输出: 英语
    print(mapper.get_language("xx"))  # 输出: None（未知语言）

    # 测试
    text = "This is a test sentence."
    print(mapper.detect_language(text))  # 输出: 英语

    text2 = "这是一个测试句子。"
    print(mapper.detect_language(text2))  # 输出: 中文

    text3 = "Hello , how are you?!"
    print(mapper.detect_language(text3))  #预期输出：英文
