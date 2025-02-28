import json

def json_to_markdown(json_data):
    md = []
    
    # Title
    md.append(f"# {json_data['title']}\n")
    md.append(f"{json_data['description']}\n")
    
    # Features
    md.append("## Features\n")
    for feature in json_data['features']:
        md.append(f"- {feature}")
    md.append("\n")
    
    # Prerequisites
    md.append("## Prerequisites\n")
    for req in json_data['prerequisites']['requirements']:
        md.append(f"- {req}")
    md.append("\n")
    
    # FFmpeg Installation
    md.append("### Installing ffmpeg\n")
    for os_name, command in json_data['prerequisites']['ffmpeg_installation'].items():
        md.append(f"**{os_name}:**\n```\n{command}\n```\n")
    
    # Installation
    md.append("## Installation\n")
    for step in json_data['installation']['steps']:
        md.append(f"1. {step['title']}:\n")
        if 'command' in step:
            md.append(f"```\n{step['command']}\n```\n")
        elif 'commands' in step:
            for cmd_name, cmd in step['commands'].items():
                if isinstance(cmd, dict):
                    for os_name, os_cmd in cmd.items():
                        md.append(f"# {os_name}:\n```\n{os_cmd}\n```\n")
                else:
                    md.append(f"```\n{cmd}\n```\n")
        if 'description' in step:
            md.append(f"{step['description']}\n")
            if 'example' in step:
                md.append(f"```\n{step['example']}\n```\n")
    
    # Usage
    md.append("## Usage\n")
    for section_name, section in json_data['usage'].items():
        md.append(f"### {section['title']}\n")
        md.append(f"{section['description']}\n")
        md.append(f"```\n{section['command']}\n```\n")
    
    # Output Files
    md.append("## Output Files\n")
    for filename, description in json_data['output_files'].items():
        md.append(f"- `{filename}`: {description}\n")
    
    # Configuration
    md.append("## Configuration\n")
    md.append("### Main Variables\n")
    for var_name, description in json_data['configuration']['main_variables'].items():
        md.append(f"- `{var_name}`: {description}\n")
    
    md.append("\n### Interval Processing\n")
    md.append(f"{json_data['configuration']['interval_processing']['description']}\n")
    md.append(f"```python\n{json_data['configuration']['interval_processing']['example']}\n```\n")
    
    # Error Handling
    md.append("## Error Handling\n")
    for feature in json_data['error_handling']['features']:
        md.append(f"- {feature}\n")
    
    return "\n".join(md)

if __name__ == "__main__":
    # Read JSON
    with open('README.json', 'r') as f:
        readme_data = json.load(f)
    
    # Convert to markdown
    markdown_content = json_to_markdown(readme_data)
    
    # Save markdown
    with open('README.md', 'w') as f:
        f.write(markdown_content)
    
    print("README.md has been generated successfully!") 