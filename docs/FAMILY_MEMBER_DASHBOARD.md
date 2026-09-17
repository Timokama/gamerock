# Family Member Dashboard System

## Overview
This system enables Spouse and Child users to log in and automatically be redirected to their primary member's dashboard, where they can view family contributions, deposits, and overview information in a read-only mode.

## Status: ✅ IMPLEMENTED & TESTED

- **13 tests passing** (`python tests/test_family_member_redirect.py`)
- All Python files compile successfully
- Authentication flow redirects family users
- Data isolation enforced via route-level permissions
- Templates display family view indicators
- Family contributions aggregated in deposit views

## Architecture

### Key Components

1. **User Relationship Discovery** (`app/register/routes.py`)
   - `get_primary_member_id()`: Checks if current user has a Spouse or Child relationship with a primary member
   - `is_family_user()`: Convenience function to check if user is a family member

2. **Authentication Flow** (`app/auth.py`)
   - After successful login, checks if user is a spouse/child
   - Redirects family users to their primary member's dashboard
   - Regular users continue to normal login flow

3. **Context Processor** (`app/__init__.py`)
   - `is_viewing_family`: Boolean flag for templates
   - `family_member_name`: Name of the family member currently viewing

4. **Dashboard Routes** (`app/register/routes.py`)
   - `/dashboard`: Entry point that redirects based on user type
   - `/dashboard/<int:member_id>`: Main dashboard view with permission checks

5. **Deposit Views** (`app/deposit/routes.py`, `app/register/routes.py`)
   - Deposit views include contributions from family members who are also registered members

## User Roles and Permissions

### Admin Roles (DEVEL, ADMIN, WELFARE_OFFICER, TREASURER)
- Can view/edit any member's dashboard
- Can create/delete family members
- Can edit/delete contributions
- Full access to all features

### Family Member Users (USER with spouse/child link)
- **Redirected**: Automatically redirected to primary member's dashboard
- **Read-Only**: Cannot edit member profiles
- **Contribution Access**: Can view all family contributions
- **Event Access**: Cannot contribute to events (primary member must do this)

### Regular Users (USER without family link)
- View their own member dashboard
- Full control over their own data
- Cannot view other members' data

## Implementation Details

### Login Flow
```
User Login → Auth Route → Check User Role
  ├─ USER role → Check if Spouse/Child linked to Member
  │   ├─ Yes → Redirect to /dashboard/<primary_member_id>
  │   └─ No → Redirect to /dashboard/<own_member_id> or /dashboard/0
  └─ Admin Role → Redirect to /overview (admin dashboard)
```

### Dashboard Access Control
The `dashboard_member()` route enforces:
- Family users can only view their primary member's dashboard
- Regular users can only view their own member dashboard
- Admin roles can view any member dashboard

### Template Context Variables
- `is_viewing_family`: True when user is spouse/child viewing primary member's dashboard
- `family_member_name`: The name of the logged-in family member
- `family_contributions`: Contributions from family members (spouses/children with Member profiles)
- `total_family_deposits`: Total contributions from family members only

### Family Contribution Aggregation
Both deposit views and dashboard routes now aggregate contributions from:
1. The primary member
2. Family members (spouses/children) who have their own Member profiles

This allows families to see combined contribution totals while tracking individual contributions.

## Creating Family Member Accounts

### Via Admin Interface
1. Navigate to Member Profile
2. Go to Family section
3. Add Spouse or Child with email address
4. System creates User account with:
   - Role: USER
   - Derived password from id_number
   - Link to spouse/child record

### Via Registration
1. Family member signs up with email
2. Admin links them to primary member's family
3. User account is associated with Spouse/Child record

## Testing

Run the test suite:
```bash
python tests/test_family_member_redirect.py
```

Tests cover:
- `get_primary_member_id()` for spouses, children, regular users, and admins
- Family view indicator in templates
- Dashboard contribution aggregation

## Troubleshooting

### Family member not redirecting
- Check that `spouse.user_id` or `child.user_id` is set
- Verify `member_id` is populated in spouse/child records
- Check user role is set to USER (not admin roles)

### Contributions not showing family totals
- Verify spouse/child has a Member profile (linked via `user_id`)
- Check that the Member's `user_id` matches the spouse/child's `user_id`

### Template not showing family view badge
- Ensure `is_viewing_family` context variable is passed
- Check the context processor in `__init__.py` is enabled