# LinkedIn Insight

LinkedIn Insight is a Python-based tool for collecting and analyzing company information from LinkedIn. It provides insights into company structures, employees, and job listings.

## Features

- Collect company information, employee data, and job listings from LinkedIn
- Generate CSV files with employee data
- Create hierarchical pyramids of company structures
- Generate HTML visualizations of company hierarchies

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/linkedin_insight.git
   cd linkedin_insight
   ```

2. Install the required packages:
   ```
   pip install -e .
   ```

3. Create a `.env` file in the main directory with your LinkedIn credentials:
   ```
   LINKEDIN_USERNAME=your_username
   LINKEDIN_PASSWORD=your_password
   ```

## Usage

Run the main script with:

```
python -m src.main
```

Optional arguments:
- `--json`: Path to a JSON file to generate CSV and hierarchy pyramid
- `--create-pyramid`: Create a hierarchy pyramid
- `--create-html-pyramid`: Create an HTML hierarchy pyramid
- `--force`: Force a new scan even if a cache exists

### Creating the HTML Hierarchy Pyramid

There are two ways to create the HTML hierarchy pyramid:

1. **During scanning**:
   Add the `--create-html-pyramid` option when running the script:
   ```
   python -m src.main --create-html-pyramid
   ```

2. **From an existing JSON file**:
   If you already have a JSON file with company data, you can create the HTML pyramid using:
   ```
   python -m src.main --json path/to/your/file.json --create-html-pyramid
   ```

The HTML pyramid will be saved in the output directory with the name `company_name_pyramid.html`.

## License

This project is licensed under the terms of the MIT License - see the [LICENSE](LICENSE) file for details.

## Legal Disclaimer

This software is provided "as is," without warranty of any kind, express or implied. Use of this tool for scraping data from LinkedIn or any other platform may violate the terms of service of those platforms and applicable local, national, or international laws. **The author disclaims all responsibility for any legal violations, damages, or consequences resulting from the use of this tool.**

It is the user's responsibility to ensure compliance with all applicable laws and regulations when using this software. By using this tool, you agree to indemnify the author from any legal liability.

---

Please make sure to read the legal disclaimer carefully and use the tool responsibly.
