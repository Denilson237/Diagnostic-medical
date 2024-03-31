from django.contrib import admin
from medical.models import data,search_user,hopitaux
# Register your models here.

class dataAdmin(admin.ModelAdmin):
    list_display = ('Maladies',"slug", 'Symptomes', 'Traitement', 'Examens',"Similarite","Categorie")
    search_fields = ('Maladies',)
admin.site.register(data, dataAdmin)

class searchAdmin(admin.ModelAdmin):
    list_display = ("search", "auteur","date_creation",)
    #readonly_fields = ("date_creation",)
admin.site.register(search_user, searchAdmin)

class hopitauxAdmin(admin.ModelAdmin):
    list_display = ('Nom',"Biometrie", 'Quartier', 'Localisation', 'Telephone',"categori")
    search_fields = ('Nom',)
admin.site.register(hopitaux, hopitauxAdmin)