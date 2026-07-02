import enum
import logging

from admin_extra_buttons.mixins import ExtraButtonsMixin
from adminfilters.mixin import AdminAutoCompleteSearchMixin, AdminFiltersMixin

logger = logging.getLogger(__name__)


class ButtonColor(enum.Enum):
    LINK = "link"
    ACTION = "action"
    LOCK = "lock"
    UNLOCK = "unlock"


class BaseAdmin[T](AdminFiltersMixin, AdminAutoCompleteSearchMixin, ExtraButtonsMixin):
    pass
