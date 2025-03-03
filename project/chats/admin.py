from click import Group
from django.contrib import admin
from .models import Connection, Message, User


admin.site.site_title = 'CHATS NELO'
admin.site.site_header = 'Nelo Api,s'
admin.site.register(User)
admin.site.register(Connection)

admin.site.register(Message)

# Register your models here.
