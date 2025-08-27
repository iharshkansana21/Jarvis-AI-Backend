from django.contrib import admin
from .models import AIHistory

# Register your models here.
@admin.register(AIHistory)
class AIHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'prompt', 'response', 'timestamp')
    search_fields = ('user__username', 'prompt', 'response')
    list_filter = ('timestamp',)