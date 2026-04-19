from __future__ import annotations

import html
from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from detector import DataLeakDetector


APP_TITLE = "Demo Phát Hiện Rò Rỉ Dữ Liệu"
APP_SUBTITLE = "Nạp câu mẫu, nhập tay hoặc tải file .txt / .csv để kiểm tra nhanh."
MODEL_PATH = Path("models/model.joblib")

SAMPLE_LIBRARY = [
    {
        "name": "Nghiệp vụ nội bộ",
        "text": (
            "Phòng vận hành vừa chốt timeline triển khai cho hồ sơ HS-2048-A, "
            "đồng thời cập nhật lên bảng nội bộ để cả nhóm theo dõi."
        ),
    },
    {
        "name": "Có dữ liệu nhạy cảm",
        "text": (
            "Bộ phận chăm sóc khách hàng cần xác minh số điện thoại 0913456789 "
            "và email vip.customer@example.com của chị Lan, rồi cập nhật hồ sơ "
            "trên CRM nội bộ trước khi đóng ticket."
        ),
    },
    {
        "name": "Rủi ro rò rỉ cao",
        "text": (
            "Nhân viên mới đã tổng hợp số CCCD 123456789123 và tài khoản ngân hàng "
            "880000001234 của khách, sau đó gửi sang Gmail cá nhân để tối nay làm tiếp ở nhà."
        ),
    },
]

LABEL_META = {
    "safe": {
        "title": "An toàn",
        "tone": "tone-safe",
        "description": "Văn bản nội bộ thông thường, chưa thấy tín hiệu rò rỉ.",
    },
    "sensitive": {
        "title": "Dữ liệu nhạy cảm",
        "tone": "tone-sensitive",
        "description": "Có thông tin nhạy cảm cần được kiểm soát chặt.",
    },
    "leak_risk": {
        "title": "Nguy cơ rò rỉ",
        "tone": "tone-risk",
        "description": "Có dấu hiệu chia sẻ dữ liệu nhạy cảm ra ngoài.",
    },
}

RISK_META = {
    "Thấp": {"tone": "tone-safe", "description": "Ngữ cảnh nhìn chung an toàn."},
    "Trung bình": {
        "tone": "tone-sensitive",
        "description": "Cần rà soát thêm vì có dữ liệu nhạy cảm hoặc ngữ cảnh đáng chú ý.",
    },
    "Cao": {
        "tone": "tone-risk",
        "description": "Nên cảnh báo ngay vì có tín hiệu rò rỉ rõ ràng.",
    },
}

ENTITY_LABELS = {
    "email": "Email",
    "phone": "Số điện thoại",
    "cccd": "CCCD",
    "bank_account": "Tài khoản ngân hàng",
}


def configure_page() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --paper: #f5efe2;
                --ink: #1d2a26;
                --olive: #4f684a;
                --amber: #a86b19;
                --brick: #8d3f2f;
                --panel: rgba(255, 251, 243, 0.88);
                --line: rgba(29, 42, 38, 0.12);
                --shadow: 0 18px 38px rgba(45, 48, 34, 0.10);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(211, 162, 74, 0.18), transparent 30%),
                    linear-gradient(160deg, #f7f1e3 0%, #fbf7ef 45%, #eef3e8 100%);
                color: var(--ink);
                font-family: "Aptos", "Segoe UI", sans-serif;
            }

            .block-container {
                padding-top: 1.3rem;
                padding-bottom: 2rem;
            }

            h1, h2, h3 {
                color: var(--ink);
                font-family: "Palatino Linotype", Georgia, serif;
            }

            .hero-card, .panel-card {
                background: var(--panel);
                border: 1px solid var(--line);
                border-radius: 24px;
                box-shadow: var(--shadow);
            }

            .hero-card {
                padding: 1.35rem 1.6rem;
                margin-bottom: 1rem;
            }

            .hero-tag {
                display: inline-block;
                padding: 0.28rem 0.66rem;
                border-radius: 999px;
                background: rgba(79, 104, 74, 0.10);
                color: var(--olive);
                font-size: 0.82rem;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }

            .hero-title {
                margin: 0.7rem 0 0.25rem 0;
                font-size: 2.25rem;
                line-height: 1.08;
            }

            .hero-copy {
                margin: 0;
                font-size: 1rem;
                line-height: 1.65;
                color: rgba(29, 42, 38, 0.84);
            }

            .panel-card {
                padding: 1.15rem 1.2rem;
                margin-bottom: 1rem;
            }

            .badge {
                display: inline-flex;
                align-items: center;
                padding: 0.34rem 0.74rem;
                border-radius: 999px;
                font-size: 0.86rem;
                font-weight: 700;
            }

            .tone-safe {
                background: rgba(79, 104, 74, 0.12);
                color: #2f5336;
            }

            .tone-sensitive {
                background: rgba(211, 162, 74, 0.20);
                color: #8a5b12;
            }

            .tone-risk {
                background: rgba(141, 63, 47, 0.15);
                color: #7b2f22;
            }

            .summary-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.8rem;
                margin-top: 0.7rem;
            }

            .summary-card {
                border-radius: 18px;
                padding: 0.95rem 1rem;
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid var(--line);
            }

            .summary-label {
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.07em;
                color: rgba(29, 42, 38, 0.62);
                margin-bottom: 0.35rem;
            }

            .summary-value {
                font-size: 1.08rem;
                font-weight: 800;
                line-height: 1.25;
            }

            .summary-help {
                font-size: 0.92rem;
                line-height: 1.48;
                color: rgba(29, 42, 38, 0.78);
                margin-top: 0.35rem;
            }

            .entity-card {
                border-radius: 18px;
                padding: 0.85rem 0.95rem;
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid var(--line);
                margin-bottom: 0.65rem;
            }

            .entity-title {
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: rgba(29, 42, 38, 0.62);
                margin-bottom: 0.3rem;
            }

            .entity-values {
                font-size: 0.97rem;
                line-height: 1.55;
                word-break: break-word;
            }

            .small-muted {
                color: rgba(29, 42, 38, 0.68);
                font-size: 0.92rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
def load_detector() -> DataLeakDetector:
    return DataLeakDetector(str(MODEL_PATH))


def bootstrap_state() -> None:
    if "input_text" not in st.session_state:
        st.session_state["input_text"] = SAMPLE_LIBRARY[0]["text"]
    if "selected_sample" not in st.session_state:
        st.session_state["selected_sample"] = SAMPLE_LIBRARY[0]["name"]


def label_title(label: str) -> str:
    return LABEL_META.get(label, {}).get("title", label)


def label_tone(label: str) -> str:
    return LABEL_META.get(label, {}).get("tone", "tone-sensitive")


def risk_tone(risk_level: str) -> str:
    return RISK_META.get(risk_level, {}).get("tone", "tone-sensitive")


def format_confidence(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value) * 100:.1f}%"


def render_header() -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-tag">Demo</div>
            <h1 class="hero-title">{APP_TITLE}</h1>
            <p class="hero-copy">{APP_SUBTITLE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def decode_text_file(file_bytes: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1258", "utf-16"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("latin-1", errors="replace")


def read_csv_bytes(file_bytes: bytes) -> pd.DataFrame:
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "cp1258", "latin-1"):
        try:
            return pd.read_csv(BytesIO(file_bytes), encoding=encoding, dtype=str).fillna("")
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    raise ValueError(f"Không đọc được file CSV: {last_error}")


def infer_text_column(df: pd.DataFrame) -> str:
    preferred_columns = ["text", "content", "message", "body", "noi_dung", "van_ban"]
    lowered = {column.lower(): column for column in df.columns}
    for preferred in preferred_columns:
        if preferred in lowered:
            return lowered[preferred]
    return df.columns[0]


def summarize_entities(entities: dict[str, list[str]]) -> str:
    if not entities:
        return ""

    parts = []
    for entity_name, values in entities.items():
        readable_name = ENTITY_LABELS.get(entity_name, entity_name)
        parts.append(f"{readable_name}: {', '.join(values)}")
    return " | ".join(parts)


@st.cache_data(show_spinner=False)
def analyze_uploaded_csv(file_bytes: bytes, text_column: str) -> pd.DataFrame:
    detector = load_detector()
    source_df = read_csv_bytes(file_bytes)

    if text_column not in source_df.columns:
        raise ValueError(f"Không tìm thấy cột `{text_column}` trong file CSV.")

    rows = []
    for raw_text in source_df[text_column].astype(str):
        text = raw_text.strip()
        if not text:
            rows.append(
                {
                    text_column: raw_text,
                    "predicted_label": "",
                    "risk_level": "",
                    "confidence": "",
                    "sensitive_entities": "",
                }
            )
            continue

        result = detector.analyze_text(text)
        rows.append(
            {
                text_column: raw_text,
                "predicted_label": result["predicted_label"],
                "risk_level": result["risk_level"],
                "confidence": format_confidence(result["confidence"]),
                "sensitive_entities": summarize_entities(result["sensitive_entities"]),
            }
        )

    return pd.DataFrame(rows)


def batch_result_to_csv(batch_df: pd.DataFrame) -> bytes:
    return batch_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


def render_input_panel() -> Any:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("### Nhập nội dung kiểm tra")

    sample_names = [sample["name"] for sample in SAMPLE_LIBRARY]
    selected_name = st.selectbox("Câu mẫu", options=sample_names, key="selected_sample")
    selected_text = next(
        sample["text"] for sample in SAMPLE_LIBRARY if sample["name"] == selected_name
    )

    action_col_1, action_col_2 = st.columns(2)
    with action_col_1:
        if st.button("Nạp câu mẫu", use_container_width=True):
            st.session_state["input_text"] = selected_text
    with action_col_2:
        if st.button("Xóa nội dung", use_container_width=True):
            st.session_state["input_text"] = ""

    uploaded_file = st.file_uploader(
        "Tải file .txt hoặc .csv",
        type=["txt", "csv"],
        accept_multiple_files=False,
    )

    if uploaded_file is not None and uploaded_file.name.lower().endswith(".txt"):
        file_bytes = uploaded_file.getvalue()
        txt_content = decode_text_file(file_bytes)
        st.caption(f"Đã tải file TXT: `{uploaded_file.name}`")
        if st.button("Dùng nội dung file TXT", use_container_width=True):
            st.session_state["input_text"] = txt_content

    st.text_area(
        "Văn bản cần kiểm tra",
        key="input_text",
        height=320,
        placeholder="Nhập hoặc dán nội dung nội bộ vào đây...",
    )
    st.caption("Mẹo: thử thêm email, số điện thoại, CCCD, tài khoản ngân hàng hoặc cụm như Gmail cá nhân.")
    st.markdown("</div>", unsafe_allow_html=True)

    return uploaded_file


def render_result_panel(result: dict[str, Any] | None) -> None:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("### Kết quả")

    if not result:
        st.info("Nhập văn bản bên trái để xem kết quả phân tích.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    predicted_label = result["predicted_label"]
    risk_level = result["risk_level"]
    label_info = LABEL_META.get(predicted_label, {})
    risk_info = RISK_META.get(risk_level, {})

    st.markdown(
        f"""
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-label">Nhãn dự đoán</div>
                <div class="summary-value">
                    <span class="badge {label_tone(predicted_label)}">
                        {label_info.get('title', predicted_label)}
                    </span>
                </div>
                <div class="summary-help">{label_info.get('description', '')}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Mức độ rủi ro</div>
                <div class="summary-value">
                    <span class="badge {risk_tone(risk_level)}">{risk_level}</span>
                </div>
                <div class="summary-help">{risk_info.get('description', '')}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">Độ tin cậy</div>
                <div class="summary-value">{format_confidence(result.get('confidence'))}</div>
                <div class="summary-help">Model càng tự tin thì tỷ lệ này càng cao.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Dữ liệu nhạy cảm phát hiện được")
    entities = result["sensitive_entities"]
    if not entities:
        st.success("Không phát hiện dữ liệu nhạy cảm.")
    else:
        for entity_name, values in entities.items():
            readable_name = ENTITY_LABELS.get(entity_name, entity_name)
            escaped_name = html.escape(readable_name)
            escaped_values = "<br>".join(html.escape(value) for value in values)
            st.markdown(
                f"""
                <div class="entity-card">
                    <div class="entity-title">{escaped_name}</div>
                    <div class="entity-values">{escaped_values}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    probabilities = result.get("probabilities") or {}
    if probabilities:
        st.markdown("#### Xác suất theo nhãn")
        sorted_items = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
        for label, score in sorted_items:
            st.write(f"**{label_title(label)}**: {score * 100:.2f}%")
            st.progress(float(score))
        st.caption("Thanh càng dài thì mô hình càng nghiêng về nhãn đó.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_csv_panel(uploaded_file: Any) -> None:
    if uploaded_file is None or not uploaded_file.name.lower().endswith(".csv"):
        return

    file_bytes = uploaded_file.getvalue()
    try:
        preview_df = read_csv_bytes(file_bytes)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Không đọc được file CSV: {exc}")
        return

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown("### Kết quả cho file CSV")

    column_col, info_col_1, info_col_2 = st.columns([1.4, 0.8, 0.8])
    with column_col:
        default_column = infer_text_column(preview_df)
        text_column = st.selectbox(
            "Cột chứa nội dung cần kiểm tra",
            options=list(preview_df.columns),
            index=list(preview_df.columns).index(default_column),
        )
    with info_col_1:
        st.metric("Số dòng", len(preview_df))
    with info_col_2:
        st.metric("Số cột", len(preview_df.columns))

    with st.spinner("Đang phân tích file CSV..."):
        batch_df = analyze_uploaded_csv(file_bytes, text_column)

    st.dataframe(batch_df, use_container_width=True, height=360)
    st.download_button(
        "Tải kết quả CSV",
        data=batch_result_to_csv(batch_df),
        file_name="ket_qua_phan_tich.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    configure_page()
    inject_styles()
    bootstrap_state()

    if not MODEL_PATH.exists():
        st.error("Chưa tìm thấy model. Hãy chạy `python train.py` trước.")
        st.stop()

    try:
        detector = load_detector()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Không thể tải model: {exc}")
        st.stop()

    render_header()

    input_col, result_col = st.columns([1.05, 0.95], gap="large")

    with input_col:
        uploaded_file = render_input_panel()

    text = st.session_state.get("input_text", "").strip()
    result = detector.analyze_text(text) if text else None

    with result_col:
        render_result_panel(result)

    render_csv_panel(uploaded_file)


if __name__ == "__main__":
    main()
