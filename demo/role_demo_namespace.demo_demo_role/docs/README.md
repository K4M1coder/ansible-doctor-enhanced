# role_demo_namespace.demo_demo_role

Demonstration role showcasing all ansible-doctor-enhanced features

**Generated:** 2025-11-30 04:13 | **Version:** 0.14.0

---

## Table of Contents

- [Overview](#overview)
- [Variables](#variables)- [Tags](#tags)- [Examples](#examples)
---

## Overview

**Role Name:** role\_demo\_namespace\.demo\_demo\_role

**Author:** Ansible Doctor Enhanced Demo
**License:** MIT
**Platforms:**
- Ubuntu (focal, jammy)- Debian (bullseye, bookworm)- EL (8, 9)
**Dependencies:**
- `name='geerlingguy.nginx' version='3.1.0' source=None`
- `name='geerlingguy.postgresql' version='3.4.0' source=None`

---

## Variables

26 variable(s) defined:

### `app\_name`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `demo\-app`

### `app\_port`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `8000`

### `app\_debug`


- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `False`

### `app\_workers`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `2`

### `db\_host`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `localhost`

### `db\_port`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `5432`

### `db\_name`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `\{\{ app\_name \}\}\_db`

### `db\_user`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `\{\{ app\_name \}\}\_user`

### `db\_password`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `changeme`

### `web\_ssl\_enabled`


- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `False`

### `web\_ssl\_cert`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** ``

### `web\_ssl\_key`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** ``

### `web\_domain`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `localhost`

### `app\_install\_dir`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/opt/\{\{ app\_name \}\}`

### `app\_config\_dir`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/etc/\{\{ app\_name \}\}`

### `app\_log\_dir`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/var/log/\{\{ app\_name \}\}`

### `old\_app\_path`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/usr/local/\{\{ app\_name \}\}`

### `db\_connection\_pool\_size`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `10`

### `db\_query\_timeout`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `15`

### `app\_cache\_enabled`


- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `True`

### `app\_cache\_ttl`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `300`

### `app\_rate\_limit`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `60`

### `app\_allowed\_origins`


- **Type:** `VariableType.LIST`
- **Required:** No
- **Value:** `\['\*'\]`

### `metrics\_enabled`


- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `False`

### `metrics\_port`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `9100`

### `log\_format`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `text`


---

## Tags

14 tag(s) available:

### `always`


- **Usage Count:** 1
- **Locations:**
  - `tasks/main.yml:1`

### `configuration`


- **Usage Count:** 3
- **Locations:**
  - `tasks/main.yml:4`
  - `tasks/main.yml:5`
  - `tasks/main.yml:9`

### `database`


- **Usage Count:** 2
- **Locations:**
  - `tasks/main.yml:7`
  - `tasks/main.yml:8`

### `deployment`


- **Usage Count:** 4
- **Locations:**
  - `tasks/main.yml:9`
  - `tasks/main.yml:11`
  - `tasks/main.yml:12`
  - `tasks/main.yml:13`

### `directories`


- **Usage Count:** 1
- **Locations:**
  - `tasks/main.yml:3`

### `healthcheck`


- **Usage Count:** 2
- **Locations:**
  - `tasks/main.yml:12`
  - `tasks/main.yml:13`

### `info`


- **Usage Count:** 1
- **Locations:**
  - `tasks/main.yml:1`

### `installation`


- **Usage Count:** 4
- **Locations:**
  - `tasks/main.yml:2`
  - `tasks/main.yml:3`
  - `tasks/main.yml:6`
  - `tasks/main.yml:10`

### `packages`


- **Usage Count:** 1
- **Locations:**
  - `tasks/main.yml:6`

### `services`


- **Usage Count:** 1
- **Locations:**
  - `tasks/main.yml:11`

### `setup`


- **Usage Count:** 2
- **Locations:**
  - `tasks/main.yml:7`
  - `tasks/main.yml:8`

### `systemd`


- **Usage Count:** 1
- **Locations:**
  - `tasks/main.yml:10`

### `users`


- **Usage Count:** 1
- **Locations:**
  - `tasks/main.yml:2`

### `webserver`


- **Usage Count:** 2
- **Locations:**
  - `tasks/main.yml:4`
  - `tasks/main.yml:5`


---


---

## Examples

2 example(s):

### Running installation tasks only


```yaml
ansible-playbook site.yml --tags "installation"
```

### Checking application status


```yaml
ansible-playbook site.yml --tags "healthcheck"
```


---

*Documentation generated by ansible-doctor-enhanced v0.4.0*