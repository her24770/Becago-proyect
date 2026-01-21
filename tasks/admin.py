from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
import pandas as pd

from .models import Task, Inscripcion

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ()

admin.site.register(Task, TaskAdmin)
admin.site.register(Inscripcion, TaskAdmin)

def obtener_horas_excel(username):
    try:
        df = pd.read_excel('./Horas_Beca.xlsx')
        resultado = df[df['Usuario'].str.strip().str.lower() == username.strip().lower()]
        if not resultado.empty:
            return int(resultado['Horas Beca'].values[0])
    except Exception as e:
        return "Error"
    return "No registradas"

class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('horas_beca',)

    def horas_beca(self, obj):
        return obtener_horas_excel(obj.username)
    horas_beca.short_description = "Horas de Beca"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
