import scrapy
import json
from datetime import datetime
from urllib.parse import urljoin
import os

class XinhuanetSpider(scrapy.Spider):
    name = 'xinhuanet'
    allowed_domains = ['news.cn']
    start_urls = ['http://www.news.cn/tech/', 'http://www.news.cn/local/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []  # 用于存储抓取的新闻数据

    def parse(self, response):
        # 获取新闻列表页面的所有新闻链接和标题
        news_items = response.css('div.tit a')
        for news in news_items:
            title = news.css('::text').get()
            link = news.css('::attr(href)').get()
            if link and title:
                full_url = urljoin(response.url, link)
                self.logger.info(f'Title: {title}, Link: {full_url}')  # 调试输出
                # 将标题传递到详情页解析方法
                yield scrapy.Request(full_url, callback=self.parse_news, meta={'title': title})

        # 获取下一页链接
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)

    def parse_news(self, response):
        # 从 meta 中获取传递的标题
        title = response.meta['title']
        # 提取新闻内容，过滤掉空段落
        content_paragraphs = response.css('span#detailContent p::text').getall()
        content = ' '.join([paragraph.strip() for paragraph in content_paragraphs if paragraph.strip()])
        # 提取日期
        year = response.css('span.year em::text').get()
        day_parts = response.css('span.day em::text').getall()
        day = '-'.join(day_parts) if day_parts else None
        date = f"{year}-{day}" if year and day else datetime.now().strftime('%Y-%m-%d')
        # 提取 URL
        url = response.url

        if content:
            # 构建新闻数据
            news_item = {
                'title': title.strip(),
                'content': content,
                'url': url,
                'date': date
            }

            self.logger.info(f"Scraped item: {news_item}")  # 调试输出
            self.items.append(news_item)  # 保存到类变量
            yield news_item

    def closed(self, reason):
        # 确保 data 文件夹存在
        if not os.path.exists('data'):
            os.makedirs('data')

        # 爬虫关闭时，将数据保存为 JSON 文件
        with open('../data/news.json', 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Spider closed: {reason}. Total items scraped: {len(self.items)}")