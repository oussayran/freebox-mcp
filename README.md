# Freebox Révolution MCP

Un serveur MCP local en Python pour piloter un **Freebox Révolution Player** : volume, touches de télécommande et saisie d’un numéro de chaîne. Il fonctionne sur le Mac et envoie des requêtes HTTP au Player sur le réseau local.

Le serveur utilise **FastMCP avec le transport stdio**. Aucun logiciel n’est installé sur la Freebox. Un client MCP lance le processus Python et appelle ses outils.

```text
Client MCP → serveur Python sur le Mac → réseau local HTTP → Freebox Player → TV
```

## État du projet

Le 27 octobre 2026, sur une installation macOS avec Python 3.14 :

- les quatre tests unitaires ont réussi ;
- la découverte des quatre outils via un vrai client MCP a réussi ;
- Claude Code a reconnu le serveur avec l’état « Connected » ;
- les commandes de baisse et de hausse du volume ont été acceptées par le Player, et leur effet a été confirmé visuellement par l’utilisateur sur sa TV.

Les autres touches, la sélection des chaînes et les autres systèmes d’exploitation n’ont pas fait l’objet d’une validation sur matériel dans cette installation. Ce projet indépendant n’est ni un produit officiel Free ni une intégration certifiée.

## 1. Conditions nécessaires

### Matériel et réseau

- Un **Freebox Révolution Player**, le boîtier relié à la TV. Le Freebox Server est un autre appareil.
- Un Mac et un Player sur un réseau local où ils peuvent communiquer. Le Wi-Fi invité, l’isolation des appareils ou certains VPN peuvent empêcher cette communication.
- Le Player allumé pour le premier test, avec la TV visible pour confirmer le résultat.
- Une adresse locale du Player accessible sur le port HTTP 80.
- Le **code de télécommande réseau** du Player. Il ne s’agit pas du code parental, du mot de passe Wi-Fi ou du mot de passe Freebox OS.

Cette implémentation cible le Player Révolution. La compatibilité avec Pop, Android TV, Delta/Devialet ou d’autres modèles n’est pas garantie.

### Logiciels

- Python **3.10 minimum** selon les dépendances ; environnement effectivement testé : **3.14**.
- Git pour cloner et versionner le projet.
- Accès Internet lors de l’installation des dépendances. Le pilotage lui-même passe par le réseau local.
- Un client MCP acceptant le transport stdio pour l’usage conversationnel. Claude Code est facultatif : les scripts de test fonctionnent sans lui et sans compte de modèle.

Les bibliothèques peuvent imposer des contraintes supplémentaires selon la version de Python ou le système. `requirements.lock.txt` conserve les versions exactes de l’environnement testé ; leur installation sur d’autres plateformes reste à vérifier.

## 2. Installation après clonage

Dans Terminal, remplacez `VOTRE_COMPTE` par le nom du compte GitHub qui hébergera le dépôt :

```bash
git clone https://github.com/VOTRE_COMPTE/freebox-mcp.git
cd freebox-mcp
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.lock.txt
```

Si `python3` est trop ancien, utilisez le chemin d’un interpréteur Python 3.10 ou supérieur pour créer l’environnement. Sur le Mac déjà configuré, l’environnement `.venv` existe : inutile de le recréer.

Alternative avec `uv`, s’il est déjà installé :

```bash
uv venv --python 3.14
uv pip sync --python .venv/bin/python requirements.lock.txt
```

`requirements.txt` liste les trois dépendances directes. Le fichier `requirements.lock.txt` fixe aussi leurs dépendances transitives pour reproduire l’environnement testé. Ce dernier est un relevé de versions, sans hachages de validation des distributions.

## 3. Configuration privée

Pour une nouvelle installation seulement :

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

Ne recopiez pas le modèle sur un `.env` déjà configuré : cela remplacerait ses valeurs.

Renseignez :

```dotenv
FREEBOX_PLAYER_HOST=192.168.1.100
FREEBOX_REMOTE_CODE=VOTRE_CODE_NUMERIQUE
```

L’adresse ci-dessus est un exemple. Remplacez-la par celle de votre Player, sans `http://`, sans port et sans chemin.

Pour le code, cherchez **Code télécommande réseau** dans les réglages/informations du Freebox Player affichés sur la TV. Le nom exact du menu peut varier selon le firmware. Enregistrez dans nano avec **Ctrl+O**, Entrée, puis quittez avec **Ctrl+X**.

Le fichier `.env` est masqué dans Finder : **Commande+Maj+point** affiche les fichiers cachés.

### Trouver l’adresse du bon boîtier

Consultez l’adresse IP dans les informations réseau du Player ou dans la liste des appareils de votre routeur. Le nom `freebox-player.local` peut fonctionner selon votre réseau. Une réservation DHCP peut stabiliser l’adresse IP.

Ne supposez pas que `hd1.freebox.fr` désigne votre Player : dans l’environnement testé, ce nom renvoyait une adresse publique. Le serveur vérifie que le nom configuré se résout vers des adresses privées avant l’envoi. L’utilisation d’une adresse IPv4 locale explicite est la méthode la plus simple ; la syntaxe IPv6 n’est pas prise en charge par le validateur de configuration actuel.

Les variables d’environnement du processus, si elles existent, ont priorité sur `.env`. Le fichier est lu à chaque appel : changer son code ne nécessite pas de redémarrer le serveur. Il est lu relativement à `server.py`, et non au dossier courant du Terminal.

## 4. Tester sans Claude Code

Toutes les commandes ci-dessous se lancent depuis la racine de ce dépôt.

### Tests unitaires : aucune action sur la TV

```bash
.venv/bin/python -m unittest discover -s . -p 'test_freebox.py' -v
```

Les quatre tests vérifient le refus des touches inconnues, le refus d’un code absent, l’absence du code dans le message d’erreur HTTP et la construction d’une touche avec appui long. Ils simulent le réseau : leur succès ne prouve pas la connexion au Player.

### Vérifier le protocole MCP et la réponse réseau

```bash
.venv/bin/python check_mcp.py
```

Le script démarre le serveur en stdio, découvre ses outils et appelle `connection_status`. Les outils attendus sont `connection_status`, `press_key`, `change_channel` et `adjust_volume`.

Cette sonde envoie une requête **sans touche et sans code**. Un HTTP 403 peut donc être attendu. Elle ne valide jamais le code : `remote_code_verified` reste `False`, même après une configuration correcte. `service_responded` signifie uniquement qu’une réponse HTTP a été reçue.

### Test réel du volume

Avec le Player allumé et un volume permettant de voir une variation :

```bash
.venv/bin/python test_live.py
```

Le script envoie **volume −1**, attend brièvement, puis envoie **volume +1**. Deux résultats contenant `accepted: True` indiquent que les deux requêtes ont été acceptées. Confirmez l’effet sur la TV.

Si le premier appel échoue, le script s’arrête. Si la baisse réussit mais que la hausse échoue, le volume peut rester un cran plus bas. Aux limites de volume, la séquence ne garantit pas le retour au même niveau.

### Depuis une conversation avec un agent

Un agent disposant d’un accès autorisé au Terminal de ce Mac et au réseau local peut exécuter ces scripts depuis le dépôt. C’est ainsi que le test a été réalisé dans la conversation de préparation.

Cloner le dépôt ne donne pas automatiquement à une conversation hébergée dans le cloud un accès à votre réseau domestique. Il faut soit un client MCP local, soit un agent avec accès explicite à la machine. Aucun compte ChatGPT ou Claude particulier n’est nécessaire pour les scripts Python eux-mêmes.

## 5. Raccordement facultatif à Claude Code

Depuis le dossier du dépôt, avec Claude Code déjà installé :

```bash
claude mcp add --transport stdio --scope project freebox -- "$PWD/.venv/bin/python" "$PWD/server.py"
claude mcp get freebox
claude
```

Approuvez la configuration du serveur du projet si Claude Code le demande. Dans une nouvelle session, `/mcp` permet de vérifier sa disponibilité. Les chemins sont absolus pour que le lancement ne dépende pas du dossier courant.

Alternative manuelle : copiez `.mcp.json.example` vers `.mcp.json`, puis remplacez les deux chemins d’exemple par les chemins absolus de votre clone. Ce fichier local est exclu de Git ; seul son modèle est partageable. Ne mettez pas le code de télécommande dans le JSON.

Exemples de demandes :

- « Baisse le volume de la Freebox d’un cran. »
- « Appuie sur Home sur la Freebox. »
- « Passe sur la chaîne 2. » (le Player doit déjà être en télévision en direct)

La configuration locale existante dans le dossier parent `TEMP` continue de pointer vers ce serveur. Le dépôt contient son propre exemple pour les futures installations.

## 6. Outils et limites

| Outil | Paramètres | Effet |
|---|---|---|
| `connection_status` | aucun | Sonde HTTP sans action sur la TV ; ne valide pas le code. |
| `press_key` | `key`, `long_press=False` | Envoie une touche autorisée, avec appui long optionnel. |
| `change_channel` | `channel` de 1 à 9999 | Saisit les chiffres du numéro ; nécessite le contexte TV. |
| `adjust_volume` | `direction`: `up`/`down`, `steps`: 1 à 10 | Envoie des pressions successives sur le volume. |

Touches déclarées : `power`, `home`, `back`, `up`, `down`, `left`, `right`, `ok`, `vol_inc`, `vol_dec`, `mute`, `prgm_inc`, `prgm_dec`, `red`, `green`, `yellow`, `blue`, `play`, `pause`, `stop`, `rec`, `fwd`, `bwd`, `next`, `prev`, `info`, `epg`, `tv`, et les chiffres `0` à `9`. Leur effet dépend du contexte et du firmware ; toutes n’ont pas été testées physiquement.

**Pas de lecture de l’état réel.** HTTP 200 indique l’acceptation d’une requête, pas une confirmation de la chaîne, du niveau sonore ou de l’alimentation. Aucun réglage absolu à « 50 % » ou « 100 % » n’est fourni. Une pression n’est pas une mesure garantie de pourcentage. Un volume HDMI, celui du téléviseur ou d’un amplificateur peut être indépendant.

`power` et `mute` sont des bascules. Ne les relancez pas automatiquement après une réponse incertaine. L’effet sur l’alimentation de la TV dépend notamment de sa configuration HDMI-CEC. Aucune automatisation horaire, ouverture fiable d’applications, API Freebox OS ou commande du routeur n’est implémentée.

## 7. Dépannage

| Symptôme | Vérification |
|---|---|
| HTTP 403 lors du test réel | Vérifier le code réseau du Player et l’adresse du boîtier ; ne pas utiliser le PIN parental. |
| HTTP 403 dans `check_mcp.py` uniquement | Possible pour la sonde anonyme ; lancer le test réel pour valider le code. |
| `Cannot reach Freebox Player` | Player allumé, bonne IP, même réseau, port 80 accessible, VPN/isolation réseau et permissions de l’agent. |
| `Cannot resolve` | Essayer l’IPv4 locale connue plutôt qu’un nom mDNS. |
| `must resolve to a private` | Le nom renvoie une adresse publique ; utiliser l’adresse privée du Player. |
| `Set FREEBOX_REMOTE_CODE` | Vérifier `.env`, sa valeur numérique et d’éventuelles variables d’environnement prioritaires. |
| MCP connecté, mais aucune action | La connexion MCP seule ne valide ni le code ni l’effet sur la TV. |
| `ModuleNotFoundError` | Utiliser `.venv/bin/python` et installer les dépendances dans cet environnement. |

## 8. Confidentialité et conditions d’utilisation

N’utilisez ce serveur que pour un appareil que vous êtes autorisé à contrôler. Il est prévu pour un réseau local de confiance. Le code est envoyé à l’API du Player par HTTP sans chiffrement : ne redirigez pas ce service vers Internet.

`.env`, les environnements Python, caches, journaux et la configuration MCP propre à la machine sont exclus de Git. Seul `.env.example`, vide de secret, doit être publié. Évitez les captures d’écran ou journaux contenant une URL de commande complète, car elle peut contenir le code. Les exclusions Git ne suppriment pas un secret déjà présent dans un ancien commit.

Aucune licence de réutilisation du code n’a été choisie pour ce dépôt. Avant d’encourager la redistribution ou les contributions publiques, choisissez une licence adaptée et ajoutez un fichier `LICENSE`. Les dépendances conservent leurs propres licences.

## 9. Publier plus tard sur GitHub

Le dépôt local est prêt sur la branche `main`. Aucune publication n’est réalisée par ces instructions tant que vous n’exécutez pas les commandes d’envoi.

### Vérifier ce qui sera partagé

```bash
git status --short
git ls-files
git check-ignore .env .venv .cache .DS_Store .mcp.json
```

L’absence de `.env` dans `git ls-files` est essentielle. Le fichier `.env.example`, lui, doit être présent. Vérifiez aussi votre identité Git avant de publier : le nom et l’adresse d’auteur des commits deviennent visibles avec le dépôt.

### Créer et envoyer le dépôt

Sur GitHub, créez un dépôt vide nommé par exemple `freebox-mcp`, public ou privé selon votre choix. Ne l’initialisez pas avec un README, une licence ou un `.gitignore`, puisque ces fichiers sont préparés localement. Une authentification GitHub valide en HTTPS ou SSH est nécessaire.

Depuis la racine du dépôt, remplacez `VOTRE_COMPTE` :

```bash
git remote add origin https://github.com/VOTRE_COMPTE/freebox-mcp.git
git push -u origin main
```

Si `origin` existe déjà, consultez d’abord `git remote -v` et vérifiez son adresse. Pour les modifications suivantes :

```bash
git add README.md server.py
git commit -m "Décrire la modification"
git push
```

Adaptez les noms de fichiers aux changements à publier. Ne forcez pas l’ajout du `.env` avec `git add -f`.

### Récupération par une autre personne

La personne clone le dépôt, installe les dépendances, copie `.env.example` vers `.env` et renseigne **l’adresse et le code de sa propre Freebox**. Votre fichier privé et votre environnement virtuel ne sont pas distribués.

## 10. Organisation du dépôt

```text
server.py                 Serveur et outils MCP
check_mcp.py              Découverte MCP et sonde sans action
test_live.py              Test physique du volume
test_freebox.py           Tests unitaires simulant le réseau
requirements.txt          Dépendances directes
requirements.lock.txt     Versions de l’environnement testé
.env.example              Modèle de configuration sans secret
.mcp.json.example         Modèle de configuration client
.gitignore                Exclusions des fichiers locaux
README.md                 Ce guide
```

## Documentation de référence

- [Ajouter un dépôt local à GitHub](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [Connecter Claude Code à un serveur MCP](https://code.claude.com/docs/en/mcp)
- [FastMCP](https://gofastmcp.com/)
