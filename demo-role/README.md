# Demo Role

A comprehensive demonstration role showcasing all ansible-doctor-enhanced features.

## Overview

This role demonstrates:
- Galaxy metadata with argument specs
- Comprehensive variable annotations with types and examples
- Tasks with TODO annotations and tags
- Handlers for service management
- Config file discovery and validation
- Multiple documentation formats (Markdown, HTML, RST)
- Watch mode for auto-regeneration

## Requirements

- Ansible >= 2.9
- Python >= 3.8
- ansible-doctor-enhanced >= 0.4.0

## Role Variables

See the generated documentation below (run `ansible-doctor-enhanced generate .` to regenerate).

## Dependencies

- geerlingguy.nginx
- geerlingguy.postgresql

## Example Playbook

```yaml
- hosts: webservers
  roles:
    - role: demo-role
      vars:
        app_name: myapp
        app_port: 8080
        db_host: localhost
        db_password: "{{ vault_db_password }}"
```

## Documentation Generation

Generate documentation in different formats:

```bash
# Markdown (default, uses .ansibledoctor.yml config)
ansible-doctor-enhanced generate .

# HTML output
ansible-doctor-enhanced generate . --format html --output docs/index.html

# RST output
ansible-doctor-enhanced generate . --format rst --output docs/index.rst

# Custom template
ansible-doctor-enhanced generate . --template custom-template.j2
```

## Watch Mode

Auto-regenerate documentation on file changes:

```bash
ansible-doctor-enhanced watch . --output README.md
```

## Configuration

This role includes a `.ansibledoctor.yml` config file demonstrating:
- Output format and file configuration
- Content filtering options
- Watch mode settings
- Parent directory config discovery

## Testing

Validate the configuration:

```bash
ansible-doctor-enhanced config validate
ansible-doctor-enhanced config show
```

## License

MIT

## Author

Ansible Doctor Enhanced Demo
