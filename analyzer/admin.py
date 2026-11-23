from django.contrib import admin
from .models import SkillDependency, CareerRole, RequiredSkill

admin.site.register(SkillDependency)
admin.site.register(CareerRole)
admin.site.register(RequiredSkill)
