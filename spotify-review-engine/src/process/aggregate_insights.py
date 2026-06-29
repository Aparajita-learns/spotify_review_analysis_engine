"""
src/process/aggregate_insights.py
---------------------------------
Phase 5 — Insight aggregation and PM summary generation.
Aggregates classified themes and segments into PM-ready insights.
"""

from src.db.repository import get_client
from src.utils.logging import get_logger
from src.process.evidence_builder import get_evidence_for_theme, get_evidence_for_segment

logger = get_logger(__name__)

def generate_insights():
    """
    Analyzes document_themes and document_segments to generate actionable insights.
    Saves them to the `insights` table.
    """
    logger.info("Starting insight generation...")
    client = get_client()
    
    # 1. Clear existing insights
    client.table("insights").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    
    inserts = []
    
    # 2. Top Themes Insight
    # In standard SQL we'd do a GROUP BY, but via Supabase REST we might have to do it in memory for MVP, 
    # or use a raw RPC. For MVP, we can fetch all document_themes and count them in pandas, or just fetch the themes and their counts.
    # Actually, a simple REST approach: fetch all `document_themes` and count them.
    dt_res = client.table("document_themes").select("theme_id, themes(theme_name, theme_group, theme_code)").execute()
    
    theme_counts = {}
    theme_meta = {}
    
    for row in (dt_res.data or []):
        tid = row["theme_id"]
        theme_counts[tid] = theme_counts.get(tid, 0) + 1
        if tid not in theme_meta and row.get("themes"):
            theme_meta[tid] = row["themes"]
            
    # Check for repetitive_recommendations to always include it
    rep_rec_id = None
    for tid, meta in theme_meta.items():
        if meta.get("theme_code") == "repetitive_recommendations":
            rep_rec_id = tid
            break
            
    if rep_rec_id and theme_counts.get(rep_rec_id, 0) > 0:
        count = theme_counts[rep_rec_id]
        name = theme_meta[rep_rec_id]["theme_name"]
        group = theme_meta[rep_rec_id]["theme_group"]
        
        evidence = get_evidence_for_theme(rep_rec_id, limit=3)
        summary = f"Core Problem: '{name}' (part of {group}) continues to be reported, appearing in {count} reviews."
        if evidence:
            summary += "\n\n**User Quotes:**\n" + "\n".join([f'- "{e}"' for e in evidence])
            
        inserts.append({
            "insight_title": f"Top Friction: {name}",
            "insight_summary": summary,
            "insight_type": "friction",
            "supporting_doc_count": count,
            "theme_id": rep_rec_id,
            "segment_id": None
        })
        
        # Remove from dictionary so it doesn't duplicate in top themes
        del theme_counts[rep_rec_id]

    # Sort remaining themes by count
    sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    
    if sorted_themes:
        top_theme_id, top_theme_count = sorted_themes[0]
        top_theme_name = theme_meta[top_theme_id]["theme_name"]
        top_theme_group = theme_meta[top_theme_id]["theme_group"]
        
        evidence = get_evidence_for_theme(top_theme_id, limit=3)
        summary = f"The most prevalent issue reported by users is '{top_theme_name}' (part of {top_theme_group}), appearing in {top_theme_count} reviews."
        if evidence:
            summary += "\n\n**User Quotes:**\n" + "\n".join([f'- "{e}"' for e in evidence])
            
        inserts.append({
            "insight_title": f"Top Friction: {top_theme_name}",
            "insight_summary": summary,
            "insight_type": "friction" if "friction" in top_theme_group else "behavior",
            "supporting_doc_count": top_theme_count,
            "theme_id": top_theme_id,
            "segment_id": None
        })
        
        # Second top theme
        if len(sorted_themes) > 1:
            second_theme_id, second_theme_count = sorted_themes[1]
            second_theme_name = theme_meta[second_theme_id]["theme_name"]
            
            evidence2 = get_evidence_for_theme(second_theme_id, limit=3)
            summary2 = f"'{second_theme_name}' is also a major theme, appearing in {second_theme_count} reviews."
            if evidence2:
                summary2 += "\n\n**User Quotes:**\n" + "\n".join([f'- "{e}"' for e in evidence2])
                
            inserts.append({
                "insight_title": f"Key Theme: {second_theme_name}",
                "insight_summary": summary2,
                "insight_type": "pattern",
                "supporting_doc_count": second_theme_count,
                "theme_id": second_theme_id,
                "segment_id": None
            })

    # 3. Top Segments Insight
    ds_res = client.table("document_segments").select("segment_id, user_segments(segment_name)").execute()
    
    segment_counts = {}
    segment_meta = {}
    
    for row in (ds_res.data or []):
        sid = row["segment_id"]
        segment_counts[sid] = segment_counts.get(sid, 0) + 1
        if sid not in segment_meta and row.get("user_segments"):
            segment_meta[sid] = row["user_segments"]
            
    sorted_segments = sorted(segment_counts.items(), key=lambda x: x[1], reverse=True)
    
    if sorted_segments:
        top_seg_id, top_seg_count = sorted_segments[0]
        top_seg_name = segment_meta[top_seg_id]["segment_name"]
        
        evidence = get_evidence_for_segment(top_seg_id, limit=2)
        summary = f"The '{top_seg_name}' persona is the most vocal segment in the dataset, accounting for {top_seg_count} reviews."
        if evidence:
            summary += "\n\n**Representative Voices:**\n" + "\n".join([f'- "{e}"' for e in evidence])
            
        inserts.append({
            "insight_title": f"Dominant Persona: {top_seg_name}",
            "insight_summary": summary,
            "insight_type": "behavior",
            "supporting_doc_count": top_seg_count,
            "theme_id": None,
            "segment_id": top_seg_id
        })

    # 4. Save to DB
    if inserts:
        client.table("insights").insert(inserts).execute()
        logger.info(f"Generated and saved {len(inserts)} insights.")
    else:
        logger.warning("No data found to generate insights. Run Theme/Segment classification first.")
        
    return {"insights_generated": len(inserts)}

if __name__ == "__main__":
    res = generate_insights()
    print("Result:", res)
