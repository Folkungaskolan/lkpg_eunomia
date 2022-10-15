# coding=utf-8
"""youtube :

Python tricks: All there is to know about Exceptions
https://www.youtube.com/watch?v=b0PAVVchc7c

"""

""":Documentation träd:

https://docs.python.org/3.7/library/exceptions.html
BaseException
 +-- SystemExit
 +-- KeyboardInterrupt
 +-- GeneratorExit
 +-- Exception
      +-- StopIteration
      +-- StopAsyncIteration
      +-- ArithmeticError
      |    +-- FloatingPointError
      |    +-- OverflowError
      |    +-- ZeroDivisionError
      +-- AssertionError
      +-- AttributeError
      +-- BufferError
      +-- EOFError
      +-- ImportError
      |    +-- ModuleNotFoundError
      +-- LookupError
      |    +-- IndexError
      |    +-- KeyError
      +-- MemoryError
      +-- NameError
      |    +-- UnboundLocalError
      +-- OSError
      |    +-- BlockingIOError
      |    +-- ChildProcessError
      |    +-- ConnectionError
      |    |    +-- BrokenPipeError
      |    |    +-- ConnectionAbortedError
      |    |    +-- ConnectionRefusedError
      |    |    +-- ConnectionResetError
      |    +-- FileExistsError
      |    +-- FileNotFoundError
      |    +-- InterruptedError
      |    +-- IsADirectoryError
      |    +-- NotADirectoryError
      |    +-- PermissionError
      |    +-- ProcessLookupError
      |    +-- TimeoutError
      +-- ReferenceError
      +-- RuntimeError
      |    +-- NotImplementedError
      |    +-- RecursionError
      +-- SyntaxError
      |    +-- IndentationError
      |         +-- TabError
      +-- SystemError
      +-- TypeError
      +-- ValueError
      |    +-- UnicodeError
      |         +-- UnicodeDecodeError
      |         +-- UnicodeEncodeError
      |         +-- UnicodeTranslateError
      +-- Warning
           +-- DeprecationWarning
           +-- PendingDeprecationWarning
           +-- RuntimeWarning
           +-- SyntaxWarning
           +-- UserWarning
           +-- FutureWarning
           +-- ImportWarning
           +-- UnicodeWarning
           +-- BytesWarning
           +-- ResourceWarning

"""

""":användbara bas exceptions som grund
ValueError
exception ValueError¶
Raised when an operation or function receives an argument that has the right type but an inappropriate value,
and the situation is not described by a more precise exception such as IndexError.

exception ConnectionError
A base class for connection-related issues.

exception TypeError
Raised when an operation or function is applied to an object of inappropriate type. 
The associated value is a string giving details about the type mismatch.

grund bult Exception

"""


class AktivitetNotFoundError(Exception):    pass


class AnkHasNoStaffError(Exception):    pass


class DelaEnlElevAntal_pERROR(Exception):    pass


class DelaEnligtElevAntalError(Exception):    pass


class FASIT_CBA_Agent_Not_AvaliableError(Exception):    pass


class GearAlreadyExistsError(Exception):    pass


class GearMarkedForDisposalError(Exception):    pass


class GearNotAssignedToAUserError(Exception):    pass


class GearNotFoundError(Exception):    pass


class GearNotFoundInFASIT_CBAError(Exception):    pass


class GearPropertySetError(Exception):    pass


class GearReturnedToLKDATA(Exception):    pass


class GearUnknownGearIDFormat(Exception):    pass


class LogInFailure(Exception):    pass


class ImDoesNotExistsError(Exception):    pass


class InformationMissingError(Exception):    pass


class IngenAnknytningHittadError(Exception):    pass


class InvalidArgumentsError(Exception):    pass


class Lindesk_ID_NotFoundError(Exception):    pass


class NameToShortError(ValueError):    pass


class NoAssignedUserError(Exception):    pass


class NoDataError(Exception):    pass


class NoInfoFoundError(Exception):    pass


class NoLinkToAssignAStudentFound(Exception):    pass


class NoneUniqeResultFoundError(Exception):    pass


class NoRepairIdFoundError(Exception):    pass


class NoStatusSetError(Exception):    pass


class NoUserFoundError(Exception):    pass


class NoPasswordFoundError(Exception):    pass


class PersonNummerAlreadyExistsError(Exception):    pass


class PersonummerNotFoundError(Exception):    pass


class RetryHTMLError(Exception):    pass


class TjansteFordelningSaknasError(Exception):    pass


class UserAlreadyExistsError(Exception):    pass


class DBUnableToCrateUser(Exception):    pass
