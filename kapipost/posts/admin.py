from django.contrib import admin

from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    # We list the fields that should be displayed in the admin panel
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    # Interface to search through post-text
    search_fields = ('text',)
    # Filtration options
    list_filter = ('pub_date', 'author')
    # Edit options
    list_editable = ('group',)
    empty_value_display = '-empty-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
