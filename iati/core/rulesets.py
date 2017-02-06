"""A module containg a core representation of IATI Rulesets."""


class Ruleset(object):
    """Representation of a Ruleset as defined within the IATI SSOT."""

    pass


class Rule(object):
    """Representation of a Rule contained within a Ruleset.

    Acts as a base class for specific types of Rule that actually do something.
    """

    pass


class NoMoreThanOne(Rule):
    """Representation of a Rule that checks that there is no more than one Element matching a given XPath."""

    pass
