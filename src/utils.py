import pandas as pd
from io import StringIO
import csv

def process_data(file):
    """Process uploaded file and return DataFrame"""
    if file.name.endswith('csv'):
        return pd.read_csv(file)
    return pd.read_excel(file)

def save_results(results):
    """Save search results to CSV"""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Title', 'Link', 'Snippet'])
    writer.writerows(results)
    return output.getvalue()
