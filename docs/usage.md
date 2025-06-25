# 📘 Usage Guide

## 🧾 Input Format

- Input should be a `.xlsx` Excel file
- Must contain a column named `url`
- Multiple URLs in a single cell should be newline (`\n`) separated

**Example:**

```

[https://pubmed.ncbi.nlm.nih.gov/12345678](https://pubmed.ncbi.nlm.nih.gov/12345678)
[https://doi.org/10.1001/jama.2020.1585](https://doi.org/10.1001/jama.2020.1585)
[www.nature.com/articles/s41586-020-2012-7](http://www.nature.com/articles/s41586-020-2012-7)

````

---

## 🧪 Supported URL Types

| Type      | Description                               |
|-----------|-------------------------------------------|
| PubMed    | e.g., `https://pubmed.ncbi.nlm.nih.gov/12345678` |
| PMC       | e.g., `https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/` |
| DOI       | e.g., `https://doi.org/10.1001/jama.2020.1585` |
| Journal   | Article URLs from Nature, Science, JAMA, etc. |

---

## 🛠️ Running the Script

```bash
python -m literature_parser
````

You will be prompted to:

* Enter input Excel path (default: `literature_urls.xlsx`)
* Enter output Excel path (default: `processed_urls.xlsx`)

---

## 📤 Output Explanation

| Column                  | Description                                       |
| ----------------------- | ------------------------------------------------- |
| Original URLs (List 1)  | Raw URLs from input Excel                         |
| Valid URLs (List 2)     | Recognized URLs (PubMed, PMC, DOI, Journal)       |
| Generated URLs (List 3) | New URLs generated from identifiers               |
| Unique URLs (List 4)    | Newly generated URLs not present in original list |
| Invalid URLs (List 5)   | Unrecognized or malformed URLs                    |

---

## 🔧 Configurations

Edit the following in `config.py` or main file:

```python
YOUR_EMAIL = "your_email@example.com"
```

This is used in API headers to access NCBI/CrossRef services.

---

## 💡 Tips

* You can edit the `classify_url()` and `extract_doi_from_url()` logic to adapt to more journals.
* All requests have retry logic and timeout fallback.
* Time delay is added to avoid API rate limiting.

---

## 👩🏻‍💻 Contact

👩🏻‍🔬 Author: Yunjie Fu

📧 Email: [fyj20000313@126.com](mailto:fyj20000313@126.com)

💻 GitHub: [literature-url-cleaner](https://github.com/your-username/literature-url-cleaner)
💻 GitHub: [literature-url-cleaner](https://github.com/your-username/literature-url-cleaner)

