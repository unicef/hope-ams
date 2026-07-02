import factory

from hope_ams.detection.rules.prevention.pregnant_child import PregnantChildRule
from hope_ams.models import ProgrammeRuleConfiguration
from hope_ams.models.choices import CommonPhase

from .base import AutoRegisterModelFactory
from .programme import ProgrammeFactory


class ProgrammeRuleConfigurationFactory(AutoRegisterModelFactory):
    class Meta:
        model = ProgrammeRuleConfiguration

    name = "test-programme-config"
    rule = PregnantChildRule
    enabled = True
    config = {}
    phase = CommonPhase.BOTH
    programme = factory.SubFactory(ProgrammeFactory)
