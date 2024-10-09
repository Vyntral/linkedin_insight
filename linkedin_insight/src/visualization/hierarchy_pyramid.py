import graphviz
import subprocess
from ..utils.logger import setup_logger

logger = setup_logger()

def create_hierarchy_pyramid(employees, company_name, output_dir):
    try:
        subprocess.run(['dot', '-V'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.critical("Graphviz is not installed or the 'dot' executable is not in PATH. Hierarchy pyramid will not be created.")
        return

    hierarchy_mapping = {
        'CEO': 1, 'Chief Executive Officer': 1, 'Founder': 1, 'President': 1,
        'CTO': 2, 'CFO': 2, 'COO': 2, 'Vice President': 2,
        'Director': 3,
        'Manager': 4, 'Team Lead': 4,
        'Senior': 5,
        'Junior': 6, 'Associate': 6,
        'Intern': 7
    }

    for employee in employees:
        title = employee.get('title', '').lower()
        employee['hierarchy_level'] = 999
        for key in hierarchy_mapping:
            if key.lower() in title:
                employee['hierarchy_level'] = hierarchy_mapping[key]
                break

    employees_sorted = sorted(employees, key=lambda x: x.get('hierarchy_level', 999))

    dot = graphviz.Digraph(comment='Hierarchy Pyramid')

    for idx, employee in enumerate(employees_sorted):
        name = employee.get('name', f"Employee {idx+1}")
        title = employee.get('title', 'Unknown')
        dot.node(str(idx), f"{name}\n{title}")

    previous_level_nodes = {}
    for idx, employee in enumerate(employees_sorted):
        level = employee.get('hierarchy_level', 999)
        if level > 1:
            for sup_level in range(level-1, 0, -1):
                if sup_level in previous_level_nodes:
                    sup_node = previous_level_nodes[sup_level]
                    dot.edge(sup_node, str(idx))
                    break
        previous_level_nodes[level] = str(idx)

    pyramid_filepath = os.path.join(output_dir, f"{company_name}_hierarchy_pyramid")
    try:
        dot.render(pyramid_filepath, format='png', cleanup=True)
        logger.info(f"Hierarchy pyramid created: {pyramid_filepath}.png")
    except Exception as e:
        logger.error(f"Error creating hierarchy pyramid: {str(e)}")