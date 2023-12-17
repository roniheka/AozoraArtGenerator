import streamlit as st

from html import unescape
from openai import OpenAI

def image_generator(api_key="",input_text="",style=""):
    client = OpenAI(api_key=api_key)
    try:
        response = client.images.generate(
        model="dall-e-3",
        prompt="以下の小説の場面を表現した、1枚のイラストを生成してください。\
            登場人物の性別や外観は、人物の名前や振る舞い、発言内容から推定してください。"
            +style
            +"(Note: YOU MUST NOT show any text on the image!)"
            +input_text,
        size="1024x1024",
        quality="standard",
        n=1,
        response_format="b64_json",
        )
        return response
    except Exception as e:
        return None
