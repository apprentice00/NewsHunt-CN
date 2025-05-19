BOT_NAME = "xinhuanet"

SPIDER_MODULES = ["xinhuanet.spiders"]
NEWSPIDER_MODULE = "xinhuanet.spiders"

# 遵守robots.txt规则
ROBOTSTXT_OBEY = True

# 配置请求头
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 下载延迟
DOWNLOAD_DELAY = 1

# 启用自动限速
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0 