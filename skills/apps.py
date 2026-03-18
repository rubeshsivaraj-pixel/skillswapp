from django.apps import AppConfig


class SkillsConfig(AppConfig):
    name = 'skills'

    def ready(self):
        import skills.signals  # noqa: F401
