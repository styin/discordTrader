class MemberNotExistException(Exception):
    """Raised when the member could not be found in our database"""
    pass

class TickerNotExistException(Exception):
    """Raised when the ticker provided was not found"""
    pass

class TickerNotSupportedException(Exception):
    """Raised when the ticker provided is not yet supported"""
    pass

class InsufficientBalanceException(Exception):
    """Raised when the member has insufficient balance"""
    pass

class InsufficientHoldingsException(Exception):
    """Raised when a member's holdings are insufficient to complete an action"""
    pass

class ConnectionException(Exception):
    """Raised when a connection to finance.yahoo.com could not be established"""
    pass
