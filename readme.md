# Sing-box Node Config Server Tools / 节点配置服务工具

----
从节点文件读取 `节点信息` 并生成完整的 `sing-box 配置信息`

## 使用说明
### 安装模块

```bash
pip install jinja2
pip install watchdog
```

### 运行脚本
```
python3 sev.py
```

### 使用说明
默认 `8000` 端口, 访问地址为 `http://127.0.0.1:8000/?type=ios&password=password`

请求参数说明
| 参数     | 说明                                           | 其他       |
|----------|----------------------------------------------|------------|
| `type`     | 类型,用于多端,返回不同配置使用                 | 例如 `linux` |
| `password` | 访问密码 ,默认 `password` , 在 `sev.py` 内修改 |            |


### 规则模版说明
脚本默认从 `node.json` 读取所有节点信息


`{{ allNodes }}` 生成所有节点详细配置列表, 不含 json 的 []

`{{ NodeNameFilter() }}` 生成所有节点名字列表, 含有[]

`{{ NodeNameFilter('日本') }}` 生成 tag 为 日本的节点名字列表, 含有[]

`{% if setType == 'linux' %} "auto_redirect": true,{% else %} "auto_route": true, {% endif %}` 用于多端返回不同配置