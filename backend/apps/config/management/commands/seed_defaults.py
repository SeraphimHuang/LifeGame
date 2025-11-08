from django.core.management.base import BaseCommand
from apps.config.models import AttributeMapping, DropConfig


DEFAULT_MAPPINGS = [
    ("求职-简历投递", dict(learning=0, stamina=0, charisma=0, craft=0, inspiration=0)),
    ("笔试/面试", dict(learning=0.5, stamina=0.0, charisma=0.5, craft=0, inspiration=0)),
    ("学业-上课/作业", dict(learning=1, stamina=0.0, charisma=0, craft=0, inspiration=0.2)),
    ("运动训练", dict(learning=0.0, stamina=1, charisma=0.3, craft=0, inspiration=0.2)),
    ("作息-早睡早起", dict(learning=0, stamina=0.7, charisma=0.1, craft=0, inspiration=0.1)),
    ("家务/做饭", dict(learning=0, stamina=0, charisma=0, craft=1, inspiration=0)),
    ("社交/会友", dict(learning=0, stamina=0, charisma=1, craft=0, inspiration=0)),
    ("创作/写作", dict(learning=0, stamina=0.0, charisma=0, craft=0, inspiration=1)),
]

DEFAULT_BANDS = [
    {"min": 0, "max": 12, "prob": 0.10},
    {"min": 13, "max": 25, "prob": 0.24},
    {"min": 26, "max": 40, "prob": 0.40},
    {"min": 41, "max": 50, "prob": 0.60},
]


class Command(BaseCommand):
    help = "Seed default attribute mappings and drop config"

    def handle(self, *args, **options):
        created = 0
        for label, weights in DEFAULT_MAPPINGS:
            obj, was_created = AttributeMapping.objects.get_or_create(label=label, defaults={"weights": weights})
            if was_created:
                created += 1
        dc, _ = DropConfig.objects.get_or_create(id=1, defaults={"bands": DEFAULT_BANDS})
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} mappings; drop bands set.")) 



