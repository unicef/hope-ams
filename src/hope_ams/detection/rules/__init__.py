from hope_ams.detection.rules.registry import rule_registry as registry

from .pregnancy_validity import PregnancyValidityRule

registry.register(PregnancyValidityRule)
