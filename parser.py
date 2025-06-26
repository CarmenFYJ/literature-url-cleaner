import pandas as pd
import re
from urllib.parse import urlparse
from .utils import ensure_protocol
from .extractor import extract_identifier, journal_url_to_identifiers
from .apis import fetch_identifiers, generate_all_urls

def load_urls_from_excel(file_path, column_name="url"):
    """从Excel加载URL数据，确保每个URL有协议前缀"""
    try:
        df = pd.read_excel(file_path)

        df[column_name] = df[column_name].apply(
            lambda x: [ensure_protocol(url) for url in x.split('\n') if url.strip()] 
            if isinstance(x, str) and x.strip() != "" else []
        )
        return df
    except Exception as e:
        print(f"读取Excel文件出错: {e}")
        return pd.DataFrame()

def classify_url(url):
    """将URL分类为 pmc / pubmed / doi / journal"""
    if not isinstance(url, str) or not url.strip():
        return None
    url = url.lower()

    # 改进的PMC URL识别
    pmc_patterns = [
        r"https?://(?:www|pmc)\.ncbi\.nlm\.nih\.gov/pmc/articles/pmc\d+",  # 标准格式
        r"https?://pmc\.ncbi\.nlm\.nih\.gov/articles/pmc\d+",  # 真实网址格式
        r"https?://pmc\.ncbi\.nlm\.nih\.gov/articles/pmc\d+/",  # 带斜杠的真实网址格式
        r"https?://articles/pmc\d+",  # 仅路径格式
        r"https?://articles/pmc\d+/"  # 带斜杠的路径格式
    ]
    
    for pattern in pmc_patterns:
        if re.search(pattern, url):
            return "pmc"

    # PubMed
    if re.match(r"https?://pubmed\.ncbi\.nlm\.nih\.gov/\d+", url):
        return "pubmed"

    # DOI
    if re.search(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b", url):
        return "doi"

    # Journal
    journal_keywords = ["/article/", "/abstract/", "/fulltext/", "/content/"]
    journal_domains = [
        "nature.com", "science.org", "thelancet.com", "jamanetwork.com",
        "nejm.org", "ahajournals.org", "bmj.com", "springer.com",
        "wiley.com", "tandfonline.com", "mdpi.com", "elsevier.com"
    ]
    parsed = urlparse(url)
    if any(k in parsed.path for k in journal_keywords) or any(d in parsed.netloc for d in journal_domains):
        return "journal"
    return None

def filter_urls(url_list):
    """过滤URL，分为有效和无效两类"""
    list2 = [u for u in url_list if classify_url(u) in ["pubmed", "pmc", "doi", "journal"]]
    list5 = [u for u in url_list if u not in list2]
    return list2, list5

def process_cell(urls):
    """处理单个单元格中的URL集合"""
    list1 = urls
    list2, list5 = filter_urls(list1)
    identifiers = {"pmid": None, "pmcid": None, "doi": None}

    for url in list2:
        url_type = classify_url(url)
        if url_type in ["pubmed", "pmc", "doi"]:
            id_val = extract_identifier(url, url_type)
            if id_val:
                identifiers[url_type] = id_val
        elif url_type == "journal":
            doi, pmid, pmcid = journal_url_to_identifiers(url)
            identifiers["doi"] = identifiers["doi"] or doi
            identifiers["pmid"] = identifiers["pmid"] or pmid
            identifiers["pmcid"] = identifiers["pmcid"] or pmcid

    # 尝试补全缺失标识符
    for id_type in ["pmid", "pmcid", "doi"]:
        if identifiers[id_type]:
            result = fetch_identifiers(identifiers[id_type], id_type)
            if result.get("status") == "ok":
                for k in ["pmid", "pmcid", "doi"]:
                    identifiers[k] = identifiers[k] or result.get(k)

    list3 = generate_all_urls(
        identifiers["doi"], identifiers["pmid"], identifiers["pmcid"]
    ) if any(identifiers.values()) else []

    list4 = [url for url in list3 if url not in list2]

    return {
        "list1": list1,
        "list2": list2,
        "list3": list3,
        "list4": list4,
        "list5": list5
    }