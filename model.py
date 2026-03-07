import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from gensim.models import Word2Vec
from gensim.utils import simple_preprocess

# Sample Data
vendors = [
    {'vendor_id': 1, 'product': 'apple phone repair service'},
    {'vendor_id': 2, 'product': 'banana wholesale supply'},
    {'vendor_id': 3, 'product': 'apple phone screen replacement'}
]

customer_requests = [
    {'customer_id': 1, 'request': 'iphone repair'},
    {'customer_id': 2, 'request': 'buy bananas'}
]

# Preprocess and Tokenize Product/Service Descriptions
def preprocess(text):
    return simple_preprocess(text)

product_descriptions = [preprocess(vendor['product']) for vendor in vendors]
requests = [preprocess(request['request']) for request in customer_requests]

# Train Word2Vec Model
word2vec_model = Word2Vec(sentences=product_descriptions + requests, vector_size=100, window=5, min_count=1, workers=4)

# Function to get the vector representation of a product/service description
def get_vector(description):
    vectors = [word2vec_model.wv[word] for word in description if word in word2vec_model.wv]
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        return np.zeros(word2vec_model.vector_size)

# Vectorize Product/Service Descriptions
product_vectors = np.array([get_vector(description) for description in product_descriptions])

# Clustering
kmeans = KMeans(n_clusters=2)  # Set the number of clusters
kmeans.fit(product_vectors)

# Assign Clusters
clusters = kmeans.predict(product_vectors)
vendor_clusters = {i: [] for i in range(2)}
for i, cluster in enumerate(clusters):
    vendor_clusters[cluster].append(vendors[i])

# KNN for Finding Nearest Clusters
knn = NearestNeighbors(n_neighbors=1, metric='cosine')
knn.fit(product_vectors)

def find_nearest_cluster(new_product):
    new_product_vector = get_vector(preprocess(new_product))
    distances, indices = knn.kneighbors([new_product_vector])
    nearest_cluster = clusters[indices[0][0]]
    return nearest_cluster, distances[0][0]

# Adding a New Vendor
new_vendor = {'vendor_id': 4, 'product': 'banana fruit supply'}
nearest_cluster, distance = find_nearest_cluster(new_vendor['product'])

if distance < 0.5:  # Threshold for similarity
    vendor_clusters[nearest_cluster].append(new_vendor)
else:
    # Create a new cluster
    all_vectors = np.vstack([product_vectors, get_vector(preprocess(new_vendor['product']))])
    kmeans = KMeans(n_clusters=len(vendor_clusters) + 1)
    kmeans.fit(all_vectors)
    clusters = kmeans.predict(all_vectors)
    vendor_clusters = {i: [] for i in range(len(vendor_clusters) + 1)}
    for i, cluster in enumerate(clusters):
        if i < len(vendors):
            vendor_clusters[cluster].append(vendors[i])
        else:
            vendor_clusters[cluster].append(new_vendor)

# Handling Customer Request
for request in customer_requests:
    nearest_cluster, distance = find_nearest_cluster(request['request'])
    matched_vendors = vendor_clusters[nearest_cluster]
    print(f"Customer {request['customer_id']} matched with vendors: {matched_vendors}")