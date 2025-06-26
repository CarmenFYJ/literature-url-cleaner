# literature_parser/__main__.py

import argparse
from .main import main

def cli():
    parser = argparse.ArgumentParser(description="文献 URL 清洗与结构化工具")
    parser.add_argument(
        "--input", "-i", type=str, default="literature_urls.xlsx",
        help="输入 Excel 文件路径（默认: literature_urls.xlsx）"
    )
    parser.add_argument(
        "--output", "-o", type=str, default="processed_urls.xlsx",
        help="输出 Excel 文件路径（默认: processed_urls.xlsx）"
    )
    args = parser.parse_args()
    main(input_path=args.input, output_path=args.output)

if __name__ == "__main__":
    cli()