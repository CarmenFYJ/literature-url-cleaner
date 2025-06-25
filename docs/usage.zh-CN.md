# 📘 使用说明（中文）

[🇺🇸 English Usage Guide](./usage.md)

## 📌 项目简介

本工具用于批量处理文献链接，支持从 Excel 文件中提取 PubMed / PMC / DOI / 期刊链接，自动识别并补全缺失的标识符（如 PMID / PMCID / DOI），并输出标准化的新链接。

---

## 🧾 输入格式要求

* 输入文件必须是 `.xlsx` 格式（Excel）。
* 至少包含一个名为 `url` 的列。
* 每个单元格可以包含多个 URL，用换行符（`\n`）分隔。

**示例输入：**

| url                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------- |
| [https://pubmed.ncbi.nlm.nih.gov/12345678](https://pubmed.ncbi.nlm.nih.gov/12345678)                                            |
| [www.nature.com/articles/s41586-020-2012-7](http://www.nature.com/articles/s41586-020-2012-7)<br>doi.org/10.1001/jama.2020.1585 |

---

## 🧪 支持的链接类型

| 类型     | 描述                                                 |
| ------ | -------------------------------------------------- |
| PubMed | `https://pubmed.ncbi.nlm.nih.gov/PMID/`            |
| PMC    | `https://www.ncbi.nlm.nih.gov/pmc/articles/PMCID/` |
| DOI    | `https://doi.org/10.xxxx/xxx`                      |
| 期刊页面   | Nature、JAMA、Science 等期刊文章 URL                      |

---
#### 😄 URL 协议补全说明
本项目支持自动识别不带协议头的 URL（例如以 www. 或 doi.org/10.1234/... 开头），在处理过程中将自动补全为带协议的标准形式（默认为 https://）。无需手动修正原始链接，程序将自动处理这些情况。


## ⚙️ 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行脚本

```bash
python -m literature_parser
```

运行后程序将引导你输入：

* Excel 文件路径（如 `literature_urls.xlsx`）
* 输出文件路径（如 `processed_urls.xlsx`）

---

## 📥 输出说明

输出为一个新的 Excel 文件，包含以下列：

| 列名            | 内容说明                              |
| ------------- | --------------------------------- |
| Original URLs| 原始 Excel 输入的 URL                  |
| Valid URLs| 成功识别为 PubMed/PMC/DOI/期刊格式 的 URL     |
| Generated URLs | 基于标识符生成的新链接，如 PubMed/PMC/DOI 标准链接 |
| Unique New URLs| 新生成且在原始版本中没有的 URL                    |
| Invalid URLs | 无法识别或无效的 URL                      |

---

## 🧰 高级功能

* 自动补全缺失的 DOI/PMID/PMCID（通过 CrossRef 和 NCBI API）
* 支持从网页中提取标题并反查 DOI
* 自动生成规范链接格式
* 网络请求自动重试（避免因网络波动导致失败）

---

## 👩🏻‍💻 作者信息

* 作者：傅韵洁（Yunjie Fu）
* 联系方式：[fyj20000313@126.com](mailto:fyj20000313@126.com)
* GitHub 项目主页：[Literature URL Cleaner](https://github.com/your-username/literature-url-cleaner)

---

## 📜 许可协议

本项目基于 [MIT License](../LICENSE) 协议开源，欢迎自由使用与修改。

---
