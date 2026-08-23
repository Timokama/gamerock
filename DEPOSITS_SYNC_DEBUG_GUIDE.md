# Deposits Section Synchronization - Debugging Guide

## Overview
This guide provides systematic steps to diagnose and resolve issues where the Deposits section of the developer dashboard fails to reflect recent changes or updates.

---

## Quick Diagnosis Checklist

Run through these verification steps in order:

### 1. Verify Server Status
```bash
# Check if Flask is running
netstat -ano | findstr :5000

# Expected: Shows LISTENING on port 5000
```

### 2. Verify Routes Are Registered
```bash
# Run in project directory
python -c "from app import create_app; app = create_app(); [print(r) for r in app.url_map.iter_rules() if 'contribution' in str(r)]"

# Expected output includes:
# /contribution/api/member/<int:member_id>/pending-contributions
```

### 3. Test API Endpoint Directly
Open browser DevTools (F12) → Console and run:
```javascript
fetch('/contribution/api/member/1/pending-contributions')
    .then(r => {
        console.log('Status:', r.status);
        return r.json();
    })
    .then(data => console.log('Response:', data))
    .catch(err => console.error('Error:', err));

# Expected: Status 200 with JSON containing pending_contributions array
```

### 4. Check for JavaScript Errors
In browser Console, look for:
- `404 Not Found` → Wrong URL
- `403 Forbidden` → Permission issue
- `ReferenceError` → Undefined variable
- `TypeError` → Null reference

### 5. Verify Dropdown Initialization
```javascript
// In browser Console
console.log('membersData:', membersData);
console.log('Dropdowns:', document.querySelectorAll('.pending-contributions-select').length);
```

---

## Common Causes and Solutions

### Cause 1: Browser Caching
**Symptoms:** Changes not visible after code updates

**Solutions:**
- Hard refresh: `Ctrl + Shift + R` or `Ctrl + F5`
- Clear browser cache: `Ctrl + Shift + Delete`
- Open DevTools → Network tab → Check "Disable cache"

### Cause 2: Wrong API URL
**Symptoms:** 404 errors in Network tab

**Verify in admin_dashboard.html line 2810:**
```javascript
// CORRECT:
fetch('/contribution/api/member/' + selectedMemberId + '/pending-contributions')

// WRONG:
fetch('/deposit/api/member/' + selectedMemberId + '/pending-contributions')
```

**Why:** Blueprint is registered with `/contribution` prefix:
```python
# app/__init__.py line 82-83
app.register_blueprint(contribute_bp, url_prefix='/contribution')
```

### Cause 3: Permission Denied (403)
**Symptoms:** API returns 403 status

**Check:** User must have ADMIN or DEVEL role:
```python
# In Python shell
from flask_login import current_user
print(current_user.role.name)  # Must be 'ADMIN' or 'DEVEL'
```

### Cause 4: Template Variable Not Passed
**Symptoms:** `membersData is not defined`

**Verify in app/main.py the template receives `all_members`:**
```python
return render_template('admin_dashboard.html',
                     ...
                     all_members=all_members,
                     ...)
```

### Cause 5: JavaScript Not Initialized
**Symptoms:** Dropdown doesn't populate or respond

**Verify DOMContentLoaded handler exists:**
```javascript
document.addEventListener('DOMContentLoaded', function() {
    initializeMemberDropdowns();
    // ...
});
```

### Cause 6: Stale Database Session
**Symptoms:** Old data displayed after updates

**Solution:** Flask-SQLAlchemy may cache results. Force refresh:
```python
db.session.expire_all()
```

---

## Diagnostic Commands

### Check Template Variables
```javascript
// In browser Console
console.log('membersData length:', membersData?.length);
console.log('Dropdowns found:', document.querySelectorAll('.pending-contributions-select').length);
console.log('pendingContributionsCache:', pendingContributionsCache);
```

### Test API with Specific Member
```javascript
// Replace 1 with actual member ID
fetch('/contribution/api/member/1/pending-contributions')
    .then(r => r.json())
    .then(data => {
        console.log('Member:', data.member_name);
        console.log('Pending count:', data.count);
        console.log('Pending items:', data.pending_contributions);
    });
```

### Verify Dropdown Population
```javascript
document.querySelectorAll('.pending-contributions-select').forEach((s, i) => {
    console.log(`Dropdown ${i}: ${s.options.length} options, value="${s.value}"`);
});
```

---

## Error Messages and Fixes

| Error Message | Likely Cause | Solution |
|--------------|--------------|----------|
| `404 Not Found` | Wrong URL prefix | Use `/contribution/api/...` |
| `403 Forbidden` | User role issue | Login as ADMIN/DEVEL |
| `membersData is not defined` | Template variable missing | Check `all_members` passed to template |
| `Cannot read property 'forEach' of undefined` | API returned error | Check API response format |
| `select is null` | DOM not ready | Wrap code in DOMContentLoaded |
| No network activity | JavaScript error | Check Console for errors |

---

## Step-by-Step Resolution

### Step 1: Clear All Caches
```bash
# Clear Python cache
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# Restart Flask
set FLASK_DEBUG=1
flask run --reload
```

### Step 2: Hard Refresh Browser
```
Ctrl + Shift + R
```

### Step 3: Verify in Browser Console
```javascript
// Should show populated data
console.log('membersData:', membersData);
// Should show dropdown count > 0
console.log('Dropdowns:', document.querySelectorAll('.pending-contributions-select').length);
```

### Step 4: Test API Response
```javascript
fetch('/contribution/api/member/1/pending-contributions')
    .then(r => r.json())
    .then(d => console.log('API OK:', d))
    .catch(e => console.error('API FAIL:', e));
```

### Step 5: Test Dropdown Interaction
```javascript
// Select a different member in dropdown
// Check Network tab for API call
// Check Console for errors
```

---

## Prevention Best Practices

1. **Always use `--reload` flag** during development:
   ```bash
   flask run --reload
   ```

2. **Use cache-busting** in fetch calls:
   ```javascript
   fetch('/contribution/api/member/' + id + '/pending-contributions?_=' + Date.now())
   ```

3. **Enable template auto-reload**:
   ```python
   app.config['TEMPLATES_AUTO_RELOAD'] = True
   ```

4. **Check Console regularly** for JavaScript errors

5. **Verify API routes** after adding new endpoints:
   ```bash
   flask routes
   ```

---

## Files to Check When Debugging

| File | What to Verify |
|------|----------------|
| `app/__init__.py` | Blueprint registered with `/contribution` prefix |
| `app/main.py` | `all_members` passed to template |
| `app/deposit/routes.py` | API endpoint exists and returns correct JSON |
| `app/templates/admin_dashboard.html` | Fetch URL is `/contribution/api/...` |
| `app/templates/admin_dashboard.html` | `membersData` array is populated |
| `app/templates/admin_dashboard.html` | `DOMContentLoaded` handler initializes dropdowns |

---

## Quick Fix Summary

```bash
# 1. Clear caches
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

# 2. Restart server with reload
set FLASK_DEBUG=1
flask run --reload --port 5000

# 3. In browser: Ctrl+Shift+R (hard refresh)

# 4. In Console: verify membersData and API response
```
