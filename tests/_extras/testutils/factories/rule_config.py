from hope_ams.detection.rules.pregnancy_validity import PregnancyValidityRule
from hope_ams.models import RuleConfig

from .base import AutoRegisterModelFactory


class RuleConfigFactory(AutoRegisterModelFactory):
    class Meta:
        model = RuleConfig

    name = "test-config"
    rule = PregnancyValidityRule
    enabled = True
    config = {}
    phase = "prevention"
