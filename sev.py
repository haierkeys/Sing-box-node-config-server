import http.server
import json
import os
from jinja2 import Environment, FileSystemLoader
import urllib.parse

envPassword = "password"
envServerPort = 8000
nodesName = []



current_dir = os.path.dirname(os.path.abspath(__file__))
# 读取节点信息
node_file = current_dir+'/node.json'
if os.path.exists(node_file):
    # 读取 JSON 文件内容
    with open(node_file, 'r', encoding='utf-8') as file:
        node_data = json.load(file)
        for item in node_data:
            nodesName.append(item['tag'])

# 设置全部节点变量
allNodes = json.dumps(node_data, ensure_ascii=False)[1:-1]

def NodeNameFilter(param: str = ""):
    nameParams = param.split("|")  # 将输入的 name 按 '|' 分割成一个列表

    filtered_list = []  # 创建一个空列表来保存符合条件的元素

    # 如果 name 是空字符串，返回整个 nodesName 列表
    if param == "":
        filtered_list = nodesName
    else:
        # 遍历 nodesName 中的每个元素，如果该元素在 names 中出现，则添加到 filtered_list 中
        for nodeName in nodesName:
            for name in nameParams:
                if name in nodeName:
                    filtered_list.append(nodeName)
    # 自定义函数逻辑
    return json.dumps(filtered_list, ensure_ascii=False)

class JSONRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # 设置响应状态码和头部信息
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        setType = query_params.get('type', [''])[0]
        password = query_params.get('password', [''])[0]

        if password != envPassword:
            self.wfile.write("Password Error".encode('utf-8'))
            return

        # 读取规则模版
        template_file = 'template.json'
        # 获取当前脚本所在的目录路径

        # 创建 Jinja2 环境，指定模板加载器
        env = Environment(loader=FileSystemLoader(current_dir))
        env.globals['NodeNameFilter'] = NodeNameFilter

        # 加载模板文件
        template = env.get_template(template_file)

        json_content = template.render(
            allNodes=allNodes,
            setType=setType
        )
        self.wfile.write(json_content.encode('utf-8'))


if __name__ == '__main__':
    # 设置服务器地址和端口
    server_address = ('', envServerPort)  # 监听所有可用的接口，端口号为 envServerPort
    # 创建 HTTP 服务器实例
    httpd = http.server.HTTPServer(server_address, JSONRequestHandler)
    print('Server is running on port '+ str(envServerPort)+'...')
    # 启动服务器，开始监听请求
    httpd.serve_forever()
