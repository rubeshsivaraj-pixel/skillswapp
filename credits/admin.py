from django.contrib import admin
from django.utils.html import format_html
from .models import CreditTransaction, CreditPackage


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'amount_display', 'balance_after', 'description_short', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('User & Transaction', {'fields': ('user', 'transaction_type')}),
        ('Credits', {'fields': ('amount', 'balance_after')}),
        ('Related Object', {'fields': ('related_object_type', 'related_object_id')}),
        ('Details', {'fields': ('description', 'created_at')}),
    )

    def amount_display(self, obj):
        colour = 'green' if obj.amount > 0 else 'red'
        sign = '+' if obj.amount > 0 else ''
        return format_html('<span style="color:{};font-weight:bold;">{}{}</span>', colour, sign, obj.amount)
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'

    def description_short(self, obj):
        if not obj.description:
            return '-'
        return obj.description[:50] + '…' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'


@admin.register(CreditPackage)
class CreditPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'credits', 'bonus_credits', 'total_credits', 'price', 'is_active']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['name']
    readonly_fields = ['created_at']
