#!/bin/sh

# 定义变量
PYTHON_CMD="python3"
PIP_CMD="pip3"
SCRIPT_DIR=$(dirname "$0")  # 自动获取脚本当前目录
SCRIPT_NAME="$SCRIPT_DIR/sb-config.py"
LOG_FILE="c.log"

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查依赖
check_deps() {
    # 检查 Python
    if ! command_exists "$PYTHON_CMD"; then
        echo "Error: $PYTHON_CMD not found. Please install $PYTHON_CMD manually to proceed."
        exit 1
    fi

    # 检查 pip
    if ! command_exists "$PIP_CMD"; then
        echo "Error: $PIP_CMD not found. Please install $PIP_CMD manually to proceed."
        exit 1
    fi

    # 安装 Python 包
    for package in watchdog jinja2; do
        if ! $PIP_CMD show "$package" >/dev/null 2>&1; then
            echo "Installing $package..."
            $PIP_CMD install "$package"
        fi
    done
}

# 获取脚本的 PID
get_pid() {
    pid=$(pgrep -f "[$PYTHON_CMD] $SCRIPT_NAME" | grep -v $$ )
    echo "$pid"
}

# 启动服务
start_service() {
    check_deps
    pid=$(get_pid)
    if [ -n "$pid" ]; then
        echo "Service is already running with PID: $pid"
    else
        echo "Starting $SCRIPT_NAME..."
        nohup $PYTHON_CMD "$SCRIPT_NAME" > "$LOG_FILE" 2>&1 &
        sleep 1
        pid=$(get_pid)
        if [ -n "$pid" ]; then
            echo "Service started with PID: $pid"
        else
            echo "Failed to start service"
            return 1
        fi
    fi
}

# 停止服务
stop_service() {
    pid=$(get_pid)
    if [ -n "$pid" ]; then
        echo "Stopping service (PID: $pid)..."
        kill "$pid"
        sleep 1
        if [ -z "$(get_pid)" ]; then
            echo "Service stopped"
        else
            echo "Failed to stop service"
            return 1
        fi
    else
        echo "Service is not running"
    fi
}

# 重启服务
restart_service() {
    stop_service
    sleep 1
    start_service
}

# 检查服务状态
status_service() {
    pid=$(get_pid)
    if [ -n "$pid" ]; then
        echo "Service is running with PID: $pid"
    else
        echo "Service is not running"
    fi
}

# 主逻辑
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0