import factory

from hope_ams.detection.rules.pregnancy_validity import PregnancyValidityRule
from hope_ams.models import ProgrammeRuleConfiguration
from hope_ams.models.choices import Phase

from .base import AutoRegisterModelFactory
from .programme import ProgrammeFactory


class ProgrammeRuleConfigurationFactory(AutoRegisterModelFactory):
    class Meta:
        model = ProgrammeRuleConfiguration

    name = "test-programme-config"
    rule = PregnancyValidityRule
    enabled = True
    config = {}
    phase = Phase.PREVENTION
    programme = factory.SubFactory(ProgrammeFactory)
