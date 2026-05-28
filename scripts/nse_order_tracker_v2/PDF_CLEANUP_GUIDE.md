# 🧹 Automatic PDF Cleanup Feature

## Overview

The V2 NSE Order Book Tracker now includes **automatic PDF cleanup** to prevent disk space accumulation from daily downloads. Old PDFs are automatically deleted based on a configurable retention period.

---

## 🎯 Key Features

- **Automatic Cleanup**: Runs before every scraping job
- **Configurable Retention**: Default 7 days (customizable)
- **Safe Deletion**: Only removes files older than retention period
- **Space Reporting**: Logs how much disk space was freed
- **Non-Blocking**: Continues even if cleanup fails

---

## ⚙️ How It Works

### Default Behavior

By default, PDFs older than **7 days** are automatically deleted when you run the orchestrator:

```bash
python orchestrator.py --days 3
```

**Cleanup Process:**
1. Checks modification time of each PDF in `downloads/nse_pdfs/`
2. Compares against cutoff date (today - retention_days)
3. Deletes PDFs older than cutoff
4. Reports number of files deleted and space freed

### Example Output

```
2026-05-29 00:19:04 - INFO - Cleaning up PDFs older than 7 days (before 2026-05-22)
2026-05-29 00:19:04 - INFO - ✓ Cleaned up 12 old PDF(s), freed 5.47 MB
```

---

## 🛠️ Configuration

### Command-Line Option

Use the `--retention-days` flag to customize how long PDFs are kept:

```bash
# Keep PDFs for 14 days
python orchestrator.py --days 3 --retention-days 14

# Keep PDFs for 30 days
python orchestrator.py --days 7 --retention-days 30

# Delete all old PDFs (keep only today's)
python orchestrator.py --days 1 --retention-days 0
```

### GitHub Actions (Automated Runs)

The workflow is configured with **7-day retention** by default:

```yaml
- name: Run V2 API scraper with auto-cleanup
  run: |
    cd scripts/nse_order_tracker_v2
    python orchestrator.py --days 3 --retention-days 7
```

**Why not commit PDFs to git?**
- Large binary files bloat repository size
- PDFs are automatically re-downloadable from NSE
- Only JSON/Excel outputs are committed (small, text-based)

---

## 📊 Retention Guidelines

### Recommended Settings

| Use Case | Retention Days | Rationale |
|----------|----------------|-----------|
| **Daily automated runs** | 7 days | Keeps last week's data for reference |
| **Development/Testing** | 3 days | Short retention for frequent testing |
| **Long-term archival** | 30 days | Monthly historical data |
| **Minimal disk usage** | 1 day | Keep only latest downloads |
| **No cleanup** | 365+ days | Essentially disable auto-cleanup |

### Disk Space Estimates

Average PDF size: ~500 KB per file

| Retention Period | Avg Daily Orders | Estimated Disk Usage |
|------------------|------------------|----------------------|
| 7 days | 5 orders/day | ~17.5 MB |
| 14 days | 5 orders/day | ~35 MB |
| 30 days | 5 orders/day | ~75 MB |

---

## 🔧 Manual Cleanup

### Clean All Old PDFs Manually

```python
from orchestrator import OrderBookOrchestrator

# Create orchestrator with 0-day retention
orch = OrderBookOrchestrator(pdf_retention_days=0)

# Run cleanup
orch.cleanup_old_pdfs()
```

### Delete All PDFs

```bash
# Caution: Deletes ALL PDFs
rm -rf downloads/nse_pdfs/*.pdf
```

---

## 🚫 Disabling Auto-Cleanup

If you want to keep all PDFs indefinitely, set a very high retention period:

```bash
# Keep PDFs for 10 years
python orchestrator.py --days 3 --retention-days 3650
```

Or modify the code to skip cleanup by commenting out the cleanup call in `orchestrator.py`:

```python
def run(self, search_term: str = "awarding of order", days_back: int = 30):
    logger.info("STARTING ORDER BOOK ORCHESTRATOR")
    logger.info(f"Search: '{search_term}', Days: {days_back}\n")

    try:
        # Step 0: Cleanup old PDFs
        # self.cleanup_old_pdfs()  # COMMENTED OUT - no cleanup

        # Step 1: Scrape announcements
        self.scrape_announcements(search_term, days_back)
```

---

## 📁 File Organization

### Directory Structure

```
downloads/nse_pdfs/
├── LIKHITHA_2026-05-28.pdf     ← Recent (kept)
├── INNOVISION_2026-05-27.pdf   ← Recent (kept)
├── ACMESOLAR_2026-05-26.pdf    ← Recent (kept)
├── MAHEPC_2026-05-20.pdf       ← Old (deleted after 7 days)
└── PIGL_2026-04-29.pdf         ← Very old (already deleted)
```

### Naming Convention

PDFs are named: `{SYMBOL}_{YYYY-MM-DD}.pdf`

- Easy to identify company and date
- Alphabetically sortable
- Unique per company per day

---

## 🔍 Monitoring Cleanup

### Check Cleanup Logs

```bash
# Run with verbose output
python orchestrator.py --days 3 2>&1 | grep "Cleaning up"
```

### Output Examples

**No files to delete:**
```
2026-05-29 00:19:04 - INFO - Cleaning up PDFs older than 7 days (before 2026-05-22)
2026-05-29 00:19:04 - INFO - ✓ No old PDFs to clean up
```

**Files deleted:**
```
2026-05-29 00:19:13 - INFO - Cleaning up PDFs older than 7 days (before 2026-05-22)
2026-05-29 00:19:13 - INFO - ✓ Cleaned up 17 old PDF(s), freed 9.29 MB
```

---

## ⚠️ Important Notes

1. **Cleanup is based on file modification time**, not filename date
   - If you manually edit/touch a PDF, its modification time updates
   - This could prevent it from being cleaned up

2. **Cleanup runs at the START of each orchestrator run**
   - Old PDFs are deleted BEFORE new ones are downloaded
   - Ensures disk space is available for new downloads

3. **PDFs are not backed up before deletion**
   - Once deleted, they're gone (but can be re-downloaded from NSE if needed)
   - The JSON/Excel outputs still contain extracted data

4. **Cleanup errors are non-fatal**
   - If a PDF can't be deleted (permissions, locked file), a warning is logged
   - The scraper continues normally

---

## 🧪 Testing Cleanup

### Test with Short Retention

```bash
# Test cleanup with 0-day retention (deletes all old PDFs)
python -c "
from orchestrator import OrderBookOrchestrator
orch = OrderBookOrchestrator(pdf_retention_days=0)
orch.cleanup_old_pdfs()
"
```

### Verify PDFs Deleted

```bash
# Before cleanup
ls -lh downloads/nse_pdfs/*.pdf

# After cleanup (should show fewer files)
ls -lh downloads/nse_pdfs/*.pdf
```

---

## 💡 Best Practices

1. **Use 7-day retention for production**
   - Balances disk usage and data availability
   - Keeps recent orders accessible

2. **Archive important PDFs separately**
   - If specific orders need long-term retention
   - Copy to separate archive directory outside `downloads/`

3. **Monitor disk usage periodically**
   ```bash
   du -sh downloads/nse_pdfs/
   ```

4. **Check cleanup logs in GitHub Actions**
   - Review workflow run logs to ensure cleanup is working
   - Verify disk space is being freed

5. **Coordinate retention with JSON/Excel exports**
   - JSON/Excel files contain extracted data
   - Even after PDFs are deleted, data is preserved

---

## 🔗 Related Documentation

- **V2_SETUP_COMPLETE.md** - Main setup guide
- **DASHBOARD_COMPLETE.md** - Dashboard features
- **docs/QUICK_START_GUIDE.md** - Getting started

---

## 📝 Summary

The automatic PDF cleanup feature ensures your disk doesn't fill up with old order PDFs while maintaining recent data accessibility. With configurable retention periods and automatic operation, it provides a hands-off solution to disk space management.

**Default Configuration:**
- ✅ Auto-cleanup: Enabled
- ✅ Retention: 7 days
- ✅ Frequency: Every orchestrator run
- ✅ Logging: Verbose (files deleted + space freed)
- ✅ Git: PDFs excluded from repository

**No action needed** - it just works! 🎉
