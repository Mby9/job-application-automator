import difflib
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database_dir import database
from services.ai_engine import semantic_match_fields

logger = logging.getLogger("copilot.semantic_matcher")

COMMON_SYNONYMS = {
    "first name": ["given name", "forename", "first"],
    "last name": ["surname", "family name", "last"],
    "full name": ["name", "complete name"],
    "email": ["email address", "e-mail"],
    "phone": ["phone number", "cell phone", "mobile", "telephone", "contact number"],
    "resume": ["cv", "resume/cv", "upload resume", "curriculum vitae"],
    "linkedin": ["linkedin profile", "linkedin url", "social profile"],
    "website": ["portfolio", "personal website", "github", "social link"],
    "location": ["city", "address", "current location", "where are you based"]
}

class HybridSemanticMatcher:
    def __init__(self, db: Session):
        self.db = db

    def _normalize(self, text: str) -> str:
        """Lowercase and strip characters to help with simple matching."""
        if not text: return ""
        return "".join(c for c in text.lower() if c.isalnum() or c.isspace()).strip()

    def get_cached_match(self, page_label: str) -> str:
        """Check the database for a previously learned match."""
        cached = self.db.query(database.LabelCache).filter(
            database.LabelCache.page_label == page_label
        ).first()
        return cached.stored_label if cached else None

    def save_match_to_cache(self, page_label: str, stored_label: str):
        """Save a new match to the database cache."""
        try:
            if not self.get_cached_match(page_label):
                new_cache = database.LabelCache(page_label=page_label, stored_label=stored_label)
                self.db.add(new_cache)
                self.db.commit()
        except Exception as e:
            logger.warning(f"Could not save to LabelCache: {e}")
            self.db.rollback()

    async def match_fields(self, current_labels: List[str], saved_labels: List[str]) -> Dict[str, str]:
        """
        Matches current page labels to saved labels using a hybrid approach:
        1. Exact & Synonym Match
        2. Database Cache (Result of previous AI matches)
        3. Fuzzy match (difflib)
        4. LLM fallback
        """
        results = {}
        missing_labels = []

        # Step 1 & 2: Local Matching (Heuristics + Cache)
        for label in current_labels:
            norm_label = self._normalize(label)
            matched = False
            
            # 1. Exact/Synonym Match
            for saved in saved_labels:
                norm_saved = self._normalize(saved)
                
                # Check exact
                if norm_label == norm_saved:
                    results[label] = saved
                    matched = True
                    break
                
                # Check synonyms
                found_syn = False
                if norm_saved in COMMON_SYNONYMS:
                    if norm_label in COMMON_SYNONYMS[norm_saved]:
                        found_syn = True
                
                if not found_syn:
                    for canonical, syns in COMMON_SYNONYMS.items():
                        if norm_label == canonical and norm_saved in syns:
                            found_syn = True
                            break
                
                if found_syn:
                    logger.info(f"Synonym Match: '{label}' -> '{saved}'")
                    results[label] = saved
                    matched = True
                    break
            
            if matched: continue

            # 2. persistent cache
            cached_val = self.get_cached_match(label)
            if cached_val and cached_val in saved_labels:
                logger.info(f"Cache Match: '{label}' -> '{cached_val}'")
                results[label] = cached_val
                continue
            
            missing_labels.append(label)

        if not missing_labels:
            return results

        # Step 3: Fuzzy Matching for remaining
        still_missing = []
        for label in missing_labels:
            norm_label = self._normalize(label)
            best_match = None
            best_ratio = 0.0
            
            for saved in saved_labels:
                norm_saved = self._normalize(saved)
                ratio = difflib.SequenceMatcher(None, norm_label, norm_saved).ratio()
                if ratio > 0.85 and ratio > best_ratio:
                    best_ratio = ratio
                    best_match = saved
            
            if best_match:
                logger.info(f"Fuzzy Match: '{label}' -> '{best_match}' (ratio: {best_ratio:.2f})")
                results[label] = best_match
            else:
                still_missing.append(label)

        if not still_missing:
            return results

        # Step 4: LLM Fallback
        logger.info(f"LLM Fallback required for labels: {still_missing}")
        try:
            ai_matches = await semantic_match_fields(still_missing, saved_labels)
            for page_label, stored_label in ai_matches.items():
                if page_label in current_labels and stored_label in saved_labels:
                    results[page_label] = stored_label
                    # Learn from the AI for next time!
                    self.save_match_to_cache(page_label, stored_label)
        except Exception as e:
            logger.error(f"LLM Semantic Match failed: {e}")

        return results
