# 🔄 Enable Dynamic Badges

Your repository is configured with **static badges** by default. To enable **dynamic auto-updating badges** with live metrics:

## Current Badges (Static)

✅ **Working now** - No setup required  
❌ Manual updates needed when version/stats change

## Dynamic Badges (Available)

✅ Auto-update after every CI run  
✅ Real-time coverage % with color coding  
✅ Live mypy error counts  
✅ Actual test pass/fail stats  
❌ Requires 5-minute setup

## How to Enable Dynamic Badges

### Quick Steps (5 minutes)

1. **Read the guide**: [BADGE_SETUP_QUICKSTART.md](../BADGE_SETUP_QUICKSTART.md)
2. **Create GitHub Gist** (1 min)
3. **Create Personal Access Token** (1 min) 
4. **Add GitHub Secrets** (1 min)
5. **Update README badges** (1 min)
6. **Push and verify** (1 min)

### Detailed Instructions

Full documentation: [docs/BADGES.md](../docs/BADGES.md)

### What You'll Get

**Dynamic Badge Examples:**

```markdown
<!-- Version badges auto-synced from pyproject.toml -->
![Python](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/K4M1coder/YOUR_GIST_ID/raw/python-version.json)
![Version](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/K4M1coder/YOUR_GIST_ID/raw/package-version.json)

<!-- Coverage with dynamic colors: red <80%, orange 80-90%, green >90% -->
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/K4M1coder/YOUR_GIST_ID/raw/coverage.json)

<!-- Real mypy status: "✨ 0 errors (122 files)" or "5 errors" -->
![mypy](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/K4M1coder/YOUR_GIST_ID/raw/mypy.json)

<!-- Actual test counts: "2163 passed, 50 skipped" -->
![Tests](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/K4M1coder/YOUR_GIST_ID/raw/tests.json)
```

### Comparison

| Feature | Static Badges | Dynamic Badges |
|---------|---------------|----------------|
| **Setup time** | 0 minutes ✅ | 5 minutes |
| **Works now** | ✅ Yes | After setup |
| **Auto-updates** | ❌ No | ✅ Yes |
| **Live coverage** | ❌ Manual | ✅ Auto (with colors) |
| **Live test counts** | ❌ Hardcoded | ✅ Real numbers |
| **Mypy status** | ❌ Generic | ✅ "0 errors (122 files)" |
| **Version sync** | ❌ Manual | ✅ Auto from pyproject.toml |

## When to Enable

- ✅ **Now**: If you want transparency and auto-updating stats
- ✅ **Later**: Current static badges work fine until then
- ✅ **Never**: If you prefer simple static badges

## Help

- Quick Start: [BADGE_SETUP_QUICKSTART.md](../BADGE_SETUP_QUICKSTART.md)
- Full Guide: [docs/BADGES.md](../docs/BADGES.md)
- Issues? Check troubleshooting section in guides above

---

**TL;DR:** Static badges work now. Dynamic badges available when ready - 5 min setup for auto-updating metrics.
