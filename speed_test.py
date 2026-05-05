import asyncio
import aiohttp
import time
from typing import List, Dict, Any
from dataclasses import dataclass
import statistics

@dataclass
class SpeedResult:
    proxy_name: str
    server: str
    port: int
    latency_ms: float
    status: str  # 'ok' / 'timeout' / 'error'
    error_msg: str = ""

class SpeedTester:
    """代理速度测试"""
    
    def __init__(self, test_url="http://www.gstatic.com/generate_204", timeout=5):
        self.test_url = test_url
        self.timeout = timeout
    
    async def test_single(self, proxy: Dict[str, Any]) -> SpeedResult:
        """测试单个代理"""
        proxy_name = proxy.get('name', 'unknown')
        server = proxy.get('server')
        port = proxy.get('port')
        
        try:
            start = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.test_url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ssl=False
                ) as resp:
                    latency = (time.time() - start) * 1000
                    if resp.status == 204:
                        return SpeedResult(
                            proxy_name=proxy_name,
                            server=server,
                            port=port,
                            latency_ms=latency,
                            status='ok'
                        )
                    else:
                        return SpeedResult(
                            proxy_name=proxy_name,
                            server=server,
                            port=port,
                            latency_ms=latency,
                            status='error',
                            error_msg=f"HTTP {resp.status}"
                        )
        except asyncio.TimeoutError:
            return SpeedResult(
                proxy_name=proxy_name,
                server=server,
                port=port,
                latency_ms=self.timeout*1000,
                status='timeout',
                error_msg="Connection timeout"
            )
        except Exception as e:
            return SpeedResult(
                proxy_name=proxy_name,
                server=server,
                port=port,
                latency_ms=0,
                status='error',
                error_msg=str(e)
            )
    
    async def test_batch(self, proxies: List[Dict], concurrency=5) -> List[SpeedResult]:
        """并发测试多个代理"""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def limited_test(proxy):
            async with semaphore:
                return await self.test_single(proxy)
        
        tasks = [limited_test(p) for p in proxies]
        results = await asyncio.gather(*tasks)
        return results
    
    def rank_by_speed(self, results: List[SpeedResult]) -> List[SpeedResult]:
        """按速度排序（优先 ok，然后按延迟升序）"""
        ok_results = [r for r in results if r.status == 'ok']
        ok_results.sort(key=lambda r: r.latency_ms)
        return ok_results
    
    def print_report(self, results: List[SpeedResult]):
        """打印测速报告"""
        ok = [r for r in results if r.status == 'ok']
        print(f"\n测速报告 - 总数: {len(results)}, 成功: {len(ok)}")
        print("-" * 70)
        for r in ok[:10]:
            print(f"  {r.proxy_name:20s} | {r.server:20s}:{r.port:5d} | {r.latency_ms:6.1f}ms")

# 使用示例
async def main():
    proxies = [
        {'name': '测试1', 'server': '8.8.8.8', 'port': 80},
        {'name': '测试2', 'server': '1.1.1.1', 'port': 443},
    ]
    
    tester = SpeedTester(timeout=5)
    results = await tester.test_batch(proxies, concurrency=3)
    tester.print_report(results)
    ranked = tester.rank_by_speed(results)
    print("\n排序结果:", [r.proxy_name for r in ranked])

if __name__ == "__main__":
    asyncio.run(main())
