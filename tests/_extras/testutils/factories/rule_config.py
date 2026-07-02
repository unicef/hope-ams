from hope_ams.detection.rules.prevention.pregnant_child import PregnantChildRule
from hope_ams.models import RuleConfig

from .base import AutoRegisterModelFactory


class RuleConfigFactory(AutoRegisterModelFactory):
    class Meta:
        model = RuleConfig

    name = "test-config"
    rule = PregnantChildRule
    enabled = True
    config = {}
    phase = RuleConfig.Phase.BOTH
