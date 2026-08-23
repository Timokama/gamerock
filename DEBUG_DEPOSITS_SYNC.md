# Debugging Guide: Deposits Section Synchronization Issues

## Problem Statement
The Deposits section of the developer dashboard is failing to reflect recent changes or updates.

---

## Systematic Debugging Steps

### Step 1: Verify the Flask Server is Running

```bash
# Check if Flask is running
netstat -ano | findstr :5000

# If not running, start with debug mode
cd C:\Users\user\gamerock\gamerock
set FLASK_APP=run.py
set FLASK_DEBUG=1
flask run --reload
```

### Step 2: Verify Blueprint Registration

**File:** `app/__init__.py` (line 82-83)

```python
# The deposit blueprint uses '/contribution' prefix, NOT '/deposit'
from app.deposit import bp as contribute_bp
app.register_blueprint(contribute_bp, url_prefix='/contribution')
```

**Important:** The API endpoint is at:
- ✅ `/contribution/api/member/<id>/pending-contributions`
- ❌ NOT `/deposit/api/member/<id>/pending-contributions`

### Step 3: Test API Endpoint Directly

Open browser DevTools (F12) → Console:
```javascript
// Test the API endpoint
fetch('/contribution/api/member/1/pending-contributions')
    .then(r => r.json())
    .then(data => console.log('API Response:', data))
    .catch(err => console.error('API Error:', err));
```

**Expected Response:**
```json
{
    "member_id": 1,
    "member_name": "John Doe",
    "pending_contributions": [...],
    "count": 2,
    "member_profile_image": null,
    "member_profile_mime_type": "image/jpeg"
}
```

### Step 4: Check for JavaScript Errors

In browser DevTools (F12) → Console tab, look for:
- 404 errors (wrong URL)
- 403 errors (permission denied)
- CORS errors
- JavaScript syntax errors

### Step 5: Verify Dropdown Initialization

In browser Console:
```javascript
// Check if membersData is populated
console.log('membersData:', membersData);
console.log('Dropdowns found:', document.querySelectorAll('.pending-contributions-select').length);
```

### Step 6: Test Dropdown Population

```javascript
// Check if dropdowns are populated
document.querySelectorAll('.pending-contributions-select').forEach((select, i) => {
    console.log(`Dropdown ${i}:`, select.options.length, 'options');
});
```

---

## Potential Causes and Solutions

### Cause 1: Browser Caching

**Symptoms:** Changes not visible after refresh

**Solution:**
```
Hard refresh: Ctrl + Shift + R
Or: Ctrl + F5
```

**Permanent fix:** Add cache-busting to template:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}?v=2">
```

### Cause 2: Jinja2 Template Caching

**Symptoms:** Template changes not reflecting

**Solution:** Enable template auto-reload in Flask:
```python
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
```

### Cause 3: API URL Mismatch

**Symptoms:** 404 errors in Network tab

**Verify the fetch URL in admin_dashboard.html:**
```javascript
// Line 2810 - Should be:
fetch('/contribution/api/member/' + selectedMemberId + '/pending-contributions?_=' + Date.now())

// NOT:
fetch('/deposit/api/member/' + selectedMemberId + '/pending-contributions')
```

### Cause 4: Permission Denied (403)

**Symptoms:** API returns 403 status

**Check user role:**
```python
# In Python shell or add debug logging
from flask_login import current_user
print(f"User role: {current_user.role.name}")  # Must be 'ADMIN' or 'DEVEL'
```

### Cause 5: Database Session Stale Data

**Symptoms:** Old data displayed after updates

**Solution:** Clear SQLAlchemy identity map:
```python
from app import db
db.session.expire_all()  # Force re-query from database
```

### Cause 6: JavaScript State Not Updating

**Symptoms:** UI doesn't reflect changes after dropdown selection

**Debug in Console:**
```javascript
// Clear cache and retry
pendingContributionsCache = {};
pendingContributionsLoading = {};

// Manually trigger reload
var select = document.querySelector('.pending-contributions-select');
if (select) {
    loadPendingContributions(select, select.dataset.selectedId);
}
```

### Cause 7: Event Handler Not Bound

**Symptoms:** Dropdown change doesn't trigger anything

**Verify event binding:**
```javascript
// In console
var select = document.querySelector('.pending-contributions-select');
console.log('Select element:', select);
console.log('Onchange handler:', select ? select.onchange : 'NOT FOUND');
```

---

## Diagnostic Script

Add this temporary debug code to `admin_dashboard.html` before `</body>`:

```javascript
<script>
// DEBUG: Add this temporarily before </body>
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DEBUG INFO ===');
    console.log('membersData:', membersData);
    console.log('membersData length:', membersData ? membersData.length : 'UNDEFINED');
    
    var selects = document.querySelectorAll('.pending-contributions-select');
    console.log('Dropdown selects found:', selects.length);
    
    selects.forEach(function(select, i) {
        console.log('Dropdown ' + i + ':', {
            id: select.id,
            selectedId: select.dataset.selectedId,
            optionsCount: select.options.length,
            value: select.value
        });
    });
    
    // Test API
    if (membersData && membersData.length > 0) {
        var testId = membersData[0].id;
        fetch('/contribution/api/member/' + testId + '/pending-contributions')
            .then(r => r.json())
            .then(data => console.log('API test for member ' + testId + ':', data))
            .catch(err => console.error('API test failed:', err));
    }
    console.log('=== END DEBUG ===');
});
</script>
```

---

## Verification Checklist

- [ ] Flask server running with `--reload` flag
- [ ] Browser cache cleared (Ctrl+Shift+R)
- [ ] No JavaScript errors in Console
- [ ] API endpoint returns 200 status
- [ ] `membersData` array is populated
- [ ] Dropdowns have options populated
- [ ] User role is ADMIN or DEVEL
- [ ] Database connection is active
- [ ] No SQL errors in Flask console

---

## Common Error Messages and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `404 Not Found` | Wrong URL prefix | Use `/contribution/api/...` |
| `403 Forbidden` | Wrong user role | Login as ADMIN/DEVEL |
| `membersData is not defined` | Template variable issue | Verify `all_members` passed to template |
| `Cannot read property 'forEach' of undefined` | API returned error | Check API response format |
| `select is null` | DOM not ready | Wrap in DOMContentLoaded |

---

## Performance Monitoring

Add timing to API calls:

```javascript
// In loadPendingContributions function:
console.time('API Call for member ' + selectedMemberId);

// In .then() callback:
console.timeEnd('API Call for member ' + selectedMemberId);
```

---

## Quick Fix Commands

```bash
# Clear Python cache
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force

# Restart Flask with debug
set FLASK_DEBUG=1
flask run --reload --port 5000

# Verify routes
flask routes
```

---

## Contact Points for Escalation

If issues persist after above steps:
1. Check Flask logs for SQL errors
2. Verify database migrations are up to date
3. Check for conflicting JavaScript libraries
4. Verify template inheritance chain
