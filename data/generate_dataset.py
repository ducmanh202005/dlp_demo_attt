from __future__ import annotations

import csv
from pathlib import Path


OUTPUT_PATH = Path(__file__).with_name("dataset.csv")
TOTAL_NEW_ROWS = 2000
SAFE_NEW_ROWS = 667
SENSITIVE_NEW_ROWS = 667
LEAK_RISK_NEW_ROWS = 666

SEED_ROWS = [
    ("Họp nhóm lúc 3 giờ chiều nay", "safe"),
    ("Khách hàng cần hỗ trợ đổi mật khẩu", "safe"),
    ("Vui lòng gửi báo cáo doanh số quý 1", "safe"),
    ("Số điện thoại của khách là 0912345678", "sensitive"),
    ("Email của khách hàng là nguyenvana@gmail.com", "sensitive"),
    ("Số CCCD của anh ấy là 012345678901", "sensitive"),
    ("Gửi giúp tôi danh sách số điện thoại khách hàng sang email cá nhân", "leak_risk"),
    ("Đính kèm file chứa CCCD và tài khoản ngân hàng cho đối tác", "leak_risk"),
    ("Share thông tin khách hàng ra ngoài công ty", "leak_risk"),
]

DEPARTMENTS = [
    "Phòng kinh doanh",
    "Bộ phận vận hành",
    "Nhóm chăm sóc khách hàng",
    "Tổ triển khai dự án",
    "Phòng hỗ trợ kỹ thuật",
    "Bộ phận thẩm định",
    "Nhóm quản lý đơn hàng",
    "Phòng dịch vụ khách hàng",
    "Bộ phận hậu kiểm",
    "Tổ điều phối giao hàng",
    "Phòng phân tích dữ liệu",
    "Nhóm phát triển sản phẩm",
]

ACTORS = [
    "Bạn thực tập",
    "Nhân viên mới",
    "Chuyên viên vận hành",
    "Bạn cộng tác viên",
    "Nhân sự hỗ trợ dự án",
    "Điều phối viên ca tối",
    "Nhân viên kinh doanh",
    "Bạn phụ trách hồ sơ",
    "Chuyên viên đối soát",
    "Nhân viên chăm sóc khách hàng",
]

CUSTOMER_LAST_NAMES = [
    "Nguyễn",
    "Trần",
    "Lê",
    "Phạm",
    "Hoàng",
    "Vũ",
    "Phan",
    "Đặng",
    "Bùi",
    "Đỗ",
]

CUSTOMER_MIDDLE_NAMES = [
    "Minh",
    "Gia",
    "Thu",
    "Ngọc",
    "Hải",
    "Anh",
    "Quỳnh",
    "Thanh",
    "Bảo",
    "Khánh",
]

CUSTOMER_FIRST_NAMES = [
    "An",
    "Bình",
    "Chi",
    "Dương",
    "Giang",
    "Hà",
    "Huy",
    "Lan",
    "My",
    "Nam",
    "Nhi",
    "Phong",
    "Trang",
    "Vy",
]

SAFE_ACTIONS = [
    "cần rà soát",
    "đang cập nhật",
    "vừa tổng hợp",
    "sẽ chốt",
    "cần hoàn thiện",
    "đang đối chiếu",
    "vừa xác nhận",
    "chuẩn bị bàn giao",
]

SAFE_WORK_ITEMS = [
    "kế hoạch tuần",
    "lịch họp dự án",
    "biên bản đào tạo",
    "tiến độ xử lý ticket",
    "danh sách đầu việc nội bộ",
    "báo cáo vận hành",
    "timeline triển khai",
    "ghi chú cuộc họp",
    "mẫu trình bày demo",
    "nội dung họp với khách",
]

SAFE_FOLLOWUPS = [
    "cập nhật lên bảng nội bộ",
    "nhắc cả nhóm chuẩn bị tài liệu",
    "đồng bộ vào hệ thống quản lý công việc",
    "xác nhận lại với trưởng nhóm",
    "điều chỉnh thời gian họp cho phù hợp",
    "gửi lịch làm việc cho team nội bộ",
    "hoàn tất checklist trước cuối ngày",
    "ghi chú các đầu mục còn thiếu",
]

INTERNAL_SYSTEMS = [
    "CRM nội bộ",
    "cổng quản trị nghiệp vụ",
    "hệ thống ticket nội bộ",
    "bảng theo dõi của phòng",
    "wiki vận hành",
    "hệ thống điều phối",
    "kho hồ sơ số",
    "dashboard quản lý",
]

SENSITIVE_TASKS = [
    "hoàn tất bước xác minh",
    "đối chiếu hợp đồng",
    "xử lý yêu cầu hỗ trợ",
    "chuẩn bị lịch giao hàng",
    "cập nhật hồ sơ thanh toán",
    "mở khóa tài khoản",
    "kiểm tra thông tin định danh",
    "xác nhận chủ thể yêu cầu",
]

LEAK_ACTIONS = [
    "gửi file sang",
    "chuyển tiếp bảng dữ liệu cho",
    "upload tài liệu lên",
    "đính kèm danh sách vào thư gửi",
    "sao chép dữ liệu qua",
    "chia sẻ thư mục cho",
]

EXTERNAL_DESTINATIONS = [
    "Gmail cá nhân",
    "Google Drive công khai",
    "USB riêng",
    "nhóm Zalo bên ngoài",
    "đối tác chưa ký NDA",
    "tài khoản chat cá nhân",
    "máy tính ở nhà",
    "freelancer ngoài công ty",
    "nhóm Telegram riêng",
    "email cá nhân của quản lý cũ",
]

LEAK_PURPOSES = [
    "làm tiếp ở nhà",
    "gửi cho người quen hỗ trợ",
    "tham khảo trước khi họp ngoài công ty",
    "xử lý nhanh trên thiết bị cá nhân",
    "đối chiếu với bên thứ ba",
    "chia sẻ cho cộng tác viên ngoài",
    "soạn báo cáo riêng",
    "đem đi in bên ngoài",
]

CONNECTORS = [
    "sau đó",
    "đồng thời",
    "rồi",
    "trước khi",
    "để tiếp tục",
    "và",
]

SENSITIVE_FIELDS = [
    "số điện thoại",
    "email",
    "số CCCD",
    "tài khoản ngân hàng",
]


def pick(options: list[str], index: int, stride: int) -> str:
    return options[(index * stride + stride) % len(options)]


def case_code(index: int) -> str:
    return f"HS-{index + 1000:04d}-A"


def customer_name(index: int) -> str:
    last_name = pick(CUSTOMER_LAST_NAMES, index, 2)
    middle_name = pick(CUSTOMER_MIDDLE_NAMES, index, 3)
    first_name = pick(CUSTOMER_FIRST_NAMES, index, 5)
    return f"{last_name} {middle_name} {first_name}"


def phone(index: int) -> str:
    return f"09{(10000000 + index):08d}"


def email(index: int) -> str:
    return f"khachhang{index + 1:04d}@example.com"


def cccd(index: int) -> str:
    return f"{123456789000 + index:012d}"


def bank_account(index: int) -> str:
    return f"{880000000000 + index:012d}"


def sensitive_value(field_name: str, index: int) -> str:
    if field_name == "số điện thoại":
        return phone(index)
    if field_name == "email":
        return email(index)
    if field_name == "số CCCD":
        return cccd(index)
    return bank_account(index)


def build_safe_row(index: int) -> tuple[str, str]:
    department = pick(DEPARTMENTS, index, 1)
    action = pick(SAFE_ACTIONS, index, 3)
    work_item = pick(SAFE_WORK_ITEMS, index, 5)
    follow_up = pick(SAFE_FOLLOWUPS, index, 7)
    system_name = pick(INTERNAL_SYSTEMS, index, 9)
    connector = pick(CONNECTORS, index, 11)
    text = (
        f"{department} {action} {work_item} cho hồ sơ {case_code(index)}, "
        f"{connector} {follow_up} trên {system_name} trước cuối ngày."
    )
    return text, "safe"


def build_sensitive_row(index: int) -> tuple[str, str]:
    department = pick(DEPARTMENTS, index, 2)
    system_name = pick(INTERNAL_SYSTEMS, index, 3)
    task = pick(SENSITIVE_TASKS, index, 5)
    connector = pick(CONNECTORS, index, 7)
    customer = customer_name(index)
    first_field = pick(SENSITIVE_FIELDS, index, 11)
    second_field = pick(SENSITIVE_FIELDS, index + 1, 13)
    first_value = sensitive_value(first_field, index)
    second_value = sensitive_value(second_field, index + 50)

    if index % 2 == 0:
        entity_phrase = f"{first_field} {first_value} của khách {customer}"
    else:
        entity_phrase = (
            f"{first_field} {first_value} và {second_field} {second_value} "
            f"của khách {customer}"
        )

    text = (
        f"{department} cần xác minh {entity_phrase}, {connector} cập nhật hồ sơ lên "
        f"{system_name} để {task}."
    )
    return text, "sensitive"


def build_leak_risk_row(index: int) -> tuple[str, str]:
    actor = pick(ACTORS, index, 1)
    action = pick(LEAK_ACTIONS, index, 3)
    destination = pick(EXTERNAL_DESTINATIONS, index, 5)
    purpose = pick(LEAK_PURPOSES, index, 7)
    connector = pick(CONNECTORS, index, 9)
    customer = customer_name(index + 200)
    first_field = pick(SENSITIVE_FIELDS, index, 11)
    second_field = pick(SENSITIVE_FIELDS, index + 2, 13)
    first_value = sensitive_value(first_field, index + 200)
    second_value = sensitive_value(second_field, index + 400)

    if index % 3 == 0:
        payload = (
            f"{first_field} {first_value} của khách {customer}"
        )
    else:
        payload = (
            f"{first_field} {first_value} và {second_field} {second_value} "
            f"của khách {customer}"
        )

    text = (
        f"{actor} đã tổng hợp {payload}, {connector} {action} {destination} để {purpose}."
    )
    return text, "leak_risk"


def interleave_rows(
    safe_rows: list[tuple[str, str]],
    sensitive_rows: list[tuple[str, str]],
    leak_rows: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    merged_rows = list(SEED_ROWS)
    limit = max(len(safe_rows), len(sensitive_rows), len(leak_rows))

    for index in range(limit):
        if index < len(safe_rows):
            merged_rows.append(safe_rows[index])
        if index < len(sensitive_rows):
            merged_rows.append(sensitive_rows[index])
        if index < len(leak_rows):
            merged_rows.append(leak_rows[index])

    return merged_rows


def generate_rows() -> list[tuple[str, str]]:
    safe_rows = [build_safe_row(index) for index in range(SAFE_NEW_ROWS)]
    sensitive_rows = [build_sensitive_row(index) for index in range(SENSITIVE_NEW_ROWS)]
    leak_rows = [build_leak_risk_row(index) for index in range(LEAK_RISK_NEW_ROWS)]

    rows = interleave_rows(safe_rows, sensitive_rows, leak_rows)
    expected_total = len(SEED_ROWS) + TOTAL_NEW_ROWS
    if len(rows) != expected_total:
        raise ValueError(f"Expected {expected_total} rows but generated {len(rows)} rows.")

    unique_texts = {text for text, _ in rows}
    if len(unique_texts) != len(rows):
        raise ValueError("Generated dataset contains duplicate texts.")

    return rows


def write_dataset(rows: list[tuple[str, str]]) -> None:
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "label"])
        writer.writerows(rows)


def main() -> None:
    rows = generate_rows()
    write_dataset(rows)
    print(f"Da ghi {len(rows)} dong vao {OUTPUT_PATH}.")


if __name__ == "__main__":
    main()
