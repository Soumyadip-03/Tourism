"""test_api_client.py — Integration test for api_client module."""
import sys
sys.path.insert(0, ".")
import api_client

PASS = "PASS"
FAIL = "FAIL"
results = []

def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((status, name, detail))
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))

# ── Test 1: health ─────────────────────────────────────────────────────────
print("\n=== 1. Health ===")
h, e = api_client.get_health()
check("health no error", e is None, e)
check("health status ok", h and h.get("status") == "healthy", str(h))
check("health model present", h and "Balanced Linear SVM" in h.get("model",""), str(h))
check("health catalogue_entries=433", h and h.get("catalogue_entries") == 433, str(h))

# ── Test 2: options ─────────────────────────────────────────────────────────
print("\n=== 2. Options ===")
opts, e = api_client.get_options()
check("options no error", e is None, e)
check("22 provinces", opts and len(opts.get("provinces",[])) == 22)
check("4 seasons present", opts and len(opts.get("seasons",[])) == 4)
check("recommendation_classes present", opts and len(opts.get("recommendation_classes",[])) == 3)

# ── Test 3: valid recommendations ──────────────────────────────────────────
print("\n=== 3. Valid Recommendations ===")
payload = {
    "province": "Sichuan",
    "category": "Historical Culture",
    "max_ticket_price": 100.0,
    "season": "Autumn",
    "is_holiday": "No",
    "rank_class": "Highly Recommend",
    "top_n": 5,
}
recs, e = api_client.get_recommendations(payload)
check("recommendations no error", e is None, e)
check("count > 0", recs and recs.get("count", 0) > 0)
check("recommendations list present", recs and isinstance(recs.get("recommendations"), list))
if recs and recs.get("recommendations"):
    r0 = recs["recommendations"][0]
    check("rank=1 for first result", r0.get("rank") == 1)
    check("province filter honoured (Sichuan)", r0.get("province") == "Sichuan", r0.get("province"))
    check("ticket_price <= 100", (r0.get("ticket_price") or 0) <= 100, str(r0.get("ticket_price")))
    check("svm_decision_score present", "svm_decision_score" in r0)
    check("ranking_class=Highly Recommend", r0.get("ranking_class") == "Highly Recommend")
    for r in recs["recommendations"]:
        check(f"price filter #{r['rank']}", (r.get("ticket_price") or 0) <= 100.0)

# ── Test 4: invalid province ────────────────────────────────────────────────
print("\n=== 4. Invalid Province ===")
_, e = api_client.get_recommendations({"province": "NOTREAL", "rank_class": "Highly Recommend", "top_n": 5})
check("invalid province returns error message", e is not None, e[:80] if e else "")

# ── Test 5: empty results ────────────────────────────────────────────────────
print("\n=== 5. Empty Results (tight filters) ===")
r2, e2 = api_client.get_recommendations({
    "province": "Beijing",
    "category": "Natural Scenery",
    "max_ticket_price": 0,
    "rank_class": "Highly Recommend",
    "top_n": 10,
})
check("empty result no error", e2 is None, e2)
check("count=0 for no matches", r2 and r2.get("count") == 0)
check("message present", r2 and r2.get("message"))

# ── Test 6: cities_by_province ───────────────────────────────────────────────
print("\n=== 6. Cities By Province ===")
cbp = api_client.get_cities_by_province()
check("Sichuan in mapping", "Sichuan" in cbp)
check("Sichuan has cities", bool(cbp.get("Sichuan")))
check("Cheng Du Shi in Sichuan", "Cheng Du Shi" in cbp.get("Sichuan", []))

# ── Test 7: top_n bound respected ───────────────────────────────────────────
print("\n=== 7. top_n=3 respected ===")
r3, e3 = api_client.get_recommendations({"rank_class": "Highly Recommend", "top_n": 3})
check("top_n=3 no error", e3 is None, e3)
check("at most 3 results", r3 and len(r3.get("recommendations",[])) <= 3)

# ── Summary ──────────────────────────────────────────────────────────────────
print("\n=== SUMMARY ===")
passed = sum(1 for s,_,_ in results if s == PASS)
failed = sum(1 for s,_,_ in results if s == FAIL)
print(f"Passed: {passed} / {passed+failed}")
if failed:
    print("FAILED tests:")
    for s,n,d in results:
        if s == FAIL:
            print(f"  - {n}: {d}")
sys.exit(0 if failed == 0 else 1)

