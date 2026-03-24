# =========================================================
# 🤖 AUTONOMOUS AGENT FINAL (DB CONNECTED)
# =========================================================

from app.services.scoring import compute_smart_score
from app.services.decision_engine import decide
from app.services.application_builder import build_application_pack
from app.utils.logger import debug_log

from app.db.database import SessionLocal
from app.db.models import Job, Application


def run_autonomous_agent(cv_pdf_path, profile, max_jobs=5):

    debug_log("🚀 autonomous_agent lancé")

    db = SessionLocal()

    results = []

    try:
        # =====================================================
        # 🔥 1️⃣ FETCH JOBS FROM DB
        # =====================================================
        jobs_db = db.query(Job).all()

        # 🔥 CONVERSION ORM → DICT (CRITIQUE)
        jobs = [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "description": j.description,
                "location": j.location
            }
            for j in jobs_db
        ]

        print("📦 NB JOBS =", len(jobs))

        # =====================================================
        # 🔥 2️⃣ LOOP SUR JOBS
        # =====================================================
        for job in jobs:

            try:
                job_data = job  # déjà un dict

                # =========================
                # 3️⃣ SCORING
                # =========================
                score, details = compute_smart_score(job_data, profile)

                # =========================
                # 4️⃣ DÉCISION
                # =========================
                #decision = decide(score)
                decision = "APPLY"  # 🔥 debug

                print(f"🎯 {score} | {decision} | {job_data['title']}")

                if decision == "SKIP":
                    continue

               # =========================
                # 🔥 5️⃣ ANTI-DOUBLON
                # =========================
                exists = db.query(Application).filter(
                    Application.job_id == job_data["id"]
                ).first()
                
                already_applied = exists is not None
                
                if already_applied:
                    print("⏭️ Déjà traité MAIS affiché")
                # =========================
                # 6️⃣ GÉNÉRATION
                # =========================
                pack = build_application_pack(job_data, cv_pdf_path)

                if not pack:
                    continue

                # =========================
                # 🔥 7️⃣ SAVE EN DB
                # =========================
                application = Application(
                    user_id=1,
                    job_id=job_data["id"],
                    score=score,
                    decision=decision,
                    cover_letter=pack.cover_letter,
                    tailored_cv=str(pack)
                )

                db.add(application)

                # =========================
                # 8️⃣ RESULT
                # =========================
                results.append({
                    "job": job_data,
                    "score": score,
                    "decision": decision
                })

            except Exception as e:
                print(f"❌ ERREUR JOB: {e}")
                continue

        # =====================================================
        # 🔥 9️⃣ COMMIT DB
        # =====================================================
        db.commit()

    finally:
        db.close()

    # =====================================================
    # 🔥 10️⃣ TRI FINAL
    # =====================================================
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    print(f"\n✅ APPLICATIONS CRÉÉES = {len(results)}")

    return results[:max_jobs]