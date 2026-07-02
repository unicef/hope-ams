from ..registry import rule_registry as registry
from .data_changed_after_approval import DataChangedAfterApprovalRule

registry.register(DataChangedAfterApprovalRule)
