from django.apps import AppConfig


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self) -> None:
        import chat.signals
#     def ready(self, *args, **kwargs):
#         from django.db.models.signals import post_save
#         from chat.signals import createOpportunity
        
#         lead = self.get_model('leads.Lead')
#         post_save.connect(createOpportunity, sender=lead)