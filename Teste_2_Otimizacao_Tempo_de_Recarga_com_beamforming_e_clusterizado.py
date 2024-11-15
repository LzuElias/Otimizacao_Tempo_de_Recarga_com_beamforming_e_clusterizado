
#%% Definições

# - Beta_k = ganho médio de potência no canal entre o PB e o k-ésimo dispositivo;
# - s_k = sinal transmitido (variável aleatória gaussiana de média zero e variancia unitária);
# - Psi_k = vetor beamforming analógico (Pertence aos complexos com tamanho 1xN);
# - ||Psi_k||² = Potencia de transmissão (Pt);
# - h_k = Vetor de canal (pertence aos complexos com tamanho 1xN);
# - kappa_PB_D = fator de rice;

# OBS: k = K. j = 1 e vai até j = k-1


#%% -------------------------   IMPORTAÇÕES e PARÂMETROS   ----------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN

import random

seed = np.random.seed(9)

K = 30                                  # N° dispositivos
N = 4                                   # N° de antenas
R = 50                                  # Raio [m]
L = 1                                   # N° de RIS
f = 915 *(10**6)                        # Freq. da portadora
kappa_PB_D = 1.5                        # Fator Rice PB-Disp
kappa_PB_RIS = 1.7                      # Fator Rice PB-Disp
kappa_RIS_D = 1.4                       # Fator Rice PB-Disp
mu = 10.73 * 10**(-3)                   # Max pot no IoT
a = 0.2308                              # constante circuito a
b = 5.365                               # constante circuito b  
Pt = 3                                  # Max pot. de transmissão
E_min = 1* (10**-6)                     # Min Energia no IoT [J]
alpha = 3.5                             # Coef. perda de percurso sem visada direta
alpha2 = 2                              # Coef. perda de percurso com visada direta
c = 3*(10**(8))                         # Vel. da luz
Omega = 1/(1+(np.exp(a*b)))             # Constante resposta 0_in-0_out
Pot_k = 0
# Parâmetros Ris
M = 100                                 # Linha e Coluna das células da Ris
a = 1                                   # Valor absoluto Ris



#  Para acréscimo da RIS
RIS = np.zeros((L,L))
RIS = [[1]]
theta = np.zeros((M, M)).astype(complex)                    # theta é a fase da matriz da RIS 
Beta2 = np.zeros((L))                                       # Beta para Power_Beacon-RIS e RIS-Disp


#%% ----------------------------   CONSTRUÇÃO DA RIS   ------------------------------------------------------------------

theta_aux = np.zeros(M).astype(complex)
# Montagem da RIS
for linha in range (0,M):
    ris_phase = np.random.random()
    theta_aux[linha] = np.exp(-1j*(ris_phase*2*np.pi))
theta = np.diag(theta_aux)        

# np.linalg.norm(theta, 2) -----> norma = 1


    
#%% --------------------   GERAÇÃO DA LOCALIZAÇÃO DOS DISPOSITIVOS   ------------------------------------------------------

seed = np.random.seed(7)

# Posições do PB e RIS
PB_position = np.array([0, 0])
RIS_position = np.array([R * 0.8, R * 0.8])

# Determinando o retângulo de distribuição baseado nas posições de PB e RIS
x_min, x_max = min(PB_position[0], RIS_position[0]), max(PB_position[0], RIS_position[0])
y_min, y_max = min(PB_position[1], RIS_position[1]), max(PB_position[1], RIS_position[1])

# Gerando coordenadas x e y uniformemente dentro do retângulo
x_disp = np.random.uniform(x_min, x_max, K)
y_disp = np.random.uniform(y_min, y_max, K)

# Armazenando as coordenadas dos dispositivos
loc_dispositivos = np.vstack((x_disp, y_disp)).T

# Plotando os pontos no gráfico
plt.figure(figsize=(8, 6))
plt.scatter(x_disp, y_disp, label="Dispositivos", color="blue")
plt.plot(RIS_position[0], RIS_position[1], 'rx', markersize=10, label="RIS")  # RIS em vermelho
plt.plot(PB_position[0], PB_position[1], 'ks', markersize=10, label="Power Beacon (PB)")  # PB em preto

# Configurações de exibição
plt.xlabel('X Coordenada')
plt.ylabel('Y Coordenada')
plt.legend(loc='upper left')
plt.title('Localização dos dispositivos entre PB e RIS')
plt.grid(True)
plt.show()


# %% ------------------   ELBOW METHOD PARA O N° DE CLUSTERS   -----------------------------------

from sklearn.metrics import silhouette_samples, silhouette_score

# Cria a Curva de Cotovelo para encontrar o Numero Ideal de Clusters
wcss = []
melhor_score = -1  # Inicializa com um valor baixo
melhor_n_clusters = 2  # Inicializa com o mínimo de clusters

for i in range(1, K):
    kmeans = KMeans(n_clusters = i, max_iter = 300, n_init = 10, random_state = 0)
    kmeans.fit(loc_dispositivos)
    wcss.append(kmeans.inertia_)
    
# Mostra o Gráfico
plt.plot(range(1, K), wcss)
plt.title('Curva de Cotovelo')
plt.xlabel('Numero de Clusters')
plt.ylabel('WCSS') #within cluster sum of squares
plt.show()


for i in range(2, 15):
    clusterer = KMeans(n_clusters=i)
    preds = clusterer.fit_predict(loc_dispositivos)
    score = silhouette_score(loc_dispositivos, preds)
    print('Silhueta para ' + str(i) + ' clusters : ' + str(score))

    if score > melhor_score:
        melhor_score = score
        melhor_n_clusters = i

print(f'\nMelhor número de clusters: {melhor_n_clusters} com coeficiente de silhueta de {melhor_score}')


#%% ------------------------------   CLUSTERIZAÇÃO   ----------------------------------------------------------------
seed = np.random.seed(9)

n_cluster = melhor_n_clusters
loc_dispositivos2 = np.vstack((x_disp, y_disp)).T
k_means = KMeans(n_clusters = n_cluster, random_state=seed).fit(loc_dispositivos2)
cluster_labels = k_means.labels_

# Plotando os dispositivos e o Power Beacon
plt.figure(figsize=(8, 6))
plt.scatter(loc_dispositivos2[:, 0], loc_dispositivos2[:, 1], c=cluster_labels, cmap='viridis', label="Dispositivos")
plt.scatter(PB_position[0], PB_position[1], color='red', marker='x', s=100, label="Power Beacon (PB)")
plt.scatter(RIS_position[0], RIS_position[1], color='blue', marker='x', s=100, label="RIS")
plt.xlabel('X Coordenada')
plt.ylabel('Y Coordenada')
plt.legend()
plt.title('Clusterização dos Dispositivos')
plt.show()



# --------------------   Separação dos dispositivos por cluster   --------------------------------------------------------

dbscan = DBSCAN(eps=2.5, min_samples=2).fit(loc_dispositivos2)
#labels = dbscan.labels_
labels = cluster_labels

# Separando dispositivos em clusters com base nos rótulos
unique_labels = set(labels)
clusters = {label: loc_dispositivos2[labels == label] for label in unique_labels if label != -1}
outliers = loc_dispositivos2[labels == -1]  # Dispositivos que são outliers

plt.figure(figsize=(8, 6))
colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]

for k, col in zip(unique_labels, colors):
    if k == -1:
        # Cor para outliers (pontos fora dos clusters)
        col = [0, 0, 0, 1]
        xy = outliers
    else:
        xy = clusters[k]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=8, label=f"Cluster {k}")

plt.scatter(PB_position[0], PB_position[1], color='red', marker='x', s=100, label="Power Beacon (PB)")
plt.scatter(RIS_position[0], RIS_position[1], color='blue', marker='x', s=100, label="RIS")

# Configurações do gráfico
plt.xlabel('X Coordenada')
plt.ylabel('Y Coordenada')
plt.legend(loc = 'upper left')
plt.title('Clusterização dos Dispositivos com DBSCAN')
plt.axis('equal')
plt.show()


# ------------------------   Plot dos clusters com o círculo   --------------------------------------------------------

centroids = k_means.cluster_centers_

# Calculando o raio dos círculos com base na dispersão dos pontos dentro de cada cluster
radii = []
for i in range(n_cluster):
    # Seleciona os pontos do cluster i
    cluster_points = loc_dispositivos2[cluster_labels == i]
    # Calcula o raio como a distância média dos pontos ao centroide
    radius = np.mean(np.sqrt(np.sum((cluster_points - centroids[i])**2, axis=1)))
    radii.append(radius)

# Plotando os dispositivos, o Power Beacon e os clusters com círculos
plt.figure(figsize=(8, 6))
plt.scatter(loc_dispositivos2[:, 0], loc_dispositivos2[:, 1], c=cluster_labels, cmap='viridis', label="Dispositivos")
plt.scatter(PB_position[0], PB_position[1], color='red', marker='x', s=100, label="Power Beacon (PB)")
plt.scatter(RIS_position[0], RIS_position[1], color='blue', marker='x', s=100, label="RIS")

# Desenhando círculos ao redor de cada cluster
for i, centroid in enumerate(centroids):
    circle = plt.Circle(centroid, radii[i], color='gray', fill=False, linestyle='--', linewidth=1.5)
    plt.gca().add_patch(circle)

# Configurações do gráfico
plt.xlabel('X Coordenada')
plt.ylabel('Y Coordenada')
plt.legend()
plt.title('Marcação dos clusters')
plt.axis('equal')
plt.show()


# -------------   Embaralhamento dos dispositivos dentro do seu cluster   -----------------------------------------------------------------

for label in unique_labels:
    if label != -1:  # Ignorando outliers
        cluster_points = loc_dispositivos2[labels == label]
        np.random.shuffle(cluster_points)  # Embaralhando dispositivos dentro do cluster
        clusters[label] = cluster_points
outliers = loc_dispositivos2[labels == -1]  # Dispositivos que são outliers

# # Exibindo os clusters embaralhados
# print("Dispositivos por Cluster (Embaralhados):")
# for label, cluster_points in clusters.items():
#     print(f"Cluster {label}:")
#     print(cluster_points)

# print("\nOutliers (pontos fora de clusters):")
# print(outliers)



# --------------    Reodernando os dispositivos com o PB como referência  --------------------


# Função para calcular a distância entre um ponto e o Power Beacon
def calcular_distancia_ponto(ponto, PB_position):
    return np.sqrt((ponto[0] - PB_position[0])**2 + (ponto[1] - PB_position[1])**2)

# Ordenar dispositivos dentro de cada cluster pela distância ao PB
for cluster_id, dispositivos in clusters.items():
    # Ordena cada cluster pelo dispositivo mais próximo ao PB
    clusters[cluster_id] = sorted(dispositivos, key=lambda dispositivo: calcular_distancia_ponto(dispositivo, PB_position))

# Ordenar os clusters pela distância do dispositivo mais próximo de cada cluster ao PB
cluster_ordenado_ids = sorted(clusters.keys(), key=lambda cid: calcular_distancia_ponto(clusters[cid][0], PB_position))

# Criar lista final de dispositivos ordenados por proximidade ao PB
dispositivos_ordenados_PB = []
for cid in cluster_ordenado_ids:
    dispositivos_ordenados_PB.extend(clusters[cid])


# # Exibindo as coordenadas dos dispositivos ordenados
# print("Dispositivos ordenados por proximidade ao Power Beacon:")
# for i, dispositivo in enumerate(dispositivos_ordenados_PB):
#     print(f"Dispositivo {i + 1}: posição (x, y) = {dispositivo}")



# %%--------------    Reodernando os dispositivos com a RIS como referência  --------------------


# Função para calcular a distância entre um ponto e o Power Beacon
def calcular_distancia_ponto(ponto, RIS_position):
    return np.sqrt((ponto[0] - RIS_position[0])**2 + (ponto[1] - RIS_position[1])**2)

# Ordenar dispositivos dentro de cada cluster pela distância ao PB
for cluster_id, dispositivos in clusters.items():
    # Ordena cada cluster pelo dispositivo mais próximo ao PB
    clusters[cluster_id] = sorted(dispositivos, key=lambda dispositivo: calcular_distancia_ponto(dispositivo, RIS_position))

# Ordenar os clusters pela distância do dispositivo mais próximo de cada cluster ao PB
cluster_ordenado_ids = sorted(clusters.keys(), key=lambda cid: calcular_distancia_ponto(clusters[cid][0], RIS_position))

# Criar lista final de dispositivos ordenados por proximidade ao PB
dispositivos_ordenados_RIS = []
for cid in cluster_ordenado_ids:
    dispositivos_ordenados_RIS.extend(clusters[cid])


# # Exibindo as coordenadas dos dispositivos ordenados
# print("Dispositivos ordenados por proximidade à RIS:")
# for i, dispositivo in enumerate(dispositivos_ordenados_RIS):
#     print(f"Dispositivo {i + 1}: posição (x, y) = {dispositivo}")




#%% -------------------   CONSTRUÇÃO DOS CANAIS E CÁLCULO DE BETA   ----------------------------------------------------------------------------------------------------

# ---------------------   Canal Power Beacon - Dispositivos  (K,N)   -------------------------------

h_LoS_PB_D = np.zeros((K,N)).astype(complex)
h_NLoS_PB_D = np.zeros((K,N)).astype(complex)
Beta_PB_D = np.zeros(K)
hH_PB_D = np.zeros((K,N)).astype(complex)
    # Construção do canal PB - Dispositivo (kappa_PB_D da ligação pb-disp)
h_LoS_PB_D = np.random.rand(K,N) + 1j*np.random.rand(K,N) # Matriz (KxN)
h_NLoS_PB_D = np.random.rand(K,N) + 1j*np.random.rand(K,N) # Matriz (KxN)
hH_PB_D = (np.sqrt((kappa_PB_D)/(1+kappa_PB_D)) * h_LoS_PB_D) + (np.sqrt((1)/(1+kappa_PB_D)) * h_NLoS_PB_D) # Canal PB-Device


for j in range(len(dispositivos_ordenados_PB)):
    for k in range(len(dispositivos_ordenados_PB[j])):
        # Beta PB_D:
        x = dispositivos_ordenados_PB[j][0]
        y = dispositivos_ordenados_PB[j][1]                     # [a][b] --> a varia de 0-K / b=0=x / b=1=y
        d = np.sqrt(x**2 + y**2)
        Beta_PB_D[k] = (c**2) / ((16*((np.pi)**2)) * (f**2) * (d**alpha))
        
        hH_PB_D[k, :] = np.sqrt(Beta_PB_D[k])*hH_PB_D[k, :]




# %% -------------   Canal Power Beacon - RIS (N,M)  ----------------------------------------

h_LoS_PB_RIS = np.zeros((N,M)).astype(complex)
h_NLoS_PB_RIS = np.zeros((N,M)).astype(complex)
Beta_PB_RIS = np.zeros(M)
hH_PB_RIS = np.zeros((N,M)).astype(complex)

    # Construção do canal PB-RIS (1 RIS = um canal do PB até a RIS)
h_LoS_PB_RIS = np.random.rand(N,M) + 1j*np.random.rand(N,M) # Matriz (1xL)
h_NLoS_PB_RIS = np.random.rand(N,M) + 1j*np.random.rand(N,M) # Matriz (1xL)
hH_PB_RIS = (np.sqrt((kappa_PB_RIS)/(1+kappa_PB_RIS)) * h_LoS_PB_RIS) + (np.sqrt((1)/(1+kappa_PB_RIS)) * h_NLoS_PB_RIS) # Canal PB-RIS

for k in range(0,L):
    # Beta PB_RIS:
    x = RIS_position[0]
    y = RIS_position[1]
    d = np.sqrt(x**2 + y**2)
    Beta_PB_RIS[k] = (((c/f)**2) / ((4*np.pi)**2)) * (d**(-alpha2))
    hH_PB_RIS[k] = np.sqrt(Beta_PB_RIS[k])*hH_PB_RIS[k]

# np.shape(hH_PB_RIS)

# ---------------------   Canal RIS - Dispositivos Tamanho (L, K)   ----------------------------------------

h_LoS_RIS_D = np.zeros((M,K)).astype(complex)
h_NLoS_RIS_D = np.zeros((M,K)).astype(complex)
Beta_RIS_D = np.zeros(K)
hH_RIS_D = np.zeros((M,K)).astype(complex)

    # Construção do canal RIS-Disp;
h_LoS_RIS_D = np.random.rand(M,K) + 1j*np.random.rand(M,K) # Matriz (LxK)
h_NLoS_RIS_D = np.random.rand(M,K) + 1j*np.random.rand(M,K) # Matriz (LxK)
hH_RIS_D = (np.sqrt((kappa_RIS_D)/(1+kappa_RIS_D)) * h_LoS_RIS_D) + (np.sqrt((1)/(1+kappa_RIS_D)) * h_NLoS_RIS_D) # Canal RIS-D

for j in range(len(dispositivos_ordenados_RIS)):
    for k in range(len(dispositivos_ordenados_RIS[j])):
        # Beta PB_D:
        x = dispositivos_ordenados_RIS[j][0]
        y = dispositivos_ordenados_RIS[j][1]                     # [a][b] --> a varia de 0-K / b=0=x / b=1=y
        d = np.sqrt(x**2 + y**2)
        Beta_PB_D[k] = (c**2) / ((16*((np.pi)**2)) * (f**2) * (d**alpha))
        
        hH_PB_D[k, :] = np.sqrt(Beta_PB_D[k])*hH_PB_D[k, :]



# %% -----------------------   Canal Completo (N x K)   ----------------------------------------

H = ((hH_PB_RIS @ theta @ hH_RIS_D) + np.transpose(hH_PB_D))

# np.shape(hH_PB_RIS)
# np.shape(hH_RIS_D)
# np.shape(hH_PB_D)
# np.shape(theta)
# np.shape(H)

#%% ----------------   CÁLCULO DO TEMPO DE CARREGAMENTO DOS DISPOSITIVOS   -----------------------------------------------------------------------------------------------------

# Parâmetros Carregamento
Pr = np.zeros(K)
Beamform_SCSI = np.zeros((K,N)).astype(complex)
Gamma = np.zeros(K)
tempo_carregamento = np.zeros(K)
Gamma_kj = np.zeros(K)
tempo_carregamento_total = np.zeros(K)

# Beamforming S-CSI (h_LoS_PB_D)
for k in range (0,K):
    Beamform_SCSI[k] = np.transpose(np.sqrt(Pt/N) * (h_LoS_PB_D[k]/np.abs(h_LoS_PB_D[k])))

    #Para PB-Disp e RIS-Disp
for k in range (0,K):
    Phi_NEIG = np.zeros(K)
    
    # np.shape(Phi_NEIG)
     
    # Potência
    Pr[k] = (np.abs((Beamform_SCSI[k].dot(np.transpose(H)[k]))))**2
     
    # Função Logística Tradicional (Gamma):
    Gamma[k] = mu / (1 + (np.exp(-a*(Pr[k] - b))))
    
    # Tempo de carregamento para o primeiro dispositivo:
    if k==0:
        tempo_carregamento[0] = (E_min * (1-Omega)) / (Gamma[0] - (mu*Omega))
    else:
        for j in range (0, k):
            # print(j)
            # Energia total coletada carregando o vizinho (Phi_NEIG):
            Gamma_kj[j] = mu / (1 + (np.exp(-a*((Beta_PB_D[k]*(np.abs(Beamform_SCSI[j].dot(np.transpose(H)[k]))**2))-b))))
            Phi_NEIG[j] = tempo_carregamento[j] * ((Gamma_kj[j] - (mu*Omega)) / (1 - Omega))
            
        if np.sum(Phi_NEIG) > E_min:
            tempo_carregamento[k] = 0
        else:
            tempo_carregamento[k] = ((E_min - np.sum(Phi_NEIG))*(1-Omega)) / (Gamma[k] - (mu*Omega))                           
    
tempo_carregamento_total = np.sum(tempo_carregamento)
                
       
print("Terminou de rodar\n")
# %%

