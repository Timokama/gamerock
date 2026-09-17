# GameRock - API Reference

## 4.1 Overview

GameRock is primarily a **server-rendered Flask application** using Jinja2 templates. It does not expose a traditional REST API. However, it provides several **JSON endpoints** for AJAX interactions and dashboard widgets. This document covers all programmatic interfaces.

## 4.2 Authentication

All endpoints require authentication via **Flask-Login session cookies**. No token-based authentication is implemented.

```python
# Session-based authentication
# Login: POST /<role>/login
# Logout: GET /logout
```

## 4.3 JSON Endpoints

### 4.3.1 Community Events API

#### Get Event Statistics
```http
GET /community/<int:event_id>/stats
```

**Permissions**: Authenticated users

**Response**:
```json
{
  "event_id": 1,
  "event_name": "Annual Fundraiser",
  "total": 150000,
  "contributor_count": 45,
  "goal_amount": 200000,
  "location": "Community Hall",
  "by_day": {
    "2024-01-15": 50000,
    "2024-01-16": 75000
  },
  "by_payment": {
    "MPESA": 100000,
    "Ksh": 30000,
    "BANK DEPOSIT": 20000
  },
  "top_members": {
    "John Doe": 25000,
    "Jane Smith": 20000
  }
}
```

#### Quick Contribute
```http
POST /community/<int:event_id>/contribute
Content-Type: application/x-www-form-urlencoded
```

**Permissions**: Authenticated user with member profile

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `amount` | float | Yes | Contribution amount |
| `payment_type` | string | Yes | `CASH`, `MOBILE_MONEY`, `BANK` |

**Response**:
```json
{
  "success": true,
  "new_total": 150000,
  "contributor_count": 46,
  "message": "Contribution recorded successfully."
}
```

#### Toggle Bookmark
```http
POST /community/<int:event_id>/bookmark
```

**Permissions**: Authenticated user

**Response**:
```json
{
  "success": true,
  "action": "added",
  "bookmarks": [1, 3, 5]
}
```

#### Upcoming Events
```http
GET /community/events/upcoming
```

**Permissions**: Authenticated user

**Response**:
```json
{
  "upcoming": [
    {
      "id": 1,
      "name": "Annual Fundraiser",
      "event_date": "2024-12-25",
      "location": "Community Hall",
      "goal_amount": 200000
    }
  ]
}
```

### 4.3.2 Deposit/Contribution API

#### Member Pending Contributions
```http
GET /contribution/api/member/<int:member_id>/pending-contributions
```

**Permissions**: ADMIN, DEVEL, WELFARE_OFFICER

**Response**:
```json
{
  "member_id": 1,
  "member_name": "John Doe Smith",
  "pending_contributions": [
    {
      "id": 2,
      "name": "Building Fund",
      "details": "New community center",
      "event_date": "Dec 25, 2024",
      "created_at": "Jan 15, 2024"
    }
  ],
  "count": 1,
  "has_profile_image": true,
  "member_image_url": "/member/1/image"
}
```

### 4.3.3 Reports API

#### Chart Data
```http
GET /reports/chart-data
```

**Permissions**: Authenticated user

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search across member name, ID, event, reference |
| `payment_type` | string | Filter by payment type (`CASH`, `MOBILE_MONEY`, `BANK`) |
| `date_from` | string | Start date (YYYY-MM-DD) |
| `date_to` | string | End date (YYYY-MM-DD) |
| `event` | int | Filter by event ID |

**Response**:
```json
{
  "total": 500000,
  "count": 120,
  "average": 4166,
  "monthly": {
    "2024-01": 150000,
    "2024-02": 200000,
    "2024-03": 150000
  },
  "payment_types": {
    "MPESA": 300000,
    "Ksh": 150000,
    "BANK DEPOSIT": 50000
  },
  "top_members": {
    "John Doe": 50000,
    "Jane Smith": 45000
  },
  "events": {
    "Annual Fundraiser": 200000,
    "Building Fund": 150000
  }
}
```

### 4.3.4 Member Image API

#### Get Member Image
```http
GET /member/<int:member_id>/image
```

**Permissions**: Authenticated user

**Response**: Binary image data with appropriate `Content-Type` header, or redirect to default avatar.

#### Get Current User Avatar
```http
GET /avatar
```

**Permissions**: Authenticated user

**Response**: Binary image data (JPEG/PNG/GIF/WebP) or generated SVG avatar with initials.

## 4.4 Template Global Functions

These functions are available in all Jinja2 templates via context processors:

### Access Control Globals

```jinja2
{% if is_admin_or_dev() %}
  <!-- Admin/Developer only content -->
{% endif %}

{% if can_manage_minutes() %}
  <!-- Secretary/Admin/Developer only -->
{% endif %}

{% if can_manage_treasurer() %}
  <!-- Treasurer/Admin/Developer only -->
{% endif %}

{% if can_manage_requisition() %}
  <!-- Chairperson/Admin/Developer only -->
{% endif %}
```

### Data Access Globals

```jinja2
{{ access_level_global() }}  {# Returns AccessLevel enum #}

{{ all_members }}            {# List of all Member objects (admin only) #}
{{ faq_count }}              {# Total FAQ count #}
{{ faq_categories }}         {# List of FAQ categories #}
{{ pending_deposits_count }} {# Events needing contributions #}
{{ pending_users_count }}    {# Users without member profiles #}
{{ recent_updates }}         {# Recent activity feed (admin only) #}
{{ now() }}                  {# Current datetime #}
```

### Family View Globals

```jinja2
{{ is_viewing_family }}           {# Boolean: viewing as spouse/child #}
{{ family_member_name }}          {# Name of family member being viewed #}
{{ family_primary_member_id }}    {# Primary member ID #}
```

## 4.5 Template Filters

### Data Masking Filters

```jinja2
{{ member.phone_num | mask_phone }}      {# 0712345678 → 071****678 #}
{{ member.id_number | mask_id }}         {# 12345678 → 123****678 #}

{{ member.phone_num | member_phone }}    {# Masked unless admin #}
{{ member.id_number | member_id }}       {# Masked unless admin #}
```

### Static Versioning

```jinja2
{{ static_version('css/main.css') }}     {# /static/css/main.css?v=1234567890 #}

{{ template_versions['admin_dashboard.html'] }}  {# Template modification timestamp #}
```

## 4.6 Model Reference

### 4.6.1 Core Models

#### User (`app/user.py`)

```python
class User(UserMixin, db.Model):
    id: int                          # Primary key
    surname: str                     # Surname
    first_name: str                  # First name
    email: str                       # Unique, not null
    password: str                    # PBKDF2-SHA256 hash
    phone_num: str                   # Phone number
    id_number: int                   # Unique ID number
    date_of_birth: date              # Birth date
    role: AccessLevel                # Enum: DEVEL, ADMIN, CHAIRPERSON, TREASURER, SECRETARY, WELFARE_OFFICER, USER
    status: str                      # 'pending' | 'active' | 'cancelled'
    bookmarks: dict                  # JSON: bookmarked event IDs
    created_at: datetime             # Server default
    
    # Relationships
    member_profile: Member           # One-to-one (user_id FK)
    spouse: Spouse                   # One-to-one (user_id FK)
    child: Child                     # One-to-one (user_id FK)
    image: list[Images]              # One-to-many
    contribution: list[Contribution] # One-to-many (added_by)
    event: list[CommunityEvent]      # One-to-many (created_by)
    family: list[Member]             # One-to-many (added_by)
    
    # Methods
    is_active() -> bool              # Returns status == 'active'
    passwords = property(setter)     # Hash password on set
    verify_passwords(password) -> bool
```

#### Member (`app/models/register.py`)

```python
class Member(db.Model):
    id: int                          # Primary key
    firstname: str                   # Not null
    lastname: str                    # Not null
    surname: str                     # Not null
    username: str                    # Unique, nullable
    date_of_birth: date
    created_at: datetime             # Server default
    phone_num: str
    email: str
    id_number: int                   # Unique
    user_id: int                     # FK to User, nullable
    added_by: int                    # FK to User (who added)
    
    # Relationships
    user_account: User               # Backref from User.member_profile
    spouse: list[Spouse]             # One-to-many
    child: list[Child]               # One-to-many
    contribute: list[Contribution]   # One-to-many
    requisitions: list[Requisition]  # One-to-many
```

#### Contribution (`app/models/contribute.py`)

```python
class Contribution(db.Model):
    id: int                          # Primary key
    amount: int
    trans_date: datetime             # Server default (timezone)
    payment_type: Payment            # Enum: CASH, MOBILE_MONEY, BANK, NEW
    transaction_ref: str             # Max 50 chars
    member_id: int                   # FK to Member
    propose: int                     # FK to CommunityEvent
    added_by: int                    # FK to User
    
    # Relationships
    member: Member                   # Backref
    community_event: CommunityEvent  # Backref
```

#### CommunityEvent (`app/models/community_event.py`)

```python
class CommunityEvent(db.Model):
    id: int                          # Primary key
    name: str                        # Not null, max 50
    details: str                     # Max 255
    event_date: date
    image: str                       # Filename, max 255
    location: str                    # Max 255
    goal_amount: int
    is_featured: bool                # Default False
    sort_order: int                  # Default 0
    created_at: datetime             # Server default
    update_at: datetime              # Server default + onupdate
    created_by: int                  # FK to User
    update_by: str                   # Max 20
    
    # Relationships
    contribute: list[Contribution]   # Backref
```

### 4.6.2 Financial Models

#### Budget (`app/models/budget.py`)

```python
class Budget(db.Model):
    id: int
    name: str                        # Not null, max 100
    description: text
    fiscal_year: str                 # Not null, max 10
    total_amount: int                # Default 0
    status: str                      # Draft, Approved, Active, Closed
    approved_by: int                 # FK to User
    approved_at: datetime
    created_by: int                  # FK to User
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    creator: User
    approver: User
    items: list[BudgetItem]          # Cascade delete-orphan
```

#### BudgetItem (`app/models/budget.py`)

```python
class BudgetItem(db.Model):
    id: int
    budget_id: int                   # FK to Budget
    category: str                    # Not null, max 100
    description: text
    amount: int                      # Not null
    item_type: str                   # Default 'Expense' (Income/Expense)
```

#### TreasurerRecord (`app/models/treasurer.py`)

```python
class TreasurerRecord(db.Model):
    id: int
    record_type: str                 # Default 'Transaction' (Income/Expense)
    amount: int                      # Default 0
    category: str                    # Not null, max 100
    description: text
    reference: str                   # Max 100
    transaction_date: date           # Not null
    created_by: int                  # FK to User
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    creator: User
```

### 4.6.3 Administrative Models

#### Minutes (`app/models/minutes.py`)

```python
class Minutes(db.Model):
    id: int
    title: str                       # Not null, max 150
    meeting_type: str                # Default 'General', max 50
    meeting_date: date               # Not null
    location: str                    # Max 150
    agenda: text
    discussion: text
    decisions: text
    action_items: text
    next_meeting_date: date
    attendees: text
    status: str                      # Default 'Draft' (Draft/Approved/Archived)
    approved_by: int                 # FK to User
    approved_at: datetime
    created_by: int                  # FK to User
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    creator: User
    approver: User
```

#### Requisition (`app/models/requisition.py`)

```python
class Requisition(db.Model):
    id: int
    item_name: str                   # Not null, max 100
    quantity: int                    # Default 1
    date_taken: date                 # Not null
    expected_return_date: date
    status: str                      # Default 'Pending' (Pending/Approved/Cancelled)
    member_id: int                   # FK to Member
    created_by: int                  # FK to User
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    member: Member
    creator: User
    items: list[RequisitionItem]     # Cascade delete-orphan
```

#### RequisitionItem (`app/models/requisition.py`)

```python
class RequisitionItem(db.Model):
    id: int
    requisition_id: int              # FK to Requisition
    item_name: str                   # Not null, max 100
    quantity: int                    # Default 1
```

#### Sponsor (`app/models/sponsor.py`)

```python
class Sponsor(db.Model):
    id: int
    name: str                        # Not null, max 200
    contact_person: str              # Max 200
    email: str                       # Max 200
    phone: str                       # Max 50
    address: text
    sponsorship_type: str            # Max 100
    amount: int                      # Default 0
    start_date: date
    end_date: date
    status: str                      # Default 'Active'
    notes: text
    created_by: int                  # FK to User
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    creator: User
    items: list[SponsorItem]
```

#### SponsorItem (`app/models/sponsor.py`)

```python
class SponsorItem(db.Model):
    id: int
    sponsor_id: int                  # FK to Sponsor
    item_name: str                   # Not null, max 200
    description: text
    quantity: int                    # Default 1
    unit_price: int                  # Default 0
    total_price: int                 # Default 0
    item_type: str                   # Max 50
    status: str                      # Default 'Pending'
    notes: text
    created_at: datetime
    updated_at: datetime
```

### 4.6.4 Family Models

#### Spouse (`app/models/spouse.py`)

```python
class Spouse(db.Model):
    id: int
    firstname: str                   # Not null, max 100
    lastname: str                    # Not null, max 100
    surname: str                     # Not null, max 100
    phone_num: str                   # Max 20
    email: str                       # Max 120
    date_of_birth: date
    created_at: datetime
    id_number: int                   # Unique
    member_id: int                   # FK to Member
    user_id: int                     # FK to User, nullable
    
    # Relationships
    member: Member
    child: list[Child]
    user_account: User               # uselist=False
    
    # Hybrid Property
    display_email: str               # Returns email or user_account.email
```

#### Child (`app/models/child.py`)

```python
class Child(db.Model):
    id: int
    firstname: str                   # Not null, max 100
    lastname: str                    # Not null, max 100
    surname: str                     # Not null, max 100
    phone_num: str                   # Max 20
    id_number: int
    email: str                       # Max 120
    date_of_birth: date
    created_at: datetime
    spouse_id: int                   # FK to Spouse
    member_id: int                   # FK to Member
    user_id: int                     # FK to User, nullable
    
    # Relationships
    spouse: Spouse
    member: Member
    user_account: User               # uselist=False
    
    # Hybrid Property
    display_email: str               # Returns email or user_account.email
```

### 4.6.5 Utility Models

#### FAQ (`app/models/faq.py`)

```python
class FAQ(db.Model):
    id: int
    question: str                    # Not null, max 255
    answer: text                     # Not null
    category: str                    # Max 100
    created_at: datetime
    updated_at: datetime
    created_by: int                  # FK to User
```

#### Images (`app/image.py`)

```python
class Images(db.Model):
    id: int
    name: str                        # Max 1000
    image: bytes                     # LargeBinary
    user_id: int                     # FK to User
```

#### Payment Enum (`app/models/payments.py`)

```python
class Payment(Enum):
    CASH = 'Ksh'
    MOBILE_MONEY = 'MPESA'
    BANK = 'BANK DEPOSIT'
    NEW = 'NEW'
```

#### AccessLevel Enum (`app/level.py`)

```python
class AccessLevel(Enum):
    DEVEL = 'Developer'
    ADMIN = 'Administrator'
    CHAIRPERSON = 'Chairperson'
    TREASURER = 'Treasurer'
    SECRETARY = 'Secretary'
    WELFARE_OFFICER = 'Welfare Officer'
    USER = 'User'
    
    # Properties
    display_name: str                # Returns enum value
    is_admin: bool                   # DEVEL, CHAIRPERSON, ADMIN
    is_finance: bool                 # DEVEL, CHAIRPERSON, ADMIN, TREASURER
    is_member_admin: bool            # DEVEL, CHAIRPERSON, ADMIN, SECRETARY
    is_welfare: bool                 # DEVEL, CHAIRPERSON, ADMIN, WELFARE_OFFICER
    is_sponsor_admin: bool           # DEVEL, CHAIRPERSON, ADMIN
    level: int                       # Hierarchy level (5 to 1)
```

## 4.7 Blueprint Route Reference

### Authentication (`auth` - no prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET/POST | `/` | `index` | Public |
| GET/POST | `/<role>/login` | `login` | Public |
| GET | `/signup` | `signup` | Public |
| POST | `/signup` | `signup_post` | Public |
| GET | `/logout` | `logout` | @login_required |
| GET/POST | `/forgot-password` | `forgot_password` | Public |

### Main Dashboard (`main` - no prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/` | `index` | @login_required (redirects USER to dashboard) |
| GET | `/member/<id>/image` | `member_image` | @login_required |
| GET | `/profile` | `profile` | @login_required |
| GET/POST | `/upload` | `upload_file` | @login_required |
| GET | `/image` | `get_images` | Public |
| GET | `/avatar` | `avatar` | @login_required |
| GET/POST | `/<id>/new_upload` | `uploadNew` | @login_required |
| POST | `/update_profile` | `update_profile` | @login_required |
| GET/POST | `/edit_profile` | `edit_profile` | @login_required |
| GET/POST | `/change_password` | `change_password` | @login_required |
| GET | `/about` | `about` | Public |
| GET | `/faq` | `faq` | Public |
| GET | `/contact` | `contact` | Public |

### Home (`home` - no prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/overview` | `home` | @login_required |

### Register (`register` - `/register` prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/` | `index` | @login_required |
| GET | `/<id>/` | `deposit` | @login_required |
| GET/POST | `/create` | `create` | @login_required |
| GET/POST | `/<id>/editname` | `edit_name` | @login_required |
| GET/POST | `/<id>/create_spouse/` | `create_spouse` | @login_required |
| GET/POST | `/<id>/create_child/` | `create_child` | @login_required |
| POST | `/<id>/delete/` | `delete` | @login_required (DEVEL/ADMIN) |
| GET/POST | `/<id>/edit` | `edit` | @login_required |
| GET | `/dashboard` | `dashboard` | @login_required |
| GET | `/dashboard/<id>` | `dashboard_member` | @login_required |
| POST | `/<id>/assign_admin` | `assign_admin` | DEVEL/ADMIN |
| POST | `/<id>/assign_user` | `assign_user` | DEVEL/ADMIN |
| POST | `/<id>/assign_role` | `assign_role` | DEVEL/ADMIN |
| GET | `/faq` | `faq_list` | DEVEL/ADMIN |
| GET/POST | `/faq/create` | `faq_create` | DEVEL/ADMIN |
| GET/POST | `/faq/<id>/edit` | `faq_edit` | DEVEL/ADMIN |
| POST | `/faq/<id>/delete` | `faq_delete` | DEVEL/ADMIN |
| GET | `/pending-users` | `pending_users` | DEVEL/ADMIN |
| POST | `/<id>/approve_user` | `approve_user` | DEVEL/ADMIN |
| POST | `/<id>/cancel_user` | `cancel_user` | DEVEL/ADMIN |
| POST | `/<id>/delete_user` | `delete_user` | DEVEL/ADMIN |

### Deposit (`deposit` - `/contribution` prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/` | `index` | @login_required |
| GET | `/<id>/` | `deposit` | Public |
| GET/POST | `/<id>/edit` | `edit_contribution` | TREASURER/WELFARE/ADMIN/DEVEL |
| POST | `/<id>/delete` | `delete_contribution` | ADMIN/DEVEL |
| GET/POST | `/<id>/amount` | `amount` | TREASURER/WELFARE/ADMIN/DEVEL |
| GET | `/api/member/<id>/pending-contributions` | `api_member_pending_contributions` | ADMIN/DEVEL/WELFARE |

### Family (`family` - `/family` prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/` | `index` | @login_required |
| GET | `/<id>/` | `family` | @login_required |
| GET/POST | `/<id>/edit` | `edit` | @login_required |
| GET/POST | `/<id>/create_spouse` | `create_spouse` | @login_required |
| GET/POST | `/<id>/<spouse_id>/create_child` | `create_child` | @login_required |
| POST | `/<id>/<id>/delete` | `delete` (spouse) | @login_required |
| GET/POST | `/<id>/<id>/edit_spouse` | `edit_spouse` | @login_required |
| GET/POST | `/<id>/<spouse_id>/<child_id>/edit_child` | `edit_child` | @login_required |
| GET/POST | `/<id>/<child_id>/edit_child` | `editchild` | @login_required |
| POST | `/<id>/<child_id>/delete_child` | `delete_child` | @login_required |
| POST | `/<id>/delete/` | `delete_family` | @login_required |
| POST | `/<id>/delete_member/` | `delete_member` | @login_required |
| GET | `/birthday` | `contact` | @login_required |

### Community (`community` - `/community` prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/` | `index` | @login_required |
| GET | `/export_csv` | `export_csv` | @login_required |
| GET/POST | `/add_event` | `add_event` | ADMIN/DEVEL |
| POST | `/<id>/delete` | `delete_event` | ADMIN/DEVEL/CHAIRPERSON |
| GET/POST | `/<id>/edit_event` | `edit_event` | ADMIN/DEVEL |
| GET | `/contribute/<tag_name>/` | `contribute` | @login_required |
| GET | `/contribute/<tag_name>/export_csv` | `export_contributions_csv` | @login_required |
| GET | `/<id>/stats` | `event_stats` | @login_required |
| POST | `/<id>/contribute` | `quick_contribute` | @login_required |
| POST | `/<id>/bookmark` | `toggle_bookmark` | @login_required |
| GET | `/events/upcoming` | `upcoming_events` | @login_required |
| POST | `/<id>/delete` | `delete` (contribution) | @login_required |

### Budget (`budget` - `/budget` prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/` | `index` | CHAIRPERSON/ADMIN/DEVEL |
| GET/POST | `/create` | `create` | ADMIN/DEVEL |
| GET | `/<id>` | `view` | CHAIRPERSON/ADMIN/DEVEL |
| GET/POST | `/<id>/edit` | `edit` | ADMIN/DEVEL |
| POST | `/<id>/delete` | `delete` | ADMIN/DEVEL |

### Treasurer (`treasurer` - `/treasurer` prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/` | `index` | TREASURER/ADMIN/DEVEL |
| GET/POST | `/create` | `create` | TREASURER/ADMIN/DEVEL |
| GET | `/<id>` | `view` | TREASURER/ADMIN/DEVEL |
| GET/POST | `/<id>/edit` | `edit` | TREASURER/ADMIN/DEVEL |
| POST | `/<id>/delete` | `delete` | ADMIN/DEVEL |

### Minutes (`minutes` - `/minutes` prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/` | `index` | SECRETARY/CHAIRPERSON/ADMIN/DEVEL |
| GET/POST | `/create` | `create` | SECRETARY/ADMIN/DEVEL |
| GET | `/<id>` | `view` | SECRETARY/CHAIRPERSON/ADMIN/DEVEL |
| GET/POST | `/<id>/edit` | `edit` | SECRETARY/ADMIN/DEVEL |
| POST | `/<id>/delete` | `delete` | ADMIN/DEVEL |

### Requisition (`requisition` - `/requisition` prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/` | `index` | @login_required |
| GET/POST | `/create` | `create` | @login_required |
| GET/POST | `/<id>/edit` | `edit` | @login_required (owner or CHAIRPERSON/ADMIN/DEVEL) |
| POST | `/<id>/delete` | `delete` | CHAIRPERSON/ADMIN/DEVEL |
| POST | `/<id>/status` | `update_status` | CHAIRPERSON/ADMIN/DEVEL |
| GET | `/<id>` | `view` | @login_required (owner or CHAIRPERSON/ADMIN/DEVEL) |

### Sponsor (`sponsor` - `/sponsor` prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/` | `index` | CHAIRPERSON/ADMIN/DEVEL |
| GET/POST | `/create` | `create` | CHAIRPERSON/ADMIN/DEVEL |
| GET | `/<id>` | `view` | CHAIRPERSON/ADMIN/DEVEL |
| GET/POST | `/<id>/edit` | `edit` | CHAIRPERSON/ADMIN/DEVEL |
| POST | `/<id>/delete` | `delete` | CHAIRPERSON/ADMIN/DEVEL |
| GET/POST | `/<id>/items/create` | `create_item` | CHAIRPERSON/ADMIN/DEVEL |
| GET/POST | `/<id>/items/<item_id>/edit` | `edit_item` | CHAIRPERSON/ADMIN/DEVEL |
| POST | `/<id>/items/<item_id>/delete` | `delete_item` | CHAIRPERSON/ADMIN/DEVEL |

### Reports (`reports` - `/reports` prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| GET | `/` | `index` | @login_required |
| GET | `/chart-data` | `chart_data` | @login_required |
| GET | `/<id>/reports` | `reports` | Public |

### Account (`account` - `/account` prefix)

| Method | Route | Function | Permissions |
|--------|-------|----------|-------------|
| Routes defined in `app/account/routes.py` | | | |

## 4.8 Error Responses

All JSON endpoints return standard error format:

```json
{
  "success": false,
  "message": "Error description",
  "error": "ERROR_CODE"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (validation error)
- `401` - Unauthorized (not logged in)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

## 4.9 CSV Export Formats

### Contributions Export (`/contribution/?export=csv`)

```csv
Member,ID Number,Amount,Payment Type,Event,Date
"John Doe Smith",12345678,5000,MPESA,"Annual Fundraiser","January 15, 2024"
```

### Community Events Export (`/community/export_csv`)

```csv
Event Name,Event Date,Details,Total Contributions,Contributors
"Annual Fundraiser","2024-12-25","Year-end fundraising",150000,45
```

### Event Contributions Export (`/community/contribute/<name>/export_csv`)

```csv
Member Name,ID Number,Phone Number,Payment Type,Amount,Date
"John Doe",12345678,"0712345678",MPESA,5000,"2024-01-15"
```

### Reports Export (`/reports/?export=csv`)

```csv
Date,Member,Phone Number,Amount,Type,Event
"2024-01-15","John Doe Smith","0712345678",5000,MPESA,"Annual Fundraiser"
```