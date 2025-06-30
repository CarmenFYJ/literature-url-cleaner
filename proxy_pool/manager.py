from proxy_list import ProxyManager as PLProxyManager
import random
import asyncio
import logging
from .utils import verify_proxy_async

class ProxyManager:
    def __init__(self, scheme='http', max_retries=3, timeout=5):
        """
        scheme: 'http', 'https', 'socks4', 'socks5'
        max_retries: 获取有效代理的最大尝试次数
        timeout: 验证代理时的超时时间（秒）
        """
        self.scheme = scheme
        self.max_retries = max_retries
        self.timeout = timeout
        self._manager = PLProxyManager()
        self._proxy_list = []
    
    def refresh_proxies(self):
        """刷新代理列表（从proxy-list拉取最新代理）"""
        try:
            self._proxy_list = self._manager.get_proxy_list(self.scheme)
            logging.info(f"[ProxyManager] 获取到 {len(self._proxy_list)} 个 {self.scheme} 代理")
        except Exception as e:
            logging.error(f"[ProxyManager] 刷新代理失败: {e}")
            self._proxy_list = []
    
    async def get_valid_proxy(self):
        """
        异步获取一个可用代理，进行简单验证，最多尝试 max_retries 次。
        返回格式：'http://ip:port'
        """
        if not self._proxy_list:
            self.refresh_proxies()
        
        for _ in range(self.max_retries):
            if not self._proxy_list:
                logging.warning("[ProxyManager] 代理池为空，重新刷新")
                self.refresh_proxies()
                if not self._proxy_list:
                    return None

            proxy = random.choice(self._proxy_list)
            proxy_url = f"{self.scheme}://{proxy}"
            
            try:
                if await verify_proxy_async(proxy_url, timeout=self.timeout):
                    return proxy_url
                else:
                    logging.debug(f"[ProxyManager] 代理不可用，剔除：{proxy_url}")
                    self._proxy_list.remove(proxy)
            except Exception as e:
                logging.debug(f"[ProxyManager] 验证代理异常，剔除：{proxy_url}，错误：{e}")
                if proxy in self._proxy_list:
                    self._proxy_list.remove(proxy)
        return None
