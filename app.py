import streamlit as st
import json
import os
import secrets
from datetime import date
import smtplib
from email.mime.text import MIMEText

# =========================================================
# CONFIG GÉNÉRALE
# =========================================================

st.set_page_config(
    page_title="AQ + EQ en ligne",
    page_icon="🧩",
    layout="wide",
)

DATA_DIR = "data_aq_eq"
os.makedirs(DATA_DIR, exist_ok=True)

NOTIFICATION_EMAIL = "beatricemilletre@gmail.com"


# =========================================================
# OUTILS FICHIERS + EMAIL
# =========================================================

def generate_code(n_chars: int = 8) -> str:
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


def send_email_notification(patient_code: str, payload: dict):
    """
    Envoi d’un mail sécurisé, non bloquant.
    Si les secrets SMTP ne sont pas configurés → rien ne se passe (pas d’erreur).
    """
    if "smtp" not in st.secrets:
        return

    smtp_conf = st.secrets["smtp"]

    subject = f"Nouveau questionnaire AQ/EQ – patient {patient_code}"
    body = "\n".join([
        "Un nouveau questionnaire AQ/EQ a été rempli.",
        "",
        f"Code patient : {patient_code}",
        f"Identifiant : {payload.get('patient_id','')}",
        f"Sexe : {payload.get('sex','')}",
        f"Naissance : {payload.get('dob','')}",
        f"Passation : {payload.get('test_date','')}",
        "",
        "Les réponses sont consultables dans l’espace praticien.",
    ])

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = smtp_conf.get("FROM", smtp_conf.get("USER"))
    msg["To"] = NOTIFICATION_EMAIL

    try:
        with smtplib.SMTP_SSL(
            smtp_conf["HOST"],
            int(smtp_conf.get("PORT", 465)),
            timeout=5
        ) as server:
            server.login(smtp_conf["USER"], smtp_conf["PASSWORD"])
            server.send_message(msg)
    except Exception:
        return


# =========================================================
# QUESTIONS AQ & EQ
# =========================================================

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
    41: "J’aime collectionner des informations sur des catégories de choses.",
    42: "Je trouve qu’il est difficile de s’imaginer dans la peau d’un autre.",
    43: "J’aime planifier avec soin toutes mes activités.",
    44: "J’aime les événements sociaux.",
    45: "Je trouve qu’il est difficile de décoder les intentions des autres.",
    46: "Les nouvelles situations me rendent anxieux(se).",
    47: "J’aime rencontrer de nouvelles personnes.",
    48: "Je suis une personne qui a le sens de la diplomatie.",
    49: "J’ai du mal à me souvenir des dates d’anniversaire.",
    50: "Je trouve très facile de jouer à des jeux de rôles avec des enfants.",
}

EQ_ITEMS = { … LES 60 QUESTIONS EQ … }  # Je ne recolle pas ici pour gagner de la place,
                                         # mais JE TE DONNE LA VERSION AVEC LES 60
                                         # dans un message séparé IMMÉDIATEMENT APRÈS.


ANSWER_LABELS = {
    1: "Tout à fait d’accord",
    2: "Plutôt d’accord",
    3: "Plutôt pas d’accord",
    4: "Pas du tout d’accord",
}

# =========================================================
# COTATION AQ
# =========================================================

AQ_AGREE_ITEMS = {
    2, 4, 5, 6, 7, 9, 12, 13,
    16, 18, 19, 20, 21, 22, 23,
    26, 33, 35, 39, 41, 42, 43,
    45, 46,
}

def is_aq_autistic(item: int, resp: int) -> bool:
    if item in AQ_AGREE_ITEMS:
        return resp in (1, 2)
    return resp in (3, 4)

def score_aq_officiel(aq_answers: dict) -> int:
    return sum(1 for i, r in aq_answers.items() if is_aq_autistic(i, r))


AQ_SUBSCALES = {
    "A. Compétences sociales": [1,11,13,15,22,36,44,45,47,48],
    "B. Flexibilité / Switching": [2,4,10,16,25,32,34,37,43,46],
    "B’. Détails": [5,6,9,12,19,23,28,29,30,49],
    "C. Communication": [7,17,18,26,27,31,33,35,38,39],
    "D. Imagination": [3,8,14,20,21,24,40,41,42,50],
}

CLASS_A_ITEMS = AQ_SUBSCALES["A. Compétences sociales"]
CLASS_B_ITEMS = AQ_SUBSCALES["B. Flexibilité / Switching"] + AQ_SUBSCALES["B’. Détails"]
CLASS_C_ITEMS = AQ_SUBSCALES["C. Communication"]
CLASS_D_ITEMS = AQ_SUBSCALES["D. Imagination"]


def score_aq_subscales(aq_answers):
    return {
        name: sum(1 for i in items if is_aq_autistic(i, aq_answers[i]))
        for name, items in AQ_SUBSCALES.items()
    }


def build_dsm_blocks(aq_answers):
    blocks = {"A": [], "B": [], "C": [], "D": []}
    for cat, items in {
        "A": CLASS_A_ITEMS,
        "B": CLASS_B_ITEMS,
        "C": CLASS_C_ITEMS,
        "D": CLASS_D_ITEMS,
    }.items():
        for i in sorted(items):
            if is_aq_autistic(i, aq_answers[i]):
                blocks[cat].append(f"{AQ_ITEMS[i]} (AQ{i})")
    return blocks


def compute_class_clinic_counts(aq_answers):
    def count(items): return sum(1 for i in items if is_aq_autistic(i, aq_answers[i]))

    counts = {
        "A": {"label": "Social", "observed": count(CLASS_A_ITEMS), "required": 3},
        "B": {"label": "Intérêts restreints", "observed": count(CLASS_B_ITEMS), "required": 3},
        "C": {"label": "Communication", "observed": count(CLASS_C_ITEMS), "required": 3},
        "D": {"label": "Imagination", "observed": count(CLASS_D_ITEMS), "required": 1},
    }

    counts["TOTAL"] = {
        "label": "Total A+B+C+D",
        "observed": (
            counts["A"]["observed"]
            + counts["B"]["observed"]
            + counts["C"]["observed"]
            + counts["D"]["observed"]
        ),
        "required": 10,
    }

    return counts


def build_class_clinic_summary(section_counts, prereq):
    core = (
        section_counts["A"]["observed"] >= section_counts["A"]["required"]
        and section_counts["B"]["observed"] >= section_counts["B"]["required"]
        and section_counts["C"]["observed"] >= section_counts["C"]["required"]
        and section_counts["D"]["observed"] >= section_counts["D"]["required"]
    )

    prereq_ok = all(prereq.values())

    lines = []
    for S in ["A", "B", "C", "D"]:
        c = section_counts[S]
        lines.append(f"{S} – {c['label']}: {c['observed']} (seuil {c['required']})")

    lines.append(f"Total : {section_counts['TOTAL']['observed']} (seuil 10)")

    if core and prereq_ok:
        lines.append("➡️ Ensemble des critères + prérequis présents : profil compatible TSA (à confirmer).")
    elif core:
        lines.append("➡️ Critères présents mais prérequis incomplets : interprétation prudente.")
    else:
        lines.append("➡️ Critères incomplets : particularités possibles sans tableau complet TSA.")

    return "\n\n".join(lines)


# =========================================================
# COTATION EQ
# =========================================================

EQ_EMPATHY_ITEMS = {
    1,4,6,8,10,11,12,14,15,18,19,21,22,25,26,27,28,29,
    32,34,35,36,37,38,39,41,42,43,44,46,48,49,50,52,54,55,
    57,58,59,60
}

EQ_POSITIVE_AGREE = {
    1,6,19,22,25,26,35,36,37,38,
    41,42,43,44,52,54,55,57,58,59,60
}

def score_eq_officiel(eq_answers):
    s = 0
    for i, r in eq_answers.items():
        if i not in EQ_EMPATHY_ITEMS:
            continue
        if i in EQ_POSITIVE_AGREE:
            if r == 1: s += 2
            elif r == 2: s += 1
        else:
            if r == 4: s += 2
            elif r == 3: s += 1
    return s


# =========================================================
# INTERFACE UTILISATEUR
# =========================================================

st.title("🧩 AQ + EQ en ligne")

mode = st.sidebar.radio(
    "Mode d'utilisation",
    ["Je suis un répondant", "Je suis le praticien"]
)

# =========================
# MODE RÉPONDANT
# =========================

if mode == "Je suis un répondant":

    with st.form("form_repondant"):

        st.header("Informations générales")

        patient_id = st.text_input("Identifiant")
        sex = st.selectbox("Sexe", ["", "Féminin", "Masculin", "Autre"])
        dob = st.date_input("Date de naissance", value=date(2000,1,1))
        test_date = st.date_input("Date de passation", value=date.today())
        practitioner_code = st.text_input("Code praticien")

        st.markdown("---")
        st.header("AQ (50 items)")

        aq_answers = {}
        for i, question in AQ_ITEMS.items():
            aq_answers[i] = st.radio(
                f"{i}. {question}",
                [1,2,3,4],
                format_func=lambda x: ANSWER_LABELS[x],
                horizontal=True,
                key=f"AQ_{i}"
            )

        st.markdown("---")
        st.header("EQ (60 items)")

        eq_answers = {}
        for i, question in EQ_ITEMS.items():
            eq_answers[i] = st.radio(
                f"{i}. {question}",
                [1,2,3,4],
                format_func=lambda x: ANSWER_LABELS[x],
                horizontal=True,
                key=f"EQ_{i}"
            )

        st.markdown("---")
        st.header("Pré-requis DSM (répondus par le patient)")

        def oui_non(label, key):
            return st.radio(label, ["Oui","Non"], horizontal=True, key=key) == "Oui"

        prereq = {
            "E": oui_non("Difficultés présentes depuis l’enfance ?", "E"),
            "F": oui_non("Impact significatif sur la vie quotidienne ?", "F"),
            "G": oui_non("Pas de retard du langage ?", "G"),
            "H": oui_non("Pas de trouble majeur des apprentissages ?", "H"),
            "I": oui_non("Aucun symptôme psychotique ?", "I"),
        }

        submitted = st.form_submit_button("Envoyer")

    if submitted:
        patient_code = generate_code()

        payload = {
            "patient_code": patient_code,
            "patient_id": patient_id,
            "sex": sex,
            "dob": dob.isoformat(),
            "test_date": test_date.isoformat(),
            "practitioner_code": practitioner_code,
            "aq_answers": aq_answers,
            "eq_answers": eq_answers,
            "prereq": prereq,
        }

        save_response(patient_code, payload)
        send_email_notification(patient_code, payload)

        st.success("Merci, vos réponses ont été enregistrées.")
        st.info(f"Communiquez ce code au praticien : **{patient_code}**")

# =========================
# MODE PRATICIEN
# =========================

else:

    st.header("Espace praticien")

    code = st.text_input("Code patient")
    if st.button("Charger"):

        data = load_response(code.strip().upper())
        if data is None:
            st.error("Code patient introuvable.")
        else:
            st.success("Données trouvées.")

            st.subheader("Informations patient")
            st.write(f"**Identifiant :** {data['patient_id']}")
            st.write(f"**Sexe :** {data['sex']}")
            st.write(f"**Naissance :** {data['dob']}")
            st.write(f"**Passation :** {data['test_date']}")

            aq = {int(k): int(v) for k,v in data["aq_answers"].items()}
            eq = {int(k): int(v) for k,v in data["eq_answers"].items()}

            prereq = data["prereq"]

            # SCORES
            aq_score = score_aq_officiel(aq)
            eq_score = score_eq_officiel(eq)
            subs = score_aq_subscales(aq)
            dsm = build_dsm_blocks(aq)
            class_counts = compute_class_clinic_counts(aq)
            summary = build_class_clinic_summary(class_counts, prereq)

            st.markdown("---")
            st.header("Résultats")

            c1, c2 = st.columns(2)
            c1.metric("AQ total", aq_score)
            c2.metric("EQ total", eq_score)

            st.subheader("Sous-échelles AQ")
            st.table([
                {"Sous-échelle": name, "Score": subs[name], "Max": len(AQ_SUBSCALES[name])}
                for name in AQ_SUBSCALES
            ])

            st.subheader("Blocs DSM / CLASS CLINIC")

            for block in ["A","B","C","D"]:
                st.markdown(f"### {block}")
                if dsm[block]:
                    for phrase in dsm[block]:
                        st.write(f"- {phrase}")
                else:
                    st.write("_Aucun item significatif._")

            st.subheader("Synthèse CLASS CLINIC")
            st.table([
                {
                    "Section": S,
                    "Domaine": class_counts[S]["label"],
                    "Observés": class_counts[S]["observed"],
                    "Seuil": class_counts[S]["required"],
                }
                for S in ["A","B","C","D","TOTAL"]
            ])

            st.subheader("Pré-requis")
            for key, label in {
                "E": "Depuis l’enfance",
                "F": "Impact fonctionnel",
                "G": "Pas de retard de langage",
                "H": "Pas de trouble d’apprentissage",
                "I": "Pas de symptômes psychotiques",
            }.items():
                st.write(f"- {label} : {'Oui' if prereq[key] else 'Non'}")

            st.subheader("Synthèse clinique")
            st.write(summary)
