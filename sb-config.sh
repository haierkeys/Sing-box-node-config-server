#!/bin/bash

# 定义变量
APP_NAME="sb-config"              # 服务名称
PYTHON_BIN="python3"  # Python解释器路径，根据你的环境调整
APP_PATH="./sb-config"  # Python脚本的完整路径
PID_FILE="/var/run/${APP_NAME}.pid"  # PID文件路径，用于记录进程ID
LOG_FILE="/var/log/${APP_NAME}.log"  # 日志文件路径

# 检查命令参数
case "$1" in
    start)
        echo "Starting $APP_NAME..."
        if [ -f "$PID_FILE" ]; then
            echo "$APP_NAME is already running with PID $(cat $PID_FILE)"
            exit 1
        fi
        # 后台启动Python脚本，重定向输出到日志文件
        nohup $PYTHON_BIN $APP_PATH >> $LOG_FILE 2>&1 &
        # 记录进程ID到PID文件
        echo $! > $PID_FILE
        if [ $? -eq 0 ]; then
            echo "$APP_NAME started with PID $(cat $PID_FILE)"
        else
            echo "Failed to start $APP_NAME"
            exit 1
        fi
        ;;
    stop)
        echo "Stopping $APP_NAME..."
        if [ ! -f "$PID_FILE" ]; then
            echo "$APP_NAME is not running"
            exit 1
        fi
        PID=$(cat $PID_FILE)
        # 杀掉进程并删除PID文件
        kill -9 $PID
        if [ $? -eq 0 ]; then
            rm -f $PID_FILE
            echo "$APP_NAME stopped"
        else
            echo "Failed to stop $APP_NAME"
            exit 1
        fi
        ;;
    restart)
        # 先停止，再启动
        $0 stop
        sleep 2  # 等待2秒，确保进程完全停止
        $0 start
        ;;
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat $PID_FILE)
            if ps -p $PID > /dev/null; then
                echo "$APP_NAME is running with PID $PID"
            else
                echo "$APP_NAME PID file exists but process is not running"
                rm -f $PID_FILE  # 清理无效的PID文件
            fi
        else
            echo "$APP_NAME is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0