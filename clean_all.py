import os

os.system("ps -eo pid,user,cmd|grep -P 'openai.py|fastchat.serve|multiprocessing'|grep -v grep|awk '{print $1}'|xargs kill -9")