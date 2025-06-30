from .utils import create_session
from .config import NCBI_EUTILS, IDCONV_API, YOUR_EMAIL
import requests

NCBI_EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
def fetch_pmc_to_pmid_and_doi(pmc_id): 
    """通过 esearch 查询 PMC ID 对应的 PMID 和 DOI"""
    pmc_params = {
        "db": "pubmed",  # 查询 PubMed 数据库
        "term": f"{pmc_id}[PMCID]",  # 通过 PMC ID 查询
        "retmode": "json",  # 以 JSON 格式返回结果
        "retmax": 1  # 只返回一个结果
    }

    try:
        # 发送请求
        pmc_resp = requests.get(f"{NCBI_EUTILS}/esearch.fcgi", params=pmc_params, timeout=15)
        pmc_resp.raise_for_status()  # 检查请求是否成功

        # 解析返回的 JSON 数据
        pmc_data = pmc_resp.json()

        # 判断是否找到对应的 PMID
        if int(pmc_data["esearchresult"]["count"]) > 0:
            pmid = pmc_data["esearchresult"]["idlist"][0]  # 获取第一个匹配的 PMID

            # 使用 PMID 查询 DOI
            doi_params = {
                "db": "pubmed",  # 查询 PubMed 数据库
                "id": pmid,  # 查询的 PMID
                "retmode": "xml"  # 以 XML 格式返回结果
            }
            doi_resp = requests.get(f"{NCBI_EUTILS}/esummary.fcgi", params=doi_params, timeout=15)
            doi_resp.raise_for_status()

            # 解析 DOI 数据
            doi_data = doi_resp.text
            doi = None
            if "<Item Name=\"DOI\">" in doi_data:
                doi = doi_data.split("<Item Name=\"DOI\">")[1].split("</Item>")[0]

            return pmid, pmc_id, doi  # 返回 PMID、PMC ID 和 DOI

        else:
            return None, None, None  # 未找到对应的记录

    except Exception as e:
        print(f"查询 PMC ID {pmc_id} 发生错误: {e}")
        return None, None, None

def fetch_identifiers(identifier, id_type):
    """
    通过 pmcid/pmid/doi 查询对应的 pmid/pmcid/doi。
    返回: {'pmid':..., 'pmcid':..., 'doi':..., 'status':...}
    """
    print(f"Fetching identifiers for {id_type}: {identifier}")
    session = create_session()
    params = {
        "tool": "url_converter",
        "email": YOUR_EMAIL,
        "format": "json",
        "versions": "no"
    }

    # 统一处理ID格式
    if id_type == "pmcid":
        pmcid = identifier.upper()
        if not pmcid.startswith("PMC"):
            pmcid = f"PMC{pmcid}"
        print(f"实际用于查询的pmcid: {pmcid}")
        params["ids"] = pmcid
    elif id_type == "pmid":
        params["ids"] = identifier
    elif id_type == "doi":
        params["ids"] = identifier
    else:
        print(f"不支持的id_type: {id_type}")
        return {"status": "unsupported_id_type"}

    try:
        print(f"请求IDCONV_API参数: {params}")
        resp = session.get(IDCONV_API, params=params, timeout=15)
        print(f"IDCONV_API响应状态码: {resp.status_code}")
        if resp.status_code == 404:
            print("IDCONV_API返回404，未找到")
            return {"status": "not_found"}
        resp.raise_for_status()
        data = resp.json()
        print(f"IDCONV_API返回数据: {data}")
        if data.get("records"):
            record = data["records"][0]
            doi = record.get("doi")
            if doi:
                doi = doi.replace("DOI:", "").strip()
            print(f"IDCONV_API查到: pmid={record.get('pmid')}, pmcid={record.get('pmcid')}, doi={doi}")
            return {
                "pmid": record.get("pmid"),
                "pmcid": record.get("pmcid"),
                "doi": doi,
                "status": record.get("status", "ok")
            }
        # 如果没查到，且是pmcid，尝试用esearch+esummary补查
        if id_type == "pmcid":
            print("ID Converter未查到，尝试fetch_pmc_to_pmid_and_doi兜底")
            pmid, pmcid, doi = fetch_pmc_to_pmid_and_doi(identifier)
            print(f"兜底查到: pmid={pmid}, pmcid={pmcid}, doi={doi}")
            if pmid:
                return {"pmid": pmid, "pmcid": pmcid, "doi": doi, "status": "ok"}
        print("未查到任何记录")
        return {"status": "not_found"}
    except Exception as e:
        print(f"ID转换API错误: {e}")
        return {"status": "error"}

def generate_all_urls(doi=None, pmid=None, pmcid=None):
    """根据 DOI/PMID/PMCID 生成标准URL"""
    import re
    urls = []

    if doi:
        # 保留斜杠，不进行 quote，避免 %2F 问题
        doi_clean = re.sub(r'\s+', '', doi).strip().rstrip('/')
        print(f"生成的DOI URL: https://doi.org/{doi_clean}")
        urls.append(f"https://doi.org/{doi_clean}")
        
    if pmid:
        print(f"生成的PMID URL: https://pubmed.ncbi.nlm.nih.gov/{pmid}/")
        urls.append(f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")

    if pmcid:
        print(f"生成的PMC URL: https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/")
        pmcid_clean = pmcid.upper().replace("PMC", "")
        urls.append(f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid_clean}/")

    return urls
