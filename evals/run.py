import re
import sys

import yaml

sys.path.insert(0, "assistant")
from ask import ask  # noqa: E402

THRESHOLD = 0.6


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text.replace(",", ".")).casefold()


cases = yaml.safe_load(open("evals/questions.yaml"))
passed = 0
for case in cases:
    answer = ask(case["question"])
    # TODO : ok = toutes les chaînes de must_contain sont dans answer
    #        (astuce : comparez sans espaces, et avec "." au lieu de "," pour les nombres)
    normalized_answer = normalize(answer or "")
    ok = all(normalize(expected) in normalized_answer for expected in case["must_contain"])
    # TODO : afficher PASS / FAIL, la question et la réponse ; compter passed
    print(f"{'PASS' if ok else 'FAIL'}: {case['question']}")
    print(f"Réponse : {answer}")
    if ok:
        passed += 1
score = passed / len(cases)
print(f"passed {passed}/{len(cases)} ({score:.0%})")
sys.exit(0 if score >= THRESHOLD else 1)   # code d'erreur sous le seuil : utilisable en CI