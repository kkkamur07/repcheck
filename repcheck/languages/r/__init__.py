"""R language checker and dependency resolver."""

from repcheck.languages.r.checker import RScriptChecker
from repcheck.languages.r.resolver import RScriptOrderResolver

__all__ = ['RScriptChecker', 'RScriptOrderResolver']