import csv
import os
import requests
import shutil
from ..utils.logger import setup_logger
from ..utils.config import GENERIC_USER_IMAGE

logger = setup_logger()

def write_employees_to_csv(employees, output_dir):
    csv_filepath = os.path.join(output_dir, 'employees.csv')
    images_dir = os.path.join(output_dir, "images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    with open(csv_filepath, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Photo Path', 'First Name', 'Last Name', 'Job Title']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for employee in employees:
            name = employee.get('name', '')
            nome, cognome = (name.split(' ', 1) if ' ' in name else (name, '')) if name else ('', '')
            photo_url = employee.get('photo_url', '')
            photo_path = ''
            if photo_url:
                try:
                    response = requests.get(photo_url, stream=True, timeout=10)
                    if response.status_code == 200 and not photo_url.startswith('data:image/gif;base64,'):
                        sanitized_name = ''.join(c if c.isalnum() else '_' for c in name)
                        photo_filename = f"{sanitized_name}.jpg"
                        photo_filepath = os.path.join(images_dir, photo_filename)
                        with open(photo_filepath, 'wb') as f:
                            shutil.copyfileobj(response.raw, f)
                        photo_path = os.path.relpath(photo_filepath, output_dir)
                        logger.info(f"Image downloaded for {name}: {photo_filepath}")
                    else:
                        photo_path = use_generic_image(images_dir, name)
                        logger.warning(f"Using generic image for {name}")
                except Exception as e:
                    photo_path = use_generic_image(images_dir, name)
                    logger.warning(f"Error downloading image for {name}: {str(e)}. Using generic image.")
            else:
                photo_path = use_generic_image(images_dir, name)
                logger.warning(f"No image URL for {name}. Using generic image.")
            
            writer.writerow({
                'Photo Path': photo_path,
                'First Name': nome,
                'Last Name': cognome,
                'Job Title': employee.get('title', '')
            })
    logger.info(f"CSV file created: {csv_filepath}")

def use_generic_image(images_dir, name):
    sanitized_name = ''.join(c if c.isalnum() else '_' for c in name)
    generic_filename = f"generic_{sanitized_name}.svg"
    generic_filepath = os.path.join(images_dir, generic_filename)
    with open(generic_filepath, 'w', encoding='utf-8') as f:
        f.write(GENERIC_USER_IMAGE)
    return os.path.relpath(generic_filepath, os.path.dirname(images_dir))