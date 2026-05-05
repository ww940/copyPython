#!/usr/bin/env python3
"""
主流程：爬取 -> 合并 -> 测速 -> 输出
用于 GitHub Actions 定时执行
"""

import sys
import asyncio
from pathlib import Path
import json
from datetime import datetime

from scraper import ProxyScraper
from merger import ProxyMerger
from speed_test import SpeedTester

SOURCES = [
    "https://raw.githubusercontent.com/vxiaov/free_proxies@main/clash/clash.provider.yaml",
    "https://raw.githubusercontent.com/aiboboxx/clashfree@main/clash.yml",
    "https://raw.githubusercontent.com/chengaopan/AutoMergePublicNodes/master/list.yml",
]

OUTPUT_FILE = "proxies.yaml"
STATS_FILE = "stats.json"

async def main():
    print(f"[{datetime.now()}] 开始爬取和测速流程")
    
    # 1. 爬取
    print("\n[步骤 1] 爬取代理源...")
    scraper = ProxyScraper(timeout=15)
    yaml_contents = []
    for source in SOURCES:
        content = scraper.fetch_yaml(source)
        if content:
            yaml_contents.append(content)
    
    if not yaml_contents:
        print("✗ 无法获取任何代理源")
        return 1
    
    # 2. 合并与去重
    print("\n[步骤 2] 合并并去重...")
    merged_proxies = ProxyMerger.merge_and_deduplicate(yaml_contents)
    print(f"✓ 合并后代理总数: {len(merged_proxies)}")
    
    if len(merged_proxies) < 10:
        print(f"✗ 代理数量过少 ({len(merged_proxies)} < 10)")
        return 1
    
    # 3. 测速（可选，耗时较长）
    print("\n[步骤 3] 执行速度测试...")
    tester = SpeedTester(timeout=5)
    speed_results = await tester.test_batch(merged_proxies[:20], concurrency=5)
    tester.print_report(speed_results)
    
    ranked = tester.rank_by_speed(speed_results)
    if ranked:
        # 将测速最快的代理放在前面
        fast_proxies = [r.proxy_name for r in ranked[:10]]
        print(f"✓ 最快的代理: {fast_proxies}")
    
    # 4. 输出 YAML
    print("\n[步骤 4] 输出结果...")
    output_yaml = ProxyMerger.to_yaml(merged_proxies)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output_yaml)
    print(f"✓ 已输出: {OUTPUT_FILE}")
    
    # 5. 统计信息
    stats = {
        'timestamp': datetime.now().isoformat(),
        'total_proxies': len(merged_proxies),
        'passed_speed_test': len([r for r in speed_results if r.status == 'ok']),
        'sources': len(yaml_contents)
    }
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"✓ 统计信息: {json.dumps(stats)}")
    
    print(f"\n[{datetime.now()}] 流程完成")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
