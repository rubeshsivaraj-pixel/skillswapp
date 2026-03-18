from django.contrib import admin
from .models import FriendRequest, Friendship


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username')
    actions = ['accept_selected']

    @admin.action(description='Accept selected requests')
    def accept_selected(self, request, queryset):
        from .models import Friendship
        for freq in queryset.filter(status='PENDING'):
            freq.status = 'ACCEPTED'
            freq.save()
            u1, u2 = (freq.sender, freq.receiver) if freq.sender.pk < freq.receiver.pk else (freq.receiver, freq.sender)
            Friendship.objects.get_or_create(user1=u1, user2=u2)


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at')
    search_fields = ('user1__username', 'user2__username')
    readonly_fields = ('created_at',)
