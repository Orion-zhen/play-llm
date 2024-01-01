# play llm

这是我用来探索和学习llm玩法的仓库, 目前的内容有:

- (已废弃)套接字实现llm远程调用. 对应文件在`./sockets`文件夹下, 想看看python的套接字编程的可以看看
- (已废弃)fastapi实现llm远程调用. 对应文件是`./api.py`
- (正在使用)fastchat搭建openai compatible api server. 对应文件是`./openai.py`

## fastchat搭建openai服务器

[fastchat](https://github.com/lm-sys/FastChat)是一个可以快速构建llm服务器的库, 有了它你就可以用本地的llm搭建一个openai服务器, 然后将你的各种app或chrome插件的openai api server指向你自己的llm

目前我在用的, 支持自定义openai api server的chrome扩展有:

- [ChatGPT总结助手](https://chromewebstore.google.com/detail/chatgpt-%E6%80%BB%E7%BB%93%E5%8A%A9%E6%89%8B/nnjcoododbeemlmmhbfmmkbneniepaog): 一个帮你总结网页的插件
- [Sider](https://chromewebstore.google.com/detail/sider-chatgpt%E4%BE%A7%E8%BE%B9%E6%A0%8F+-vision/difoiogjjojoaoomphldepapgpbgkhkb): 集合了很多功能, 如llm聊天, 搜索, 翻译, 对选中文本聊天, 续写, 回复什么的, UI也比较漂亮, 但是它的llm搜索是不联网的
- [MaxAI](https://chromewebstore.google.com/detail/maxaime%EF%BC%9A%E9%9A%8F%E6%97%B6%E9%9A%8F%E5%9C%B0%E4%BD%BF%E7%94%A81-click-ai/mhnlakgilnojmhinhkckjpncpbhabphi): 也集合了很多功能, 但UI不如Sider美观, 优点是这个的llm搜索是联网的, 即把搜索结果喂给llm, 让llm总结, 并且同时支持多个ai服务同时生成搜索答案; 缺点是不能重新生成, 一次搜索之后结果就永远固定了
- [ChatHub](https://chromewebstore.google.com/detail/chathub-all-in-one-chatbo/iaakpnchhognanibcahlpcplchdfmgma): 集成了不同llm资源的插件, 但只能和它们对话
- [bilibili字幕列表](https://chromewebstore.google.com/detail/%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9%E5%AD%97%E5%B9%95%E5%88%97%E8%A1%A8/bciglihaegkdhoogebcdblfhppoilclp): 自动识别B站视频字幕, 提供了基于字幕的视频总结; 能否成功比较依赖于模型性能和prompt
- [Grarity](https://chromewebstore.google.com/detail/glarity-%E5%88%A9%E7%94%A8chatgpt4%E7%94%9F%E6%88%90%E6%91%98%E8%A6%81%E5%92%8C%E7%BF%BB%E8%AF%91/cmnlolelipjlhfkhpohphpedmkfbobjc): 像Sider一样也集成了很多功能, 搜索可以联网, 也可以重复生成; 但是它的openai api server只支持`HTTPS`, 需要自己配置SSL

### 本地部署

1. 将仓库下载到本地(如果嫌麻烦的话只下载`openai.py`, `clean_all.py`, `config/`文件夹也可以)
2. 安装依赖:

    ```shell
    pip install torch --index-url=https://download.pytorch.org/whl/cu121 # 对nvidia显卡
    pip install -r requirements.txt # 对nvidia显卡

    pip install torch --index-url=https://download.pytorch.org/whl/rocm5.6 # Linux+AMD显卡
    pip install -r requirements-amd.txt # Linux+AMD显卡

    pip install torch # Mac, 要求MacOS 12.3+
    pip install -r requirements-mps.txt # Mac
    ```

3. (可选)安装SSL证书:
    1. 安装`mkcert`:

        ```shell
        sudo apt install mkcert -y

        ```

    2. 安装本地CA:

        ```shell
        mkcert -install
        ```

        > 注: 想要卸载则运行`mkcert -uninstall`

    3. 生成SSL证书和密钥:

        ```shell
        cd /path/to/store/certificates
        mkcert 127.0.0.1 # 或者localhost, 或者其他网址
        ```

    4. 设置环境变量:

        ```shell
        export SSL_KEYFILE="/path/to/cert/127.0.0.1-key.pem"
        export SSL_CERTFILE="path/to/cert/127.0.0.1,pem"
        ```

4. 生成并修改配置文件:

    ```shell
    cp ./config/model_config.py.example ./config/model_config.py
    cp ./config/server_config.py.example ./config/server_config.py
    ```

5. 开始运行!

    ```shell
    python openai.py
    ```
