# Contexte

Vous êtes data engineer chez Sport Data Solution qui est une start-up fondée par 2 sportifs :

Alexandre : Leader du groupe de vélo de route “les semis croustillants” et cofondateur de l’entreprise.

Juliette : Marathonienne convaincue et cofondatrice de l’entreprise.

L’activité de l’entreprise se concentre sur le développement de solutions de monitoring et d’analyse de performance, pour des sportifs amateurs et semi-professionnels.

Juliette, la cofondatrice de l’entreprise, est fermement convaincue que l’adoption d’un mode de vie actif et sain est un atout non seulement pour la performance individuelle mais aussi pour la dynamique collective au sein de l’entreprise. 

Elle souhaite ainsi intégrer davantage l’aspect sportif dans la culture d'entreprise, en incitant tous les employés à pratiquer une activité physique régulière. 

Dans cette optique, elle envisage de mettre en place un système d’avantages et de récompenses pour les salariés qui s'engagent dans des pratiques sportives régulières. L’objectif est de créer un environnement de travail qui valorise l’équilibre entre performance professionnelle et bien-être personnel, tout en renforçant l’esprit d’équipe et la santé de chacun.

Étant vous aussi un grand fan de sport, vous vous êtes proposé pour mener à bien cette mission. Vous êtes maintenant en charge du POC du projet avec la mise en place du pipeline de bout en bout : création, extraction, transformation, chargement, tests de qualité et monitoring continu.

Vous recevez un e-mail de Juliette, qui cadre la mission :

# Mail

    De : Juliette
    À :  Moi 
    Objet : Avantages sportifs

    Bonjour !
    J’espère que tu vas bien ! Comme discuté tout à l’heure, après avoir mis en place un système de récompense pour les employés qui prennent des actions concrètes pour l'environnement, nous souhaitons maintenant récompenser les sportifs et encourager la pratique du sport par tous. Je souhaite proposer à l’ensemble des collaborateurs des avantages s'ils ont une pratique du sport régulière. Je t’ai ajouté les fichiers en pièces jointes. 

    Pour cela, je souhaite qu’on lance un POC de la solution avant de l’annoncer.

    Ce POC vise à : 
        - Tester la faisabilité de la solution
        - Comprendre quelles données nous allons recueillir chez les salariés
        - Calculer l’impact financier pour l’entreprise de ces avantages supplémentaires. 

    Dans un premier temps, j’ai pensé a 2 avantages possibles : 
        - Une prime : Chaque salarié venant au bureau en faisant du sport (vélo, trottinette, course à pied, marche, etc.) bénéficiera d’une prime de 5% sur son salaire annuel brut. 
        - 5 journées “bien-être” par an : Tous les salariés qui ont une activité physique soutenue à côté de leur travail peuvent prétendre à 5 jours de “bien-être” pour la pratique de leur sport et améliorer leur récupération. 

    Nous souhaitons que chaque activité physique crée automatiquement une publication dans le channel slack associé pour favoriser l’émulation entre les salariés.

    Pour les deux options ci-dessus, les salariés doivent remplir certaines conditions détaillées dans la note de cadrage également en pièce jointe. 

    Pour la partie technique, tu es libre d’utiliser les outils que tu préfères, l’essentiel c’est que l’ensemble du projet soit robuste, sécurisé et fonctionnel. 

    Concernant la restitution du projet, pourras-tu : 
        - Présenter à l’aide d’un support, l’ensemble de ta solution (architecture, pipeline des données, monitoring, etc.) en justifiant tes choix ? 
        - Réaliser une démonstration live de ta solution. 
        - Présenter un rapport PowerBI avec les principaux indicateurs. Pense à permettre de relancer l’historique des indicateurs si jamais une source est modifiée (nous ne sommes pas à l’abri d’une modification du taux ou des données entrantes).

    N’hésite pas à me tenir au courant de ton avancement ou à me poser des questions si tu bloques sur certains points. 

    Merci et bon courage !

    Juliette

    Co-Fondatrice – Sport Data Solution

    Ps : Comme d’habitude, si tu vois des choses pertinentes à ajouter tu es également libre de le faire.

# Pieces jointes

- Données RH (fichier dans /data/RAW/Données+RH.xlsx)
- Données sportives (fichier dans /data/RAW/Données+Sportive.xlsx)
- Note de cadrage (fichier dans /_docs/ABAI_X1_note_cadrage.md)