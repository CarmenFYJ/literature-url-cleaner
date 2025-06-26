# 🧪 文献链接清洗工具（Literature URL Cleaner）

[![English](https://img.shields.io/badge/docs-English-blue.svg)](./README.md)
[![中文文档](https://img.shields.io/badge/文档-简体中文-red.svg)](./README.zh-CN.md)

一个面向科研人员的数据预处理工具，支持从 Excel 表格中批量提取 PubMed / PMC / DOI / 期刊链接，并通过 CrossRef 与 NCBI API 补全缺失信息，统一输出规范的文献链接格式。

---

## 🚀 项目亮点

- 📥 支持 Excel 导入与导出
- 🔍 自动识别 PubMed、PMC、DOI、各大期刊文章链接
- 🔗 提取并补全 DOI / PMID / PMCID
- 🌐 接入 CrossRef 与 NCBI API 自动检索文献信息
- 📄 输出标准化链接，便于后续 LLM 训练或文献标注使用

---

## 📦 安装方法

```bash
git clone https://github.com/CarmenFYJ/literature-url-cleaner.git
cd literature-url-cleaner
pip install -r requirements.txt
