# demo-role

Demonstration role showcasing all ansible-doctor-enhanced features

**Generated:** 2025-11-19 21:39 | **Version:** 0.3.0

---

## Table of Contents

- [Overview](#overview)
- [Variables](#variables)- [Tags](#tags)- [Examples](#examples)
---

## Overview

**Role Name:** demo\-role

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

example: "my-web-app"
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `demo\-app`

### `app\_port`

example: 8080
- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `8000`

### `app\_debug`

example: false
- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `False`

### `app\_workers`

example: 4
Database Configuration
- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `2`

### `db\_host`

example: "db.example.com"
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `localhost`

### `db\_port`

example: 5432
- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `5432`

### `db\_name`

example: "myapp_production"
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `\{\{ app\_name \}\}\_db`

### `db\_user`

example: "app_user"
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `\{\{ app\_name \}\}\_user`

### `db\_password`

example: "SecureP@ssw0rd123"
Web Server Configuration
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `changeme`

### `web\_ssl\_enabled`

example: true
- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `False`

### `web\_ssl\_cert`

example: "/etc/ssl/certs/server.crt"
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** ``

### `web\_ssl\_key`

example: "/etc/ssl/private/server.key"
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** ``

### `web\_domain`

example: "myapp.example.com"
Application Paths
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `localhost`

### `app\_install\_dir`

example: "/opt/myapp"
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/opt/\{\{ app\_name \}\}`

### `app\_config\_dir`

example: "/etc/myapp"
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/etc/\{\{ app\_name \}\}`

### `app\_log\_dir`

example: "/var/log/myapp"
Deprecated Variables (for migration demonstration)
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/var/log/\{\{ app\_name \}\}`

### `old\_app\_path`

deprecated: "Use app_install_dir instead. Will be removed in v2.0.0"
@example Basic development setup
app_name: "dev-app"
app_port: 3000
app_debug: true
app_workers: 1
db_host: "localhost"
db_name: "dev_database"
web_ssl_enabled: false
@end
@example Production deployment with SSL
app_name: "prod-api"
app_port: 8443
app_debug: false
app_workers: 8
db_host: "db-primary.internal.example.com"
db_port: 5432
db_name: "production_db"
db_user: "prod_user"
web_ssl_enabled: true
web_ssl_cert: "/etc/ssl/certs/api.example.com.crt"
web_ssl_key: "/etc/ssl/private/api.example.com.key"
web_domain: "api.example.com"
@end
@example High-availability setup with replicas
app_name: "ha-app"
app_workers: 16
db_host: "db-cluster.internal.example.com"
db_replica_hosts:
- "db-replica1.internal.example.com"
- "db-replica2.internal.example.com"
db_pool_size: 50
web_ssl_enabled: true
@end
- **Type:** `VariableType.STRING`
- **Required:** No
- **Value:** `/usr/local/\{\{ app\_name \}\}`

### `db\_connection\_pool\_size`

Maximum database connection pool size
@var db_connection_pool_size.type: int
@var db_connection_pool_size.example: 20
- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `10`

### `db\_query\_timeout`

Database query timeout in seconds
@var db_query_timeout.type: int
@var db_query_timeout.example: 30
Performance tuning
- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `15`

### `app\_cache\_enabled`

Enable in-memory application cache
@var app_cache_enabled.type: bool
- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `True`

### `app\_cache\_ttl`

Cache time-to-live in seconds
@var app_cache_ttl.type: int
@var app_cache_ttl.example: 600
Security settings
- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `300`

### `app\_rate\_limit`

Maximum requests per minute per IP
@var app_rate_limit.type: int
@var app_rate_limit.example: 100
- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `60`

### `app\_allowed\_origins`

CORS allowed origins list
@var app_allowed_origins.type: list
@var app_allowed_origins.example: ["https://example.com", "https://app.example.com"]
Monitoring and observability
- **Type:** `VariableType.LIST`
- **Required:** No
- **Value:** `\['\*'\]`

### `metrics\_enabled`

Enable Prometheus metrics endpoint
@var metrics_enabled.type: bool
- **Type:** `VariableType.BOOLEAN`
- **Required:** No
- **Value:** `False`

### `metrics\_port`

Port for metrics endpoint
@var metrics_port.type: int
@var metrics_port.example: 9090
- **Type:** `VariableType.NUMBER`
- **Required:** No
- **Value:** `9100`

### `log\_format`

Log output format (json or text)
@var log_format.type: str
@var log_format.example: json
@var log_format.choices: [json, text]
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

5 example(s):

### Basic development setup


```yaml
app_name: "dev-app"
app_port: 3000
app_debug: true
app_workers: 1
db_host: "localhost"
db_name: "dev_database"
web_ssl_enabled: false
```

### Production deployment with SSL


```yaml
app_name: "prod-api"
app_port: 8443
app_debug: false
app_workers: 8
db_host: "db-primary.internal.example.com"
db_port: 5432
db_name: "production_db"
db_user: "prod_user"
web_ssl_enabled: true
web_ssl_cert: "/etc/ssl/certs/api.example.com.crt"
web_ssl_key: "/etc/ssl/private/api.example.com.key"
web_domain: "api.example.com"
```

### High\-availability setup with replicas


```yaml
app_name: "ha-app"
app_workers: 16
db_host: "db-cluster.internal.example.com"
db_replica_hosts:
  - "db-replica1.internal.example.com"
  - "db-replica2.internal.example.com"
db_pool_size: 50
web_ssl_enabled: true
```

### Running installation tasks only


```yaml
ansible-playbook site.yml --tags "installation"
```

### Checking application status


```yaml
ansible-playbook site.yml --tags "healthcheck"
```


---

*Documentation generated by ansible-doctor-enhanced v0.3.0*