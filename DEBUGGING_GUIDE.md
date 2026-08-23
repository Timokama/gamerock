# Debugging Guide: Deposit-Table-Card Component Updates

## Quick Diagnostic Checklist

Run through these steps in order:

### 1. Verify Server is Running Correctly
```bash
# Check if Flask is running
netstat -ano | findstr :5000

# Restart with debug mode and auto-reload
set FLASK_APP=run.py
set FLASK_DEBUG=1
flask run --reload
```

### 2. Clear All Caches
```bash
# Clear Python cache
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force

# Clear browser cache (in browser console)
# Press Ctrl+Shift+Delete → Clear cached images and files
```

### 3. Verify Blueprint Registration
The deposit blueprint uses `/contribution` prefix, NOT `/deposit`:
```python
# app/__init__.py line 82-83
from app.deposit import bp as contribute_bp
app.register_blueprint(contribute_bp, url_prefix='/contribution')
```

**API Endpoint URL:** `/contribution/api/member/<id>/pending-contributions`

### 4. Test API Endpoint Directly
```bash
# In browser or curl, test:
GET /contribution/api/member/1/pending-contributions

# Expected JSON response:
{
    "member_id": 1,
    "member_name": "John Doe",
    "pending_contributions": [...],
    "count": 2,
    "member_profile_image": null,
    "member_profile_mime_type": "image/jpeg"
}
```

### 5. Check Browser Console for Errors
```javascript
// In browser DevTools (F12) Console tab, look for:
// - 404 errors (wrong URL)
// - 403 errors (permission denied)
// - CORS errors
// - JavaScript syntax errors
```

### 6. Verify Template Changes
```bash
# Check if template is being loaded
# Add temporary debug output in admin_dashboard.html:
<!-- DEBUG: Template loaded at {{ now() if now is defined else "N/A" }} -->
```

---

## Common Issues and Solutions

### Issue: Changes Not Reflecting After Save

**Cause:** Jinja2 template caching
**Solution:**
```python
# In app config
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
```

### Issue: API Returns 404

**Cause:** Wrong URL prefix
**Solution:** Use `/contribution/api/...` not `/deposit/api/...`

### Issue: API Returns 403

**Cause:** User doesn't have ADMIN/DEVEL role
**Solution:** Check user role in database:
```python
# In Python shell
from app.models.user import User
user = User.query.get(1)
print(user.role.name)  # Should be 'ADMIN' or 'DEVEL'
```

### Issue: Dropdown Change Not Triggering Update

**Cause:** JavaScript error or wrong function binding
**Solution:** Check browser console, verify:
```javascript
// In console, test:
document.querySelectorAll('.pending-contributions-select').length
// Should return > 0
```

### Issue: Profile Images Not Displaying

**Cause:** Image data not loaded or wrong MIME type
**Solution:** Check API response includes `member_profile_image`

---

## Implementation Summary

### Files Modified:
1. `app/templates/admin_dashboard.html` - Frontend template
2. `app/deposit/routes.py` - API endpoint

### Key Components:

#### Frontend (admin_dashboard.html):
- **CSS:** `.pending-contributions-select`, `.pending-contributions-list`, `.loading` state
- **HTML:** Dropdown select with `onchange` handler, ARIA attributes
- **JavaScript:** 
  - `loadPendingContributions(select, rowMemberId)` - Main fetch function
  - `renderPendingContributions(listEl, data, rowMemberId)` - Render function
  - `retryPendingContributions(selectedMemberId, rowMemberId)` - Error retry
  - `invalidatePendingContributionsCache(memberId)` - Cache management
  - State: `pendingContributionsCache`, `pendingContributionsLoading`

#### Backend (deposit/routes.py):
- **Endpoint:** `/contribution/api/member/<int:member_id>/pending-contributions`
- **Method:** GET
- **Auth:** `@login_required` + role check
- **Response:** JSON with pending events + member profile image

---

## Testing Procedure

1. **Login as Admin/Devel user**
2. **Navigate to Dashboard** (`/home/overview`)
3. **Locate "Recent Contributions" table**
4. **Verify dropdown shows member names**
5. **Select a different member from dropdown**
6. **Verify loading state appears**
7. **Verify pending contributions list updates**
8. **Check member profile image displays (if available)**
9. **Test error handling by temporarily disconnecting network**
10. **Verify retry button appears and works**

---

## Performance Considerations

- **Caching:** Responses cached in `pendingContributionsCache` object
- **Cache invalidation:** Cleared on page visibility change
- **Loading states:** Prevents duplicate requests
- **Max list height:** 200px with overflow scroll

---

## Accessibility Features

- `aria-label` on select element
- `aria-controls` linking select to list
- `aria-expanded` toggles on selection
- `aria-live="polite"` on results region
- `aria-busy` during loading
- Keyboard navigable dropdown
