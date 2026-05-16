#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Manual validation of stage5.schema.json against spec."""

import json
import sys

path = r'C:\xjp\代码\rag-demo\skills\aero-engine-assembly-scheme\templates\schemas\stage5.schema.json'

schema = json.loads(open(path, encoding='utf-8').read())

# ====== Check 1: required fields ======
print("=" * 60)
print("CHECK 1: Required Fields")
print("=" * 60)
expected_required = {"stage4b_ref", "review_panel", "kc_traceability_matrix", "overall_score", "recommendation", "uncertainty"}
actual_required = set(schema.get("required", []))
if expected_required == actual_required:
    print("✅ PASS: All required fields present")
    for f in expected_required:
        print(f"   - {f}")
else:
    print("❌ FAIL: Required fields mismatch")
    print(f"   Expected: {expected_required}")
    print(f"   Actual:   {actual_required}")
    print(f"   Missing:  {expected_required - actual_required}")
    print(f"   Extra:    {actual_required - expected_required}")

# ====== Check 2: review_panel ======
print("\n" + "=" * 60)
print("CHECK 2: review_panel field")
print("=" * 60)
rp = schema["properties"].get("review_panel", {})
checks = [
    ("type is array", rp.get("type") == "array"),
    ("minItems = 3", rp.get("minItems") == 3),
    ("maxItems = 3", rp.get("maxItems") == 3),
]
items_schema = rp.get("items", {})
item_checks = [
    ("items.type is object", items_schema.get("type") == "object"),
    ("items.required has [role, findings, severity_issues]",
     set(items_schema.get("required", [])) == {"role", "findings", "severity_issues"}),
    ("role enum", set(items_schema.get("properties", {}).get("role", {}).get("enum", []))
     == {"工艺工程师", "质量工程师", "设计工程师"}),
]
all_passed = True
for desc, passed in checks + item_checks:
    status = "✅" if passed else "❌"
    print(f"{status} {desc}")
    if not passed:
        all_passed = False

# Check severity enum inside severity_issues array
sev_items = items_schema.get("properties", {}).get("severity_issues", {}).get("items", {})
sev_enum = set(sev_items.get("properties", {}).get("severity", {}).get("enum", []))
expected_sev = {"low", "medium", "high"}
if sev_enum == expected_sev:
    print(f"✅ severity_issues items have correct enum")
else:
    print(f"❌ severity enum mismatch: expected {expected_sev}, got {sev_enum}")
    all_passed = False

sev_required = set(sev_items.get("required", []))
if sev_required == {"issue", "severity"}:
    print(f"✅ severity_issues items.required correct")
else:
    print(f"❌ severity_issues items.required mismatch: {sev_required}")
    all_passed = False

# ====== Check 3: kc_traceability_matrix ======
print("\n" + "=" * 60)
print("CHECK 3: kc_traceability_matrix field")
print("=" * 60)
ktm = schema["properties"].get("kc_traceability_matrix", {})
ktm_items = ktm.get("items", {})
ktm_required = set(ktm_items.get("required", []))
expected_ktm = {"kc_id", "kc_name", "procedures", "qc_checkpoints", "covered"}
if ktm_required == expected_ktm:
    print(f"✅ kc_traceability_matrix items.required correct")
else:
    print(f"❌ kc_traceability_matrix items.required mismatch")
    print(f"   Expected: {expected_ktm}")
    print(f"   Actual:   {ktm_required}")
    all_passed = False

# ====== Check 4: overall_score ======
print("\n" + "=" * 60)
print("CHECK 4: overall_score field")
print("=" * 60)
os_schema = schema["properties"].get("overall_score", {})
os_checks = [
    ("type is number", os_schema.get("type") == "number"),
    ("minimum = 0", os_schema.get("minimum") == 0),
    ("maximum = 5", os_schema.get("maximum") == 5),
]
for desc, passed in os_checks:
    status = "✅" if passed else "❌"
    print(f"{status} {desc}")
    if not passed:
        all_passed = False

# ====== Check 5: recommendation ======
print("\n" + "=" * 60)
print("CHECK 5: recommendation field")
print("=" * 60)
rec = schema["properties"].get("recommendation", {})
rec_enum = set(rec.get("enum", []))
expected_rec = {"approved", "approved_with_revision", "rejected"}
if rec_enum == expected_rec:
    print(f"✅ recommendation enum correct")
else:
    print(f"❌ recommendation enum mismatch")
    print(f"   Expected: {expected_rec}")
    print(f"   Actual:   {rec_enum}")
    all_passed = False

# ====== Check 6: uncertainty ======
print("\n" + "=" * 60)
print("CHECK 6: uncertainty field")
print("=" * 60)
unc = schema["properties"].get("uncertainty", {})
unc_enum = set(unc.get("enum", []))
expected_unc = {"高", "中", "低"}
if unc_enum == expected_unc:
    print(f"✅ uncertainty enum correct")
else:
    print(f"❌ uncertainty enum mismatch")
    print(f"   Expected: {expected_unc}")
    print(f"   Actual:   {unc_enum}")
    all_passed = False

# ====== Check 7: iterations ======
print("\n" + "=" * 60)
print("CHECK 7: iterations field (if present)")
print("=" * 60)
it = schema["properties"].get("iterations", {})
if it:
    it_items = it.get("items", {})
    it_required = set(it_items.get("required", []))
    expected_it = {"issue", "severity", "iterate_to", "reason"}
    if it_required == expected_it:
        print(f"✅ iterations items.required correct")
        it_sev = set(it_items.get("properties", {}).get("severity", {}).get("enum", []))
        if it_sev == {"low", "medium", "high"}:
            print(f"✅ iterations severity enum correct")
        else:
            print(f"❌ iterations severity enum mismatch: {it_sev}")
            all_passed = False
    else:
        print(f"❌ iterations items.required mismatch")
        print(f"   Expected: {expected_it}")
        print(f"   Actual:   {it_required}")
        all_passed = False
else:
    print("⚠️  iterations field not present (optional)")

# ====== Final Result ======
print("\n" + "=" * 60)
if all_passed:
    print("✅ OVERALL: Schema is COMPLIANT with spec")
else:
    print("❌ OVERALL: Schema has COMPLIANCE ISSUES")
print("=" * 60)
