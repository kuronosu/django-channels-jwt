from django.contrib import admin

from .models import UserChannelSesion


# Register your models here.
class CurrentUsersAdmin(admin.ModelAdmin):
    fields = ('user', 'channel')
    readonly_fields = ('connected_at',)
    list_display = ('id', 'user', 'connected_at', 'group', 'channel')
    ordering = ('-connected_at',)


admin.site.register(UserChannelSesion, CurrentUsersAdmin)
