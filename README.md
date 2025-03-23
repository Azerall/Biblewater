# 📖 Bienvenue sur **Biblewater**  

**Biblewater** est une application web et mobile permettant d'effectuer des recherches avancées dans une bibliothèque de 1664 livres.  

---

## 🌍 Accès à l'application en ligne

- **Frontend** : [Biblewater](https://azerall.github.io/Biblewater/)  
- **Backend** : [API Biblewater](https://biblewater-phi.vercel.app/gutenberg/books/)  

---

## 🌟 Fonctionnalités principales  

1️⃣ **Recherche simple** 🔍  
   - Recherche de livres par mot-clé.  
   - À partir d'une entrée texte S, l’application retourne la liste de tous les documents contenant S.  
   - Peut également prendre en entrée une liste de mots, séparés par un espace, une virgule, un point-virgule ou un slash (ex : mot1, mot2; mot3 / mot4).

2️⃣ **Recherche avancée (RegEx)** 🧐  
   - Recherche de livres par expression régulière (RegEx).  
   - À partir d'une entrée RegEx, l'application retourne la liste des documents contenant une chaîne correspondant à l’expression régulière.  

3️⃣ **Classement des résultats** 📊  
   - Classement des résultats selon :  
     - Nombre d’occurrences du mot-clé dans le document.  
     - Indices de **closeness** et **betweenness**.  

4️⃣ **Suggestion intelligente** 🤖  
   - Proposition de documents similaires aux résultats les plus pertinents.  
   - Basé sur un **graphe de Jaccard** reliant les documents proches en contenu.  

---

## 🛠️ **Liste des pré-requis**  

### 🔹 **Backend (Django & DRF)**  
- Python 3+  
- Django & Django REST Framework  
- SQLite (fourni avec Django)  

### 🔹 **Frontend (React + Vite)**  
- Node.js 16+  
- npm ou yarn  

---

## 🚀 **Lancer l'application en local**  

### 🖥️ **Démarrer le backend (Django)**  

```sh
python3 -m venv myTidyVEnv
source myTidyVEnv/bin/activate
pip3 install django djangorestframework requests

cd backend/TME_webAPI_DAAR/mySearchEngine
python3 manage.py runserver
```

Le serveur Django sera accessible en local sur http://127.0.0.1:8000/gutenberg/.  

#### 🌐 **Liste des URLs disponibles**  
- http://127.0.0.1:8000/gutenberg/books/  
- http://127.0.0.1:8000/gutenberg/book/<id>  
- http://127.0.0.1:8000/gutenberg/book/<id>/coverImage/  
- http://127.0.0.1:8000/gutenberg/frenchbooks/  
- http://127.0.0.1:8000/gutenberg/englishbooks/  
- http://127.0.0.1:8000/gutenberg/search/<keyword>/  
- http://127.0.0.1:8000/gutenberg/regex/<regex>/  
- http://127.0.0.1:8000/gutenberg/search_with_ranking/<keyword>/<ranking>  
- http://127.0.0.1:8000/gutenberg/search_with_suggestions/<keyword>  

👉 **Note** : ranking peut être occurrences, closeness ou betweenness.  

---

### 🎨 **Démarrer le frontend (React + Vite)**  

```sh
cd frontend
npm install
npm run dev
```

L'interface sera accessible sur en local http://localhost:5173/.  

---

✨ **Bonne recherche avec Biblewater !** 📚🚀
