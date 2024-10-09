import os
import json
from urllib.parse import urlparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .scraper.linkedin_scraper import linkedin_scraper
from .data_processing.csv_generator import write_employees_to_csv
from .data_processing.json_processor import process_json
from .visualization.hierarchy_pyramid import create_hierarchy_pyramid
from .visualization.html_generator import create_html_pyramid
from .utils.config import get_delay_config, parse_arguments
from .utils.logger import setup_logger

logger = setup_logger()

def main(args):
    if args.json:
        json_path = args.json
        if not os.path.isfile(json_path):
            print(f"Specified JSON file does not exist: {json_path}")
            logger.error(f"Specified JSON file does not exist: {json_path}")
            return
        company_name_input = os.path.splitext(os.path.basename(json_path))[0].replace('_linkedin_data', '')
        output_dir = process_json(json_path, company_name_input, args)
        return

    company_input = input("Enter the LinkedIn company URL or name: ").strip()
    company_url, company_name = parse_company_input(company_input)
    
    if not company_name:
        print("Invalid LinkedIn company URL. Please enter a valid URL or company name.")
        return

    output_dir = create_or_use_cache(company_name, args.force)
    
    try:
        logger.info(f"Starting scraping process for company: {company_name}")
        print("Note: After login, the script will pause to allow you to solve any CAPTCHAs.")
        print("Press Enter when you are ready to continue after solving the CAPTCHAs.")
        company_network = linkedin_scraper(company_url, output_dir)
        
        if company_network:
            save_and_process_data(company_network, company_name, output_dir, args)
        else:
            logger.error("Scraping failed.")
    except Exception as e:
        logger.critical(f"Critical error during script execution: {str(e)}")

def parse_company_input(company_input):
    if company_input.startswith("http://") or company_input.startswith("https://"):
        company_url = company_input
        company_name = extract_company_name_from_url(company_url)
    else:
        company_name = company_input
        company_url = f"https://www.linkedin.com/company/{company_name}/"
    return company_url, company_name

def extract_company_name_from_url(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split('/')
    if 'company' in path_parts:
        company_index = path_parts.index('company')
        if company_index + 1 < len(path_parts):
            return path_parts[company_index + 1].replace('%20', '-')
    return None

def create_or_use_cache(company_name, force):
    cached_dir = cache_exists(company_name)
    if cached_dir and not force:
        print(f"Using cached data from {cached_dir}")
        return cached_dir
    else:
        directory = create_company_directory(company_name)
        print(f"Starting a new scan and saving data in {directory}")
        return directory

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

def save_and_process_data(company_network, company_name, output_dir, args):
    # Save JSON data
    output_file = os.path.join(output_dir, f"{company_name}_linkedin_data.json")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(company_network, f, ensure_ascii=False, indent=4)
        print(f"Data saved in {output_file}")
        logger.info(f"Scraping completed successfully. Data saved in {output_file}")
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
    
    # Create CSV file
    employees = company_network.get('employees', [])
    write_employees_to_csv(employees, output_dir)
    
    # Create hierarchy pyramid if requested
    if args.create_pyramid:
        create_hierarchy_pyramid(employees, company_name, output_dir)
    
    # Create HTML hierarchy pyramid if requested
    if args.create_html_pyramid:
        create_html_pyramid(company_network, output_dir)
    
    # Delete downloaded HTML files
    delete_html_files(output_dir)

def delete_html_files(output_dir):
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    logger.info(f"HTML file deleted: {file_path}")
                except Exception as e:
                    logger.warning(f"Unable to delete HTML file {file_path}: {str(e)}")

if __name__ == "__main__":
    load_dotenv()
    args, delay_config = get_delay_config()
    main(args)