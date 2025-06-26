import time
from .utils import create_session
from .config import NCBI_EUTILS, IDCONV_API, YOUR_EMAIL

def fetch_identifiers_from_ncbi(doi):
    """通过 DOI 查询 PMID / PMCID（使用 NCBI E-utilities）"""
    session = create_session()
    pmid, pmcid = None, None
    try:
        # Step 1: DOI → PMID
        pubmed_params = {
            "db": "pubmed",
            "term": f"{doi}[DOI]",
            "retmode": "json",
            "retmax": 1
        }
        pubmed_resp = session.get(f"{NCBI_EUTILS}/esearch.fcgi", params=pubmed_params, timeout=15)
        pubmed_data = pubmed_resp.json()

        if int(pubmed_data["esearchresult"]["count"]) > 0:
            pmid = pubmed_data["esearchresult"]["idlist"][0]

            # Step 2: PMID → PMCID
            pmc_params = {
                "dbfrom": "pubmed",
                "db": "pmc",
                "id": pmid,
                "retmode": "json"
            }
            pmc_resp = session.get(f"{NCBI_EUTILS}/elink.fcgi", params=pmc_params, timeout=15)
            pmc_data = pmc_resp.json()

            linksets = pmc_data.get("linksets", [])
            if linksets:
                links = linksets[0].get("linksetdbs", [])
                if links and links[0].get("dbto") == "pmc":
                    pmc_ids = links[0].get("links", [])
                    if pmc_ids:
                        pmcid = f"PMC{pmc_ids[0]}"
    except Exception as e:
        print(f"NCBI API 错误: {e}")
    return pmid, pmcid

def fetch_identifiers(identifier, id_type):
    """使用 NCBI ID Converter 工具获取 DOI / PMID / PMCID"""
    session = create_session()
    params = {
        "tool": "url_converter",
        "email": YOUR_EMAIL,
        "format": "json",
        "versions": "no"
    }

    if id_type == "pmid":
        params["ids"] = identifier
    elif id_type == "pmcid":
        params["ids"] = identifier if identifier.startswith("PMC") else f"PMC{identifier}"
    elif id_type == "doi":
        params["ids"] = identifier

    try:
        resp = session.get(IDCONV_API, params=params, timeout=15)
        if resp.status_code == 404:
            return {"status": "not_found"}
        resp.raise_for_status()
        data = resp.json()

        if data.get("records"):
            record = data["records"][0]
            return {
                "pmid": record.get("pmid"),
                "pmcid": record.get("pmcid"),
                "doi": record.get("doi", "").replace("DOI:", "") if record.get("doi") else None,
                "status": record.get("status", "ok")
            }
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
        urls.append(f"https://doi.org/{doi_clean}")

    if pmid:
        urls.append(f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")

    if pmcid:
        pmcid_clean = pmcid.upper().replace("PMC", "")
        urls.append(f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid_clean}/")

    return urls
