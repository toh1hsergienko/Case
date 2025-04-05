from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def cluster_embeddings(embeddings, n_clusters=5):
    # Снижение размерности
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(embeddings)
    
    # Кластеризация
    kmeans = KMeans(n_clusters=n_clusters)
    clusters = kmeans.fit_predict(reduced)
    
    # Визуализация
    plt.scatter(reduced[:,0], reduced[:,1], c=clusters)
    plt.show()
    
    return clusters, kmeans.cluster_centers_