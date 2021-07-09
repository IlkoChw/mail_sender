from django.contrib import admin


# класс для фильтрации и отображения объектов, созданных конкретным юзером
class FilterUserAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def get_queryset(self, request):
        qs = super(FilterUserAdmin, self).get_queryset(request)
        return qs.filter(_created_by=request.user)
