# Hierarchical Project Test Fixture

This fixture contains a more complex project with multiple collections for testing hierarchical index generation.

## Structure

```
hierarchical_project/
├── collections/
│   └── ansible_collections/
│       ├── namespace1/
│       │   └── collection1/
│       │       ├── galaxy.yml
│       │       └── roles/
│       │           ├── role1/
│       │           ├── role2/
│       │           ├── role3/
│       │           ├── role4/
│       │           └── role5/
│       ├── namespace1/
│       │   └── collection2/
│       │       ├── galaxy.yml
│       │       └── roles/
│       │           ├── role6/
│       │           ├── role7/
│       │           ├── role8/
│       │           ├── role9/
│       │           └── role10/
│       └── namespace2/
│           └── collection3/
│               ├── galaxy.yml
│               └── roles/
│                   ├── role11/
│                   ├── role12/
│                   ├── role13/
│                   ├── role14/
│                   └── role15/
```

## Components

- 3 collections across 2 namespaces
- 15 roles total (5 per collection)
- Multiple dependency relationships
- Mix of tags for filtering tests
