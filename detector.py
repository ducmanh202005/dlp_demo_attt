from __future__ import annotations

import re
from typing import Any, Dict, List

import joblib


class DataLeakDetector:
    def __init__(self, model_path: str = "models/model.joblib"):
        self.model_bundle = joblib.load(model_path)
        self.model = self.model_bundle["model"]
        self.vectorizer = self.model_bundle["vectorizer"]
        self.labels = self.model_bundle.get("labels", [])
        self.metrics = self.model_bundle.get("metrics", {})

        self.patterns = {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            "phone": re.compile(r"(?<!\d)(?:0|\+84)[0-9]{9,10}(?!\d)"),
            "cccd": re.compile(r"(?<!\d)\d{12}(?!\d)"),
            "bank_account": re.compile(r"(?<!\d)\d{8,16}(?!\d)"),
        }

        self.context_patterns = {
            "cccd": re.compile(
                r"(?:cccd|căn cước|chứng minh nhân dân)[^\d]{0,20}(?P<value>\d{12})",
                re.IGNORECASE,
            ),
            "bank_account": re.compile(
                r"(?:tài khoản ngân hàng|số tài khoản|stk)[^\d]{0,20}(?P<value>\d{8,16})",
                re.IGNORECASE,
            ),
        }

        self.leak_action_keywords = [
            "gửi",
            "send",
            "chia sẻ",
            "share",
            "đính kèm",
            "upload",
            "chuyển tiếp",
            "sao chép",
            "copy",
        ]
        self.external_keywords = [
            "ra ngoài",
            "bên ngoài",
            "email cá nhân",
            "gmail cá nhân",
            "google drive công khai",
            "đối tác",
            "usb riêng",
            "telegram riêng",
            "zalo bên ngoài",
            "máy tính ở nhà",
            "freelancer ngoài công ty",
            "tài khoản chat cá nhân",
            "công khai",
        ]

    def _find_matches(self, entity_name: str, text: str) -> List[str]:
        pattern = self.patterns[entity_name]
        return [match.group(0) for match in pattern.finditer(text)]

    def _find_contextual_numbers(self, entity_name: str, text: str) -> List[str]:
        pattern = self.context_patterns[entity_name]
        return [match.group("value") for match in pattern.finditer(text)]

    def detect_sensitive_entities(self, text: str) -> Dict[str, List[str]]:
        found: Dict[str, List[str]] = {}
        phone_numbers = set(self._find_matches("phone", text))
        cccd_numbers = set(self._find_contextual_numbers("cccd", text))
        if not cccd_numbers:
            cccd_numbers = set(self._find_matches("cccd", text))

        bank_account_numbers = set(self._find_contextual_numbers("bank_account", text))
        if not bank_account_numbers:
            bank_account_numbers = set(self._find_matches("bank_account", text))

        protected_numbers = phone_numbers | cccd_numbers

        email_matches = self._find_matches("email", text)
        if email_matches:
            found["email"] = email_matches

        if phone_numbers:
            found["phone"] = sorted(phone_numbers)

        if cccd_numbers:
            found["cccd"] = sorted(cccd_numbers)

        filtered_bank_accounts = [
            match for match in sorted(bank_account_numbers) if match not in protected_numbers
        ]
        if filtered_bank_accounts:
            found["bank_account"] = filtered_bank_accounts

        return found

    def score_risk(self, label: str, entities: Dict[str, List[str]], text: str) -> str:
        normalized_text = text.lower()
        has_sensitive_data = len(entities) > 0
        has_leak_action = any(keyword in normalized_text for keyword in self.leak_action_keywords)
        has_external_target = any(keyword in normalized_text for keyword in self.external_keywords)
        has_leak_context = has_leak_action and has_external_target

        if label == "leak_risk":
            return "Cao"
        if has_sensitive_data and has_leak_context:
            return "Cao"
        if label == "sensitive" or has_sensitive_data:
            return "Trung bình"
        if has_leak_context:
            return "Trung bình"
        return "Thấp"

    def analyze_text(self, text: str) -> Dict[str, Any]:
        entities = self.detect_sensitive_entities(text)
        X = self.vectorizer.transform([text])
        predicted_label = self.model.predict(X)[0]

        probabilities = None
        confidence = None
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(X)[0]
            probabilities = {
                cls: float(score)
                for cls, score in zip(self.model.classes_, proba)
            }
            confidence = max(probabilities.values())

        risk_level = self.score_risk(predicted_label, entities, text)

        return {
            "text": text,
            "predicted_label": predicted_label,
            "sensitive_entities": entities,
            "risk_level": risk_level,
            "probabilities": probabilities,
            "confidence": confidence,
        }
