import asyncio
import time
import json
import gc
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field
from playwright.async_api import async_playwright, Browser, BrowserContext
import psutil
import os
from asyncio import Queue, Semaphore
import signal
import sys

@dataclass
class PageConfig:
    """页面配置"""
    name: str
    url: str
    interval_seconds: int  # 每n秒
    batch_count: int      # 发送m次
    actions: List[Dict[str, Any]] = field(default_factory=list)  # 页面动作配置

@dataclass
class TestResult:
    """测试结果"""
    page_name: str
    success_count: int = 0
    failed_count: int = 0
    response_times: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)

class BrowserPool:
    """浏览器池管理"""
    def __init__(self, size: int = 3):
        self.pool = Queue(maxsize=size)
        self.size = size
        self.browsers: List[Browser] = []
        
    async def init(self, playwright):
        """初始化浏览器池"""
        for i in range(self.size):
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--single-process',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--max_old_space_size=512'
                ]
            )
            self.browsers.append(browser)
            await self.pool.put(browser)
            print(f"[浏览器池] 初始化浏览器 {i+1}/{self.size}")
            
    async def acquire(self) -> Browser:
        """获取浏览器实例"""
        return await self.pool.get()
        
    async def release(self, browser: Browser):
        """释放浏览器实例"""
        await self.pool.put(browser)
        
    async def close_all(self):
        """关闭所有浏览器"""
        for browser in self.browsers:
            try:
                await browser.close()
            except:
                pass

class OptimizedMultiPageStressTest:
    def __init__(self, page_configs: List[PageConfig], duration_minutes: int = 30):
        self.page_configs = page_configs
        self.duration_minutes = duration_minutes
        self.browser_pool = BrowserPool(size=5)  # 浏览器池大小
        self.semaphore = Semaphore(10)  # 最大并发数
        self.results: Dict[str, TestResult] = {
            config.name: TestResult(page_name=config.name) 
            for config in page_configs
        }
        self.running = True
        self.start_time = None
        
    async def execute_page_action(self, browser: Browser, config: PageConfig) -> tuple:
        """执行单个页面的操作"""
        context: BrowserContext = None
        page = None
        start_time = time.time()
        
        async with self.semaphore:  # 限制并发
            try:
                # 创建新的上下文
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    ignore_https_errors=True,
                    bypass_csp=True
                )
                context.set_default_timeout(15000)
                
                page = await context.new_page()
                
                # 阻止不必要的资源加载
                await page.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2}", 
                               lambda route: route.abort())
                
                # 导航到页面
                await page.goto(config.url, wait_until='domcontentloaded', timeout=10000)
                
                # 执行配置的动作
                for action in config.actions:
                    if action['type'] == 'fill':
                        await page.fill(action['selector'], action['value'], timeout=5000)
                    elif action['type'] == 'click':
                        await page.click(action['selector'], timeout=5000)
                    elif action['type'] == 'wait':
                        await page.wait_for_selector(action['selector'], timeout=5000)
                    elif action['type'] == 'wait_for_load':
                        await page.wait_for_load_state('networkidle', timeout=10000)
                        
                elapsed = time.time() - start_time
                return True, elapsed, None
                
            except Exception as e:
                elapsed = time.time() - start_time
                return False, elapsed, str(e)
                
            finally:
                # 确保资源释放
                if page:
                    await page.close()
                if context:
                    await context.close()
                    
    async def execute_batch(self, config: PageConfig):
        """批量执行测试"""
        tasks = []
        
        for i in range(config.batch_count):
            browser = await self.browser_pool.acquire()
            
            async def task_wrapper(browser, config):
                try:
                    success, elapsed, error = await self.execute_page_action(browser, config)
                    
                    # 更新结果
                    result = self.results[config.name]
                    if success:
                        result.success_count += 1
                        result.response_times.append(elapsed)
                    else:
                        result.failed_count += 1
                        if error and len(result.errors) < 100:  # 限制错误记录数量
                            result.errors.append(f"{datetime.now()}: {error}")
                            
                finally:
                    await self.browser_pool.release(browser)
                    
            task = task_wrapper(browser, config)
            tasks.append(task)
            
            # 添加小延迟避免瞬间并发
            await asyncio.sleep(0.1)
            
        # 等待所有任务完成
        await asyncio.gather(*tasks, return_exceptions=True)
        
    async def page_worker(self, config: PageConfig):
        """页面工作协程"""
        print(f"[{config.name}] 开始测试 - 每{config.interval_seconds}秒发送{config.batch_count}次请求")
        
        while self.running:
            batch_start = time.time()
            
            try:
                # 执行批量测试
                await self.execute_batch(config)
                
                # 显示该批次结果
                result = self.results[config.name]
                total = result.success_count + result.failed_count
                success_rate = (result.success_count / total * 100) if total > 0 else 0
                avg_response = (sum(result.response_times[-config.batch_count:]) / 
                              min(config.batch_count, len(result.response_times))) if result.response_times else 0
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {config.name}: "
                      f"本轮完成 {config.batch_count} 次请求, "
                      f"累计成功率: {success_rate:.1f}%, "
                      f"本轮平均响应: {avg_response:.2f}秒")
                
            except Exception as e:
                print(f"[错误] {config.name}: {str(e)}")
                
            # 计算下次执行时间
            elapsed = time.time() - batch_start
            sleep_time = max(0, config.interval_seconds - elapsed)
            
            if sleep_time > 0 and self.running:
                await asyncio.sleep(sleep_time)
                
    async def monitor_resources(self):
        """监控系统资源"""
        process = psutil.Process(os.getpid())
        
        while self.running:
            try:
                cpu_percent = process.cpu_percent(interval=1)
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                # 计算总体统计
                total_success = sum(r.success_count for r in self.results.values())
                total_failed = sum(r.failed_count for r in self.results.values())
                total_requests = total_success + total_failed
                overall_success_rate = (total_success / total_requests * 100) if total_requests > 0 else 0
                
                elapsed_minutes = (time.time() - self.start_time) / 60 if self.start_time else 0
                
                print(f"\n{'='*80}")
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 运行状态")
                print(f"已运行: {elapsed_minutes:.1f} 分钟 / {self.duration_minutes} 分钟")
                print(f"系统资源 - CPU: {cpu_percent}%, 内存: {memory_mb:.1f}MB")
                print(f"总体统计 - 总请求: {total_requests}, 成功: {total_success}, "
                      f"失败: {total_failed}, 成功率: {overall_success_rate:.1f}%")
                
                # 各页面简要统计
                for name, result in self.results.items():
                    if result.success_count + result.failed_count > 0:
                        page_success_rate = (result.success_count / 
                                           (result.success_count + result.failed_count) * 100)
                        print(f"  {name}: 成功 {result.success_count}, "
                              f"失败 {result.failed_count}, "
                              f"成功率 {page_success_rate:.1f}%")
                
                print(f"{'='*80}\n")
                
                # 内存管理
                if memory_mb > 1000:
                    gc.collect()
                    print("[警告] 内存使用超过1GB，已触发垃圾回收")
                    
            except Exception as e:
                print(f"[监控错误] {str(e)}")
                
            await asyncio.sleep(30)  # 每30秒更新一次
            
    async def run_test(self):
        """运行压力测试"""
        print(f"\n{'='*80}")
        print(f"多页面压力测试")
        print(f"测试时长: {self.duration_minutes} 分钟")
        print(f"页面配置: {len(self.page_configs)} 个")
        print(f"{'='*80}\n")
        
        async with async_playwright() as playwright:
            try:
                # 初始化浏览器池
                await self.browser_pool.init(playwright)
                
                self.start_time = time.time()
                end_time = self.start_time + (self.duration_minutes * 60)
                
                # 启动所有任务
                tasks = []
                
                # 启动监控任务
                monitor_task = asyncio.create_task(self.monitor_resources())
                tasks.append(monitor_task)
                
                # 启动各页面的测试任务
                for config in self.page_configs:
                    task = asyncio.create_task(self.page_worker(config))
                    tasks.append(task)
                    
                # 等待测试时间结束
                while time.time() < end_time and self.running:
                    await asyncio.sleep(1)
                    
                self.running = False
                
                # 等待所有任务结束
                await asyncio.gather(*tasks, return_exceptions=True)
                
            finally:
                # 清理资源
                await self.browser_pool.close_all()
                
        # 生成最终报告
        self.generate_final_report()
        
    def generate_final_report(self):
        """生成最终测试报告"""
        print(f"\n{'='*80}")
        print(f"压力测试最终报告")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试时长: {self.duration_minutes} 分钟")
        print(f"{'='*80}\n")
        
        # 总体统计
        total_success = sum(r.success_count for r in self.results.values())
        total_failed = sum(r.failed_count for r in self.results.values())
        total_requests = total_success + total_failed
        overall_success_rate = (total_success / total_requests * 100) if total_requests > 0 else 0
        
        print(f"总体统计:")
        print(f"  总请求数: {total_requests}")
        print(f"  成功请求: {total_success}")
        print(f"  失败请求: {total_failed}")
        print(f"  总体成功率: {overall_success_rate:.2f}%")
        print(f"  平均RPS: {total_requests / (self.duration_minutes * 60):.2f}")
        
        # 各页面详细统计
        print(f"\n各页面详细统计:")
        for name, result in self.results.items():
            print(f"\n[{name}]")
            total = result.success_count + result.failed_count
            if total > 0:
                success_rate = (result.success_count / total * 100)
                avg_response = sum(result.response_times) / len(result.response_times) if result.response_times else 0
                max_response = max(result.response_times) if result.response_times else 0
                min_response = min(result.response_times) if result.response_times else 0
                
                print(f"  总请求: {total}")
                print(f"  成功: {result.success_count}")
                print(f"  失败: {result.failed_count}")
                print(f"  成功率: {success_rate:.2f}%")
                print(f"  平均响应时间: {avg_response:.2f}秒")
                print(f"  最大响应时间: {max_response:.2f}秒")
                print(f"  最小响应时间: {min_response:.2f}秒")
                
                # 显示前5个错误
                if result.errors:
                    print(f"  最近错误 (最多显示5个):")
                    for error in result.errors[-5:]:
                        print(f"    - {error}")
                        
        print(f"\n{'='*80}")

# 使用示例
async def main():
    # 配置多个页面的测试
    page_configs = [
        PageConfig(
            name="登录页面A",
            url="https://example
