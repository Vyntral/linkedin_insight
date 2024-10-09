import os
import base64
from jinja2 import Environment, FileSystemLoader
from ..utils.logger import setup_logger
from ..utils.config import GENERIC_USER_IMAGE

logger = setup_logger()

def create_html_pyramid(company_network, output_dir):
    company = company_network['company']
    employees = company_network['employees']

    def get_hierarchy_level(title):
        title = title.lower()
        if any(role in title for role in ['ceo', 'chief executive', 'founder', 'president']):
            return 1
        elif any(role in title for role in ['cto', 'cfo', 'coo', 'vice president']):
            return 2
        elif 'director' in title:
            return 3
        elif any(role in title for role in ['manager', 'head of']):
            return 4
        elif 'senior' in title:
            return 5
        elif 'junior' in title or 'associate' in title:
            return 6
        else:
            return 7

    for employee in employees:
        employee['level'] = get_hierarchy_level(employee.get('title', ''))
    employees.sort(key=lambda x: (x['level'], x.get('name', '')))

    employees_by_level = {}
    for employee in employees:
        level = employee['level']
        if level not in employees_by_level:
            employees_by_level[level] = []
        employees_by_level[level].append(employee)

    env = Environment(loader=FileSystemLoader('.'))
    template = env.from_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ company.name }} - Company Hierarchy Pyramid</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-color: #e0e5ec;
                --text-color: #333;
                --shadow-color: #a3b1c6;
                --highlight-color: #ffffff;
            }
            body {
                font-family: 'Roboto', sans-serif;
                line-height: 1.6;
                color: var(--text-color);
                background-color: var(--bg-color);
                padding: 2em;
                margin: 0;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: var(--bg-color);
                border-radius: 15px;
                padding: 2em;
                box-shadow: 
                    -8px -8px 12px var(--highlight-color),
                    8px 8px 12px var(--shadow-color);
            }
            .company-info {
                text-align: center;
                margin-bottom: 3em;
                padding: 2em;
                border-radius: 10px;
                background: var(--bg-color);
                box-shadow: 
                    inset -8px -8px 12px var(--highlight-color),
                    inset 8px 8px 12px var(--shadow-color);
            }
            .company-logo {
                max-width: 200px;
                border-radius: 50%;
                box-shadow: 
                    -5px -5px 10px var(--highlight-color),
                    5px 5px 10px var(--shadow-color);
            }
            .company-name {
                font-size: 2.5em;
                margin: 0.5em 0;
                color: var(--text-color);
            }
            .company-description {
                font-size: 1.2em;
                max-width: 800px;
                margin: 1em auto;
            }
            .hierarchy-level {
                margin-bottom: 3em;
                padding: 1.5em;
                border-radius: 10px;
                background: var(--bg-color);
                box-shadow: 
                    -8px -8px 12px var(--highlight-color),
                    8px 8px 12px var(--shadow-color);
            }
            .level-title {
                text-align: center;
                font-weight: bold;
                font-size: 1.8em;
                margin-bottom: 1em;
                color: var(--text-color);
                text-transform: uppercase;
            }
            .employee-grid {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 2em;
            }
            .employee-card {
                padding: 1.5em;
                text-align: center;
                width: 220px;
                border-radius: 15px;
                background: var(--bg-color);
                box-shadow: 
                    -8px -8px 12px var(--highlight-color),
                    8px 8px 12px var(--shadow-color);
                transition: box-shadow 0.3s ease;
                cursor: pointer;
            }
            .employee-card:hover {
                box-shadow: 
                    -4px -4px 6px var(--highlight-color),
                    4px 4px 6px var(--shadow-color);
            }
            .employee-photo {
                width: 120px;
                height: 120px;
                border-radius: 50%;
                object-fit: cover;
                margin-bottom: 1em;
                border: 4px solid var(--bg-color);
                box-shadow: 
                    -4px -4px 6px var(--highlight-color),
                    4px 4px 6px var(--shadow-color);
            }
            .employee-name {
                font-size: 1.2em;
                font-weight: bold;
                margin: 0.5em 0;
                color: var(--text-color);
            }
            .employee-title {
                font-size: 0.9em;
                color: var(--text-color);
                opacity: 0.8;
            }
            .tooltip {
                position: relative;
                display: inline-block;
            }
            .tooltip .tooltiptext {
                visibility: hidden;
                width: 200px;
                background-color: var(--bg-color);
                color: var(--text-color);
                text-align: center;
                border-radius: 6px;
                padding: 10px;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                margin-left: -100px;
                opacity: 0;
                transition: opacity 0.3s;
                font-size: 0.9em;
                box-shadow: 
                    -4px -4px 6px var(--highlight-color),
                    4px 4px 6px var(--shadow-color);
            }
            .tooltip:hover .tooltiptext {
                visibility: visible;
                opacity: 1;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="company-info">
                <img src="{{ company.logo_url }}" alt="{{ company.name }} logo" class="company-logo">
                <h1 class="company-name">{{ company.name }}</h1>
                <p class="company-description">{{ company.description }}</p>
            </div>
            <h2 style="text-align: center; color: var(--text-color); margin-bottom: 1.5em;">Company Hierarchy Pyramid</h2>
            {% for level, level_employees in employees_by_level.items() %}
            <div class="hierarchy-level">
                <div class="level-title">Level {{ level }}</div>
                <div class="employee-grid">
                    {% for employee in level_employees %}
                    <div class="employee-card tooltip" onclick="window.open('{{ employee.profile_url }}', '_blank')">
                        {% if employee.photo_url %}
                        <img src="{{ employee.photo_url }}" alt="{{ employee.name }}" class="employee-photo">
                        {% else %}
                        <img src="data:image/svg+xml;base64,{{ generic_user_image }}" alt="{{ employee.name }}" class="employee-photo">
                        {% endif %}
                        <h3 class="employee-name">{{ employee.name }}</h3>
                        <p class="employee-title">{{ employee.title }}</p>
                        <span class="tooltiptext">Click to view LinkedIn profile</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    ''')
    
    generic_user_image_base64 = base64.b64encode(GENERIC_USER_IMAGE.encode('utf-8')).decode('utf-8')
    
    html_content = template.render(
        company=company, 
        employees_by_level=employees_by_level,
        generic_user_image=generic_user_image_base64
    )
    
    output_file = os.path.join(output_dir, f"{company['name']}_pyramid.html")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"HTML company hierarchy pyramid created: {output_file}")
    return output_file