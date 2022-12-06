from django.utils.datastructures import MultiValueDictKeyError
import snscrape.modules.twitter as sntwitter
import pandas as pd
import re
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from bs4 import BeautifulSoup

load_model = pickle.load(open("python/SVM_Model.pkl", 'rb'))
load_Tfidf = pickle.load(open("python/Tfidf.pkl","rb"))  


stop_words = set(stopwords.words("english"))

query = "donald trump lang:en" #kata kunci pencarian dengan filter language english
tweets = []
limit = 10 #menentukan limit tweet yang ingin di scrap. angka dapat di tambah atau di kurang.

for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    
    # print(vars(tweet))
    # break
    
    if len(tweets) == limit:
        break
    else:
        tweets.append([tweet.content, tweet.user.username])

df = pd.DataFrame(tweets, columns=["Tweet","User"])
tweets = df["Tweet"]

#print(df)

def data_processing(Tweet):
    #membersihkan teks
    Tweet = Tweet.lower()
    Tweet = re.sub(r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$","",Tweet, flags = re.MULTILINE)
    Tweet = re.sub(r"\@\w+|\#","",Tweet)
    Tweet = re.sub(r"[^\w\s]","",Tweet)
    #token
    tweet_tokens = word_tokenize(Tweet)
    filtered_tweet = [w for w in tweet_tokens if not w in stop_words]
    return " ".join(filtered_tweet)

df.Fil_Tweets = tweets.apply(data_processing) #buat manggil fungsi data_processing

lemmatizer = WordNetLemmatizer()
def lemmatizing(data):

    data_tokens = word_tokenize(data)
    Tweet = [lemmatizer.lemmatize(words) for words in data_tokens]
    return " ".join(Tweet)

df.Fil_Tweets = df.Fil_Tweets.apply(lambda x: lemmatizing(x))

#print(df)

tf_array =load_Tfidf.transform(df.Fil_Tweets).toarray()

predicted_class = load_model.predict(tf_array)

def class_to_name(class_label):
    if class_label == 0:
        return "Neutral"
    elif class_label == 1:
        return "Sexist/Racist"

predicts = []
Neutral = 0
Racist_Sexist = 0
for i,t in enumerate(df.Fil_Tweets):
        predict = class_to_name(predicted_class[i])
        if predicted_class[i] == 0:
            Neutral +=1
        else:
            Racist_Sexist +=1
        predicts.append([t,predict])

df2 = pd.DataFrame(predicts, columns=["Filtered Tweets","Prediction"])

print("Neutral = ", Neutral)
print("Racist/Sexist = ", Racist_Sexist)

final = pd.concat([df, df2],axis = 1)

print(final)

final.to_csv("temp.csv")