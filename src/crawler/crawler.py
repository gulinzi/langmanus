"""
网页爬取模块

提供基于Jina客户端的网页内容提取功能，将HTML转换为结构化文章对象
包含命令行执行入口，支持指定URL或使用默认测试地址
"""

import sys

# 导入本地模块
from .article import Article                 # 文章数据结构定义
from .jina_client import JinaClient          # Jina网页抓取客户端
from .readability_extractor import ReadabilityExtractor  # 可读性内容提取器


class Crawler:
    """
    网页爬取器类
    
    功能说明：
    1. 使用JinaClient获取网页原始HTML
    2. 通过ReadabilityExtractor提取可读性内容
    3. 构建结构化Article对象返回
    
    设计决策：
    - 选择Jina原因：免费易用，适合基础爬取需求
    - 自定义提取器优势：相比Jina内置转换，提供更优的可读性处理
    - 模块化设计：各组件可独立替换升级
    """
    
    def crawl(self, url: str) -> Article:
        """
        执行网页爬取和内容提取流程
        
        参数:
            url (str): 需要抓取的网页URL
            
        返回:
            Article: 包含提取结果的结构化文章对象
            
        处理流程：
        1. 创建Jina客户端实例
        2. 获取网页HTML内容
        3. 使用提取器解析HTML生成文章对象
        4. 设置文章源URL属性
        """
        jina_client = JinaClient()  # 初始化Jina客户端
        html = jina_client.crawl(url, return_format="html")  # 获取原始HTML
        
        extractor = ReadabilityExtractor()  # 创建提取器实例
        article = extractor.extract_article(html)  # 提取可读性内容
        
        article.url = url  # 保存源URL
        return article  # 返回结构化结果


if __name__ == "__main__":
    """
    模块自执行入口
    
    使用方式：
    python crawler.py [URL]
    
    参数说明：
    - URL: 可选参数，指定需要抓取的网页地址
         若未指定，使用默认测试地址
    
    输出结果：
    提取后的Markdown格式内容
    """
    # 解析命令行参数
    if len(sys.argv) == 2:
        url = sys.argv[1]  # 使用用户指定URL
    else:
        # 默认测试地址（示例）
        url = "https://fintel.io/zh-hant/s/br/nvdc34"
    
    crawler = Crawler()  # 创建爬虫实例
    article = crawler.crawl(url)  # 执行爬取操作
    print(article.to_markdown())  # 输出Markdown结果
