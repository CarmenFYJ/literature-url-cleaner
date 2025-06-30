import random
import logging
import asyncio
from proxy_list import ProxyManager as PLProxyManager
from .utils import verify_proxy_async

class ProxyPoolManager:
    def __init__(self, scheme='http', max_retries=3, timeout=5):
        """
        scheme: 'http', 'https', 'socks4', 'socks5'
        max_retries: 尝试获取可用代理最大次数
        timeout: 验证代理连接超时时间
        """
        self.scheme = scheme
        self.max_retries = max_retries
        self.timeout = timeout
        self._proxy_manager = PLProxyManager()
        self._proxy_list = []
    
    def refresh_proxy_list(self):
        try:
            self._proxy_list = self._proxy_manager.get_proxy_list(self.scheme)
            logging.info(f"[ProxyPoolManager] 获取 {len(self._proxy_list)} 个 {self.scheme} 代理")
        except Exception as e:
            logging.error(f"[ProxyPoolManager] 刷新代理列表失败: {e}")
            self._proxy_list = []
    
    async def get_valid_proxy_async(self):
        """
        异步获取一个有效代理，最多尝试 max_retries 次
        返回格式：scheme://ip:port 或 None
        """
        if not self._proxy_list:
            self.refresh_proxy_list()

        for _ in range(self.max_retries):
            if not self._proxy_list:
                logging.warning("[ProxyPoolManager] 代理池空，刷新中...")
                self.refresh_proxy_list()
                if not self._proxy_list:
                    return None
            
            proxy = random.choice(self._proxy_list)
            proxy_url = f"{self.scheme}://{proxy}"
            try:
                if await verify_proxy_async(proxy_url, timeout=self.timeout):
                    return proxy_url
                else:
                    logging.debug(f"[ProxyPoolManager] 代理不可用，移除: {proxy_url}")
                    self._proxy_list.remove(proxy)
            except Exception as e:
                logging.debug(f"[ProxyPoolManager] 验证代理异常，移除: {proxy_url}, 错误: {e}")
                if proxy in self._proxy_list:
                    self._proxy_list.remove(proxy)
        return None
    
    def get_random_proxy(self):
        """
        同步接口，直接返回随机代理字符串，不做检测（兼容旧代码）
        如果代理池为空，先刷新代理池
        """
        if not self._proxy_list:
            self.refresh_proxy_list()
        if not self._proxy_list:
            return None
        proxy = random.choice(self._proxy_list)
        return f"{self.scheme}://{proxy}"
