import numpy as np
import re
from nltk.tokenize import word_tokenize
from unidecode import unidecode
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from medical.models import data, search_user,hopitaux
import pandas as pd
from django.contrib.auth.models import User


# netoyage de donnees
stop_words = stopwords.words('french')
ps = PorterStemmer()

#graphaque data cleaning
def Clean(text):
            
    new_stopwords =["facilement","tres","pendant"]

    stop_words.extend(new_stopwords)
            # Supprimer des ponctuations
    text = re.sub("[^\w\s]", " ", text)
            
    text = ' '.join([word.lower() for word in word_tokenize(text) if word.isalnum() and word.lower() not in stop_words])
    
            # supprimer les chiffres
    text = re.sub("\d", "", text)

            #text = [remove_s(word) for word in text]
    text = list(set(text.split()))
    return text

# PRETRAITEMENT DES DONNEES
def Cleaning(text):
            
    new_stopwords =["facilement","tres","pendant"]

    stop_words.extend(new_stopwords)
    
    def remove_s(word):
        if word.endswith('s'):
            return word[:-1]
        if word.endswith('ment'):
            return word[:-4]
        else:
            return word

    liste2 = ["abdomin ","abdomen","abdominal"]
    liste1 = ["douleur","mal"]

            # Supprimer des ponctuations
    text = re.sub("[^\w\s]", " ", text)
            
    text = ' '.join([ps.stem(unidecode(word.lower())) for word in word_tokenize(text) if word.isalnum() and word.lower() not in stop_words])

            # supprimer les chiffres
    text = re.sub("\d", "", text)

            #text = [remove_s(word) for word in text]

    text = text.replace("ee ","e ")
    text = text.replace("cutane","peau")

    for i in liste2:
        text = text.replace(i,"ventre ")

    text = list(set(text.split()))

    text = ' '.join([remove_s(word) for word in text])

    for i in liste1:
        text = text.replace(i,"maux")

    text = text.replace(" e "," ")
    return text


# DATASET DE SORTIES
def Resultats(df, val):
        
        query = val

        processed_query = Cleaning(query)
        
        
        tif2 = TfidfVectorizer()

        cosine_similarite = []

        for i in range(len(df["Symptomes_stem_token"])):
            tfidf2 = tif2.fit_transform([df['Symptomes_stem_token'][i]]).toarray()
            cosine_similaritie = cosine_similarity(tfidf2, tif2.transform([processed_query]))[0]
            cosine_similarite.append(cosine_similaritie)
        
        cosine_similaritie = np.array(cosine_similarite)
        df['Similarite'] = 100*cosine_similaritie.flatten()
        df['Similarite'] = round(df['Similarite'],2)

        dft= df.sort_values(by='Similarite', ascending=False)
        dft = dft[df['Similarite'] > 49]
        #dft["nom"] = dft["Maladies"].apply(lambda x : "_".join(x.split()))
        return dft

#traitement

def traitement(query):

    items = data.objects.all()
                    
     # Convertir les données en un dictionnaire
    datar = {'Maladies': [], 'Symptomes': [] ,'Traitement': [],'Examens': [],"Similarite": [],"slug": []}

    for instance in items:
        datar['Maladies'].append(instance.Maladies)
        datar['slug'].append(instance.slug)
        datar['Symptomes'].append(instance.Symptomes)
        datar['Traitement'].append(instance.Traitement)
        datar['Examens'].append(instance.Examens)
        datar['Similarite'].append(instance.Similarite)

    df = pd.DataFrame(datar)
    df["Symptomes_stem_token"] = df["Symptomes"].apply(lambda x: Cleaning(x))
            
    items = Resultats(df, query)

    items = items.to_dict("records") 
    
    return items   


def EtraireChiffres(text):
    
    text = re.findall(r'\d+', text)
    
    text = " ".join(" ".join(text).replace(" ", ""))
    
    return text

def Cleaning2(text):
            # Supprimer des ponctuations
    text = re.sub("[^\w\s]", " ", text)
            
    text = ' '.join([ps.stem(unidecode(word.lower())) for word in word_tokenize(text) if word.isalnum() and word.lower() not in stop_words])

            # supprimer les chiffres
    text = re.sub("\d", "", text)
    text = " ".join(set(text.split()))

    return text
#traitement hopitaux

# DATASET DE SORTIES
def Resultats_hop(d, val ,df):
        
        query = val

        processed_query = Cleaning2(query)
        
        
        tif2 = TfidfVectorizer()

        cosine_similarite = []

        for i in range(len(d)):
            tfidf2 = tif2.fit_transform([d[i]]).toarray()
            cosine_similaritie = cosine_similarity(tfidf2, tif2.transform([processed_query]))[0]
            cosine_similarite.append(cosine_similaritie)
        
        cosine_similaritie = np.array(cosine_similarite)
        df['Similarite'] = 100*cosine_similaritie.flatten()
        df['Similarite'] = round(df['Similarite'],2)

        dft= df.sort_values(by='Similarite', ascending=False)
        return dft
        

def traitement_hop(query):

    items = hopitaux.objects.all()
                    
     # Convertir les données en un dictionnaire
    datar = {'Nom': [], 'Biometrie': [] ,'categori': [],'Quartier': [],"Localisation": [],"Telephone": []}

    for instance in items:
        datar['Nom'].append(instance.Nom)
        datar['Biometrie'].append(instance.Biometrie)
        datar['Quartier'].append(instance.Quartier)
        datar['Localisation'].append(instance.Localisation)
        datar['Telephone'].append(instance.Telephone)
        datar['categori'].append(instance.categori)

    df = pd.DataFrame(datar)
    df1 =df["Telephone"]
    df2 = df.drop("Telephone", axis = 1)
    df2["Biometrie"] = df2["Biometrie"].apply(lambda x : str(x).replace("Oui", "Biometrie").replace("Non", " "))
    for i in df2.columns:
        df2[i] = df2[i].apply(lambda x : str(x).replace("nan", " "))
    df1 = df1.apply(lambda x : EtraireChiffres(str(x)))
    df2["global"] = df2["Nom"]+" " + df2["Biometrie"]+" " + df2["Quartier"] +" "+ df2["Localisation"]+" " + df2["categori"]

    df2['global'] = df2['global'].apply(lambda x : Cleaning2(str(x)))
    df2['total'] = df1 +" "+df2['global']
    items = Resultats_hop(df2['total'], query , df)
    items = items.to_dict("records") 
    
    return items 