import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from tabulate import tabulate
import matplotlib.pyplot as plt
import matplotlib as mpl
import logging

# Configure logging
logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to scrape product prices from the website
def scrape_prices(url: str) -> list[list[str]]:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        soup = BeautifulSoup(response.text, 'lxml')  # Use lxml parser for better HTML parsing
        product_data: list[list[str]] = []
        for product in soup.find_all('div', class_='MuiBox-root css-1p9qlrd'):
            name = product.find('div', class_='MuiBox-root css-r0hfyj').text.strip()
            price = product.find('p', class_='MuiTypography-root MuiTypography-body1 css-ez05by').text.strip()
            price = price.replace(',', '')
            brand = product.find('div', class_='MuiBox-root css-1rtv77d').text.strip()
            product_data.append([name, price, brand])
        return product_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error scraping {url}: {e}")
        return []

def step_1(urls: list[str]) -> None:
    
    # Create 'results' folder if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')
        
    columns = ['Name', 'Price', 'Brand', 'Date']
    consolidated_data = []

    # Scrape prices from each URL and append to consolidated_data list with current date
    for url in urls:
        product_data = scrape_prices(url)
        today = datetime.now().strftime('%Y-%m-%d')
        consolidated_data.extend([data + [today] for data in product_data])

    # Create a DataFrame from the consolidated product data
    df = pd.DataFrame(consolidated_data, columns=columns)

    # Drop duplicates
    df.drop_duplicates(inplace=True)
    # Sort the DataFrame by the 'Name' column
    df_sorted = df.sort_values(by='Name')

    # Reset the index after sorting
    df_sorted = df_sorted.reset_index(drop=True)

    # Append data to existing CSV file or create a new one
    with open('results/product_price.csv', 'a', newline='') as f:
        df_sorted.to_csv(f, header=f.tell() == 0, index=False)

    # Display DataFrame
    # print(tabulate(df_sorted, headers='keys', tablefmt='psql'))

def step_2(df: pd.DataFrame) -> None:
    grouped = df.groupby('Name')['Price'].apply(list).reset_index()
    grouped.columns = ['Name', 'Prices']
    grouped.to_csv('results/grouped_product_prices.csv', index=False)
    
def plot_graph(search_strings, df):
    # Add the font file
    mpl.font_manager.fontManager.addfont('Sarabun-Regular.ttf')
    mpl.rc('font', family='Sarabun')

    # Create 'results' folder if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')

    # Iterate over each search string
    for search_string in search_strings:
        # Filter DataFrame based on substring match in 'Name' column
        df_filtered = df[df['Name'].str.contains(search_string)].copy()  # Use .copy() to avoid SettingWithCopyWarning

        # Convert the 'Prices' column to a list of numbers
        df_filtered['Prices'] = df_filtered['Prices'].apply(lambda x: [float(''.join(y.split(','))) for y in x.strip('[]').split(',')])

        # Create a new figure and axis for each search string
        fig, ax = plt.subplots(figsize=(13, 15))

        # Define a list of colors for lines
        colors = plt.cm.tab20.colors

        # Iterate over each row and plot the prices
        num_colors = len(colors)
        for i, (name, prices) in enumerate(zip(df_filtered['Name'], df_filtered['Prices'])):
            color = colors[i % num_colors]  # Reuse colors if needed
            ax.plot(range(len(prices)), prices, marker='o', label=name, color=color, linestyle='-', linewidth=2, markersize=6)  # Reduce marker size

            # Annotate price points
            for x, y in enumerate(prices):
                ax.annotate(f'{y:.2f}', (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=13)  # Adjust xytext and fontsize


        # Add labels and title
        ax.set_xlabel('Time Points')
        ax.set_ylabel('Price (Bath)')
        ax.set_title(f'Price Variation Over Time - {search_string}', fontsize=16)

        # Add legend on the left side
        ax.legend(fontsize=10, loc='upper left')

        # Set background color
        ax.set_facecolor('whitesmoke')

        # Grid lines
        ax.grid(True, linestyle='--', alpha=0.7)

        # Rotate x-axis labels for better visibility
        plt.xticks(rotation=45)

        # Add a horizontal line at y=0 for reference
        ax.axhline(0, color='black', linewidth=0.5)

        # Adjust subplot parameters to give some spacing
        plt.tight_layout()

        # Save the plot as a PNG file
        plt.savefig(f'results/{search_string}_plot.png', bbox_inches='tight')

        # Show the plot
        # plt.show()

def create_html_for_png_files(directory):
    # List all PNG files in the directory
    png_files = [file for file in os.listdir(directory) if file.endswith('.png')]
    
    # Create the HTML content
    html_content = """<!DOCTYPE html>
<html>
<head>
<title>Plot Gallery</title>
<style>
body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    margin: 0;
    padding: 20px;
}
.container {
    max-width: 800px;
    margin: 0 auto;
}
h2 {
    color: #333;
}
img {
    display: block;
    margin: 10px auto;
    box-shadow: 0px 0px 5px 0px rgba(0,0,0,0.75);
}
</style>
</head>
<body>
<div class="container">\n"""
    
    # Add image tags for each PNG file
    for png_file in png_files:
        html_content += f"<h2>{png_file}</h2>\n"
        html_content += f'<img src="{os.path.join(directory, png_file)}" alt="{png_file}" width="800">\n'
        html_content += "<br>\n"
    
    # Close HTML tags
    html_content += "</div>\n</body>\n</html>"
    
    # Write HTML content to a file
    with open('plot_gallery.html', 'w') as html_file:
        html_file.write(html_content)

if __name__ == '__main__':
    # Define the list of URLs
    urls = [
        # 'Search: เนื้อพิคานย่า'
        "https://www.makro.pro/c/search?q=%E0%B9%80%E0%B8%99%E0%B8%B7%E0%B9%89%E0%B8%AD%E0%B8%9E%E0%B8%B4%E0%B8%84%E0%B8%B2%E0%B8%99%E0%B8%A2%E0%B9%88%E0%B8%B2",
        # 'Search:โปรบุชเชอร์ สันนอก'
        "https://www.makro.pro/c/search?q=%E0%B9%82%E0%B8%9B%E0%B8%A3%E0%B8%9A%E0%B8%B8%E0%B8%8A%E0%B9%80%E0%B8%8A%E0%B8%AD%E0%B8%A3%E0%B9%8C+%E0%B8%AA%E0%B8%B1%E0%B8%99%E0%B8%99%E0%B8%AD%E0%B8%81",
        # 'Search:สันนอกวัว'   
        "https://www.makro.pro/c/search?q=%E0%B8%AA%E0%B8%B1%E0%B8%99%E0%B8%99%E0%B8%AD%E0%B8%81%E0%B8%A7%E0%B8%B1%E0%B8%A7",
        # 'Search:สันแหลม'
        "https://www.makro.pro/c/search?q=%E0%B8%AA%E0%B8%B1%E0%B8%99%E0%B9%81%E0%B8%AB%E0%B8%A5%E0%B8%A1",
        # 'Search:เนื้อสันแหลมริบอาย'
        "https://www.makro.pro/c/search?q=%E0%B9%80%E0%B8%99%E0%B8%B7%E0%B9%89%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%99%E0%B9%81%E0%B8%AB%E0%B8%A5%E0%B8%A1%E0%B8%A3%E0%B8%B4%E0%B8%9A%E0%B8%AD%E0%B8%B2%E0%B8%A2"
        # 'Search:โปรบุชเชอร์ เนื้อ สันคอ'
        "https://www.makro.pro/c/search?q=%E0%B9%82%E0%B8%9B%E0%B8%A3%E0%B8%9A%E0%B8%B8%E0%B8%8A%E0%B9%80%E0%B8%8A%E0%B8%AD%E0%B8%A3%E0%B9%8C+%E0%B9%80%E0%B8%99%E0%B8%B7%E0%B9%89%E0%B8%AD+%E0%B8%AA%E0%B8%B1%E0%B8%99%E0%B8%84%E0%B8%AD"
    ]

    # Scrapping web
    step_1(urls)

    # Read the existing CSV file
    df_existing = pd.read_csv('results/product_price.csv')

    # Groupping product price
    step_2(df_existing)
    
    # Read the existing CSV file
    df = pd.read_csv('results/grouped_product_prices.csv', encoding='utf8')
    
    # Plot Graph
    search_str = ['พิคานย่า', 'สันคอ', 'สันนอก', 'สันแหลม', 'วากิว']
    plot_graph(search_str, df)
    
    # Specify the directory containing the PNG files
    directory = 'results'

    # Create HTML file for the PNG files in the specified directory
    create_html_for_png_files(directory)
    