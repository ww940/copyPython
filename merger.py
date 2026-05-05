import yaml
from typing import List, Dict, Any
import hashlib

class ProxyMerger:
    """合并多个代理来源的 YAML 文件"""
    
    @staticmethod
    def parse_yaml(content: str) -> Dict[str, Any]:
        """解析 YAML 内容"""
        try:
            return yaml.safe_load(content) or {}
        except yaml.YAMLError as e:
            print(f"YAML 解析错误: {e}")
            return {}
    
    @staticmethod
    def extract_proxies(data: Dict) -> List[Dict]:
        """从 YAML 提取代理列表"""
        return data.get('proxies', [])
    
    @classmethod
    def merge_and_deduplicate(cls, yaml_contents: List[str]) -> List[Dict]:
        """合并多个 YAML 的代理，并去重"""
        all_proxies = []
        seen = set()
        
        for content in yaml_contents:
            data = cls.parse_yaml(content)
            proxies = cls.extract_proxies(data)
            
            for proxy in proxies:
                # 用 server + port 作为唯一标识
                proxy_key = f"{proxy.get('server')}:{proxy.get('port')}"
                if proxy_key not in seen:
                    all_proxies.append(proxy)
                    seen.add(proxy_key)
        
        print(f"合���后代理总数: {len(all_proxies)}")
        return all_proxies
    
    @classmethod
    def to_yaml(cls, proxies: List[Dict]) -> str:
        """转为 YAML 格式"""
        data = {'proxies': proxies}
        return yaml.dump(data, allow_unicode=True, default_flow_style=False)

# 使用示例
if __name__ == "__main__":
    yaml_list = [
        """
proxies:
  - name: 代理1
    server: 1.2.3.4
    port: 1080
    type: ss
  - name: 代理2
    server: 5.6.7.8
    port: 443
    type: trojan
""",
        """
proxies:
  - name: 代理3
    server: 9.10.11.12
    port: 1080
    type: ss
"""
    ]
    
    merged = ProxyMerger.merge_and_deduplicate(yaml_list)
    output_yaml = ProxyMerger.to_yaml(merged)
    print(output_yaml)
