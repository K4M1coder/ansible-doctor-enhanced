# Simple Project Test Fixture

This fixture contains a minimal project structure for testing basic index generation.

## Structure

```
simple_project/
├── collections/
│   └── ansible_collections/
│       └── test_namespace/
│           └── test_collection/
│               ├── galaxy.yml
│               └── roles/
│                   ├── role1/
│                   │   └── meta/
│                   │       └── main.yml
│                   ├── role2/
│                   │   └── meta/
│                   │       └── main.yml
│                   └── role3/
│                       └── meta/
│                           └── main.yml
```

## Components

- 1 collection (test_namespace.test_collection)
- 3 roles (role1, role2, role3)
- Simple metadata with minimal dependencies
