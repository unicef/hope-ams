import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import country_workspace
from country_workspace.config import env
from country_workspace.security.utils import setup_workspace_group
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management import BaseCommand, call_command
from django.core.validators import validate_email
from django.utils.text import slugify

from strategy_field.utils import fqn

from hope_ams.detection.rules.registry import rule_registry
from hope_ams.models import Office, RuleConfig

if TYPE_CHECKING:
    from argparse import ArgumentParser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def add_arguments(self, parser: "ArgumentParser") -> None:
        parser.add_argument(
            "--with-checks",
            action="store_true",
            dest="checks",
            default=False,
            help="Run checks",
        )
        parser.add_argument(
            "--no-migrate",
            action="store_false",
            dest="migrate",
            default=True,
            help="Do not run migrations",
        )
        parser.add_argument(
            "--prompt",
            action="store_true",
            dest="prompt",
            default=False,
            help="Let ask for confirmation",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            dest="debug",
            default=False,
            help="debug mode",
        )
        parser.add_argument(
            "--no-static",
            action="store_false",
            dest="static",
            default=True,
            help="Do not run collectstatic",
        )

        parser.add_argument(
            "--sync",
            action="store_true",
            dest="sync_with_hope",
            default=False,
            help="Run HOPE synchronisation",
        )

        parser.add_argument(
            "--admin-email",
            action="store",
            dest="admin_email",
            default="",
            help="Admin email",
        )
        parser.add_argument(
            "--admin-password",
            action="store",
            dest="admin_password",
            default="",
            help="Admin password",
        )

    def get_options(self, options: dict[str, Any]) -> None:
        self.verbosity = options["verbosity"]
        self.run_check = options["checks"]
        self.prompt = not options["prompt"]
        self.static = options["static"]
        self.migrate = options["migrate"]
        self.debug = options["debug"]
        self.sync_with_hope = options["sync_with_hope"]

        self.admin_email = str(options["admin_email"] or env("ADMIN_EMAIL", ""))
        self.admin_password = str(options["admin_password"] or env("ADMIN_PASSWORD", ""))

    def halt(self, e: Exception) -> None:  # pragma: no cover
        self.stdout.write(str(e), style_func=self.style.ERROR)
        self.stdout.write("\n\n***", style_func=self.style.ERROR)
        self.stdout.write("SYSTEM HALTED", style_func=self.style.ERROR)
        self.stdout.write("Unable to start...", style_func=self.style.ERROR)
        if self.debug:
            raise e

        sys.exit(1)

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: C901, PLR0915, PLR0912

        self.get_options(options)
        if self.verbosity >= 1:
            echo = self.stdout.write
        else:

            def echo(*a: Any, **kw: Any) -> None:
                return None

        try:
            extra = {
                "no_input": not self.prompt,
                "verbosity": self.verbosity - 1,
                "stdout": self.stdout,
            }
            echo(
                f"Running upgrade of version {country_workspace.VERSION}",
                style_func=self.style.WARNING,
            )

            if self.run_check:
                call_command("check", deploy=True, verbosity=self.verbosity - 1)
            if self.static:
                static_root = Path(env("STATIC_ROOT"))
                echo(f"Run collectstatic to: '{static_root}' - '{static_root.absolute()}")
                if not static_root.exists():
                    static_root.mkdir(parents=True)
                call_command("collectstatic", **extra)

            if self.migrate:
                echo("Run migrations")
                call_command("migrate", **extra)
                call_command("create_extra_permissions")

            echo("Remove stale contenttypes")
            call_command("remove_stale_contenttypes", **extra)
            if self.sync_with_hope:
                echo("Run HOPE synchronisation")
                call_command("sync", **extra)

            if self.admin_email:
                if User.objects.filter(email=self.admin_email).exists():
                    echo(
                        f"User {self.admin_email} found, skip creation",
                        style_func=self.style.WARNING,
                    )
                else:
                    echo("Creating superuser")
                    validate_email(self.admin_email)
                    os.environ["DJANGO_SUPERUSER_USERNAME"] = self.admin_email
                    os.environ["DJANGO_SUPERUSER_EMAIL"] = self.admin_email
                    os.environ["DJANGO_SUPERUSER_PASSWORD"] = self.admin_password
                    call_command(
                        "createsuperuser",
                        email=self.admin_email,
                        username=self.admin_email,
                        verbosity=self.verbosity - 1,
                        interactive=False,
                    )

            echo("Setup base security")
            setup_workspace_group()
            # This creates the main office using an env var or default
            tenant_hq = env("TENANT_HQ", "HQ Office")
            Office.objects.get_or_create(
                slug=slugify(tenant_hq),
                name=tenant_hq,
            )
            call_command("upgradescripts", ["apply"])

            echo("Seed RuleConfig entries for registered rules")
            for rule_cls in rule_registry:
                rule_fqn = fqn(rule_cls)
                if not RuleConfig.objects.filter(rule=rule_fqn).exists():
                    RuleConfig.objects.create(
                        name=rule_cls.verbose_name or rule_cls.name,
                        rule=rule_cls,
                        enabled=True,
                        config=rule_cls.default_config,
                        phase=rule_cls.phase,
                    )
                    echo(f"  Created RuleConfig for {rule_cls.verbose_name or rule_cls.name}")

            echo("Upgrade completed", style_func=self.style.SUCCESS)
        except ValidationError as e:  # pragma: no cover
            self.halt(Exception("\n- ".join(["Wrong argument(s):", *e.messages])))
        except Exception as e:  # pragma: no cover
            self.stdout.write(str(e), style_func=self.style.ERROR)
            logger.exception(e)
            self.halt(e)
