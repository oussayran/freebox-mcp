# Freebox MCP

Contrôlez un **Freebox Révolution Player** depuis un client MCP, avec des commandes comme « baisse le volume » ou « passe à la chaîne 2 ».

Le serveur Python fonctionne sur votre ordinateur et communique avec le Player sur le réseau local. Claude Code est un client possible ; les scripts de test fonctionnent aussi sans lui.

## Conditions

- Un **Freebox Révolution Player** allumé.
- **L’ordinateur qui exécute le serveur et la Freebox doivent être sur le même réseau local**, en Wi-Fi ou Ethernet, et pouvoir communiquer.
- Si vous utilisez un mobile comme interface, connectez-le au même réseau domestique. Une connexion 4G/5G seule ne suffit pas. Ce dépôt ne fournit pas d’application mobile.
- L’adresse IP locale du Player et son **code de télécommande réseau**, disponible dans ses réglages. Ce code est différent du PIN parental et du mot de passe Freebox OS.
- Python **3.10 ou supérieur**, Git et Internet pour installer les dépendances.

Testé sur macOS avec Python 3.14 et un Player Révolution. Les autres modèles Freebox et systèmes restent à vérifier.

## Installation

```bash
git clone https://github.com/oussayran/freebox-mcp.git
cd freebox-mcp
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
cp .env.example .env
chmod 600 .env
nano .env
```

Dans `.env`, remplacez les valeurs par celles de votre Player :

```dotenv
FREEBOX_PLAYER_HOST=192.168.1.100
FREEBOX_REMOTE_CODE=VOTRE_CODE_NUMERIQUE
```

L’adresse IP est un exemple. Utilisez l’adresse du **Player**, pas celle du routeur. Ne recopiez pas `.env.example` sur un fichier déjà configuré.

Dans nano : **Ctrl+O**, Entrée pour enregistrer, puis **Ctrl+X** pour quitter. Dans Finder, **Commande+Maj+point** affiche les fichiers cachés comme `.env`.

Le fichier est relu à chaque commande : inutile de redémarrer après une modification du code. Les variables d’environnement ont priorité sur `.env`.

## Tester

Depuis le dossier du dépôt :

```bash
# Tests unitaires : aucune commande envoyée au Player
.venv/bin/python -m unittest discover -s . -p 'test_freebox.py' -v

# Vérification du serveur MCP et de la réponse réseau
.venv/bin/python check_mcp.py

# Test réel : baisse le volume d’un cran, puis le remonte
.venv/bin/python test_live.py
```

La sonde `check_mcp.py` n’envoie aucun code : **HTTP 403 peut être normal** et ne valide pas votre code. Le test réel doit renvoyer deux résultats avec `accepted: True` ; vérifiez aussi l’effet sur votre installation. Si une étape échoue, le script s’arrête.

## Utiliser avec Claude Code

Avec Claude Code déjà installé, depuis le dossier du dépôt :

```bash
claude mcp add --transport stdio --scope project freebox -- "$PWD/.venv/bin/python" "$PWD/server.py"
claude mcp get freebox
claude
```

Autorisez le serveur si demandé, puis vérifiez son état avec `/mcp`.

Exemples : « Baisse le volume de 2 crans », « Appuie sur Home », « Passe à la chaîne 2 ».

Un agent ayant accès à votre ordinateur et au réseau local peut également appeler les scripts depuis une conversation. Le clonage du dépôt ne donne pas, à lui seul, cet accès à un service dans le cloud.

## Outils disponibles

| Outil | Utilisation |
|---|---|
| `connection_status()` | Vérifie la réponse réseau sans appuyer sur une touche. Ne valide pas le code. |
| `press_key(key, long_press=False)` | Envoie une touche de télécommande, avec appui long optionnel. |
| `change_channel(channel)` | Saisit un numéro de chaîne de 1 à 9999, depuis le mode direct. |
| `adjust_volume(direction, steps=1)` | Monte (`up`) ou baisse (`down`) le volume de 1 à 10 crans. |

Touches acceptées par `press_key` :

| Fonction | Touches |
|---|---|
| Marche/veille et muet | `power`, `mute` |
| Volume et chaînes | `vol_inc`, `vol_dec`, `prgm_inc`, `prgm_dec` |
| Menus | `home`, `back`, `up`, `down`, `left`, `right`, `ok` |
| Lecture | `play`, `pause`, `stop`, `fwd`, `bwd`, `next`, `prev` |
| Autres | `rec`, `info`, `epg`, `tv`, `red`, `green`, `yellow`, `blue` |
| Chiffres | `0` à `9` |

## Limites et dépannage

- **Volume confirmé sur matériel**, avec quatre tests unitaires réussis. Les autres touches dépendent du contexte et ne sont pas toutes validées.
- **Chaînes à plusieurs chiffres : problème constaté.** Une demande de canal 646 a sélectionné le canal 6. La saisie multi-chiffres reste à corriger ou à valider ; une réponse HTTP positive ne garantit pas la bonne chaîne.
- **Pas de retour d’état** : ni niveau exact du volume, ni chaîne courante, ni état marche/veille. Un réglage garanti à 50 % ou 100 % n’est pas disponible.
- `power` et `mute` sont des bascules : évitez de les répéter automatiquement après un résultat incertain.
- **403 lors du test réel** : vérifiez le code réseau et l’adresse du Player.
- **Connexion impossible** : vérifiez que le Player est allumé, sur le même réseau, sans isolation Wi-Fi ni VPN bloquant.
- **Adresse publique refusée** : utilisez l’IP privée du Player. `hd1.freebox.fr` ne désigne pas toujours l’appareil local. Le validateur actuel attend un nom ou une adresse IPv4, sans port ni chemin.

## Confidentialité et partage

Le fichier **`.env` est exclu de Git**, avec l’environnement Python, les caches et la configuration MCP locale. Ne publiez jamais votre code de télécommande. Seuls les modèles `.env.example` et `.mcp.json.example` sont partageables.

Le contrôle utilise HTTP non chiffré sur un réseau local de confiance. Ne l’exposez pas sur Internet et utilisez uniquement des appareils que vous êtes autorisé à contrôler.

Aucune licence de réutilisation n’a encore été choisie. Une licence devra être ajoutée pour préciser les droits de redistribution et de modification.

## Mettre à jour le dépôt GitHub

Avant chaque envoi, vérifiez les fichiers suivis : `.env` ne doit pas apparaître.

```bash
git status --short
git ls-files
git add README.md  # adaptez aux fichiers modifiés
git commit -m "Mettre à jour la documentation"
git push origin main
```

Chaque utilisateur doit créer son propre `.env` avec les informations de sa Freebox.

## Fichiers

- `server.py` : serveur MCP.
- `test_freebox.py` : tests unitaires.
- `check_mcp.py` : vérification MCP et réseau.
- `test_live.py` : test réel du volume.
- `requirements.lock.txt` : versions exactes de l’environnement testé.
- `requirements.txt` : dépendances directes.
- `.env.example` et `.mcp.json.example` : modèles de configuration.
