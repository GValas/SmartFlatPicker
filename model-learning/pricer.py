import multiprocessing
import pandas as pd
from pymongo import MongoClient
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.neighbors import KNeighborsRegressor

# config
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DATABASE = 'SmartFlatPicker'
MONGO_COLLECTION = 'annonces'
MONGO_FIELDS = {'idannonce': [int, 'remove'],
                'nbpiece': [int, 'median'],
                'nbchambre': [int, 'median'],
                'surface': [float, 'remove'],
                'cp': [int, 'remove'],
                'nbsallesdebain': [int, 1],
                'nbsalleseau': [int, 0],
                'nbtoilettes': [int, 1],
                'nbparkings': [int, 0],
                'nbboxes': [int, 0],
                'nbphotos': [int, 0],
                'nbterrasses': [int, 0],
                'prix': [float, 'remove']}


def get_flats_data():
    with MongoClient(MONGO_HOST, MONGO_PORT) as client:
        db = client[MONGO_DATABASE]
        collection = db[MONGO_COLLECTION]

        # docs = collection.find({})
        # fields = set()
        # for doc in docs:
        #     keys = list(doc['annonce'].keys())
        #     fields.update(keys)

        fields = {k: '$annonce.' + k for k, v in MONGO_FIELDS.items()}
        documents = collection.aggregate([{'$project': fields}])
        df = pd.DataFrame(list(documents))

    # print(df.count())

    #  completing data with na
    for field, rule in MONGO_FIELDS.items():
        if rule[1] == 'median':
            medians = df[field].dropna().median()
            df[field] = df[field].fillna(medians)
        elif rule[1] == 'remove':
            df = df.dropna(subset=[field])
        else:
            df[field] = df[field].fillna(rule[1])
        df[field] = df[field].astype(rule[0])

    # print(df.count())
    # print(df.info())

    #  data
    X = df.get(['nbpiece', 'nbchambre', 'surface', 'cp', 'nbsallesdebain', 'nbsalleseau', 'nbtoilettes',
                'nbparkings', 'nbboxes', 'nbterrasses']).values
    y = df.get(['prix']).values
    return X, y


# data
X, y = get_flats_data()
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=42)

# hyper params search
# grid_search = GridSearchCV(KNeighborsRegressor(),
#                            {'n_neighbors': range(1, 21)},
#                            cv=10,
#                            n_jobs=multiprocessing.cpu_count())
# grid_results = grid_search.fit(X_train, y_train)
# for result in grid_results.grid_scores_:
#     print(result)

# use classifier with relevant K
clf = KNeighborsRegressor(n_neighbors=10)
clf.fit(X_train, y_train)
scores = cross_val_score(clf, X_train, y_train, cv=5)
print(scores.mean())

# price custom flat
#x = clf.predict([3, 2, 69 + 18 / 3, 75011, 1, 0, 1, 0, 1, 1])
x = clf.predict([4, 3, 105.6 + 40. / (2), 75011, 1, 1, 2, 1, 0, 1])
print(x)
