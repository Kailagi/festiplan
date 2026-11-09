# FestiPlan

FestiPlan est une API FastAPI de gestion de festivals, conçue autour du
**Domain-Driven Design (DDD)** et de l’**Architecture Hexagonale (Ports &
Adaptateurs)**. Les règles métier sont séparées des mécanismes HTTP et de la
persistance afin de faciliter leur compréhension, leur test et leur évolution.

L’application couvre la gestion des festivals, des artistes, des scènes, des
concerts et des incidents, notamment la planification, le déplacement et
l’annulation des concerts ainsi que la publication des festivals.

## Architecture et découpage en couches

Les dépendances sont orientées vers le cœur métier : le domaine ne dépend ni de
FastAPI ni de SQLAlchemy.

| Couche | Rôle |
|---|---|
| `app/domain/` — Domaine pur | Entités, objets-valeurs, événements et règles métier. Cette couche ne dépend d’aucun framework. |
| `app/application/` — Application | Commandes, résultats, ports et handlers/use cases. Les handlers orchestrent les opérations métier et les transactions via le port `UnitOfWork`. |
| `app/api/` — Adaptateurs entrants | Routes FastAPI, validation et traduction des erreurs applicatives en réponses HTTP. Les routes délèguent aux handlers injectés. |
| `app/adapters/outbound/sqlalchemy/` — Adaptateurs sortants | Repositories SQLAlchemy, mapping entre modèles de persistance et domaine, Unit of Work et stockage des événements Outbox. |
| `app/bootstrap/` — Composition | Assemblage des repositories, de l’Outbox et des cas d’usage, ainsi que l’initialisation explicite de la base. |

### Transactions et événements

L’**Unit of Work** regroupe la persistance de l’agrégat et l’ajout de ses
événements à l’Outbox dans la même transaction : les deux écritures sont
validées ensemble lors du commit.

Un dispatcher d’événements Outbox est présent. En revanche, son exécution
automatique par un worker asynchrone n’est pas encore intégrée : le dépilage
périodique et la livraison en arrière-plan restent une extension future.

## Installation, base de données et lancement

Prérequis : Python 3.11 ou supérieur.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Sous Windows, activez plutôt l’environnement avec :

```powershell
.venv\Scripts\Activate.ps1
```

La configuration utilise les variables d’environnement préfixées par
`FESTIPLAN_`. Par défaut, la base est SQLite (`sqlite:///./festiplan.db`) et le
fichier est créé dans le répertoire courant. Les tables sont initialisées au
démarrage de l’application.

Pour charger les données de démonstration :

```bash
PYTHONPATH=. python app/seed.py
```

**Attention :** le seed efface les données métier et les événements Outbox de
la base configurée. Il demande une confirmation stricte : saisissez exactement
`OUI` pour continuer. Toute autre réponse annule l’opération sans modifier les
données.

Lancer l’API depuis la racine du projet :

```bash
PYTHONPATH=. uvicorn app.main:app --reload
```

La documentation interactive est disponible à
[`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs).

## Suite de tests

Depuis la racine du projet, exécutez :

```bash
PYTHONPATH=. pytest -v
```
