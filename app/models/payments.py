from enum import Enum

class Payment(Enum):
    CASH = 'Ksh'
    MOBILE_MONEY = 'MPESA'
    BANK = 'BANK DEPOSIT'