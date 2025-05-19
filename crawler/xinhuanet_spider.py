import scrapy
import json
from datetime import datetime
from urllib.parse import urljoin

class XinhuanetSpider(scrapy.Spider):
    name = 'xinhuanet'
    allowed_domains = ['news.cn']
    start_urls = ['http://www.news.cn/politics/', 'http://www.news.cn/local/']
    
    def parse(self, response):
        # 获取新闻列表页面的所有新闻链接
        news_links = response.css('a::attr(href)').getall()
        for link in news_links:
            if link.startswith('/') or 'news.cn' in link:
                full_url = urljoin(response.url, link)
                yield scrapy.Request(full_url, callback=self.parse_news)
        
        # 获取下一页链接
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)
    
    def parse_news(self, response):
        # 提取新闻内容
        title = response.css('h1::text').get()
        content = ' '.join(response.css('div.article p::text').getall())
        date = response.css('span.time::text').get()
        url = response.url
        
        if title and content:
            # 清理数据
            title = title.strip()
            content = content.strip()
            if date:
                date = date.strip()
            else:
                date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 构建新闻数据
            news_item = {
                'title': title,
                'content': content,
                'url': url,
                'date': date
            }
            
            yield news_item

    def closed(self, reason):
        # 爬虫关闭时，将数据保存为JSON文件
        items = []
        for item in self.crawler.stats.get_stats().get('item_scraped_count', 0):
            items.append(item)
        
        with open('data/news.json', 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2) 