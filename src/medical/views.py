from pathlib import Path
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg') 
import seaborn as sns
from medical.utilitaires import *
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from wordcloud import WordCloud
from medical.models import data, search_user,hopitaux


def error_404(request, exception):
    return render(request, '404.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('searchPreview')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')


def user_logout(request):
    logout(request)
    return redirect('base')

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        try:
            if not (username.strip() and first_name.strip() and email.strip() and password.strip() and password_confirm.strip()):
                messages.error(request, 'All fields are required.')
                return render(request, 'auth/register.html')
        except:
            messages.error(request, 'Erreur: Veuillez remplir correctement le formulaire') 
            return render(request, 'auth/register.html')
        
        if len(username)>20:
            messages.add_message(request,messages.ERROR, 'Please the username must not be more than 20 character.')
            return render(request,'auth/register.html',{'messages':messages.get_messages(request)})
        if len(password)<8:
            messages.add_message(request,messages.ERROR, 'Votre mot de passe doit avoir au moins 8 characteres')
            return render(request, 'auth/register.html',{'messages':messages.get_messages(request)})
        if len(username)<4:
            messages.add_message(request,messages.ERROR, 'Please the username must be at leat 5 characters.')
            return render(request,'auth/register.html',{'messages':messages.get_messages(request)})
        if not username.isalnum():
            messages.add_message(request,messages.ERROR, 'username must be alphanumeric')
            return render(request,'auth/register.html',{'messages':messages.get_messages(request)})

        if password == password_confirm:
            if not User.objects.filter(username=username).exists():
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name)
                    user.save()
                    login(request, user)
                    messages.success(request, 'Account created successfully.')
                    return redirect('searchPreview')
                else:
                    messages.error(request, 'Email already exists.')
            else:
                messages.error(request, 'Username already exists.')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'auth/register.html')


def reset_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')
        print(new_password,new_password_confirm)

        if len(new_password)<8:
            messages.add_message(request,messages.ERROR, 'Votre mot de passe doit avoir au moins 8 characteres')
            return render(request, 'auth/reset_password.html',{'messages':messages.get_messages(request)})
        
        try:
            if not (username.strip() and first_name.strip() and email.strip() and new_password.strip() and new_password_confirm.strip()):
                messages.error(request, 'All fields are required.')
                return render(request, 'auth/reset_password.html')
        except:
            messages.error(request, 'Erreur: Veuillez remplir correctement le formulaire') 
            return render(request, 'auth/reset_password.html')
        
        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            messages.error(request, 'No user found with that username and email combination.')
            return render(request, 'auth/reset_password.html')

        if user.first_name != first_name:
            messages.error(request, 'Invalid first name.')
            return render(request, 'auth/reset_password.html')

        if new_password != new_password_confirm:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'auth/reset_password.html')

        try:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect("login")
        except:
            messages.error(request, 'veuillez remplir les champ comme il se doit')

    return render(request, 'auth/reset_password.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')
            
        if len(new_password)<8:
            messages.add_message(request,messages.ERROR, 'Votre mot de passe doit avoir au moins 8 characteres')
            return render(request, 'auth/change_passeWord.html',{'messages':messages.get_messages(request)})
        
        try:
            if not (old_password.strip() and new_password.strip() and new_password_confirm.strip()):
                messages.error(request, 'All fields are required.')
                return render(request, 'auth/change_passeWord.html')
        except :
            messages.error(request, 'Erreur: Veuillez remplir correctement le formulaire') 
            return render(request, 'auth/change_passeWord.html')
        
        if user.check_password(old_password):
            if new_password == new_password_confirm:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                logout(request)
                return redirect('validation')
            else:
                messages.error(request, 'New passwords do not match.')
        else:
            messages.error(request, 'Invalid old password.')
    return render(request, 'auth/change_passeWord.html')


@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')
        new_first_name = request.POST.get('first_name')
            
        try:
            if not (new_username.strip() and new_email.strip() and new_first_name.strip()):
                messages.error(request, 'All fields are required.')
                return render(request, 'auth/update_profil.html')
        except:
            messages.error(request, 'Erreur: Veuillez remplir correctement le formulaire') 
            return render(request, 'auth/update_profil.html')
          
        if new_username != user.username and not User.objects.filter(username=new_username).exists():
            user.username = new_username
            user.first_name = new_first_name
            user.email = new_email
            user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('validation')
        else:
            messages.error(request, 'Username already exists or is the same as the current one.')
    return render(request, "auth/update_profil.html")


@login_required
def delete(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if request.user.check_password(password):
            request.user.delete()
            return redirect('base')
        else:
            messages.error(request, 'Le mot de passe est incorrect. Veuillez réessayer.')
            return redirect('delete')
    return render(request, 'auth/delete.html')


def base(request):
    return render(request, "navbar.html")

def stats(request):

     # Premier graphique
    def Symptomes_les_plus_repandus(name = "Symptomes_les_plus_repandus.png"):
        Symptomes = df.set_index('Maladies').Symptomes.str.upper().str.split(',', expand = True).stack().reset_index(level = 1, drop = True)
        plt.figure(figsize = (16,10))
        sns.countplot(y = Symptomes, order = Symptomes.value_counts().index[:15], palette = 'cool')
        plt.title("Les 15 Symptomes les plus répandus", fontsize = 20)
        plt.ylabel('Symptomes',fontsize = 16)
        plt.xlabel('Nombre de maladies', fontsize = 16)
        plt.savefig(f'theme/static/images/{name}', dpi=300)
        plt.close()
        return Symptomes

    # Deuxième graphique
    def Maladies_ayant_le_plus_de_symptomes(Symptomes):
        plt.figure(figsize = (16,10))
        Synptomes = pd.DataFrame(Symptomes)
        Synptomes.columns=["Synptomes"]
        Synptomes = Synptomes.reset_index()
        Synptome = Synptomes.set_index("Synptomes")
        maladie = Synptome["Maladies"].value_counts()[:15]
        maladie.plot.pie(autopct = '%1.1f%%', shadow = False,cmap = 'cool', figsize = (16,10))
        plt.title('Maladies ayant le plus de symptomes', fontsize = 16)
        plt.savefig('theme/static/images/Maladies_ayant_le_plus_de_symptomes.png', dpi=300)
        plt.close()
        return Synptomes

    # Troisième graphique
    def Maladies_ayant_les_15_symptomes_les_plus_repandus(Synptomes):
        plt.figure(figsize = (16,10))
        symptomes_repandu = Synptomes[(Synptomes['Synptomes']=="FATIGUE")|(Synptomes['Synptomes']=="FIÈVRE")
                        |(Synptomes['Synptomes']=="PERTE DE POIDS INEXPLIQUÉE")|(Synptomes['Synptomes']=="ESSOUFFLEMENT")
                        |(Synptomes['Synptomes']=="MAUX DE TÊTE")|(Synptomes['Synptomes']=="DOULEURS ABDOMINALES")
                        |(Synptomes['Synptomes']=="DOULEUR PENDANT LES RAPPORTS SEXUELS")|(Synptomes['Synptomes']=="DOULEURS MUSCULAIRES")
                        |(Synptomes['Synptomes']=="TOUX PERSISTANTE")|(Synptomes['Synptomes']=="GONFLEMENT DES GANGLIONS LYMPHATIQUES")]
        maladie_symptomes_repandu = symptomes_repandu["Maladies"].value_counts().head(15)
        maladie_symptomes_repandu.plot.pie(autopct = '%1.1f%%', shadow = False,cmap = 'cool', figsize = (16,10))
        plt.title('Les 15 Maladies ayant les 10 symptomes les plus repandus', fontsize = 16)
        plt.savefig('theme/static/images/Maladies_ayant_les_15_symptomes_les_plus_repandus.png', dpi=300)
        plt.close()

    # Quatrieme graphique
    def Nuage_des_mots_present_dans_nos_symptomes(name = "Nuage_des_mots_present_dans_nos_symptomes.png"):
        df["Symptomes_lem_token"] = df["Symptomes"].apply(lambda x: Clean(x))
        textData = df["Symptomes_lem_token"].apply(lambda x: " ".join(x))
        textData = " ".join(textData)
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(textData)

        plt.figure(figsize = (16, 10), facecolor = None) 
        plt.imshow(wordcloud) 
        plt.axis("off") 
        plt.tight_layout(pad = 0) 
        plt.title('Nuage des mots present dans nos symptomes', fontsize = 25)
        # Exporter le graphique en tant qu'image pnj
        plt.savefig(f'theme/static/images/{name}', dpi=500);
        plt.close()

    def statuser():
        
        df["Symptomes"] = df["Symptomes"].apply(lambda x: Clean(x))
        df["Symptomes"] = df["Symptomes"].apply(lambda x: ",".join(x))
        Symptomes_les_plus_repandus(name="Symptomes_les_plus_repandus_search.png")
        Nuage_des_mots_present_dans_nos_symptomes(name="Nuage_des_mots_present_dans_nos_symptomes_search.png")


    if request.method == 'GET':
        param = request.GET.get('param')
    
        if param == "1" :
            items = data.objects.all()
                # Convertir les données en un dictionnaire
            datar = {'Maladies': [], 'Symptomes': [] }

            for instance in items:
                datar['Maladies'].append(instance.Maladies)
                datar['Symptomes'].append(instance.Symptomes)

            df = pd.DataFrame(datar)

            Symptomes = Symptomes_les_plus_repandus()
            Synptomes = Maladies_ayant_le_plus_de_symptomes(Symptomes)
            Maladies_ayant_les_15_symptomes_les_plus_repandus(Synptomes)
            Nuage_des_mots_present_dans_nos_symptomes()
            return render(request, "stats.html")

        elif param == "2":
            auteur = request.user
            items = search_user.objects.filter(auteur=auteur)
            datar = {'Maladies': [], 'Symptomes': [] }

            for instance in items:
                datar['Maladies'].append(instance.auteur)
                datar['Symptomes'].append(instance.search)

            df = pd.DataFrame(datar)
            statuser()
            return render(request, "statUSer.html")
        
    else:
        redirect("base")
  

def searchPreview(request):
    return render(request, "searchPreview.html")

@login_required
def statReseach(request):

    items = hopitaux.objects.all()

    if request.method == 'POST':
        search_query = request.POST.get('param')
        if search_query is not None and len(search_query) > 2:
            items = traitement_hop(search_query)
            context = {
                    "items": items,
                }

            return render(request, "statReseach.html", context)
    else:
        context = {
                    "items": items,
                }
        return render(request, "statReseach.html", context)
                                       

def detailMaladie(request, slug):
    datas = get_object_or_404(data, slug = slug)
    maladies = datas.Maladies.split("(")[:1]
    symptomes = datas.Symptomes.split(",")
    examens = datas.Examens.split(",")
    traitements = datas.Traitement.split(",")

    context = {
        "symptomes" : symptomes,
        "examens" : examens,
        "traitements" : traitements,
        'datas': datas,
        "maladies" : maladies
    }
    return render(request, 'detailMaladie.html', context)


def previewNotModal(request , err = ""):

    auteur = request.user
    searReturn = search_user.objects.filter(auteur=auteur).order_by("-date_creation")
    context = {
             "search_query" : searReturn,
             "err" : err
            }

    return render(request, "previewNotModal.html", context)

def validation(request):
    return render(request, "auth/validation.html")

@login_required
def search(request):
    if request.method == 'POST':
        if 'search_query' in request.POST:
            search_query = request.POST.get('search_query', '')
            
            if search_query is not None and len(search_query) > 5:
                auteur = request.user
                mon_objet = search_user(auteur=auteur, search=search_query)
                mon_objet.save()

                searReturn = search_user.objects.filter(auteur=auteur).order_by("-date_creation")
                items = traitement(search_query)
                count = len(items)

                context = {
                    "items": items,
                    "search_query": searReturn,
                    "count" : count
                }

                return render(request, "search.html", context)
            else:
                return previewNotModal(request, err = "Veuiileez entrer au moins 5 characteres avant d'éffectuer une rechercche ...")
        
        elif 'search_query2' in request.POST:
            search_query = request.POST.get('search_query2', '')
            
            if search_query is not None and len(search_query) > 5:
                auteur = request.user
                searReturn = search_user.objects.filter(auteur=auteur).order_by("-date_creation")
                items = traitement(search_query)
                count = len(items)

                context = {
                    "items": items,
                    "search_query": searReturn,
                    "count" : count
                }

                return render(request, "search.html", context)
        
    return previewNotModal(request)
        


# caharger les donnees dans la base de donnees.
'''df = pd.read_csv(Path(__file__).resolve().parent/"dataset.csv")
data.objects.all().delete()
for index, row in df.iterrows():
    data.objects.create(Maladies=row['Maladies'], slug=row['slug'], Symptomes=row["Symptomes"], Traitement=row["Traitement"], Examens=row["Examens"] )'''
#search_user.objects.all().delete()

'''df = pd.read_csv(Path(__file__).resolve().parent/"hopitaux.csv")
hopitaux.objects.all().delete()
for index, row in df.iterrows():
    hopitaux.objects.create(Nom=row['Nom'], Biometrie=row['Biométrie'], Quartier=row["Quartier"],categori=row["categorie"], Localisation=row["Localisation exacte"], Telephone=row["Téléphone"] )'''
