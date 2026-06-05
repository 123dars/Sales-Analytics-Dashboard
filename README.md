# 📊 Sales & Customer Analytics Dashboard

End-to-end data analysis project on Superstore Sales dataset using Python, Pandas, Matplotlib, Seaborn and Power BI.

> 📈 Analysed **9,994 records** | Identified **5 key business insights** | Built **5 KPI Power BI dashboard**

---

## 🛠 Tech Stack
Python · Pandas · NumPy · Matplotlib · Seaborn · Power BI · SQL · Jupyter Notebook

---

## 📁 Project Structure
```
DA_Project/
├── analysis.ipynb        # Main Jupyter notebook with full EDA
├── superstore.csv        # Dataset
├── charts/               # Auto-generated chart images
│   ├── 01_sales_by_region.png
│   ├── 02_monthly_trend.png
│   ├── 03_category_analysis.png
│   ├── 04_segment_analysis.png
│   └── 05_top_products.png
├── dashboard/            # Power BI screenshots
└── README.md
```

---

## 📊 Key Insights
1. **West region** is the top revenue contributor (31% of total sales)
2. **Technology** is the highest selling category
3. **Tables and Bookcases** are loss-making sub-categories — recommend review
4. **Consumer segment** generates highest profit
5. **November** is the peak sales month — plan inventory accordingly
---
---

## 🗄️ SQL Analysis

Loaded dataset into SQLite database and performed analytical queries:

```sql
SELECT Region, ROUND(SUM(Sales),2) as Total_Sales 
FROM sales GROUP BY Region ORDER BY Total_Sales DESC;
```

**Sales by Region:**
| Region | Total Sales |
|--------|------------|
| West | $725,457.82 |
| East | $678,781.24 |
| Central | $501,239.89 |
| South | $391,721.91 |

**Profit by Category:**
| Category | Total Profit |
|----------|-------------|
| Technology | $145,454.95 |
| Office Supplies | $122,490.80 |
| Furniture | $18,451.27 |

**Orders by Segment:**
| Segment | Total Orders | Total Sales |
|---------|-------------|------------|
| Consumer | 2,586 | $1,161,401.34 |
| Corporate | 1,514 | $706,146.37 |
| Home Office | 909 | $429,653.15 |

**Top 5 Products by Sales:**
| Product | Total Sales |
|---------|------------|
| Canon imageCLASS 2200 Advanced Copier | $61,599.82 |
| Fellowes PB500 Electric Punch | $27,453.38 |
| Cisco TelePresence System EX90 | $22,638.48 |
| HON 5400 Series Task Chairs | $21,870.58 |
| GBC DocuBind TL300 Electric Binding | $19,823.48 |
---

## 👨‍💻 Author
**Darshan B** | github.com/123dars
