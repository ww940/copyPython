import requests
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyScraper:
    """代理数据爬虫基类"""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_yaml(self, url: str) -> str:
        """从 URL 拉取 YAML 格式数据"""
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            logger.info(f"✓ 成功拉取: {url} ({len(resp.text)} bytes)")
            return resp.text
        except requests.RequestException as e:
            logger.error(f"✗ 拉取失败 {url}: {e}")
            return ""
    
    def fetch_multiple(self, urls: List[str]) -> Dict[str, str]:
        """并发拉取多个来源"""
        results = {}
        for url in urls:
            results[url] = self.fetch_yaml(url)
        return results

# 使用示例
if __name__ == "__main__":
    scraper = ProxyScraper(timeout=15)
    
    sources = [
        "https://raw.githubusercontent.com/vxiaov/free_proxies@main/clash/clash.provider.yaml",
        "https://raw.githubusercontent.com/aiboboxx/clashfree@main/clash.yml",
    ]
    
    data = scraper.fetch_multiple(sources)
    for url, content in data.items():
        print(f"{url}: {len(content)} bytes")
