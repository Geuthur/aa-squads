from django.db.models.signals import post_save, pre_delete

from allianceauth import hooks

from squads.hooks import get_extension_logger
from squads.models import filters as model

logger = get_extension_logger(__name__)


class HookCache:
    all_hooks = None

    def get_hooks(self):
        if self.all_hooks is None:
            hook_array = set()
            _hooks = hooks.get_hooks("squads_filters")
            for app_hook in _hooks:
                for filter_model in app_hook():
                    if filter_model not in hook_array:
                        hook_array.add(filter_model)
            self.all_hooks = hook_array
        return self.all_hooks


filters = HookCache()


# pylint: disable=broad-exception-caught, unused-argument
def new_filter(sender, instance, created, **kwargs):
    try:
        if created:
            model.SquadFilter.objects.create(filter_object=instance)
        else:
            pass
    except Exception as e:
        logger.error("New filter failed: %s", e)


# pylint: disable=broad-exception-caught, unused-argument
def rem_filter(sender, instance, **kwargs):
    try:
        model.SquadFilter.objects.get(
            object_id=instance.pk, content_type__model=instance.__class__.__name__
        ).delete()
    except Exception as e:
        logger.error("Remove filter failed: %s", e)


for _filter in filters.get_hooks():
    post_save.connect(new_filter, sender=_filter)
    pre_delete.connect(rem_filter, sender=_filter)
