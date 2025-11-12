import argparse
import logging
import os
import yaml
import configparser
from typing import Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('configguard.log'), logging.StreamHandler()]
)

def load_config(filepath: str) -> Dict:
    """Load YAML or INI config file as a dictionary."""
    if not os.path.isfile(filepath):
        logging.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"File not found: {filepath}")
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.yaml' or ext == '.yml':
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    elif ext == '.ini':
        config = configparser.ConfigParser()
        config.read(filepath)
        return {s: dict(config.items(s)) for s in config.sections()}
    else:
        logging.error("Unsupported file type. Use .yaml, .yml, or .ini.")
        raise ValueError("Unsupported file type. Use .yaml, .yml, or .ini.")

def compare_dicts(dict1: Dict, dict2: Dict) -> Dict:
    report = {'missing_keys': {}, 'extra_keys': {}, 'mismatched_values': {}}
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())
    all_keys = keys1 | keys2

    for key in all_keys:
        v1 = dict1.get(key)
        v2 = dict2.get(key)

        if key not in dict2:
            # Key is in dict1 but not in dict2 ==> Missing from dict2 (so, in 'extra_keys')
            report['extra_keys'][key] = v1
        elif key not in dict1:
            # Key is in dict2 but not in dict1 ==> Missing from dict1 (so, in 'missing_keys')
            report['missing_keys'][key] = v2
        elif isinstance(v1, dict) and isinstance(v2, dict):
            subreport = compare_dicts(v1, v2)
            for rtype in report:
                if subreport[rtype]:
                    report[rtype][key] = subreport[rtype]
        elif v1 != v2:
            report['mismatched_values'][key] = {'file1': v1, 'file2': v2}
    return report

def format_report(report: Dict) -> str:
    lines = []
    for section in ['missing_keys', 'extra_keys', 'mismatched_values']:
        lines.append(f"\n{section.replace('_', ' ').capitalize()}:")
        if not report[section]:
            lines.append("  None")
        else:
            for key, val in report[section].items():
                lines.append(f"  {key}: {val}")
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description="Compare .ini or .yaml configuration files for consistency.")
    parser.add_argument("file1", type=str, help="First config file (.ini/.yaml)")
    parser.add_argument("file2", type=str, help="Second config file (.ini/.yaml)")
    parser.add_argument("--output", type=str, default=None, help="Write diff report to this .txt file")
    args = parser.parse_args()
    try:
        config1 = load_config(args.file1)
        config2 = load_config(args.file2)
        report = compare_dicts(config1, config2)
        result = format_report(report)
        print(result)
        if args.output:
            with open(args.output, "w") as f:
                f.write(result)
            logging.info(f"Diff report saved to {args.output}")
    except Exception as e:
        logging.error(f"Error comparing configs: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
