from ast import arg
from config.model_config import DEFULT_PROMPT
from utils.Handlers import create_worker
from transformers import pipeline
from urllib import parse
from pprint import pprint
import argparse
import requests
import gradio
import time
import html
import re

par = argparse.ArgumentParser()
par.add_argument(
    "--python",
    "-p",
    action="store_true",
    default=False,
    help="to load python specified model or not",
)
argument = par.parse_args()

CODER = "codellama-34b-gptq" if not argument.python else "codellama-34b-python-gptq"
GOOGLE_TRANSLATE_URL = "http://translate.google.com/m?q=%s&tl=%s&sl=%s"
cur_prompt = DEFULT_PROMPT
worker = create_worker(CODER)


def set_prompt(prompt: str) -> str:
    cur_prompt = prompt
    return cur_prompt


def reset_prompt() -> str:
    cur_prompt = DEFULT_PROMPT
    return cur_prompt


def translate(text, to_language="auto", text_language="auto"):
    text = parse.quote(text)
    url = GOOGLE_TRANSLATE_URL % (text, to_language, text_language)
    response = requests.get(url)
    data = response.text
    expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
    result = re.findall(expr, data)
    if len(result) == 0:
        return ""

    return html.unescape(result[0])


def pipe_gen(
    user_inputs: str,
    language: str,
    max_new_tokens: int = 8192,
    do_sample: bool = True,
    temperature: float = 0.7,
    top_p: float = 0.7,
    # top_k: float = 0.95,
    repetition_penalty: float = 1.1,
    translated=True,
):
    msg = cur_prompt.format(sys=language, user=user_inputs)
    generator = pipeline(
        "text-generation",
        model=worker.model,
        tokenizer=worker.tokenizer,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        temperature=temperature,
        top_p=top_p,
        # top_k=top_k,
        repetition_penalty=repetition_penalty,
    )
    # yield "Thinking..."
    response = str(generator(msg)[0]["generated_text"])
    response = response.replace(msg, "")
    # pprint(response)

    if translated:
        splited_texts = response.split("```")
        translated_texts = []
        # 代码段和非代码段必然交替出现, 且第一段必然为非代码段
        is_code = False
        for splited_one in splited_texts:
            if not is_code:
                # pprint(splited_one)
                splited_one = translate(splited_one, "zh-CN", "en")
                # pprint(splited_one)
                is_code = True
            else:
                is_code = False
            translated_texts.append(splited_one)
        response = "\n```".join(translated_texts)

    pprint("------------------------------------------------------------")
    pprint(response)
    pprint("------------------------------------------------------------")
    # return response
    stream_res = ""
    for ch in response:
        time.sleep(0.005)
        stream_res += ch
        yield stream_res


# 可选的themes: NoCrypt/miku, xiaobaiyuan/theme_land, gradio/soft
with gradio.Blocks(theme="gradio/soft", title="CodeLlama-34B") as webui:
    with gradio.Tab("Inference"):
        with gradio.Row():
            with gradio.Column():
                user_inputs = gradio.Textbox(
                    label="Input", lines=30, scale=16, show_copy_button=True
                )
                with gradio.Row():
                    max_new_tokens = gradio.Number(label="Max New Tokens", value=8192)
                    language = gradio.Dropdown(
                        label="Language",
                        choices=[
                            "C++",
                            "Python",
                            "C",
                            "HTML",
                            "Java",
                            "JavaScript",
                            "Assembly",
                            "Go",
                            "Rust",
                            "C#",
                            "cmake",
                            "Bash",
                        ],
                        value="C++" if CODER == "codellama-34b-gptq" else "Python",
                    )
                with gradio.Row():
                    do_sample = gradio.Checkbox(label="Do Sample", value=True)
                    output_translation = gradio.Checkbox(
                        label="Output Translation", value=False
                    )
                with gradio.Row():
                    temperature = gradio.Slider(
                        label="Temperature",
                        value=0.7,
                        step=0.05,
                        minimum=0.0,
                        maximum=2.0,
                    )
                    top_p = gradio.Slider(
                        label="Top P", value=0.7, step=0.05, minimum=0.0, maximum=1.0
                    )
                    top_k = gradio.Slider(
                        label="Top K", value=0.95, step=0.05, minimum=0.0, maximum=1.0
                    )
                    repetition_penalty = gradio.Slider(
                        label="Repetition Penalty",
                        value=1.1,
                        step=0,
                        minimum=0.0,
                        maximum=2.0,
                    )
            with gradio.Column():
                model_res_markdown = gradio.Markdown(
                    value="Model Output", visible=not argument.python, line_breaks=True
                )
                model_res_box = gradio.Textbox(
                    label="Model Output", visible=argument.python, lines=30
                )
                gen_btn = gradio.Button(value="Generate")
                gen_btn.click(
                    fn=pipe_gen,
                    inputs=[
                        user_inputs,
                        language,
                        max_new_tokens,
                        do_sample,
                        temperature,
                        top_p,
                        # top_k,
                        repetition_penalty,
                        output_translation,
                    ],
                    outputs=model_res_markdown
                    if not argument.python
                    else model_res_box,
                )

    with gradio.Tab("Prompt"):
        with gradio.Row():
            with gradio.Column():
                prompt_input = gradio.Textbox(label="Prompt Input", lines=10)
                set_btn = gradio.Button(value="Set Prompt")
            with gradio.Column():
                prompt_output = gradio.Textbox(
                    label="Current Prompt", lines=10, value=cur_prompt
                )
                reset_btn = gradio.Button(value="Reset Prompt")
        set_btn.click(fn=set_prompt, inputs=prompt_input, outputs=prompt_output)
        reset_btn.click(fn=reset_prompt, inputs=None, outputs=prompt_output)

    with gradio.Tab("Translators"):
        with gradio.Row():
            with gradio.Column():
                text_language = gradio.Dropdown(
                    label="Source Language",
                    choices=["auto", "en", "zh-CN", "ja"],
                    value="en",
                )
                source_text = gradio.Textbox(
                    label="Source Text", lines=10, show_copy_button=True
                )
                provider = gradio.Dropdown(
                    label="Translator", choices=["Google"], value="Google"
                )
            with gradio.Column():
                to_language = gradio.Dropdown(
                    label="Target Language",
                    choices=["auto", "en", "zh-CN", "ja"],
                    value="zh-CN",
                )
                output_text = gradio.Textbox(
                    label="Translated Text", lines=10, show_copy_button=True
                )
                translate_btn = gradio.Button(label="Translate")
                translate_btn.click(
                    fn=translate,
                    inputs=[source_text, to_language, text_language],
                    outputs=output_text,
                )


if __name__ == "__main__":
    webui.queue()
    webui.launch()
