import os
import argparse
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

GENERIC_USER_IMAGE = '''
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="50" fill="#e0e0e0"/>
  <circle cx="50" cy="40" r="20" fill="#bdbdbd"/>
  <path d="M50 65 Q50 85 80 85 A40 40 0 0 1 20 85 Q50 85 50 65" fill="#bdbdbd"/>
</svg>
'''

class DelayConfig:
    def __init__(self, enabled=True, login=(1, 2), navigation=(2, 4), profile=(1, 3)):
        self.enabled = enabled
        self.login = login
        self.navigation = navigation
        self.profile = profile

def get_delay_config():
    parser = argparse.ArgumentParser(description="LinkedIn Scraper Configuration")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--delay", action='store_true', help="Enable delays (default: enabled)")
    group.add_argument("--no-delay", action='store_true', help="Disable delays")
    
    parser.add_argument("--login-delay", type=float, nargs=2, metavar=('MIN', 'MAX'), default=[1, 2], help="Login delay (default: 1 2)")
    parser.add_argument("--navigation-delay", type=float, nargs=2, metavar=('MIN', 'MAX'), default=[2, 4], help="Navigation delay (default: 2 4)")
    parser.add_argument("--profile-delay", type=float, nargs=2, metavar=('MIN', 'MAX'), default=[1, 3], help="Profile delay (default: 1 3)")
    
    parser.add_argument("--json", type=str, help="Path to JSON file to generate CSV and hierarchy pyramid")
    parser.add_argument("--create-pyramid", action='store_true', help="Create hierarchy pyramid (default: disabled)")
    parser.add_argument("--create-html-pyramid", action='store_true', help="Create HTML hierarchy pyramid (default: disabled)")
    parser.add_argument("--force", action='store_true', help="Force a new scan even if cache exists")
    
    args = parser.parse_args()
    
    enabled = not args.no_delay
    
    return args, DelayConfig(
        enabled=enabled,
        login=tuple(args.login_delay),
        navigation=tuple(args.navigation_delay),
        profile=tuple(args.profile_delay)
    )

def parse_arguments():
    parser = argparse.ArgumentParser(description="LinkedIn Scraper")
    parser.add_argument("--json", type=str, help="Path to JSON file to generate CSV and hierarchy pyramid")
    parser.add_argument("--create-pyramid", action='store_true', help="Create hierarchy pyramid")
    parser.add_argument("--create-html-pyramid", action='store_true', help="Create HTML hierarchy pyramid")
    parser.add_argument("--force", action='store_true', help="Force a new scan even if cache exists")
    return parser.parse_args()