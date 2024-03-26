## Product Price Scraper

This Python script scrapes product prices from a specific website, performs data processing tasks, and generates visualizations of price variations over time.

### Dependencies

- requests
- BeautifulSoup (bs4)
- pandas
- tabulate
- matplotlib

### Installation

You can install the required dependencies using pip:

```
pip install requests beautifulsoup4 pandas tabulate matplotlib
```

### Usage

1. Ensure you have Python installed on your system.
2. Clone or download the script.
3. Run the script using Python:

```
python scraper.py
```

### Description

The script performs the following steps:

1. **Scraping Prices**: It fetches product prices from a list of URLs provided in the script. Scraped data is stored in a CSV file located in the `results` folder.

2. **Data Processing**:
   - Duplicate entries are removed.
   - Product prices are grouped by product name.
   - Grouped data is stored in a separate CSV file (`grouped_product_prices.csv`) in the `results` folder.

3. **Visualization**:
   - Price variations over time are plotted for specific product categories.
   - Plots are saved as PNG files in the `results` folder.

4. **HTML Gallery**:
   - An HTML file (`plot_gallery.html`) is generated, containing a gallery of PNG plots with clickable links.

### Files

- `scraper.py`: Main Python script containing the scraping, processing, and visualization logic.
- `Sarabun-Regular.ttf`: Font file for custom font usage in plots.
- `results`: Folder containing generated CSV files and PNG plots.

### Note

Ensure that you have a stable internet connection while running the script to fetch data from the specified URLs.
