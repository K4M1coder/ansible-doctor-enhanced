# role_demo_namespace.demo_demo_role

Demonstration role showcasing all ansible-doctor-enhanced features

**Generated:** 2025-12-03 00:59 | **Version:** 0.1.0

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
- **Source:** `defaults\main.yml:None`
### `app\_port`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `8000`
- **Source:** `defaults\main.yml:None`
### `app\_debug`


- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `False`
- **Source:** `defaults\main.yml:None`
### `app\_workers`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `2`
- **Source:** `defaults\main.yml:None`
### `db\_host`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `localhost`
- **Source:** `defaults\main.yml:None`
### `db\_port`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `5432`
- **Source:** `defaults\main.yml:None`
### `db\_name`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `\{\{ app\_name \}\}\_db`
- **Source:** `defaults\main.yml:None`
### `db\_user`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `\{\{ app\_name \}\}\_user`
- **Source:** `defaults\main.yml:None`
### `db\_password`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `changeme`
- **Source:** `defaults\main.yml:None`
### `web\_ssl\_enabled`


- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `False`
- **Source:** `defaults\main.yml:None`
### `web\_ssl\_cert`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** ``
- **Source:** `defaults\main.yml:None`
### `web\_ssl\_key`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** ``
- **Source:** `defaults\main.yml:None`
### `web\_domain`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `localhost`
- **Source:** `defaults\main.yml:None`
### `app\_install\_dir`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/opt/\{\{ app\_name \}\}`
- **Source:** `defaults\main.yml:None`
### `app\_config\_dir`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/etc/\{\{ app\_name \}\}`
- **Source:** `defaults\main.yml:None`
### `app\_log\_dir`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/var/log/\{\{ app\_name \}\}`
- **Source:** `defaults\main.yml:None`
### `old\_app\_path`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/usr/local/\{\{ app\_name \}\}`
- **Source:** `defaults\main.yml:None`
### `db\_connection\_pool\_size`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `10`
- **Source:** `vars\main.yml:None`
### `db\_query\_timeout`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `15`
- **Source:** `vars\main.yml:None`
### `app\_cache\_enabled`


- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `True`
- **Source:** `vars\main.yml:None`
### `app\_cache\_ttl`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `300`
- **Source:** `vars\main.yml:None`
### `app\_rate\_limit`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `60`
- **Source:** `vars\main.yml:None`
### `app\_allowed\_origins`


- **Type:** `VariableType.LIST`
- **Required:** No
- **Value:** `\['\*'\]`
- **Source:** `vars\main.yml:None`
### `metrics\_enabled`


- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `False`
- **Source:** `vars\main.yml:None`
### `metrics\_port`


- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `9100`
- **Source:** `vars\main.yml:None`
### `log\_format`


- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `text`
- **Source:** `vars\main.yml:None`

---

## Tags

14 tag(s) available:

### `always`


- **Usage Count:** 1
- **Locations:**
  - `tasks\main.yml:1`

### `configuration`


- **Usage Count:** 3
- **Locations:**
  - `tasks\main.yml:4`
  - `tasks\main.yml:5`
  - `tasks\main.yml:9`

### `database`


- **Usage Count:** 2
- **Locations:**
  - `tasks\main.yml:7`
  - `tasks\main.yml:8`

### `deployment`


- **Usage Count:** 4
- **Locations:**
  - `tasks\main.yml:9`
  - `tasks\main.yml:11`
  - `tasks\main.yml:12`
  - `tasks\main.yml:13`

### `directories`


- **Usage Count:** 1
- **Locations:**
  - `tasks\main.yml:3`

### `healthcheck`


- **Usage Count:** 2
- **Locations:**
  - `tasks\main.yml:12`
  - `tasks\main.yml:13`

### `info`


- **Usage Count:** 1
- **Locations:**
  - `tasks\main.yml:1`

### `installation`


- **Usage Count:** 4
- **Locations:**
  - `tasks\main.yml:2`
  - `tasks\main.yml:3`
  - `tasks\main.yml:6`
  - `tasks\main.yml:10`

### `packages`


- **Usage Count:** 1
- **Locations:**
  - `tasks\main.yml:6`

### `services`


- **Usage Count:** 1
- **Locations:**
  - `tasks\main.yml:11`

### `setup`


- **Usage Count:** 2
- **Locations:**
  - `tasks\main.yml:7`
  - `tasks\main.yml:8`

### `systemd`


- **Usage Count:** 1
- **Locations:**
  - `tasks\main.yml:10`

### `users`


- **Usage Count:** 1
- **Locations:**
  - `tasks\main.yml:2`

### `webserver`


- **Usage Count:** 2
- **Locations:**
  - `tasks\main.yml:4`
  - `tasks\main.yml:5`


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

*Documentation generated by ansible-doctor-enhanced v0.1.0*