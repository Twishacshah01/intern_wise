from flask import Flask, jsonify, request
from flask_cors import CORS
import json, math

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "works"

with open('internships.json', 'r', encoding='utf-8') as f:
    DATA = json.load(f)

def jaccard(a, b):
    A, B = set(x.lower() for x in a), set(x.lower() for x in b)
    inter = len(A & B)
    union = len(A | B) or 1
    return inter / union

def score(base, cand):
    s1 = jaccard(base.get("skills", []), cand.get("skills", []))
    s2 = jaccard(base.get("tags", []), cand.get("tags", []))
    s3 = 1.0 if base.get("city","").lower()==cand.get("city","").lower() else 0.0
    s4 = 1.0 if base.get("mode")==cand.get("mode") else 0.0
    return 0.5*s1 + 0.25*s2 + 0.15*s3 + 0.10*s4

@app.get("/api/internships")
def list_internships():
    city = request.args.get("city")
    skill = request.args.get("skill")
    mode = request.args.get("mode")  # Remote/Hybrid/On-site
    min_stipend = int(request.args.get("min_stipend", 0))
    results = DATA
    if city: results = [r for r in results if r["city"].lower()==city.lower()]
    if skill: results = [r for r in results if skill.lower() in [s.lower() for s in r["skills"]]]
    if mode: results = [r for r in results if r["mode"].lower()==mode.lower()]
    results = [r for r in results if r.get("stipend",0) >= min_stipend]
    return jsonify(results)

@app.get("/api/similar/<int:item_id>")
def similar(item_id):
    base = next((x for x in DATA if x["id"]==item_id), None)
    if not base: return jsonify([])
    scored = [
        {**c, "_score": round(score(base, c), 3)}
        for c in DATA if c["id"]!=item_id
    ]
    scored.sort(key=lambda x: x["_score"], reverse=True)
    return jsonify(scored[:10])

if __name__ == "__main__":
    app.run(debug=True)
