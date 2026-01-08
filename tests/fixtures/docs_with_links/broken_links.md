# Documentation with Broken Links

This document contains broken links for testing link validation.

## Broken Internal Links

- [Missing File](does_not_exist.md) - This file doesn't exist
- [Wrong Path](../../../../../../missing.md) - Path goes outside project
- [Invalid Section](#nonexistent-section) - Section doesn't exist

## Broken External Links

- [Dead Link](https://this-domain-does-not-exist-12345.com/)
- [404 Page](https://httpstat.us/404)
- [Timeout](https://httpstat.us/200?sleep=30000)

## Malformed Links

- [Empty Target]()
- [Space in URL](https://example.com/space in url)
