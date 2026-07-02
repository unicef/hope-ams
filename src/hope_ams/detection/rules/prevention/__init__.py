from ..registry import rule_registry as registry
from .llm_sanity_check import LLMSanityCheckRule
from .pregnant_child import PregnantChildRule
from .too_young_pregnant import TooYoungPregnantRule

registry.register(PregnantChildRule)
registry.register(LLMSanityCheckRule)
registry.register(TooYoungPregnantRule)
