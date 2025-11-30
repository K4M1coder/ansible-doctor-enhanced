#!/usr/bin/python
# Test module plugin
from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(argument_spec={})
    module.exit_json(changed=False)


if __name__ == "__main__":
    main()
