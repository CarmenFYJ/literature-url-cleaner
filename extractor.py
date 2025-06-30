import re
import logging
import time
import random
import cloudscraper
from bs4 import BeautifulSoup
from .utils import create_session
from .config import CROSSREF_API, YOUR_EMAIL
from urllib.parse import quote

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
    ]

def extract_identifier(url, url_type):
    """根据URL类型提取 DOI/PMID/PMCID"""
    try:
        if url_type == "pubmed":
            return re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d+)", url).group(1)
        elif url_type == "pmc":
            return re.search(r"articles/(PMC\d+)", url, re.IGNORECASE).group(1)
        elif url_type == "doi":
            return re.search(r"\b(10\.\d{4,9}/[^\s?&#]+)", url).group(1)
    except:
        return None

def extract_doi_from_url(url):
    patterns = [
        r"doi\.org/(10\.\d{4,9}/[-._;()/:A-Z0-9]+)",
        r"doi/(10\.\d{4,9}/[-._;()/:A-Z0-9]+)"
    ]
    for p in patterns:
        m = re.search(p, url, re.IGNORECASE)
        if m:
            return m.group(1)
    return None

def get_doi_from_webpage(url):
    session = create_session()
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
    }

    try:
        r = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, 'html.parser')

        # Step 1: meta tag candidates
        meta_candidates = [
            {"name": "citation_doi"},
            {"name": "dc.identifier"},
            {"name": "dc.DOI"},
            {"name": "DOI"},
            {"name": "prism.doi"},
            {"scheme": "doi"}
        ]
        for meta_attrs in meta_candidates:
            tag = soup.find('meta', attrs=meta_attrs)
            if tag and tag.get('content'):
                doi = tag['content'].strip()
                return doi[4:] if doi.lower().startswith('doi:') else doi

        # Step 2: script tag from altmetric
        for script in soup.find_all('script', src=re.compile(r'api\.altmetric\.com')):
            m = re.search(r'doi/([^?]+)', script['src'])
            if m:
                return m.group(1)

        # Step 3: a tag with doi.org
        for link in soup.find_all('a', href=re.compile(r'doi\.org')):
            m = re.search(r'(10\.\d{4,9}/[^\s?#]+)', link['href'])
            if m:
                return m.group(1)

        # Step 4: in full text
        m = re.search(r'\b10\.\d{4,}/[^\s"<]+', soup.get_text(), re.IGNORECASE)
        if m:
            return m.group(0)

    except Exception as e:
        logging.warning(f"[get_doi_from_webpage] 网页提取DOI失败: {e}")
        return None

def get_title_from_webpage(url, max_retries=3, delay=3, failed_url_list=None):
    blacklist_keywords = ["access denied", "just a moment", "403", "error", "robot check", "cloudflare"]
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'mobile': False
        }
    )

    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/',
        'DNT': '1',  # 不要跟踪
    }
    
    for attempt in range(max_retries):
        try:
            logging.info(f"[get_title_from_webpage] 第{attempt+1}次尝试访问网页获取标题：{url}")
            r = scraper.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                logging.warning(f"[get_title_from_webpage] 状态码非200: {r.status_code}")
                time.sleep(delay)
                continue
            
            page_text = r.text.lower()
            # 简单判断是否为反爬页面
            if any(bad in page_text for bad in blacklist_keywords):
                logging.warning(f"[get_title_from_webpage] 反爬页面内容检测到黑名单关键词，跳过: {url}")
                if failed_url_list is not None:
                    failed_url_list.append(url)
                return None
            
            soup = BeautifulSoup(r.content, 'html.parser')
            
            for selector in ['meta[property="og:title"]', 'meta[name="citation_title"]', 'h1', 'title']:
                el = soup.select_one(selector)
                if el:
                    title = el.get('content') if el.name == 'meta' else el.get_text()
                    if not title:
                        continue
                    title_clean = re.sub(r'[\n\r\t]+', ' ', title).strip()
                    if any(bad in title_clean.lower() for bad in blacklist_keywords) or len(title_clean) < 5:
                        logging.warning(f"[get_title_from_webpage] ⚠️ 页面标题疑似无效，跳过，标题内容：'{title_clean}'")
                        if failed_url_list is not None:
                            failed_url_list.append(url)
                        return None
                    
                    logging.info(f"[get_title_from_webpage] 成功提取标题：{title_clean}")
                    return title_clean
            
            logging.warning(f"[get_title_from_webpage] 未找到合适的标题标签")
            if failed_url_list is not None:
                failed_url_list.append(url)
            return None
        
        except Exception as e:
            logging.error(f"[get_title_from_webpage] 访问异常: {e}")
            time.sleep(delay)
    
    logging.error(f"[get_title_from_webpage] 多次尝试失败，跳过该URL：{url}")
    if failed_url_list is not None:
        failed_url_list.append(url)
    return None

def get_doi_from_title(title):
    session = create_session()
    try:
        headers = {"User-Agent": f"LiteratureConverter/1.0 (mailto:{YOUR_EMAIL})"}
        params = {"query.title": title, "rows": 1}
        r = session.get(CROSSREF_API, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
        if data["message"]["total-results"] > 0:
            return data["message"]["items"][0].get("DOI")
    except Exception as e:
        print(f"CrossRef标题查询失败: {e}")
        return None

def journal_url_to_identifiers(journal_url):
    doi = extract_doi_from_url(journal_url) or get_doi_from_webpage(journal_url)
    title = get_title_from_webpage(journal_url) if not doi else None
    if title and not doi:
        doi = get_doi_from_title(title)
    from .apis import fetch_identifiers_from_ncbi
    pmid, pmcid = fetch_identifiers_from_ncbi(doi) if doi else (None, None)
    return doi, pmid, pmcid
