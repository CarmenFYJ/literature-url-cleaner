# literature_parser/main.py

from .parser import load_urls_from_excel, process_cell
#from .extractor import get_title_from_webpage
import pandas as pd



def main(input_path="literature_urls.xlsx", output_path="processed_urls.xlsx"):
    df = load_urls_from_excel(input_path)
    if df.empty:
        print("Excel数据为空或读取失败")
        return
    #title = get_title_from_webpage(url,fialed_url_list=failed_urls_list)
    results = []
    for _, row in df.iterrows():
        result = process_cell(row["url"])
        results.append({
            "原始URL": "\n".join(result["list1"]),
            "有效URL": "\n".join(result["list2"]),
            "生成的新URL": "\n".join(result["list3"]),
            "去重后新URL": "\n".join(result["list4"]),
            "疑似非文献URL": "\n".join(result["list5"])
            #"疑似因反爬机制导致无法提取信息": "\n".join(result["failed_url"])
        })

    pd.DataFrame(results).to_excel(output_path, index=False)
    print(f"处理完成，保存到 {output_path}")