from html import unescape
import re
import random
import requests
from bs4 import BeautifulSoup

def get_xhtml_content(card_url):
    response = requests.get(card_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    copyright_div = soup.find('div', class_='copyright')
    # 著作権情報の有無をチェック
    if copyright_div and "著作権存続" in copyright_div.get_text():
        copyright_flag = True
        copyright = copyright_div.get_text()
    else:
        copyright_flag = False
        copyright = ""
    # XHTMLファイルのリンクを見つける
    xhtml_link = soup.find('a', string='いますぐXHTML版で読む')
    if not xhtml_link:
        return "XHTMLファイルが見つかりませんでした。「全文を読みに行く」ボタンから青空文庫のページを確認してください", None
    xhtml_url = requests.compat.urljoin(card_url, xhtml_link['href'])
    xhtml_response = requests.get(xhtml_url)
    xhtml_content = xhtml_response.content.decode('shift_jis')
    soup = BeautifulSoup(xhtml_content, 'html.parser')
    main_text_div = soup.find('div', class_='main_text')
    #クリエイティブ・コモンズを確認
    if copyright_flag:
        for br in soup.find_all("br"):
            br.replace_with("\n")
        text_parts = soup.get_text().split("\n")
        copyright = "NG"
        for part in reversed(text_parts):
            if "クリエイティブ・コモンズ" in part:
                copyright = part
                break
    return main_text_div.get_text(), copyright

def remove_html_tags(html_text):
    text_without_rt = re.sub(r'<rt>.*?</rt>', '', html_text)
    text_without_tags = re.sub(r'<[^>]+>', '', text_without_rt)
    decoded_text=unescape(text_without_tags)
    text_without_spaces = re.sub(r'\u3000|\（\）', '', decoded_text)
    cleaned_text = re.sub(r'[\r\n\t]+', ' ', text_without_spaces).strip()
    return cleaned_text

def split_into_sentences(text):
    sentences = re.split(r'(?<=[。])', text)
    return [sentence for sentence in sentences if sentence]

def extract_sentences(sentences, max_length=300):
    # ランダムに文を選ぶ
    start_index = random.randint(0, len(sentences) - 1)
    extracted_text = sentences[start_index]
    current_length = len(extracted_text)
    while current_length < max_length and start_index + 1 < len(sentences):
        next_sentence = sentences[start_index + 1]
        if current_length + len(next_sentence) > max_length:
            break
        extracted_text += next_sentence
        current_length += len(next_sentence)
        start_index += 1
    return extracted_text

