from pathlib import Path
import pandas as pd
import pandas as pd
import numpy as np
import re
from nltk.tokenize import word_tokenize
from unidecode import unidecode
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer,PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from collections import OrderedDict
from datetime import datetime

filename = "Ressources/"
# INITIALISATION
df = pd.read_csv(f"{filename}DTfinal.csv")
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(df["Symptomes_stem_token"]).toarray()
lemmatizer = WordNetLemmatizer()
ps = PorterStemmer()
stop_words = list(set(stopwords.words('french')))
new_stopwords =["facilement","tres","pendant"]
stop_words.extend(new_stopwords)


# GESTION DE LA SAUVEGARDE ET DE LA MISE A JOUR DES NOUVELLES DONNEES
if os.path.exists(f"{filename}Nouveaux Symptomes.csv"):
    New_dataRV = pd.read_csv(f"{filename}Nouveaux Symptomes.csv")
    New_dataR = New_dataRV["Nouveaux Symptomes"].tolist()
else:
    New_dataR = []

New_data = []


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

        New_data.append(query)
        New_dataR.extend(New_data)
        df_col = pd.DataFrame({'Nouveaux Symptomes' : list(OrderedDict.fromkeys(New_dataR)), "Heure D'Utilisation" : datetime.now()})
        df_col.to_csv('Ressources/Nouveaux Symptomes.csv', index=False)

        processed_query = Cleaning(query)
        
        
        tif2 = TfidfVectorizer()

        cosine_similarite = []

        for i in range(len(df["Symptomes_stem_token"])):
            tfidf2 = tif2.fit_transform([df['Symptomes_stem_token'][i]]).toarray()
            cosine_similaritie = cosine_similarity(tfidf2, tif2.transform([processed_query]))[0]
            cosine_similarite.append(cosine_similaritie)
        
        cosine_similaritie = np.array(cosine_similarite)
        df['Similarite_%'] = 100*cosine_similaritie.flatten()
        df['Similarite_%'] = round(df['Similarite_%'],2)

        df_tri = df.sort_values(by='Similarite_%', ascending=False)

        return df_tri[["Maladies",'Similarite_%',"Traitement"]]
