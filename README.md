# B 站直播提醒

在指定房间开播时发送邮件通知。

用于解决 B 站手机端 99% 开播都不能及时推送的问题。

- [x] 同时监控多个直播间
- [x] 开播时给所有指定的邮箱发送邮件

## 配置

完全使用环境变量进行配置，参见 [.env.example](./.env.example)

推荐将环境变量写入 .env 文件然后再使用 [godotenv](https://github.com/joho/godotenv) 在配置的环境下执行命令

## 从命令行运行

```bash
python3.8 -m pip install -r requirements.txt
python3.8 -m bilibili_live_notification
```
