import difflib


from . import ui_select_tmAndterminology

from dao import TM_dao
"""
query：  表示查询字符串，即你想用来匹配的文本。
sentences：表示一个字符串列表，包含多个待匹配的句子。
threshold=0.0：这是一个带默认值的参数，表示相似度阈值，默认值是 0.0。
        相似度低于阈值的句子会被过滤掉，不会出现在最终结果中。
返回值：  一个列表list , 按相似度降序排序
        每个元组包含两个元素：
        第一个元素是字符串（句子）
        第二个元素是浮点数（相似度分数）

"""
def fuzzy_match(query, sentences, threshold=0.0):
    results = []
    for sentence in sentences:
        ratio = difflib.SequenceMatcher(None, query, sentence).ratio()
        results.append((sentence, ratio))
    # 按相似度降序排序
    results.sort(key=lambda x: x[1], reverse=True)
    # 过滤出相似度大于等于阈值的句子
    filtered = [r for r in results if r[1] >= threshold]
    return filtered

class Fuzzy_match:
    def __init__(self, query_text=None, memories=None):
        self.text = query_text or "测试句子 "
        self.memories = memories  # 由外部传入，避免耦合UI

    def fuzzy_match_table_terms(self, threshold=0.3):
        print(f"memories: {self.memories}")

        try:
            all_source_texts = []
            source_text_map = []

            if not self.memories:
                default_tm_name = "TM"
                entries = TM_dao.query_tm_entries(default_tm_name)
                default_id = entries[0][0] if entries else ""  # tm_id在第0位
                self.memories = [(default_tm_name, default_id)]

            for name in self.memories:
                print(f"Querying table: {name}")

                entries = TM_dao.query_tm_entries(name[0])
                for entry in entries:
                    source = entry[1]  # source_text在第1位
                    target = entry[2]  # target_text在第2位
                    tm_term_id = entry[0] #term_id在第0位
                    if source:
                        all_source_texts.append(source)
                        source_text_map.append((name, tm_term_id, source , target))

            matches = fuzzy_match(self.text, all_source_texts, threshold)

            results = []
            for matched_text, score in matches:
                for name, tm_term_id, source ,target in source_text_map:
                    if source == matched_text:
                        results.append((name, tm_term_id, matched_text,target ,score ))
                        break
            return results
        except Exception as e:
            print(f"fuzzy_match_table_terms error: {e}")
            return []




if __name__ == '__main__':
    # 示例数据
    sentences = [
        "这是一个测试句子",
        "这是另一个例子",
        "测试模糊匹配功能"
    ]

    query = "测试句子"
    matches = fuzzy_match(query, sentences)

    # 输出每个句子的相似度
    print("每个句子的相似度：")
    for sentence, score in matches:
        print(f"句子：{sentence}，相似度：{score:.2f}")

    # 输出相似度最高的句子
    if matches:
        best_match = matches[0]
        print(f"\n相似度最高的句子：{best_match[0]}，相似度：{best_match[1]:.2f}")
    else:
        print("没有匹配的句子。")



