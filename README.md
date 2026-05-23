# Venice Autocars 🚗

Plateforme de gestion de location de voitures premium.

## Lancer le projet

```bash
cd venice_autocars_project
python3 manage.py runserver
```

## Accès

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | Site client |
| http://127.0.0.1:8000/voitures/ | Liste des voitures |
| http://127.0.0.1:8000/admin-panel/login/ | Dashboard admin |
| http://127.0.0.1:8000/api/cars/ | API REST voitures |

**Identifiants admin :** `admin` / `admin123`

## Stack

- Backend : Django 4.2 + Django REST Framework
- Frontend : TailwindCSS (CDN) + FontAwesome
- Base de données : SQLite (dev) → PostgreSQL (prod)
- PDF : ReportLab
- Graphiques : Chart.js
