class Texts:
    # ── Welcome / Start ──
    WELCOME = (
        "🚀 <b>Bienvenue sur FollowBoost FR !</b>\n\n"
        "Le bot qui t'aide à grandir sur Instagram "
        "grâce à la communauté francophone. 🇫🇷\n\n"
        "🎮 <b>Comment ça marche ?</b>\n"
        "1️⃣ Tu enregistres ton compte Instagram\n"
        "2️⃣ Tu reçois des missions (comptes à suivre)\n"
        "3️⃣ Tu suis ces comptes, on vérifie ✅\n"
        "4️⃣ En échange, d'autres membres te suivent !\n\n"
        "⭐ En plus, tu gagnes des <b>Étoiles</b> pour chaque action.\n\n"
        "📸 <b>Envoie-moi ton nom d'utilisateur Instagram</b> (sans le @) pour commencer !"
    )

    WELCOME_BACK = (
        "👋 Content de te revoir, <b>{username}</b> !\n\n"
        "⭐ Tes Étoiles : <b>{etoiles}</b>\n"
        "📊 Niveau : {level_emoji} <b>{level}</b>\n"
        "🔥 Série : <b>{streak}</b> jour(s)\n\n"
        "Que veux-tu faire ?"
    )

    ASK_INSTAGRAM_USERNAME = (
        "📸 Envoie-moi ton <b>nom d'utilisateur Instagram</b> "
        "(sans le @) pour commencer :"
    )

    INSTAGRAM_VERIFYING = "🔍 Vérification de <b>@{username}</b> en cours..."

    INSTAGRAM_NOT_FOUND = (
        "❌ Compte Instagram <b>@{username}</b> introuvable.\n"
        "Vérifie l'orthographe et réessaie."
    )

    INSTAGRAM_PRIVATE = (
        "🔒 Ton compte <b>@{username}</b> est privé.\n"
        "Rends-le <b>public</b> pour participer au Follow-for-Follow."
    )

    INSTAGRAM_REGISTERED = (
        "✅ Parfait ! Ton compte <b>@{username}</b> est enregistré !\n\n"
        "🎁 Tu as reçu <b>+{bonus} ⭐ Étoiles</b> de bienvenue !\n\n"
        "Tape /mission pour recevoir ta première mission. 🎯"
    )

    INSTAGRAM_ALREADY_TAKEN = (
        "⚠️ Ce compte Instagram est déjà enregistré par un autre utilisateur."
    )

    INSTAGRAM_INVALID_FORMAT = (
        "⚠️ Format invalide. Envoie uniquement ton nom d'utilisateur Instagram "
        "(lettres, chiffres, points et underscores, max 30 caractères)."
    )

    # ── Referral Welcome ──
    REFERRAL_WELCOME_BONUS = (
        "🎉 Tu as été parrainé ! Ton parrain recevra <b>+{bonus} ⭐</b> grâce à toi."
    )

    # ── Missions ──
    MISSION_HEADER = (
        "🎯 <b>MISSION #{batch_num}</b>\n\n"
        "Suis ces <b>{count}</b> comptes Instagram :\n\n"
    )

    MISSION_ITEM = "  {i}. 📸 <b>@{username}</b>\n"

    MISSION_FOOTER = (
        "\n⏰ <i>Expire dans 24h</i>\n\n"
        "Une fois que tu les as tous suivis, "
        "appuie sur <b>✅ Vérifier</b> pour valider ta mission !"
    )

    MISSION_ALREADY_ACTIVE = (
        "⚠️ Tu as déjà une mission en cours !\n"
        "Termine-la d'abord ou attends qu'elle expire."
    )

    MISSION_NO_POOL = (
        "😕 Pas assez de comptes dans le pool pour l'instant.\n"
        "Reviens plus tard ou invite des amis avec /parrainage !"
    )

    MISSION_EXPIRED = "⏰ Ta mission a expiré. Demande-en une nouvelle avec /mission."

    MISSION_NOT_REGISTERED = (
        "⚠️ Tu dois d'abord enregistrer ton compte Instagram.\n"
        "Utilise /start pour commencer."
    )

    # ── Verification ──
    VERIFY_STARTING = "🔍 Vérification en cours... Cela peut prendre quelques secondes. ⏳"

    VERIFY_PROGRESS = "🔍 Vérification {current}/{total}..."

    VERIFY_SUCCESS_ALL = (
        "🎉 <b>Bravo ! Tous les follows sont vérifiés !</b>\n\n"
        "💰 <b>+{etoiles} ⭐ Étoiles</b> gagnées !\n"
        "⭐ Ton total : <b>{total} Étoiles</b>\n"
        "📊 Niveau : {level_emoji} <b>{level}</b>\n\n"
        "Tape /mission pour une nouvelle mission ! 🎯"
    )

    VERIFY_PARTIAL = (
        "📊 <b>Vérification terminée :</b>\n\n"
        "✅ Vérifiés : <b>{verified}/{total}</b>\n"
        "❌ Manquants :\n{missing}\n\n"
        "Suis les comptes manquants et réessaie avec <b>✅ Vérifier</b>."
    )

    VERIFY_NONE = (
        "❌ Aucun follow détecté.\n"
        "Assure-toi d'avoir suivi tous les comptes de ta mission."
    )

    VERIFY_NO_ACTIVE_MISSION = (
        "⚠️ Tu n'as pas de mission active.\n"
        "Tape /mission pour en recevoir une."
    )

    VERIFY_COOLDOWN = (
        "⏳ Patiente <b>{seconds}</b> secondes avant de relancer une vérification."
    )

    # ── Profile ──
    PROFILE = (
        "👤 <b>PROFIL</b>\n\n"
        "📸 Instagram : <b>@{instagram}</b>\n"
        "📊 Niveau : {level_emoji} <b>{level}</b>\n"
        "⭐ Étoiles : <b>{etoiles}</b>\n\n"
        "📈 <b>Statistiques</b>\n"
        "┣ Follows donnés : <b>{given}</b>\n"
        "┣ Follows reçus : <b>{received}</b>\n"
        "┣ Série actuelle : <b>{streak}</b> 🔥\n"
        "┗ Plus longue série : <b>{longest_streak}</b>\n\n"
        "🗓 Membre depuis : <b>{since}</b>\n\n"
        "🏅 <b>Badges</b> : {badges}"
    )

    NO_BADGES = "<i>Aucun badge pour l'instant</i>"

    # ── Levels ──
    LEVEL_EMOJIS = {
        "Debutant": "🌱",
        "Explorateur": "🧭",
        "Influenceur": "📸",
        "Star": "⭐",
        "Legende": "👑",
    }

    LEVEL_UP = (
        "🎊 <b>LEVEL UP !</b>\n\n"
        "Tu es maintenant {level_emoji} <b>{level}</b> !\n"
        "Continue comme ça ! 💪"
    )

    # ── Leaderboard ──
    LEADERBOARD_HEADER = "🏆 <b>CLASSEMENT - {board_type}</b>\n\n"

    LEADERBOARD_ROW = "{medal} {rank}. <b>{username}</b> — {value}\n"

    LEADERBOARD_EMPTY = "Le classement est vide pour l'instant ! 🏜"

    LEADERBOARD_YOUR_RANK = "\n📍 <b>Ton classement : #{rank}</b>"

    MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

    # ── Referral ──
    REFERRAL_INFO = (
        "🔗 <b>PARRAINAGE</b>\n\n"
        "Invite tes amis et gagne des Étoiles ! ⭐\n\n"
        "📎 <b>Ton lien de parrainage :</b>\n"
        "<code>{link}</code>\n\n"
        "🎁 <b>Récompenses :</b>\n"
        "┣ +{signup_bonus} ⭐ quand quelqu'un rejoint\n"
        "┗ +{mission_bonus} ⭐ quand il termine sa 1ère mission\n\n"
        "📊 <b>Tes stats :</b>\n"
        "┣ Filleuls : <b>{count}</b>\n"
        "┗ Étoiles gagnées : <b>{earned} ⭐</b>"
    )

    # ── Auto Mode ──
    AUTO_MODE_INFO = (
        "🚀 <b>MODE AUTO</b>\n\n"
        "Active le mode auto pour apparaître <b>3x plus souvent</b> "
        "dans les missions des autres !\n\n"
        "💰 Coût : <b>{cost} ⭐</b> pour 24h\n"
        "⭐ Tes Étoiles : <b>{current}</b>"
    )

    AUTO_MODE_ACTIVATED = (
        "✅ <b>Mode auto activé pour 24h !</b>\n"
        "Tu apparaîtras plus souvent dans les missions. 🚀"
    )

    AUTO_MODE_NOT_ENOUGH = (
        "❌ Tu n'as pas assez d'Étoiles.\n"
        "Il te faut <b>{cost} ⭐</b> (tu en as <b>{current}</b>)."
    )

    AUTO_MODE_ALREADY_ACTIVE = (
        "✅ Le mode auto est déjà actif jusqu'à <b>{until}</b>."
    )

    # ── Daily Checkin ──
    DAILY_CHECKIN = (
        "🌅 <b>Bonus quotidien !</b>\n"
        "+{etoiles} ⭐ | Série : {streak} jour(s) 🔥"
    )

    DAILY_CHECKIN_STREAK_BONUS = (
        "🎊 <b>BONUS SÉRIE {days} JOURS !</b>\n"
        "+{bonus} ⭐ Étoiles supplémentaires ! 🔥🔥🔥"
    )

    # ── Achievements ──
    ACHIEVEMENT_UNLOCKED = (
        "🏅 <b>BADGE DÉBLOQUÉ !</b>\n\n"
        "<b>{name}</b>\n"
        "<i>{description}</i>"
    )

    ACHIEVEMENT_DEFINITIONS = {
        "first_follow": ("Premier Pas 👣", "Tu as donné ton premier follow !"),
        "ten_follows": ("Followeur Assidu 💪", "10 follows donnés !"),
        "fifty_follows": ("Influenceur en Herbe 🌱", "50 follows donnés !"),
        "hundred_follows": ("Machine à Follow ⚡", "100 follows donnés !"),
        "first_referral": ("Ambassadeur 🤝", "Tu as parrainé ton premier ami !"),
        "five_referrals": ("Recruteur d'Élite 🎖", "5 filleuls actifs !"),
        "streak_7": ("Régulier 📅", "Série de 7 jours !"),
        "streak_30": ("Inarrêtable 🔥", "Série de 30 jours !"),
        "level_explorateur": ("Explorateur 🧭", "Tu as atteint le niveau Explorateur !"),
        "level_influenceur": ("Influenceur 📸", "Tu as atteint le niveau Influenceur !"),
        "level_star": ("Star ⭐", "Tu as atteint le niveau Star !"),
        "level_legende": ("Légende 👑", "Tu as atteint le niveau Légende !"),
        "auto_mode_first": ("Turbo 🚀", "Tu as activé le mode auto pour la première fois !"),
    }

    # ── Help ──
    HELP = (
        "📖 <b>AIDE - FollowBoost FR</b>\n\n"
        "🎮 <b>Commandes disponibles :</b>\n\n"
        "/start — Inscription / Accueil\n"
        "/mission — Recevoir une nouvelle mission\n"
        "/verifier — Vérifier tes follows\n"
        "/profil — Voir ton profil et tes stats\n"
        "/classement — Classement des joueurs\n"
        "/parrainage — Lien de parrainage\n"
        "/auto — Activer le mode automatique\n"
        "/parametres — Paramètres\n"
        "/aide — Cette aide\n\n"
        "🎯 <b>Comment ça marche ?</b>\n"
        "1. Enregistre ton Instagram\n"
        "2. Reçois des missions (5 comptes à suivre)\n"
        "3. Suis les comptes demandés\n"
        "4. Valide pour gagner des ⭐ Étoiles\n"
        "5. D'autres te suivent en retour !\n\n"
        "⭐ <b>Étoiles :</b>\n"
        "┣ +3 par follow donné (vérifié)\n"
        "┣ +1 par follow reçu\n"
        "┣ +2 bonus quotidien\n"
        "┣ +15 bonus série 7 jours\n"
        "┗ +10 par parrainage\n\n"
        "📊 <b>Niveaux :</b>\n"
        "🌱 Débutant → 🧭 Explorateur (51⭐) → "
        "📸 Influenceur (201⭐) → ⭐ Star (501⭐) → 👑 Légende (1001⭐)"
    )

    # ── Settings ──
    SETTINGS_MENU = "⚙️ <b>PARAMÈTRES</b>\n\nQue souhaites-tu modifier ?"

    SETTINGS_CHANGE_IG_PROMPT = (
        "📸 Envoie ton <b>nouveau nom d'utilisateur Instagram</b> (sans le @) :"
    )

    SETTINGS_IG_UPDATED = "✅ Ton Instagram a été mis à jour vers <b>@{username}</b>."

    SETTINGS_NOTIFICATIONS_ON = "🔔 Notifications <b>activées</b>."
    SETTINGS_NOTIFICATIONS_OFF = "🔕 Notifications <b>désactivées</b>."

    SETTINGS_DELETE_CONFIRM = (
        "⚠️ <b>Attention !</b>\n\n"
        "Cela supprimera définitivement ton compte et toutes tes données.\n"
        "Es-tu sûr(e) ?"
    )

    SETTINGS_DELETED = "✅ Ton compte a été supprimé. À bientôt ! 👋"

    # ── Notifications ──
    NOTIFICATION_NEW_FOLLOWER = (
        "🎉 <b>Nouveau follower !</b>\n\n"
        "Quelqu'un vient de te suivre sur Instagram grâce à FollowBoost !\n"
        "+1 ⭐ Étoile gagnée !"
    )

    # ── Errors ──
    ERROR_GENERIC = "❌ Oups, une erreur s'est produite. Réessaie plus tard."
    ERROR_NOT_REGISTERED = "⚠️ Tu n'es pas encore inscrit(e). Utilise /start pour commencer."
    ERROR_BANNED = "🚫 Ton compte a été suspendu. Contacte le support."
    ERROR_INSTAGRAM_SERVICE = (
        "⚠️ Le service Instagram est temporairement indisponible.\n"
        "Réessaie dans quelques minutes."
    )

    # ── Admin ──
    ADMIN_STATS = (
        "📊 <b>STATISTIQUES ADMIN</b>\n\n"
        "👥 Utilisateurs inscrits : <b>{total_users}</b>\n"
        "📋 Missions actives : <b>{active_missions}</b>\n"
        "✅ Follows vérifiés (total) : <b>{total_follows}</b>\n"
        "🚀 Mode auto actif : <b>{auto_mode_count}</b>"
    )

    ADMIN_SEED_SUCCESS = "✅ Compte <b>@{username}</b> ajouté au pool."
    ADMIN_SEED_FAIL = "❌ Impossible d'ajouter ce compte."
    ADMIN_BAN_SUCCESS = "✅ Utilisateur banni."
    ADMIN_UNBAN_SUCCESS = "✅ Utilisateur débanni."
