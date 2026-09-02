from enum import Enum

class AccessLevel(Enum):
    DEVEL = 'Developer'
    ADMIN = 'Administrator'
    CHAIRPERSON = 'Chairperson'
    TREASURER = 'Treasurer'
    SECRETARY = 'Secretary'
    WELFARE_OFFICER = 'Welfare Officer'
    USER = 'User'

    @property
    def display_name(self):
        return self.value

    @property
    def is_admin(self):
        return self in (AccessLevel.DEVEL, AccessLevel.CHAIRPERSON, AccessLevel.ADMIN)

    @property
    def is_finance(self):
        return self in (AccessLevel.DEVEL, AccessLevel.CHAIRPERSON, AccessLevel.ADMIN, AccessLevel.TREASURER)

    @property
    def is_member_admin(self):
        return self in (AccessLevel.DEVEL, AccessLevel.CHAIRPERSON, AccessLevel.ADMIN, AccessLevel.SECRETARY)

    @property
    def is_welfare(self):
        return self in (AccessLevel.DEVEL, AccessLevel.CHAIRPERSON, AccessLevel.ADMIN, AccessLevel.WELFARE_OFFICER)

    @property
    def is_sponsor_admin(self):
        return self in (AccessLevel.DEVEL, AccessLevel.CHAIRPERSON, AccessLevel.ADMIN)

    @property
    def level(self):
        hierarchy = {
            AccessLevel.DEVEL: 5,
            AccessLevel.CHAIRPERSON: 4,
            AccessLevel.ADMIN: 4,
            AccessLevel.TREASURER: 3,
            AccessLevel.SECRETARY: 3,
            AccessLevel.WELFARE_OFFICER: 3,
            AccessLevel.USER: 1,
        }
        return hierarchy.get(self, 0)