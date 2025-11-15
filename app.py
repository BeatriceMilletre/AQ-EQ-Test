import streamlit as st
import json
import os
import secrets
from datetime import date

# =========================
# CONFIG GÉNÉRALE
# =========================

st.set_page_config(
    page_title="AQ + EQ en ligne",
    page_icon="🧩",
    layout="wide",
)

DATA_DIR = "data_aq_eq"
os.makedirs(DATA_DIR, exist_ok=True)

# =========================
# OUTILS
# =========================

def generate_code(n_chars: int = 8) -> str:
    """Génère un code patient pseudo-aléatoire."""
    return secrets.token_hex(n_chars // 2).upper()


def save_response(patient_code: str, payload: dict):
    path = os.path.join(DATA_DIR, f"{patient_code}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load_response(patient_code: str):
    path = os.path.join(DATA_DIR, f"{patient_code}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# QUESTIONS
# =========================

AQ_ITEMS = {
    1: "Je préfère réaliser des activités avec d’autres personnes plutôt que seul(e).",
    2: "Je préfère tout faire continuellement de la même manière.",
    3: "Quand j’essaye d’imaginer quelque chose, il est très facile de m’en représenter une image mentalement.",
    4: "Je suis fréquemment tellement absorbé(e) par une chose que je perds tout le reste de vue.",
    5: "Mon attention est souvent attirée par des bruits discrets que les autres ne remarquent pas.",
    6: "Je fais habituellement attention aux numéros de plaques d’immatriculation ou à d’autres types d’informations de ce genre.",
    7: "Les gens me disent souvent que ce que j’ai dit était impoli, même quand je pense moi que c’était poli.",
    8: "Quand je lis une histoire, je peux facilement imaginer à quoi les personnages pourraient ressembler.",
    9: "Je suis fasciné(e) par les dates.",
    10: "Au sein d’un groupe, je peux facilement suivre les conversations de plusieurs personnes à la fois.",
    11: "Je trouve les situations de la vie en société faciles.",
    12: "J’ai tendance à remarquer certains détails que les autres ne voient pas.",
    13: "Je préfèrerais aller dans une bibliothèque plutôt qu’à une fête.",
    14: "Je trouve facile d’inventer des histoires.",
    15: "Je suis plus facilement attiré(e) par les gens que par les objets.",
    16: "J’ai tendance à avoir des centres d’intérêt très importants. Je me tracasse lorsque je ne peux m’y consacrer.",
    17: "J’apprécie le bavardage en société.",
    18: "Quand je parle, il n’est pas toujours facile pour les autres de placer un mot.",
    19: "Je suis fasciné(e) par les chiffres.",
    20: "Quand je lis une histoire, je trouve qu’il est difficile de me représenter les intentions des personnages.",
    21: "Je n’aime pas particulièrement lire des romans.",
    22: "Je trouve qu’il est difficile de se faire de nouveaux amis.",
    23: "Je remarque sans cesse des schémas réguliers dans les choses qui m’entourent.",
    24: "Je préfèrerais aller au théâtre qu’au musée.",
    25: "Cela ne me dérange pas si mes habitudes quotidiennes sont perturbées.",
    26: "Je remarque souvent que je ne sais pas comment entretenir une conversation.",
    27: "Je trouve qu’il est facile de « lire entre les lignes » lorsque quelqu’un me parle.",
    28: "Je me concentre habituellement plus sur l’ensemble d’une image que sur les petits détails de celle-ci.",
    29: "Je ne suis pas très doué(e) pour me souvenir des numéros de téléphone.",
    30: "Je ne remarque habituellement pas les petits changements dans une situation ou dans l’apparence de quelqu’un.",
    31: "Je sais m’en rendre compte quand mon interlocuteur s’ennuie.",
    32: "Je trouve qu’il est facile de faire plus d’une chose à la fois.",
    33: "Quand je parle au téléphone, je ne suis pas sûr(e) de savoir quand c’est à mon tour de parler.",
    34: "J’aime faire les choses de manière spontanée.",
    35: "Je suis souvent le(la) dernier(ère) à comprendre le sens d’une blague.",
    36: "Je trouve qu’il est facile de décoder ce que les autres pensent ou ressentent juste en regardant leur visage.",
    37: "Si je suis interrompu(e), je peux facilement revenir à ce que j’étais en train de faire.",
    38: "Je suis doué(e) pour le bavardage en société.",
    39: "Les gens me disent souvent que je répète continuellement les mêmes choses.",
    40: "Quand j’étais enfant, j’aimais habituellement jouer à des jeux de rôle avec les autres.",
    41: "J’aime collectionner des informations sur des catégories de choses (types de voitures, d’oiseaux, de trains, de plantes, ...).",
    42: "Je trouve qu’il est difficile de s’imaginer dans la peau d’un autre.",
    43: "J’aime planifier avec soin toute activité à laquelle je participe.",
    44: "J’aime les événements sociaux.",
    45: "Je trouve qu’il est difficile de décoder les intentions des autres.",
    46: "Les nouvelles situations me rendent anxieux(se).",
    47: "J’aime rencontrer de nouvelles personnes.",
    48: "Je suis une personne qui a le sens de la diplomatie.",
    49: "Je ne suis pas très doué(e) pour me souvenir des dates de naissance des gens.",
    50: "Je trouve qu’il est très facile de jouer à des jeux de rôle avec des enfants.",
}

EQ_ITEMS = {
    1: "Je peux facilement dire quand quelqu’un veut entamer une conversation.",
    2: "Je préfère les animaux aux êtres humains.",
    3: "J’essaie d’être à la mode.",
    4: "Je trouve difficile d’expliquer aux autres des choses que j’ai comprises facilement et que eux n’ont pas comprises du premier coup.",
    5: "Je rêve la plupart des nuits.",
    6: "J’aime prendre soin des autres.",
    7: "J’essaie de résoudre mes problèmes moi-même plutôt que d’en discuter avec d’autres.",
    8: "Je trouve difficile de savoir ce qu’il faut faire dans les relations sociales.",
    9: "C’est le matin que je suis le(la) plus efficace.",
    10: "On me dit souvent que je vais trop loin quand j’expose mon point de vue dans une discussion.",
    11: "Cela ne m’ennuie pas trop d’être en retard à un rendez-vous fixé à un ami.",
    12: "Les relations sociales sont si difficiles que j’essaie de ne pas m’en soucier.",
    13: "Je ne ferais jamais rien d’illégal même si ce n’est pas très grave.",
    14: "J’ai souvent du mal à juger si quelque chose est grossier ou familier.",
    15: "Dans une conversation, j’ai tendance à me centrer sur mes propres pensées plutôt que sur celles de mon interlocuteur.",
    16: "Je préfère les farces aux jeux de mots.",
    17: "Je vis au jour le jour.",
    18: "Quand j’étais enfant, j’aimais couper des vers de terre pour voir ce qui se passe.",
    19: "Je détecte rapidement si quelqu’un dit une chose qui en signifie une autre.",
    20: "J’ai de solides convictions sur la moralité.",
    21: "Je ne comprends pas comment des choses vexent tant certaines personnes.",
    22: "Il est pour moi facile de me mettre à la place de quelqu’un d’autre.",
    23: "Je pense que les bonnes manières sont la meilleure chose que des parents peuvent apprendre à leurs enfants.",
    24: "J’aime agir sur un coup de tête.",
    25: "Je prédis assez bien le ressenti des autres.",
    26: "Dans un groupe, je repère facilement quand quelqu’un se sent gêné ou mal à l’aise.",
    27: "Si j’offense quelqu’un en parlant, j’estime que c’est son problème et pas le mien.",
    28: "Si quelqu’un me demandait mon avis sur sa coupe de cheveux, je répondrais honnêtement même si elle ne me plaît pas.",
    29: "Je ne comprends pas toujours pourquoi une personne peut être offensée par une remarque.",
    30: "On me dit souvent que je suis imprévisible.",
    31: "En groupe, j’aime être le centre d’intérêt.",
    32: "Voir quelqu’un pleurer ne me touche pas vraiment.",
    33: "J’adore parler politique.",
    34: "Je ne mâche pas mes mots, ce qui est souvent pris pour de la grossièreté même si ce n’est pas mon intention.",
    35: "En général, je comprends facilement les situations sociales.",
    36: "On me dit généralement que je comprends bien les sentiments et les pensées des autres.",
    37: "Quand je discute avec quelqu’un, j’essaie de parler de ses expériences plutôt que des miennes.",
    38: "Ça me bouleverse de voir un animal souffrant.",
    39: "Je suis capable de prendre des décisions sans être influencé(e) par les sentiments des autres.",
    40: "Je ne peux pas me détendre sans avoir fait tout ce que j’avais planifié pour la journée.",
    41: "Je remarque facilement si quelqu’un est intéressé ou ennuyé par ce que je dis.",
    42: "Lorsque je regarde le journal télévisé, je suis triste de voir des personnes qui souffrent.",
    43: "Mes amis me parlent généralement de leurs problèmes car ils disent que je suis très compréhensif(ve).",
    44: "Je peux sentir quand je dérange les autres, même s’ils ne me le disent pas.",
    45: "Je commence souvent de nouveaux passe-temps qui m’ennuient vite et je passe à autre chose.",
    46: "Des fois, on me dit que j’exagère quand je charrie les gens.",
    47: "Je serais bien trop anxieux(se) de monter sur un manège de montagnes russes.",
    48: "On me dit souvent que je suis insensible même si je ne vois pas toujours pourquoi.",
    49: "Si je vois qu’il y a un nouveau venu dans un groupe de personnes, je crois que c’est à elles d’essayer de l’intégrer.",
    50: "D’habitude, je ne m’implique pas émotionnellement lorsque je regarde un film.",
    51: "J’aime être très organisé(e) dans ma vie de tous les jours, et je fais souvent des listes de ce que j’ai à faire.",
    52: "Je peux me mettre à l’écoute du ressenti des autres rapidement et intuitivement.",
    53: "Je n’aime pas prendre de risques.",
    54: "Je peux facilement comprendre ce que quelqu’un veut dire.",
    55: "Je peux deviner si quelqu’un masque ses émotions.",
    56: "Je pèse toujours le pour et le contre avant de prendre une décision.",
    57: "Je n’essaie pas de déchiffrer de façon consciente les règles en jeu dans les situations sociales.",
    58: "Je suis bon(ne) pour prédire ce que quelqu’un va faire.",
    59: "J’ai tendance à m’impliquer émotionnellement dans les problèmes de mes amis.",
    60: "Habituellement, je comprends le point de vue des autres même si je ne le partage pas.",
}

# Échelle de réponse (1 à 4)
ANSWER_LABELS = {
    1: "Tout à fait d’accord",
    2: "Plutôt d’accord",
    3: "Plutôt pas d’accord",
    4: "Pas du tout d’accord",
}

# =========================
# COTATION OFFICIELLE AQ / EQ
# =========================

# AQ : items où l’ACCORD (1 ou 2) = réponse "autistique"
AQ_AGREE_ITEMS = {
    2, 4, 5, 6, 7, 9, 12, 13,
    16, 18, 19, 20, 21, 22, 23,
    26, 33, 35, 39, 41, 42, 43,
    45, 46,
}

def is_aq_autistic(item: int, resp: int) -> bool:
    """Renvoie True si la réponse va dans le sens 'autistique' pour l’item AQ donné."""
    if resp is None:
        return False
    if item in AQ_AGREE_ITEMS:
        return resp in (1, 2)  # accord
    else:
        return resp in (3, 4)  # désaccord


def score_aq_officiel(aq_answers: dict) -> int:
    """
    Cotation officielle AQ (0–50).
    aq_answers : {item: 1–4}, avec 1/2 = accord, 3/4 = désaccord.
    """
    score = 0
    for item, resp in aq_answers.items():
        if is_aq_autistic(item, resp):
            score += 1
    return score


# Sous-échelles AQ (5 domaines de la publication originale)
AQ_SUBSCALES = {
    "A. Compétences sociales": [1, 11, 13, 15, 22, 36, 44, 45, 47, 48],
    "B. Flexibilité / Attention switching": [2, 4, 10, 16, 25, 32, 34, 37, 43, 46],
    "B’. Attention aux détails": [5, 6, 9, 12, 19, 23, 28, 29, 30, 49],
    "C. Communication": [7, 17, 18, 26, 27, 31, 33, 35, 38, 39],
    "D. Imagination": [3, 8, 14, 20, 21, 24, 40, 41, 42, 50],
}

def score_aq_subscales(aq_answers: dict) -> dict:
    """
    Retourne un dict {nom_sous_échelle: score (0–10)}.
    La logique de cotation (accord/désaccord) est la même que pour le score total.
    """
    subscores = {}
    for name, items in AQ_SUBSCALES.items():
        s = 0
        for item in items:
            resp = aq_answers.get(item)
            if is_aq_autistic(item, resp):
                s += 1
        subscores[name] = s
    return subscores


# === Grands blocs DSM A & B (analyse qualitative) ===

DSM_A_ITEMS = set(AQ_SUBSCALES["A. Compétences sociales"] + AQ_SUBSCALES["C. Communication"])
DSM_B_ITEMS = set(AQ_SUBSCALES["B. Flexibilité / Attention switching"] + AQ_SUBSCALES["B’. Attention aux détails"])

def build_dsm_blocks(aq_answers: dict) -> dict:
    """
    Construit les blocs A et B façon DSM, en listant les items AQ
    qui sont cotés dans le sens 'autistique', avec leur texte.
    """
    blockA = []
    blockB = []

    for item, resp in aq_answers.items():
        if not is_aq_autistic(item, resp):
            continue
        if item in DSM_A_ITEMS:
            blockA.append(f"{AQ_ITEMS[item]} (AQ{item})")
        if item in DSM_B_ITEMS:
            blockB.append(f"{AQ_ITEMS[item]} (AQ{item})")

    # Tri pour stabilité
    blockA_sorted = [p for _, p in sorted(zip([int(s.split('AQ')[1].rstrip(')')) for s in blockA], blockA))]
    blockB_sorted = [p for _, p in sorted(zip([int(s.split('AQ')[1].rstrip(')')) for s in blockB], blockB))]

    return {
        "A": blockA_sorted,
        "B": blockB_sorted,
    }


# EQ : cotation 0–80

EQ_EMPATHY_ITEMS = {
    1, 4, 6, 8, 10, 11, 12, 14, 15, 18,
    19, 21, 22, 25, 26, 27, 28, 29, 32, 34,
    35, 36, 37, 38, 39, 41, 42, 43, 44, 46,
    48, 49, 50, 52, 54, 55, 57, 58, 59, 60,
}

EQ_POSITIVE_AGREE = {
    1, 6, 19, 22, 25, 26,
    35, 36, 37, 38,
    41, 42, 43, 44,
    52, 54, 55,
    57, 58, 59, 60,
}
EQ_NEGATIVE_AGREE = EQ_EMPATHY_ITEMS - EQ_POSITIVE_AGREE

def score_eq_officiel(eq_answers: dict) -> int:
    """
    Cotation officielle EQ (0–80) :
    - 2 points pour la réponse la plus empathique
    - 1 point pour la réponse légèrement empathique
    - 0 sinon
    """
    score = 0
    for item, resp in eq_answers.items():
        if resp is None or item not in EQ_EMPATHY_ITEMS:
            continue

        if item in EQ_POSITIVE_AGREE:
            if resp == 1:
                score += 2
            elif resp == 2:
                score += 1
        else:  # item "reverse"
            if resp == 4:
                score += 2
            elif resp == 3:
                score += 1

    return score


# =========================
# UI – CHOIX DU MODE
# =========================

st.title("🧩 AQ + EQ en ligne")

mode = st.sidebar.radio(
    "Mode d’utilisation",
    ("Je suis un répondant (patient / participant)",
     "Je suis le praticien"),
)

# =========================
# MODE RÉPONDANT
# =========================

if mode.startswith("Je suis un répondant"):

    st.header("Passation des questionnaires AQ + EQ")

    with st.form("form_repondant"):

        st.subheader("Informations générales")

        patient_id = st.text_input("Identifiant (initiales ou code fourni)", "")
        sex = st.selectbox("Sexe", ["", "Féminin", "Masculin", "Autre"])
        dob = st.date_input(
            "Date de naissance",
            value=date(2000, 1, 1),
            format="DD/MM/YYYY",
        )
        test_date = st.date_input(
            "Date de passation",
            value=date.today(),
            format="DD/MM/YYYY",
        )
        practitioner_code = st.text_input(
            "Code praticien (fourni par votre psychologue / praticien)",
            "",
        )

        st.markdown("---")
        st.subheader("Questionnaire AQ (50 items)")

        aq_answers = {}
        for i, label in AQ_ITEMS.items():
            aq_answers[i] = st.radio(
                f"{i}. {label}",
                options=list(ANSWER_LABELS.keys()),
                format_func=lambda x, _labels=ANSWER_LABELS: _labels[x],
                horizontal=True,
                key=f"AQ_{i}",
            )

        st.markdown("---")
        st.subheader("Questionnaire EQ (60 items)")

        eq_answers = {}
        for i, label in EQ_ITEMS.items():
            eq_answers[i] = st.radio(
                f"{i}. {label}",
                options=list(ANSWER_LABELS.keys()),
                format_func=lambda x, _labels=ANSWER_LABELS: _labels[x],
                horizontal=True,
                key=f"EQ_{i}",
            )

        submitted = st.form_submit_button("Envoyer mes réponses")

    if submitted:
        # Générer un code patient
        patient_code = generate_code(8)

        payload = {
            "patient_code": patient_code,
            "patient_id": patient_id,
            "sex": sex,
            "dob": dob.isoformat(),
            "test_date": test_date.isoformat(),
            "practitioner_code": practitioner_code,
            "aq_answers": aq_answers,
            "eq_answers": eq_answers,
        }

        save_response(patient_code, payload)

        st.success("Merci, vos réponses ont été enregistrées.")
        st.info(
            f"Communiquez **ce code** à votre praticien : **{patient_code}**\n\n"
            "Les résultats détaillés seront discutés avec lui/elle."
        )

# =========================
# MODE PRATICIEN
# =========================

else:
    st.header("Espace praticien")

    with st.form("form_praticien"):
        patient_code = st.text_input("Code patient", "")
        submitted = st.form_submit_button("Charger les résultats")

    if submitted:
        data = load_response(patient_code.strip().upper())
        if data is None:
            st.error("Aucune donnée trouvée pour ce code patient.")
        else:
            st.subheader("Données générales du patient")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Identifiant** : {data.get('patient_id', '')}")
                st.write(f"**Code patient** : {data.get('patient_code', '')}")
                st.write(f"**Sexe** : {data.get('sex', '')}")
            with col2:
                st.write(f"**Date de naissance** : {data.get('dob', '')}")
                st.write(f"**Date de passation** : {data.get('test_date', '')}")
                st.write(f"**Code praticien enregistré** : {data.get('practitioner_code', '')}")

            # Les réponses sont stockées en JSON => clés en str
            aq_answers = {int(k): int(v) for k, v in data["aq_answers"].items()}
            eq_answers = {int(k): int(v) for k, v in data["eq_answers"].items()}

            # Scores officiels
            aq_score = score_aq_officiel(aq_answers)
            eq_score = score_eq_officiel(eq_answers)
            aq_subscores = score_aq_subscales(aq_answers)
            dsm_blocks = build_dsm_blocks(aq_answers)

            st.markdown("---")
            st.subheader("Synthèse des scores")

            c1, c2 = st.columns(2)
            with c1:
                st.metric("Score AQ (0–50)", aq_score)
                st.caption(
                    "AQ total (cotation officielle). "
                    "Un score ≥ 32 est souvent retrouvé chez les profils TSA/HFA."
                )
            with c2:
                st.metric("Score EQ (0–80)", eq_score)
                st.caption(
                    "EQ total (40 items d’empathie). "
                    "Les scores bas sont associés à une empathie plus faible."
                )

            st.markdown("### Sous-échelles AQ")
            sub_rows = []
            for name, items in AQ_SUBSCALES.items():
                sub_rows.append(
                    {
                        "Sous-échelle": name,
                        "Score": aq_subscores[name],
                        "Max": len(items),
                    }
                )
            st.table(sub_rows)

            st.markdown("### Analyse qualitative – grands blocs DSM")

            st.markdown("#### A. Trouble qualitatif de l’interaction sociale")
            if dsm_blocks["A"]:
                for phrase in dsm_blocks["A"]:
                    st.markdown(f"- {phrase}")
            else:
                st.markdown("_Aucun item AQ cliniquement significatif dans ce bloc avec le seuil actuel._")

            st.markdown("#### B. Comportements, intérêts et activités restreints, répétitifs et stéréotypés")
            if dsm_blocks["B"]:
                for phrase in dsm_blocks["B"]:
                    st.markdown(f"- {phrase}")
            else:
                st.markdown("_Aucun item AQ cliniquement significatif dans ce bloc avec le seuil actuel._")

            st.markdown("---")
            st.subheader("Réponses détaillées AQ")

            aq_table = []
            for i in sorted(aq_answers.keys()):
                aq_table.append(
                    {
                        "Item": i,
                        "Réponse": ANSWER_LABELS[aq_answers[i]],
                    }
                )
            st.dataframe(aq_table, use_container_width=True)

            st.subheader("Réponses détaillées EQ")

            eq_table = []
            for i in sorted(eq_answers.keys()):
                eq_table.append(
                    {
                        "Item": i,
                        "Réponse": ANSWER_LABELS[eq_answers[i]],
                    }
                )
            st.dataframe(eq_table, use_container_width=True)
