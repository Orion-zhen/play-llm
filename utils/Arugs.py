import argparse

parser = argparse.ArgumentParser(description="choose a model to load")
parser.add_argument("--chatglm2", "--chatglm", action="store_true", default=False, help="load chatglm2-6b")
parser.add_argument("-chatglm2-32k", "--chatglm-32k", action="store_true", default=False, help="load chatglm2-32k")
parser.add_argument("--qwen", "--Qwen", action="store_true", default=False, help="load 通义千问-7b")
parser.add_argument("--public", action="store_true", default=False, help="create a public link via ngrok")