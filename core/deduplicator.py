from models.database import SessionLocal
from models.opportunity import Opportunity

def process_opportunity(opp_data: dict, hash_val: str) -> bool:
    db = SessionLocal()
    if db.query(Opportunity).filter(Opportunity.hash == hash_val).first():
        db.close()
        return False
    new_opp = Opportunity(
        title=opp_data["title"],
        summary=opp_data.get("summary"),
        country=opp_data.get("country"),
        level=opp_data.get("level"),
        funding=opp_data.get("funding"),
        deadline=opp_data.get("deadline"),
        link=opp_data["link"],
        source=opp_data["source"],
        hash=hash_val
    )
    db.add(new_opp)
    db.commit()
    db.close()
    return True