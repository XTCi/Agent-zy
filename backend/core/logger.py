from loguru import logger
import sys
import os
from app.core.config import settings

# 确保日志目录存在
log_dir = os.path.dirname(settings.LOG_FILE)
if not os.path.exists(log_dir):
    os.makedirs(log_dir,exist_ok=True)

# 移除默认的处理器
logger.remove()
DefaultFormat = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <6}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# 添加控制台处理器
logger.add(
    sys.stderr,
    # format=settings.LOG_FORMAT,
    format = DefaultFormat,
    level=settings.LOG_LEVEL,
    colorize=True
)

# 添加文件处理器
logger.add(
    settings.LOG_FILE,
    format=DefaultFormat,
    level=settings.LOG_LEVEL,
    rotation="50 MB",
    retention="7 days",
    compression="zip"
)

def get_logger():
    return logger