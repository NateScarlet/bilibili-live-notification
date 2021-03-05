# B 站直播提醒

[![docker](https://github.com/NateScarlet/bilibili-live-notification/workflows/docker/badge.svg)](https://github.com/NateScarlet/bilibili-live-notification/actions)

在指定房间开播时发送邮件通知。

用于解决 B 站手机端 99% 开播都不能及时推送的问题。

- [x] 同时监控多个直播间
- [x] 开播时给所有指定的邮箱发送邮件
- [x] 事件节流，时间段内同一直播间内的同类型事件只处理一次。
- [x] 事件去重，通过事件生成 key ，同房间相同 key 的事件不重复处理。
- [x] 支持 Webhook （用于配合其他服务，例如使用 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 发送 QQ 消息，使用 Discord 官方 API 发送 Discord 消息）
  - [x] 所有直播间事件都支持 Webhook，不仅限于 LIVE 事件
  - [x] 根据条件跳过 Webhook
- [x] 为每个直播间单独指定设置，未指定时使用全局设置

## 配置

完全使用环境变量进行配置，参见 [.env.example](./.env.example)

推荐将环境变量写入 .env 文件然后再使用 [godotenv](https://github.com/joho/godotenv) 在配置的环境下执行命令

### 模版

除模版变量设置外的所有设置都支持模版，使用 [JinJa2](https://jinja.palletsprojects.com/) 作为模版引擎

可通过设置定义变量，并且提供内置变量。

变量覆盖优先级，序号小的值覆盖序号大的值：

1. 房间
2. 全局
3. 内置

全局模版变量值：

- datetime: type(datetime.datetime)

  datetime 模块

开播提醒：

- event:

  ```typescript
  {
      room_display_id: number,
      room_real_id: number,
      type: string,
      data: unknown | number
  }
  ```

  变量事件，data 字段的类型参见 [event.example.json](./event.example.json)

- room:

  ```typescript
  {
      name: string,
      title: string,
      url: string,
      data: unknown,
  }
  ```

  房间信息，参见 [room.ipynb](./room.ipynb)

## 从命令行运行

```bash
python3.8 -m pip install -r requirements.txt
python3.8 -m bilibili_live_notification
```

## Docker 部署

参考 [docker-compose.yml](./deployments/docker-compose.yml) 配合 .env 文件使用。
