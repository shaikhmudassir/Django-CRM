import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")
import django
django.setup()

from leads.models import Lead
from contacts.models import Contact
from chat.models import Messages, WhatsappContacts

print(Lead.objects.all().delete())
print(Contact.objects.all().delete())
print(Messages.objects.all().delete())
print(WhatsappContacts.objects.all().delete())

print("Deleted all records")

# rm -r accounts/migrations/
# rm -r leads/migrations/
# rm -r contacts/migrations/
# rm -r chat/migrations/
# rm -r opportunity/migrations/
# rm -r tasks/migrations/
# rm -r events/migrations/
# rm -r teams/migrations/
# rm -r cases/migrations/
# rm -r common/migrations/
# rm -r planner/migrations/
# rm -r invoices/migrations/
# rm -r emails/migrations/
# rm -r cms/migrations/
# rm -r accounts/__pycache__/
# rm -r leads/__pycache__/
# rm -r contacts/__pycache__/
# rm -r chat/__pycache__/
# rm -r opportunity/__pycache__/
# rm -r tasks/__pycache__/
# rm -r events/__pycache__/
# rm -r teams/__pycache__/
# rm -r cases/__pycache__/
# rm -r common/__pycache__/
# rm -r planner/__pycache__/
# rm -r invoices/__pycache__/
# rm -r emails/__pycache__/
# rm -r cms/__pycache__/

# # python manage.py makemigrations accounts leads contacts chat opportunity tasks events teams cases common planner invoices emails cms
# # python manage.py migrate


'''
{
    "title": "lead 1",
    "first_name": "Zubair",
    "last_name": "Khan",
    "phone": "+917774019249",
    "email": "zubair123@gmail.com",
    "probability": "0"
}
'''
# I = 649
# D = 5506