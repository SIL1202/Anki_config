import requests
from bs4 import BeautifulSoup
import time
import random


def get_anki_note_xml(word):
    url = f"https://dictionary.cambridge.org/zht/詞典/英語-漢語-繁體/{word}"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    try:
        time.sleep(random.uniform(2, 4))
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # 1. 抓取詞性
        pos_element = soup.select_one(".pos.dpos")
        pos_text = f"[{pos_element.text.strip()}]" if pos_element else ""

        # 開始建構 XML (Front 部分)
        xml = [
            f"<note>",
            f"  <front>",
            f"    <h1>{word}</h1>",
            f"    <p style='color: gray'>{pos_text}</p>",
            f"  </front>",
            f"  <back>",
        ]

        # 2. 抓取一般詞條 (Entry) - 紫色區塊
        entries = soup.select(".pr.entry-body__el")
        for entry in entries:
            senses = entry.select(".dsense")
            for sense in senses:
                trans = sense.select_one(".trans.dtrans")
                if not trans:
                    continue

                xml.append(f"    <h1>{trans.text.strip()}</h1>")

                examples = sense.select(".examp.dexamp")
                if examples:
                    xml.append('    <ul style="color: rgb(170, 85, 255)">')
                    for ex in examples[:2]:  # 使用切片取代計數器，更簡潔
                        eg_en = ex.select_one(".eg.deg").text.strip()
                        xml.append(f"      <li>{eg_en}</li>")
                    xml.append("    </ul>")

        # 3. 抓取片語 (Phrase) - 深綠色區塊 (放在最後面)
        # 這裡我們要把片語也塞在 <back> 標籤裡面
        phrases = soup.select(".phrase-block")  # 劍橋的片語通常在這個 class 下
        for p in phrases:
            p_title_el = p.select_one(".phrase-title")
            p_trans_el = p.select_one(".trans.dtrans")

            if p_title_el and p_trans_el:
                phrase_title = p_title_el.text.strip()
                phrase_trans = p_trans_el.text.strip()

                # 片語標題與翻譯 (深綠色)
                xml.append(
                    f"    <h1 style='color: rgb(85, 170, 0);'>{phrase_title} {phrase_trans}</h1>"
                )

                p_examples = p.select(".examp.dexamp")
                if p_examples:
                    xml.append("    <ul style='color: rgb(170, 85, 255)'>")
                    for ex in p_examples[:2]:
                        eg_text = ex.select_one(".eg.deg").text.strip()
                        # 高光處理：將關鍵字變亮綠色
                        highlighted_eg = eg_text.replace(
                            word,
                            f"<span style='color: rgb(85, 170, 0)'>{word}</span>",
                        )
                        xml.append(f"      <li>{highlighted_eg}</li>")
                    xml.append("    </ul>")

        # 4. 最後才封閉標籤
        xml.append("  </back>")
        xml.append("</note>")

        return "\n".join(xml)

    except Exception as e:
        print(f"錯誤: {e}")
        return ""


# --- 批次處理 ---
word = "chaplain"  # 建議用原形動詞抓，replace 高光才會準
with open("anki.html", "w", encoding="utf-8") as f:
    f.write("<deck>Vocabulary_7</deck>\n\n")
    print(f"正在處理: {word}")
    result = get_anki_note_xml(word)
    if result:
        f.write(result + "\n\n")

print("完成！anki.html 已更新。")
