from proxy_list import ProxyManager as PLProxyManager
import random
import logging
from .utils import verify_proxy_async

class ProxyManager:
    def __init__(self, scheme='http', max_retries=3, timeout=5):
        self.scheme = scheme
        self.max_retries = max_retries
        self.timeout = timeout
        self._manager = PLProxyManager()
        self._proxy_list = []
    
    def refresh_proxies(self):
        try:
            self._proxy_list = self._manager.get_proxy_list(self.scheme)
            logging.info(f"[ProxyManager] 拉取 {len(self._proxy_list)} 个 {self.scheme} 代理")
        except Exception as e:
            logging.error(f"[ProxyManager] 拉取代理失败: {e}")
            self._proxy_list = []
    
    async def get_valid_proxy(self):
        if not self._proxy_list:
            self.refresh_proxies()
        
        for _ in range(self.max_retries):
            if not self._proxy_list:
                logging.warning("[ProxyManager] 代理池空，刷新中...")
                self.refresh_proxies()
                if not self._proxy_list:
                    return None
            
            proxy = random.choice(self._proxy_list)
            proxy_url = f"{self.scheme}://{proxy}"
            
            try:
                if await verify_proxy_async(proxy_url, timeout=self.timeout):
                    return proxy_url
                else:
                    logging.debug(f"[ProxyManager] 代理不可用，移除：{proxy_url}")
                    self._proxy_list.remove(proxy)
            except Exception as e:
                logging.debug(f"[ProxyManager] 验证异常，移除代理：{proxy_url}，错误：{e}")
                if proxy in self._proxy_list:
                    self._proxy_list.remove(proxy)
        return None
