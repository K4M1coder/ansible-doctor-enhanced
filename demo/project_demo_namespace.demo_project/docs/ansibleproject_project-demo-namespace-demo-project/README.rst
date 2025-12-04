project\_demo\_namespace.demo\_project
======================================

Architecture
------------

.. mermaid::

   graph TD
       A[project_demo_namespace.demo_project] --> B[Roles (1)]
       A --> C[Collections (1)]
       A --> D[Playbooks (0)]
       A --> E[Inventory (0)]

Roles
-----

- role_demo_namespace.demo_demo_role

Collections
-----------

- collection_demo_namespace.demo_collection
.. image:: https://img.shields.io/badge/license-MIT-yellow


Existing Documentation
----------------------

::

       # Demo Project

   This is a demonstration Ansible project for testing ansible-doctor-enhanced's
   project documentation generation capabilities.

   ## Overview

   The demo project showcases:

   - Multi-role project structure
   - Collection integration
   - Inventory management
   - Variable precedence demonstration

   ## Project Structure

   \`\`\`
   demo\_project/
   ├── ansible.cfg          # Project configuration
   ├── collections/         # Embedded collections
   ├── roles/              # Project roles
   ├── group\_vars/         # Group variables
   └── host\_vars/          # Host variables
   \`\`\`

   ## Requirements

   - Ansible >= 2.9
   - Python >= 3.8

   ## Usage

   \`\`\`bash
   ansible-playbook -i inventory site.yml
   \`\`\`

   ## License

   MIT License - see LICENSE file for details.

   ## Author

   Demo Namespace Team


