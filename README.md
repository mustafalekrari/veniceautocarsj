# Venice Autocars 🚗

Plateforme de gestion de location de voitures premium — Casablanca, Maroc.

## Lancer en local

```bash
cd venice_autocars_project
python3 manage.py runserver
```

## Accès local

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | Site client |
| http://127.0.0.1:8000/admin-panel/dashboard/ | Dashboard admin |

**Identifiants admin :** `admin` / `admin123`

## Déploiement Railway

### 1. Ajouter PostgreSQL sur Railway
- Projet Railway → **+ New** → **Database** → **PostgreSQL**

### 2. Variables d'environnement (Railway → Variables)

| Variable | Valeur |
|----------|--------|
| `DATABASE_URL` | *(référence automatique depuis le service PostgreSQL)* |
| `SECRET_KEY` | une-cle-secrete-longue |
| `DEBUG` | False |
| `ALLOWED_HOSTS` | ton-app.railway.app |

### 3. Commande de démarrage (déjà dans railway.json)
```
python manage.py migrate && gunicorn config.wsgi --log-file -
```

### 4. Après déploiement — créer l'admin
Dans Railway → ton service → **Shell** :
```bash
python manage.py createsuperuser
```

## Stack

- Backend : Django 4.2 + Django REST Framework
- Frontend : TailwindCSS + FontAwesome + Leaflet
- Base de données : PostgreSQL (Railway) / SQLite (local)
- PDF : ReportLab
- Graphiques : Chart.js
- Statics : WhiteNoise
