import scrapy
import json
from datetime import datetime
from urllib.parse import urljoin
import os

class XinhuanetSpider(scrapy.Spider):
    name = 'xinhuanet'
    allowed_domains = ['news.cn']
    # 增加更多新闻分类
    start_urls = [
        'http://www.news.cn/tech/',
        'http://www.news.cn/local/',
        'http://www.news.cn/politics/',
        'http://www.news.cn/fortune/',
        'http://www.news.cn/ent/',
        'http://www.news.cn/sports/',
        'http://www.news.cn/mil/',
        'http://www.news.cn/edu/'
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []  # 用于存储抓取的新闻数据
        self.page_count = 0  # 用于记录已抓取的页面数
        self.max_pages = 20  # 每个分类最多抓取20页

    def parse(self, response):
        # 获取新闻列表页面的所有新闻链接和标题
        news_items = response.css('div.tit a, div.news-item a, div.news-item-title a')
        for news in news_items:
            title = news.css('::text').get()
            link = news.css('::attr(href)').get()
            if link and title:
                full_url = urljoin(response.url, link)
                self.logger.info(f'Title: {title}, Link: {full_url}')
                yield scrapy.Request(full_url, callback=self.parse_news, meta={'title': title})

        # 获取下一页链接
        self.page_count += 1
        if self.page_count < self.max_pages:
            next_page = response.css('a.next::attr(href), a.page-next::attr(href)').get()
            if next_page:
                next_url = urljoin(response.url, next_page)
                self.logger.info(f'Following next page: {next_url}')
                yield scrapy.Request(next_url, callback=self.parse)

    def parse_news(self, response):
        # 从 meta 中获取传递的标题
        title = response.meta['title']
        
        # 尝试多种可能的内容选择器
        content_selectors = [
            'span#detailContent p::text',
            'div.article p::text',
            'div.content p::text',
            'div.article-content p::text'
        ]
        
        content = ''
        for selector in content_selectors:
            paragraphs = response.css(selector).getall()
            if paragraphs:
                content = ' '.join([p.strip() for p in paragraphs if p.strip()])
                break
        
        # 尝试多种可能的日期选择器
        date = None
        date_selectors = [
            ('span.year em::text', 'span.day em::text'),
            ('span.time::text', None),
            ('div.time::text', None),
            ('span.date::text', None)
        ]
        
        for year_selector, day_selector in date_selectors:
            if day_selector:
                year = response.css(year_selector).get()
                day_parts = response.css(day_selector).getall()
                if year and day_parts:
                    day = '-'.join(day_parts)
                    date = f"{year}-{day}"
                    break
            else:
                date = response.css(year_selector).get()
                if date:
                    date = date.strip()
                    break
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
            
        url = response.url

        if content:
            # 构建新闻数据
            news_item = {
                'title': title.strip(),
                'content': content,
                'url': url,
                'date': date
            }

            self.logger.info(f"Scraped item: {news_item}")
            self.items.append(news_item)
            yield news_item

    def closed(self, reason):
        # 确保 data 文件夹存在
        if not os.path.exists('data'):
            os.makedirs('data')

        # 爬虫关闭时，将数据保存为 JSON 文件
        with open('data/news.json', 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Spider closed: {reason}. Total items scraped: {len(self.items)}") 