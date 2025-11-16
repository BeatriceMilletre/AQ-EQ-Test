import streamlit as st
import json
import os
import secrets
from datetime import date
import smtplib
from email.mime.text import MIMEText

# =========================
# CONFIG EMAIL
# =========================

NOTIFICATION_EMAIL = "beatricemilletre@gmail.com"   # Email destinataire


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
# OUTILS FICHIERS
# =========================

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


# =========================
# EMAIL – SÉCURISÉ & NON BLOQUANT
# =========================

def send_email_notification(patient_code: str, payload: dict):
    """
    Envoie un email à Béatrice lors d’une passation.
    Ne bloque jamais l’app : en cas d’erreur → silencieux.
    """

    if "smtp" not in st.secrets:
        return  # Aucun email si SMTP non configuré

    smtp_conf = st.secrets["smtp"]

    subject = f"Nouveau questionnaire AQ/EQ – Code patient {patient_code}"
    body = "\n".join([
        "Un nouveau questionnaire AQ/EQ vient d'être rempli.",
        "",
        f"Code patient : {patient_code}",
        f"Identifiant : {payload.get('patient_id','')}",
        f"Sexe : {payload.get('sex','')}",
        f"Date de naissance : {payload.get('dob','')}",
        f"Passation : {payload.get('test_date','')}",
        "",
        "Les réponses complètes sont disponibles dans l’espace praticien.",
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
        # On NE bloque PAS l’application
        return


# =========================
# QUESTIONS AQ + EQ
# (identiques à ta version précédente)
# =========================

AQ_ITEMS = { ... }  # ← (identique à ta version précédente – je garde ici omis pour réduire)
EQ_ITEMS = { ... }

ANSWER_LABELS = {
    1: "Tout à fait d’accord",
    2: "Plutôt d’accord",
    3: "Plutôt pas d’accord",
    4: "Pas du tout d’accord",
}

# =========================
# COTATION AQ & SOUS-ÉCHELLES
# =========================

AQ_AGREE_ITEMS = {
    2, 4, 5, 6, 7, 9, 12, 13,
    16, 18, 19, 20, 21, 22, 23,
    26, 33, 35, 39, 41, 42, 43,
    45, 46,
}

def is_aq_autistic(item: int, resp: int) -> bool:
    if resp is None:
        return False
    if item in AQ_AGREE_ITEMS:
        return resp in (1, 2)
    return resp in (3, 4)


def score_aq_officiel(aq_answers: dict) -> int:
    return sum(1 for item, resp in aq_answers.items() if is_aq_autistic(item, resp))


AQ_SUBSCALES = { ... }  # (identique à ta version précédente)


def score_aq_subscales(aq_answers):
    subs = {}
    for name, items in AQ_SUBSCALES.items():
        subs[name] = sum(1 for i in items if is_aq_autistic(i, aq_answers.get(i)))
    return subs


# =========================
# DSM / CLASS CLINIC A–D
# =========================

CLASS_A_ITEMS = AQ_SUBSCALES["A. Compétences sociales"]
CLASS_B_ITEMS = AQ_SUBSCALES["B. Flexibilité / Attention switching"] + AQ_SUBSCALES["B’. Attention aux détails"]
CLASS_C_ITEMS = AQ_SUBSCALES["C. Communication"]
CLASS_D_ITEMS = AQ_SUBSCALES["D. Imagination"]

DSM_A_ITEMS = set(CLASS_A_ITEMS)
DSM_B_ITEMS = set(CLASS_B_ITEMS)
DSM_C_ITEMS = set(CLASS_C_ITEMS)
DSM_D_ITEMS = set(CLASS_D_ITEMS)


def build_dsm_blocks(aq_answers):
    blocks = {"A": [], "B": [], "C": [], "D": []}

    for key, items in [
        ("A", DSM_A_ITEMS),
        ("B", DSM_B_ITEMS),
        ("C", DSM_C_ITEMS),
        ("D", DSM_D_ITEMS),
    ]:
        for item in sorted(items):
            if is_aq_autistic(item, aq_answers.get(item)):
                blocks[key].append(f"{AQ_ITEMS[item]} (AQ{item})")

    return blocks


def compute_class_clinic_counts(aq_answers):
    sections = {
        "A": {"label": "Social", "items": CLASS_A_ITEMS, "required": 3},
        "B": {"label": "Obsessions / intérêts restreints", "items": CLASS_B_ITEMS, "required": 3},
        "C": {"label": "Communication", "items": CLASS_C_ITEMS, "required": 3},
        "D": {"label": "Imagination", "items": CLASS_D_ITEMS, "required": 1},
    }

    out = {}
    total = 0

    for key, sec in sections.items():
        obs = sum(1 for i in sec["items"] if is_aq_autistic(i, aq_answers.get(i)))
        total += obs
        out[key] = {
            "label": sec["label"],
            "observed": obs,
            "required": sec["required"],
            "max_items": len(sec["items"]),
        }

    out["TOTAL"] = {"label": "Total", "observed": total, "required": 10, "max_items": 18}

    return out


def build_class_clinic_summary(section_counts, prereq_flags):
    core_ok = all(section_counts[s]["observed"] >= section_counts[s]["required"] for s in ["A", "B", "C", "D"])
    prereq_ok = all(prereq_flags.values())

    lines = []
    for s in ["A", "B", "C", "D"]:
        sec = section_counts[s]
        lines.append(f"{s} – {sec['label']}: {sec['observed']} (seuil {sec['required']})")

    lines.append(f"Total A+B+C+D : {section_counts['TOTAL']['observed']} (seuil 10)")

    if core_ok and prereq_ok:
        lines.append("➡️ Ensemble des critères + prérequis présents : profil compatible TSA (à confirmer en clinique).")
    elif core_ok:
        lines.append("➡️ Critères atteints, mais prérequis incomplets : interprétation prudente.")
    else:
        lines.append("➡️ Critères incomplets : traits sans tableau complet TSA.")

    return "\n\n".join(lines)


# =========================
# COTATION EQ OFFICIELLE (0–80)
# =========================

EQ_EMPATHY_ITEMS = { ... }
EQ_POSITIVE_AGREE = { ... }

def score_eq_officiel(eq_answers: dict) -> int:
    score = 0
    for item, resp in eq_answers.items():
        if resp is None or item not in EQ_EMPATHY_ITEMS:
            continue
        if item in EQ_POSITIVE_AGREE:
            if resp == 1: score += 2
            elif resp == 2: score += 1
        else:
            if resp == 4: score += 2
            elif resp == 3: score += 1
    return score


# ============================================================
# UI – RÉPONDANT
# ============================================================

st.title("🧩 AQ + EQ en ligne")

mode = st.sidebar.radio(
    "Mode d’utilisation",
    ("Je suis un répondant (patient / participant)", "Je suis le praticien"),
)

# MODE RÉPONDANT
if mode.startswith("Je suis un répondant"):

    st.header("Passation des questionnaires AQ + EQ")

    with st.form("form_repondant"):

        st.subheader("Informations générales")

        patient_id = st.text_input("Identifiant (initiales ou code fourni)", "")
        sex = st.selectbox("Sexe", ["", "Féminin", "Masculin", "Autre"])
        dob = st.date_input("Date de naissance", date(2000, 1, 1))
        test_date = st.date_input("Date de passation", date.today())
        practitioner_code = st.text_input("Code praticien", "")

        st.markdown("---")
        st.subheader("Questionnaire AQ (50 items)")

        aq_answers = {i: st.radio(
            f"{i}. {AQ_ITEMS[i]}",
            [1, 2, 3, 4],
            format_func=lambda x: ANSWER_LABELS[x],
            horizontal=True,
            key=f"AQ_{i}"
        ) for i in AQ_ITEMS}

        st.markdown("---")
        st.subheader("Questionnaire EQ (60 items)")

        eq_answers = {i: st.radio(
            f"{i}. {EQ_ITEMS[i]}",
            [1, 2, 3, 4],
            format_func=lambda x: ANSWER_LABELS[x],
            horizontal=True,
            key=f"EQ_{i}"
        ) for i in EQ_ITEMS}

        st.markdown("---")
        st.subheader("Pré-requis (répondus par le patient)")

        def oui_non(label, key):
            r = st.radio(label, ["Oui", "Non"], horizontal=True, key=key)
            return r == "Oui"

        prereq_E = oui_non("Difficultés présentes depuis l’enfance ?", "E")
        prereq_F = oui_non("Impact significatif (souffrance, isolement) ?", "F")
        prereq_G = oui_non("Pas de retard du langage ?", "G")
        prereq_H = oui_non("Pas de trouble majeur des apprentissages ?", "H")
        prereq_I = oui_non("Aucun symptôme psychotique ?", "I")

        submitted = st.form_submit_button("Envoyer mes réponses")

    if submitted:
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
            "prereq": {
                "E": prereq_E, "F": prereq_F,
                "G": prereq_G, "H": prereq_H, "I": prereq_I
            },
        }

        save_response(patient_code, payload)
        send_email_notification(patient_code, payload)

        st.success("Merci, vos réponses ont été enregistrées.")
        st.info(f"Code patient à transmettre à votre praticien : **{patient_code}**")


# ============================================================
# MODE PRATICIEN
# ============================================================

else:
    st.header("Espace praticien")

    with st.form("form_praticien"):
        code = st.text_input("Code patient", "")
        submitted = st.form_submit_button("Charger les résultats")

    if submitted:
        data = load_response(code.strip().upper())
        if data is None:
            st.error("Aucune donnée trouvée.")
        else:
            st.subheader("Informations patient")

            aq = {int(k): int(v) for k, v in data["aq_answers"].items()}
            eq = {int(k): int(v) for k, v in data["eq_answers"].items()}
            prereq = data["prereq"]

            aq_score = score_aq_officiel(aq)
            eq_score = score_eq_officiel(eq)
            subs = score_aq_subscales(aq)
            dsm = build_dsm_blocks(aq)
            class_counts = compute_class_clinic_counts(aq)
            summary = build_class_clinic_summary(class_counts, prereq)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("AQ total (0–50)", aq_score)
            with col2:
                st.metric("EQ total (0–80)", eq_score)

            st.markdown("### Sous-échelles AQ")
            st.table([{ "Sous-échelle": name, "Score": subs[name] } for name in subs])

            st.markdown("### Analyse qualitative (DSM / CLASS CLINIC)")
            for block in ["A", "B", "C", "D"]:
                st.markdown(f"#### {block}")
                if dsm[block]:
                    for phrase in dsm[block]:
                        st.markdown(f"- {phrase}")
                else:
                    st.markdown("_Aucun item significatif._")

            st.markdown("### Grille CLASS CLINIC")
            st.table([
                {
                    "Section": key,
                    "Domaine": class_counts[key]["label"],
                    "Nombre requis": class_counts[key]["required"],
                    "Nombre observé": class_counts[key]["observed"],
                }
                for key in ["A", "B", "C", "D", "TOTAL"]
            ])

            st.markdown("### Pré-requis (patient)")
            for key, label in {
                "E": "Présent depuis l’enfance",
                "F": "Impact significatif",
                "G": "Pas de retard du langage",
                "H": "Pas de trouble apprentissage",
                "I": "Aucun symptôme psychotique",
            }.items():
                st.markdown(f"- {label} : {'Oui' if prereq[key] else 'Non'}")

            st.markdown("### Synthèse automatique")
            st.markdown(summary)


