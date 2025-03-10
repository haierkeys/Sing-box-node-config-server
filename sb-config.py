import http.server
import json
import os
from jinja2 import Environment, FileSystemLoader
import urllib.parse
import socketserver
import logging
import time
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from config import envPassword, envServerPort, nodeFile, configTemplateFile  # 导入配置

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='server.log'
)

# 配置路径
currentDir = os.path.dirname(os.path.abspath(__file__))
nodeFilePath = os.path.join(currentDir, nodeFile)
configTemplateFilePath = os.path.join(currentDir, configTemplateFile)
excludedFilePath = os.path.join(currentDir, "server.log") # 替换成你想排除的文件路径

# 全局变量
nodesName = []
nodeData = []
allNodes = ""
env = None
template = None

def loadNodeData():
    """加载 node.json 数据"""
    global nodesName, nodeData, allNodes
    if os.path.exists(nodeFilePath):
        with open(nodeFilePath, 'r', encoding='utf-8') as file:
            nodeData = json.load(file)
            nodesName = [item['tag'] for item in nodeData]
            allNodes = json.dumps(nodeData, ensure_ascii=False)[1:-1]
        logging.info(f"Loaded {nodeFile}")
    else:
        logging.warning(f"{nodeFilePath} not found")

def loadTemplate():
    """加载 Jinja2 模板"""
    global env, template
    env = Environment(loader=FileSystemLoader(currentDir))
    env.globals['NodeNameFilter'] = lambda param = "": nodeNameFilter(param)
    template = env.get_template(configTemplateFile)
    logging.info(f"Loaded {configTemplateFile}")

# 初始加载
loadNodeData()
loadTemplate()

def nodeNameFilter(param: str = ""):
    nameParams = param.split("|")
    filteredList = nodesName if param == "" else [
        nodeName for nodeName in nodesName if any(name in nodeName for name in nameParams)
    ]
    if len(filteredList) == 0:
        return "[\"🚀 节点选择\"]"
    return json.dumps(filteredList, ensure_ascii=False)

class JSONRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            logging.info(f"Request from {self.client_address}: {self.path}")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            parsedUrl = urllib.parse.urlparse(self.path)
            queryParams = urllib.parse.parse_qs(parsedUrl.query)
            setType = queryParams.get('type', [''])[0]
            password = queryParams.get('password', [''])[0]

            if password != envPassword:
                self.wfile.write("Password Error".encode('utf-8'))
                return

            jsonContent = template.render(allNodes=allNodes, setType=setType)
            self.wfile.write(jsonContent.encode('utf-8'))
        except BrokenPipeError:
            logging.warning(f"Client {self.client_address} disconnected during response")
        except Exception as e:
            logging.error(f"Error processing request from {self.client_address}: {str(e)}")
            try:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f"Server Error: {str(e)}".encode('utf-8'))
            except BrokenPipeError:
                logging.warning(f"Client {self.client_address} disconnected during error response")

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except ValueError as e:
            logging.warning(f"Invalid request from {self.client_address}: {str(e)}")
            try:
                self.send_error(400, "Bad Request")
            except BrokenPipeError:
                logging.warning(f"Client {self.client_address} disconnected during error response")

class FileChangeHandler(FileSystemEventHandler):
    global excludedFilePath
    """文件变化处理器"""
    def on_modified(self, event):

        if not event.is_directory:
            #logging.info(event.src_path)
            filePath = event.src_path
            if filePath == excludedFilePath:
                return  # 如果是排除的文件，则直接返回，后续代码不再执行
            if filePath == nodeFilePath:
                logging.info(filePath)
                logging.info(f"Config node change in {filePath}, reloading...")
                loadNodeData()
            elif filePath == configTemplateFilePath:
                logging.info(filePath)
                logging.info(f"Config main change in {filePath}, reloading...")
                loadTemplate()

def startFileWatcher():
    """启动文件监控"""
    eventHandler = FileChangeHandler()
    observer = PollingObserver()
    observer.schedule(eventHandler, currentDir, recursive=False)
    observer.start()
    logging.info("File watcher started")
    try:
        while True:
            time.sleep(1)  # 保持线程运行
    except KeyboardInterrupt:
        logging.info("File watcher stopped by user")
        observer.stop()
    observer.join()

if __name__ == '__main__':
    # 使用 ThreadingTCPServer 支持多线程
    class ReusableThreadingTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True

    # 启动文件监控线程
    import threading
    watcherThread = threading.Thread(target=startFileWatcher, daemon=True)
    watcherThread.start()

    # 启动 HTTP 服务器
    serverAddress = ('', envServerPort)
    httpd = ReusableThreadingTCPServer(serverAddress, JSONRequestHandler)
    logging.info(f'Server is running on port {envServerPort}...')
    print(f'Server is running on port {envServerPort}...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        print("\nServer stopped.")
        httpd.server_close()