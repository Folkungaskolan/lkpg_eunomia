""" hjälp funktion för att ta bot () runt sträng"""


def strips_parentheses(string: str) -> str:
    """ hjälp funktion för att ta bot () runt sträng"""
    return string.replace("(", "").replace(")", "")
