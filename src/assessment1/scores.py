"""Fetch student scores from a REST API, calculate the mean, and chart them."""
import math

from .http_json import get_json

DEFAULT_SCORE_API_URL = "https://catalystprogrammers.in/dummy_api/get-students?page=1&limit=50"


def fetch_scores(api_url):
    payload = get_json(api_url)
    # The selected public demo API wraps its records in {"data": [...]} and
    # uses "name"; the assignment's generic contract uses a plain list and
    # "student". Accept both without guessing other response shapes.
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        payload = payload["data"]
    if not isinstance(payload, list) or not payload:
        raise ValueError("Scores API must return a non-empty JSON list")
    scores = []
    for index, record in enumerate(payload):
        if not isinstance(record, dict):
            raise ValueError(f"Score record {index + 1} must be a JSON object")
        name, score = record.get("student", record.get("name")), record.get("score")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Score record {index + 1} needs a student name")
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ValueError(f"Score for {name!r} must be numeric")
        try:
            numeric_score = float(score)
        except (OverflowError, ValueError) as exc:
            raise ValueError(f"Score for {name!r} is outside the supported numeric range") from exc
        if not math.isfinite(numeric_score) or numeric_score < 0:
            raise ValueError(f"Score for {name!r} must be finite and non-negative")
        scores.append((name.strip(), numeric_score))
    return scores


def calculate_average(scores):
    if not scores:
        raise ValueError("Cannot calculate an average without scores")
    return sum(value for _, value in scores) / len(scores)


def create_bar_chart(scores, output_path):
    if not scores:
        raise ValueError("Cannot chart an empty score list")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    average = calculate_average(scores)
    names, values = zip(*scores)
    figure, axis = plt.subplots(figsize=(10, max(6, len(scores) * 0.32)))
    bars = axis.barh(names, values, color="#315E9E")
    axis.axvline(average, color="#D87932", linestyle="--", label=f"Average: {average:.2f}")
    axis.bar_label(bars, fmt="%.1f", padding=3)
    axis.set_title("Student test scores")
    axis.set_xlabel("Score")
    axis.set_ylabel("Student")
    axis.invert_yaxis()
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)
    return average
