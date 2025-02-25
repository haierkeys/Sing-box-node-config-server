#!/bin/sh

# 配置变量
PYTHON_SCRIPT="sev.py"  # 你的Python脚本文件名
PYTHON_PATH="python3"  # Python解释器路径（可以用 which python3 检查）
LOG_FILE="$SCRIPT_DIR/script.log" # 日志文件路径
KEYWORD="sev.py"        # 用于查找进程的关键字

# 启动函数
start() {
    echo "Starting $PYTHON_SCRIPT..."
    if pgrep -f "$KEYWORD" > /dev/null; then
        echo "Script is already running!"
    else
        nohup $PYTHON_PATH $PYTHON_SCRIPT >> $LOG_FILE 2>&1 &
        sleep 1  # 等待进程启动
        if pgrep -f "$KEYWORD" > /dev/null; then
            echo "Script started successfully. PID: $(pgrep -f "$KEYWORD")"
        else
            echo "Failed to start script. Check $LOG_FILE for details."
        fi
    fi
}

# 停止函数
stop() {
    echo "Stopping $PYTHON_SCRIPT..."
    if pgrep -f "$KEYWORD" > /dev/null; then
        pkill -f "$KEYWORD"
        sleep 1  # 等待进程结束
        if pgrep -f "$KEYWORD" > /dev/null; then
            echo "Failed to stop script, forcing kill..."
            pkill -9 -f "$KEYWORD"
        else
            echo "Script stopped successfully."
        fi
    else
        echo "Script is not running."
    fi
}

# 主逻辑
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    *)
        echo "Usage: $0 {start|stop}"
        exit 1
        ;;
esac

exit 0