from django.contrib import admin
from .models import Sheet, Customer, Product, InvoiceMeta


# -----------------------------------------------------
# Inline for Products in SheetAdmin
class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    readonly_fields = ('item_total',)
    fields = ('serial_no', 'item', 'quantity', 'rate', 'item_total', 'warranty', 'checked')


# Inline for InvoiceMeta in SheetAdmin
class InvoiceMetaInline(admin.StackedInline):
    model = InvoiceMeta
    can_delete = False
    readonly_fields = ('subtotal', 'receivable', 'final_balance')
    fieldsets = (
        (None, {
            'fields': (
                'invoice_number',
                'date',
                'customer',
                'terms',
                'note',
                ('subtotal', 'adjustments'),
                ('receivable', 'received', 'final_balance'),
            )
        }),
    )


# Sheet Admin
@admin.register(Sheet)
class SheetAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    inlines = [ProductInline, InvoiceMetaInline]


# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('item', 'sheet', 'quantity', 'rate', 'item_total', 'checked')
    list_filter = ('sheet', 'checked')
    search_fields = ('item', 'serial_no')
    readonly_fields = ('item_total',)


# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at',)


# InvoiceMeta Admin
@admin.register(InvoiceMeta)
class InvoiceMetaAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'sheet', 'customer', 'subtotal', 'receivable', 'received', 'final_balance')
    search_fields = ('invoice_number', 'customer__name', 'sheet__title')
    list_filter = ('date',)
    readonly_fields = ('subtotal', 'receivable', 'final_balance')
