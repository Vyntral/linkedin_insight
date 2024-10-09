import json
import os
from datetime import datetime, timedelta
from ..utils.logger import setup_logger
from .csv_generator import write_employees_to_csv
from ..visualization.hierarchy_pyramid import create_hierarchy_pyramid
from ..visualization.html_generator import create_html_pyramid

logger = setup_logger()

def process_json(json_path, company_name_input, args):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            company_network = json.load(f)
        
        cached_dir = cache_exists(company_name_input)
        if cached_dir:
            output_dir = cached_dir
        else:
            output_dir = create_company_directory(company_name_input)
        
        employees = company_network.get('employees', [])
        write_employees_to_csv(employees, output_dir)
        
        if args.create_pyramid:
            company_name = company_network.get('company', {}).get('name', 'company')
            create_hierarchy_pyramid(employees, company_name, output_dir)
        
        if args.create_html_pyramid:
            create_html_pyramid(company_network, output_dir)
        
        logger.info(f"JSON processing completed. Output directory: {output_dir}")
        return output_dir
    except Exception as e:
        logger.error(f"Error processing JSON file: {str(e)}")
        return None

def cache_exists(company_name):
    base_path = os.getcwd()
    company_dirs = [d for d in os.listdir(base_path) if os.path.isdir(d) and company_name in d]
    for directory in company_dirs:
        try:
            dir_date_str = directory.split('_')[-1]
            dir_date = datetime.strptime(dir_date_str, '%Y-%m-%d')
            if datetime.now() - dir_date < timedelta(days=3):
                return directory
        except ValueError:
            continue
    return None

def create_company_directory(company_name):
    today = datetime.today().strftime('%Y-%m-%d')
    directory_name = f"{company_name}_{today}"
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    images_dir = os.path.join(directory_name, "images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    return directory_name