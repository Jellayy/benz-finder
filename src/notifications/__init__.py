from .discord import DiscordNotifier
# Import other notifiers here as you add them

NOTIFIER_MAP = {
    'discord': DiscordNotifier,
    # Add other notifiers here as you implement them
}

def get_notifier(notification_config):
    notifier_type = notification_config['type']
    if notifier_type not in NOTIFIER_MAP:
        raise ValueError(f"Unsupported notification type: {notifier_type}")
    return NOTIFIER_MAP[notifier_type](notification_config)