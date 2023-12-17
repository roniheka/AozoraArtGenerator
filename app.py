import streamlit as st
import pandas as pd
import base64
from PIL import Image
from io import BytesIO
import random
import io
from module.image_generator import image_generator
from module.text_processing import get_xhtml_content, remove_html_tags, split_into_sentences,extract_sentences

api_key = st.secrets.OPENAI_API_KEY

def init_page():
    st.set_page_config(
        page_title="挿絵のタイムカプセル",
        page_icon="📖"
    )
    st.header("挿絵のタイムカプセル📖")
    st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;青空文庫の豊富な文学作品の中から、お好きな物語を選んでください。\n\n　文章を基に、独創的で魅力的な挿絵を生成します。\
                \n\n　あなたが選ぶ一節が、一枚のアートワークに生まれ変わります。\n\n&nbsp;")
    st.sidebar.title("挿絵のテイスト")
    styles = {'Realistic':"イラストには写真のようなリアリズム、高いディテール、自然な色使いを持たせてください。",
               'Anime':"イラストは日本のアニメーションのような、明るく鮮やかな色使い、ドラマティックな表現を持たせてください。",
                'Comic':"イラストは日本の漫画のような、大きく表現豊かな目、シンプルで流れるような線、特徴的な髪型と色、ドラマティックな表現を持たせてください。",
                'Vintage':"イラストは昔ながらの絵本のような、温かみのある色彩、手書きの質感、シンプルで親しみやすいキャラクターデザインを持たせてください。"}

    selected_style = st.sidebar.radio("イラストのスタイルを選択:", styles.keys())
    style = styles[selected_style]
    text = st.text_area("入力された一節",st.session_state.get('text', ''))
    work_list_df = pd.read_csv("static/list_person_all_extended_utf8.csv")
    work_list_df["姓名"] = work_list_df["姓"]+work_list_df["名"].fillna("")

    footer = """
        <style>.footer {position: fixed;left: 0;bottom: 0;width: 100%;background-color: #f1f1f1;color: black;text-align: center;}
        </style><div class="footer">
        <p><a href="https://github.com/roniheka/AozoraArtGenerator" target="_blank">Developed with Streamlit</a></p>
     </div>
        """
    st.markdown(footer, unsafe_allow_html=True)

    return text, style,selected_style, work_list_df


def main():
    text,style,style_type, work_list_df = init_page()
    if st.button('挿絵を生成'):
        with st.spinner("Generating..."):
            if "text" not in st.session_state: #手動入力の場合
                st.session_state.text = text
            response = image_generator(api_key=api_key, input_text=st.session_state.text,style=style)
            if response == None:
                st.write("Bad Response. 不適切なシーンです。内容を確認してください。\n\n今月のクレジットが尽きた可能性もあります。")
                if st.button("再起動する"):
                    st.rerun()
            st.session_state.title = st.session_state.text[:10]
            image_data = base64.b64decode(response.data[0].b64_json)
            image_stream = BytesIO(image_data)
            st.session_state.image = Image.open(image_stream)

    if "URL" in st.session_state:
        st.markdown(f'<a href="{st.session_state.URL}" target="_blank"><button style="background-color:black; color:white">全文を読みに行く（青空文庫HPへ移動）</button></a>', unsafe_allow_html=True)

    if "copyright" not in st.session_state:
        st.session_state["copyright"] = ""
    else:
        st.markdown(st.session_state["copyright"])

    st.sidebar.title("青空文庫から探す📖")
    authors = work_list_df["姓名"].unique().tolist()
    if st.sidebar.button('著者をランダムに選ぶ'):
        st.session_state['selected_author'] = random.choice(authors)
        works = work_list_df[work_list_df["姓名"]==st.session_state.selected_author]["作品名"].tolist()
        st.session_state['selected_work'] = random.choice(works)
        st.rerun()
    
    if 'selected_author' not in st.session_state:
        st.session_state['selected_author'] = random.choice(authors)
    selected_author = st.sidebar.selectbox("著者を選択してください", authors,
                                   index=authors.index(st.session_state['selected_author']))
    works = work_list_df[work_list_df["姓名"]==selected_author]["作品名"].tolist()
    if 'selected_work' in st.session_state:
        try:
            st.session_state.selected_work = st.sidebar.selectbox("作品を選択してください", works,
                                        index=works.index(st.session_state['selected_work']))
        except: #著者名だけ変えた時
            st.session_state.selected_work = st.sidebar.selectbox("作品を選択してください", works,
                                    index=0)
    else:
        st.session_state.selected_work = st.sidebar.selectbox("作品を選択してください", works,
                                    index=0)
        

    if st.sidebar.button('文章をランダムに抽出'):
        with st.spinner("Searching..."):
            st.session_state.URL = work_list_df[work_list_df["作品名"]==st.session_state.selected_work]["図書カードURL"].values[0] #ランダム選択    
            xhtml_content,copyright = get_xhtml_content(st.session_state.URL)
            if copyright == "NG":
                st.markdown(f'著作権が確認できない文章です。下記の図書カードを確認してください。\n<a href="{st.session_state.URL}">{st.session_state.URL}', unsafe_allow_html=True)
            else:
                st.session_state['copyright'] = copyright
                main_text = remove_html_tags(xhtml_content)
                sentences = split_into_sentences(main_text)
                # ランダムに文を選んで、200字以内で抽出
                extracted_sentence = extract_sentences(sentences)
                st.session_state['text'] = extracted_sentence
                st.rerun()

                if 'image' in st.session_state:
                    st.image(st.session_state['image'])

    # 画像がセッション状態にある場合、保存ボタンを表示
    if 'image' in st.session_state:
        st.image(st.session_state['image'])
        buffered = io.BytesIO()
        st.session_state['image'].save(buffered, format="JPEG")
        img_byte = buffered.getvalue()
        st.download_button(
            label="画像を保存",
            data=img_byte,
            file_name=f"IMG_{st.session_state.title}_{style_type}.jpg",
            mime="image/jpeg"
        )

if __name__ == '__main__':
    main()

