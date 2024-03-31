from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class data(models.Model):
    Maladies = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    Symptomes = models.TextField()
    Traitement = models.TextField()
    Examens = models.TextField()
    Similarite = models.IntegerField(default = 0, null=True, blank=True)
    Categorie = models.CharField(max_length=200,null=True, blank=True)

    def __str__(self):
        return self.Maladies

class search_user(models.Model):
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null = True)
    search = models.TextField()
    date_creation = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.search
    
    class Meta:
        ordering = ['-date_creation']

class hopitaux(models.Model):
    Nom = models.CharField(max_length=400)
    Biometrie = models.CharField(max_length=400)
    Quartier = models.CharField(max_length=400)
    Localisation = models.CharField(max_length=400)
    Telephone = models.CharField(max_length=400)
    categori = models.CharField(max_length=400)

    def __str__(self):
        return self.Nom