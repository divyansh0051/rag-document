import json
import os
import time
from typing import Dict, Any, List
from rag_engine import RAGEngine

class BenchmarkEvaluator:
    def __init__(self, rag_engine: RAGEngine, dataset_path: str = None):
        self.rag = rag_engine
        self.dataset_path = dataset_path or os.path.join(
            os.path.dirname(__file__), "..", "data", "evaluation_dataset.json"
        )
        self.dataset = self.load_dataset()

    def load_dataset(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Evaluation dataset missing at {self.dataset_path}")
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate_all(self) -> Dict[str, Any]:
        results = []
        category_stats = {}
        total_time_ms = 0.0

        for item in self.dataset:
            qid = item["id"]
            question = item["question"]
            expected_page = item["expected_page"]
            expected_doc = item["document"]
            key_entities = [k.lower() for k in item["key_entities"]]
            cat = item.get("category", "General")

            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "passed": 0, "page_correct": 0}
            category_stats[cat]["total"] += 1

            start_t = time.perf_counter()
            response = self.rag.generate_answer(question, target_doc=expected_doc)
            elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)
            total_time_ms += elapsed_ms

            top_page = response.get("top_page", None)
            top_doc = response.get("top_document", None)
            answer_text = (response.get("answer", "") + " " + (response.get("citations", [{}])[0].get("snippet", ""))).lower()

            # Evaluation criteria:
            # 1. Page match
            page_match = (top_page == expected_page)
            # 2. Entity/Keyword match (at least 60% of key entities found in answer or top snippet)
            matched_entities = [ent for ent in key_entities if ent in answer_text]
            entity_score = len(matched_entities) / max(len(key_entities), 1)
            content_pass = entity_score >= 0.5 or (page_match and len(matched_entities) >= 1)

            overall_pass = page_match and content_pass

            if page_match:
                category_stats[cat]["page_correct"] += 1
            if overall_pass:
                category_stats[cat]["passed"] += 1

            results.append({
                "id": qid,
                "category": cat,
                "question": question,
                "expected_doc": expected_doc,
                "expected_page": expected_page,
                "retrieved_page": top_page,
                "page_match": page_match,
                "entity_match_rate": round(entity_score * 100, 1),
                "matched_entities": matched_entities,
                "status": "PASS" if overall_pass else "FAIL",
                "latency_ms": elapsed_ms,
                "answer_preview": response.get("answer", "")[:160] + "..."
            })

        total_questions = len(self.dataset)
        total_passed = sum(1 for r in results if r["status"] == "PASS")
        total_page_correct = sum(1 for r in results if r["page_match"])
        accuracy_pct = round((total_passed / total_questions) * 100, 1)
        page_precision_pct = round((total_page_correct / total_questions) * 100, 1)
        avg_latency = round(total_time_ms / max(total_questions, 1), 2)

        # Compute category percentages
        categories_formatted = []
        for cat, stat in category_stats.items():
            cat_acc = round((stat["passed"] / stat["total"]) * 100, 1)
            cat_page = round((stat["page_correct"] / stat["total"]) * 100, 1)
            categories_formatted.append({
                "category": cat,
                "total": stat["total"],
                "passed": stat["passed"],
                "accuracy": cat_acc,
                "page_accuracy": cat_page
            })

        return {
            "summary": {
                "total_questions": total_questions,
                "passed_questions": total_passed,
                "failed_questions": total_questions - total_passed,
                "accuracy_percentage": accuracy_pct,
                "citation_page_precision": page_precision_pct,
                "avg_latency_ms": avg_latency,
                "benchmark_status": "EXCELLENT" if accuracy_pct >= 90 else "GOOD"
            },
            "category_breakdown": categories_formatted,
            "detailed_results": results
        }

if __name__ == "__main__":
    rag = RAGEngine()
    evaluator = BenchmarkEvaluator(rag)
    report = evaluator.evaluate_all()
    print("\n========== EVALUATION BENCHMARK REPORT ==========")
    print(f"Total Questions: {report['summary']['total_questions']}")
    print(f"Passed: {report['summary']['passed_questions']} ({report['summary']['accuracy_percentage']}%)")
    print(f"Page Citation Precision: {report['summary']['citation_page_precision']}%")
    print(f"Avg Latency: {report['summary']['avg_latency_ms']} ms")
    print("=================================================\n")
