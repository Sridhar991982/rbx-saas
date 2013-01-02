from actstream.managers import ActionManager, stream


class PublicActivityManager(ActionManager):

    @stream
    def public_activity(self, object, enquirer):
        return object.actor_actions.filter()
