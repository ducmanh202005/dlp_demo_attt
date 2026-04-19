from __future__ import annotations

import sys

from detector import DataLeakDetector


def print_model_summary(detector: DataLeakDetector) -> None:
    metrics = detector.metrics
    if not metrics:
        return

    print("Tóm tắt mô hình:")
    print(f"- Số mẫu dataset: {metrics.get('dataset_size')}")
    print(f"- Holdout accuracy: {metrics.get('test_accuracy')}")
    print(f"- Holdout macro F1: {metrics.get('test_macro_f1')}")

    cv_folds = metrics.get("cv_folds")
    cv_accuracy = metrics.get("cv_accuracy_mean")
    cv_macro_f1 = metrics.get("cv_macro_f1_mean")
    if cv_folds and cv_accuracy is not None and cv_macro_f1 is not None:
        print(f"- {cv_folds}-fold CV accuracy: {cv_accuracy}")
        print(f"- {cv_folds}-fold CV macro F1: {cv_macro_f1}")

    print()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    detector = DataLeakDetector("models/model.joblib")
    print_model_summary(detector)

    samples = [
        "Phòng vận hành vừa chốt timeline triển khai cho hồ sơ HS-2048-A, đồng thời cập nhật lên bảng nội bộ để cả nhóm theo dõi.",
        "Bộ phận chăm sóc khách hàng cần xác minh số điện thoại 0913456789 và email vip.customer@example.com của chị Lan, rồi cập nhật hồ sơ trên CRM nội bộ trước khi đóng ticket.",
        "Nhân viên mới đã tổng hợp số CCCD 123456789123 và tài khoản ngân hàng 880000001234 của khách, sau đó gửi sang Gmail cá nhân để tối nay làm tiếp ở nhà.",
        "Tổ triển khai dự án vừa rà soát ghi chú cuộc họp với khách, rồi gửi lịch làm việc cho team nội bộ trên hệ thống điều phối trước cuối ngày.",
    ]

    for text in samples:
        result = detector.analyze_text(text)
        print("=" * 100)
        print("Văn bản:", result["text"])
        print("Nhãn dự đoán:", result["predicted_label"])
        print("Dữ liệu nhạy cảm:", result["sensitive_entities"])
        print("Mức độ rủi ro:", result["risk_level"])
        print("Độ tin cậy:", result["confidence"])
        print("Xác suất:", result["probabilities"])


if __name__ == "__main__":
    main()
