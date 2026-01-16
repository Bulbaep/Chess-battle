# 🎮 Combat des IA - Claude vs GPT aux échecs

## 📋 Ce que fait ce programme

Ce script Python fait jouer automatiquement Claude (Anthropic) contre ChatGPT (OpenAI) aux échecs sur Lichess.

- ♟️  Parties Blitz (3 min + 2 sec/coup)
- 🔄 Relance automatique des parties
- 📊 Compteur de scores en temps réel
- 🌐 Parties visibles en direct sur Lichess

## 🚀 Installation

### 1. Vérifier que Python est installé
```cmd
python --version
```
Doit afficher Python 3.x

### 2. Les bibliothèques sont déjà installées
Vous avez déjà installé : anthropic, openai, berserk, python-chess, requests

## ⚙️ Configuration

### 1. Modifier config.py (si nécessaire)

Ouvrez `config.py` et vérifiez/modifiez :
- Le nom d'utilisateur du bot GPT (si différent)
- Les modèles IA (si vous voulez tester d'autres modèles)

**Note** : Vos tokens et API keys sont déjà configurés !

## ▶️ Lancement

### Ouvrir CMD dans le dossier des fichiers

1. Ouvrez l'explorateur Windows
2. Allez dans le dossier contenant les fichiers
3. Dans la barre d'adresse, tapez `cmd` et appuyez sur Entrée
4. Ou faites Shift + Clic droit → "Ouvrir une fenêtre PowerShell ici"

### Lancer le programme

```cmd
python chess_battle.py
```

OU si ça ne marche pas :

```cmd
py chess_battle.py
```

## 🎥 Pour le stream

1. **Lancez le programme** → Il affichera les liens vers les parties Lichess
2. **Ouvrez le premier lien** dans votre navigateur
3. **Partagez l'écran de la partie Lichess** dans votre logiciel de streaming
4. **Gardez le terminal visible** (optionnel) pour montrer les scores

## 🛑 Arrêter le programme

Appuyez sur **Ctrl+C** dans le terminal.
Le programme s'arrêtera proprement et affichera les scores finaux.

## 📊 Comprendre l'affichage

```
🎮 PARTIE #1
📍 Lien : https://lichess.org/AbCd1234

♟️  Coup 1 | Claude (blancs) joue : e2e4
♟️  Coup 1 | GPT (noirs) joue    : e7e5
...

🏁 Partie terminée : mate
🏆 Victoire de Claude (blancs) !

===========================================
       🏆 COMBAT DES IA - SCORES GLOBAUX 🏆
===========================================
🤖 Claude (Blancs)  : 1 victoires
🤖 GPT    (Noirs)   : 0 victoires
⚖️  Nulles           : 0 parties
-------------------------------------------
📊 Total parties    : 1
⏱️  Temps écoulé     : 0h 8min
===========================================
```

## ⚠️ En cas de problème

### "ModuleNotFoundError"
Réinstallez les bibliothèques :
```cmd
py -m pip install anthropic openai berserk python-chess requests
```

### "API Error"
Vérifiez que vos API keys sont valides dans `config.py`

### "Challenge failed"
- Vérifiez que les deux bots sont bien connectés
- Vérifiez que les tokens Lichess sont valides
- Attendez quelques secondes et relancez

### Les IA jouent des coups invalides
C'est normal au début, le script réessaye automatiquement (max 3 fois)

## 💰 Coûts estimés

- **1 partie Blitz** : ~0.08-0.16$ (Claude + GPT)
- **1 heure de stream** (10 parties) : ~1-2$
- **Avec 5$ de crédits** : environ 30-60 parties

## 🎮 Profiter du stream

Vous pouvez :
- Commenter les coups en direct
- Analyser les stratégies des IA
- Prendre des paris sur le gagnant
- Créer des tournois multi-sessions

## 📝 Notes

- Les parties sont enregistrées sur Lichess
- Vous pouvez les revoir plus tard sur les profils des bots
- Les bots ne peuvent pas jouer de parties classées (rated)

Bon stream ! 🎮♟️
