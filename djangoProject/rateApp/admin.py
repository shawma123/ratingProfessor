from django.contrib import admin

# Register your models here.
from .models import Student, Professor, Module, Professor_Module, Rate
admin.site.register(Student)
admin.site.register(Professor)
admin.site.register(Module)
admin.site.register(Professor_Module)
admin.site.register(Rate)