import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    session.trust_env=False #关闭requests，自动读取系统代理环境变量
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def ensure_protocol(url_str):
    if not isinstance(url_str, str) or not url_str.strip():
        return ""
    url_str = url_str.strip()
    if url_str.startswith(('http://', 'https://')):
        return url_str
    if url_str.startswith('//'):
        return 'https:' + url_str
    return 'https://' + url_str