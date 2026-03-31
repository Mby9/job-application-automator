from services.filter_engine import filter_jobs

jobs = [
    {"title": "Software Engineer", "location": "Toronto, ON", "company": "Shopify", "url": "http://a", "description": "", "ats_source": "greenhouse"},
    {"title": "Data Analyst", "location": "San Francisco, CA", "company": "Meta", "url": "http://b", "description": "", "ats_source": "lever"},
    {"title": "ML Engineer", "location": "Remote", "company": "Cohere", "url": "http://c", "description": "", "ats_source": "ashby"},
    {"title": "Product Manager", "location": "Toronto", "company": "Wealthsimple", "url": "http://d", "description": "", "ats_source": "greenhouse"},
]

# Test 1: Location + keyword filter
filtered = filter_jobs(
    jobs,
    preferred_locations=["Toronto", "Remote"],
    preferred_keywords=["Engineer"],
    remote_only=False,
    priority_companies=["Shopify"],
)
print(f"Test 1 - Location+Keyword filter: {len(filtered)} jobs (expect 2)")
for j in filtered:
    print(f"  [{'PRIORITY' if j['is_priority'] else '       '}] {j['title']} @ {j['company']} ({j['location']})")

assert len(filtered) == 2, f"Expected 2, got {len(filtered)}"
assert filtered[0]["company"] == "Shopify", "Priority company should be first"
assert not any(j["company"] == "Meta" for j in filtered), "San Francisco job should be filtered"
assert not any(j["company"] == "Wealthsimple" for j in filtered), "Product Manager should be filtered by keyword"

# Test 2: No keyword filter (accept all)
filtered2 = filter_jobs(
    jobs,
    preferred_locations=["Toronto", "Remote"],
    preferred_keywords=[],
    remote_only=False,
    priority_companies=[],
)
print(f"\nTest 2 - No keyword filter: {len(filtered2)} jobs (expect 3)")
assert len(filtered2) == 3, f"Expected 3, got {len(filtered2)}"

# Test 3: Remote only
filtered3 = filter_jobs(
    jobs,
    preferred_locations=[],
    preferred_keywords=[],
    remote_only=True,
    priority_companies=[],
)
print(f"\nTest 3 - Remote only: {len(filtered3)} jobs (expect 1)")
assert len(filtered3) == 1
assert filtered3[0]["company"] == "Cohere"

print("\nALL TESTS PASSED")
