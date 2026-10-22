"""Deterministic generator for synthetic bilingual export documents and ground-truth annotations.

Produces:
- 12 synthetic shipment packages (24 PDF documents: 12 Commercial Invoices, 12 Packing Lists).
- 24 corresponding ground-truth JSON annotation files with verified bounding boxes.
- manifest.json indexing packages, documents, scenarios, and dataset partitions.
- expected_comparisons.json specifying expected rule-based verification outcomes.
"""

import json
from decimal import Decimal
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Base output directory
OUTPUT_DIR = Path("data/synthetic_pilot")
DOCS_DIR = OUTPUT_DIR / "documents"
ANNOTATIONS_DIR = OUTPUT_DIR / "annotations"

PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.28, 841.89 points


def register_fonts() -> tuple[str, str]:
    """Register TrueType Unicode fonts supporting Vietnamese diacritics."""
    regular_font = "Helvetica"
    bold_font = "Helvetica-Bold"

    arial_path = Path("C:/Windows/Fonts/arial.ttf")
    arial_bold_path = Path("C:/Windows/Fonts/arialbd.ttf")

    if arial_path.exists() and arial_bold_path.exists():
        pdfmetrics.registerFont(TTFont("ArialUnicode", str(arial_path)))
        pdfmetrics.registerFont(TTFont("ArialUnicode-Bold", str(arial_bold_path)))
        regular_font = "ArialUnicode"
        bold_font = "ArialUnicode-Bold"

    return regular_font, bold_font


FONT_REGULAR, FONT_BOLD = register_fonts()


def pt_to_bbox(x: float, y_bottom: float, width: float, height: float) -> list[float]:
    """Convert bottom-left ReportLab coordinates to top-left [x_min, y_min, x_max, y_max] box."""
    x_min = round(x, 2)
    y_min = round(PAGE_HEIGHT - (y_bottom + height), 2)
    x_max = round(x + width, 2)
    y_max = round(PAGE_HEIGHT - y_bottom, 2)
    return [x_min, y_min, x_max, y_max]


def text_bbox(
    c: canvas.Canvas, font: str, size: float, x: float, y_baseline: float, text_str: str
) -> list[float]:
    """Calculate exact bounding box for a single-line string."""
    width = c.stringWidth(text_str, font, size)
    height = size * 1.05  # font cap height + small clearance
    descender = size * 0.2
    return pt_to_bbox(x, y_baseline - descender, width, height)


def build_package_definitions() -> list[dict]:
    """Define the 12 synthetic packages with exact scenario parameters."""
    return [
        {
            "pkg_id": "PKG-001",
            "lang": "en",
            "split": "train",
            "template": "classic_standard",
            "scenario_id": "CLEAN_BASELINE_EN",
            "category": "clean",
            "desc": "Clean baseline export shipment: English, perfect cross-document agreement.",
            "seller": {
                "name": "VINAFOOD EXPORT JSC",
                "addr": "120 Pasteur, Ben Nghe, District 1, Ho Chi Minh City, Vietnam",
            },
            "buyer": {
                "name": "PACIFIC GRAIN CORP",
                "addr": "450 Market Street, Suite 800, San Francisco, CA 94105, USA",
            },
            "order_no": "PO-2026-US-001",
            "inv_no": "INV-2026-001",
            "pl_no": "PL-2026-001",
            "inv_date": "2026-10-15",
            "pl_date": "2026-10-15",
            "pol": "Cat Lai, Ho Chi Minh",
            "pod": "Oakland, USA",
            "vessel": "EVER GIVEN V.045E",
            "currency": "USD",
            "incoterm": "FOB",
            "items": [
                {
                    "line": 1,
                    "sku": "CASHEW-W240",
                    "desc": "Vietnamese Cashew Kernels W240",
                    "qty": Decimal("1000.00"),
                    "unit": "BAGS",
                    "price": Decimal("85.00"),
                    "total": Decimal("85000.00"),
                    "gross_wt": Decimal("25500.00"),
                    "net_wt": Decimal("25000.00"),
                    "pkgs": 1000,
                    "pkg_type": "VACUUM BAGS",
                }
            ],
            "inv_qty_display": "1,000",
            "pl_qty_display": "1,000",
            "inv_gw_display": "25,500.00",
            "pl_gw_display": "25,500.00",
            "inv_nw_display": "25,000.00",
            "pl_nw_display": "25,000.00",
            "inv_total_display": "85,000.00",
            "pl_seller_name": "VINAFOOD EXPORT JSC",
            "pl_buyer_name": "PACIFIC GRAIN CORP",
            "pl_order_no": "PO-2026-US-001",
        },
        {
            "pkg_id": "PKG-002",
            "lang": "vi",
            "split": "train",
            "template": "modern_grid",
            "scenario_id": "CLEAN_BASELINE_VI",
            "category": "clean",
            "desc": "Bộ chứng từ xuất khẩu mẫu sạch: Tiếng Việt, các chứng từ hoàn toàn khớp.",
            "seller": {
                "name": "CÔNG TY CP NÔNG SẢN ĐÀ NẴNG",
                "addr": "Số 45 Đường Bạch Đằng, Quận Hải Châu, TP. Đà Nẵng, Việt Nam",
            },
            "buyer": {
                "name": "TOKYO TRADING CO., LTD.",
                "addr": "3-2-1 Marunouchi, Chiyoda-ku, Tokyo 100-0005, Japan",
            },
            "order_no": "DH-2026-TYO-02",
            "inv_no": "HD-2026-002",
            "pl_no": "PK-2026-002",
            "inv_date": "2026-10-18",
            "pl_date": "2026-10-18",
            "pol": "Cảng Tiên Sa, Đà Nẵng",
            "pod": "Cảng Yokohama, Nhật Bản",
            "vessel": "PACIFIC GLORY 102N",
            "currency": "USD",
            "incoterm": "CIF",
            "items": [
                {
                    "line": 1,
                    "sku": "PEPPER-BLACK-500",
                    "desc": "Tiêu đen xuất khẩu loại 500g/l",
                    "qty": Decimal("20.00"),
                    "unit": "TẤN",
                    "price": Decimal("4200.00"),
                    "total": Decimal("84000.00"),
                    "gross_wt": Decimal("20400.00"),
                    "net_wt": Decimal("20000.00"),
                    "pkgs": 400,
                    "pkg_type": "BAO ĐAY",
                }
            ],
            "inv_qty_display": "20.00",
            "pl_qty_display": "20.00",
            "inv_gw_display": "20.400,00",
            "pl_gw_display": "20.400,00",
            "inv_nw_display": "20.000,00",
            "pl_nw_display": "20.000,00",
            "inv_total_display": "84.000,00",
            "pl_seller_name": "CÔNG TY CP NÔNG SẢN ĐÀ NẴNG",
            "pl_buyer_name": "TOKYO TRADING CO., LTD.",
            "pl_order_no": "DH-2026-TYO-02",
        },
        {
            "pkg_id": "PKG-003",
            "lang": "en",
            "split": "train",
            "template": "modern_grid",
            "scenario_id": "QTY_MISMATCH_EN",
            "category": "discrepancy",
            "desc": "Quantity mismatch: Invoice specifies 500 Bags while Packing List specifies 480 Bags.",
            "seller": {
                "name": "CENTRAL HIGHLANDS COFFEE EXPORT CORP",
                "addr": "KM 8, Highway 14, Buon Ma Thuot, Dak Lak, Vietnam",
            },
            "buyer": {
                "name": "HAMBURG BEAN ROASTERS GMBH",
                "addr": "Am Sandtorkai 48, 20457 Hamburg, Germany",
            },
            "order_no": "PO-2026-DE-003",
            "inv_no": "INV-2026-003",
            "pl_no": "PL-2026-003",
            "inv_date": "2026-10-19",
            "pl_date": "2026-10-19",
            "pol": "Cat Lai, Ho Chi Minh",
            "pod": "Hamburg, Germany",
            "vessel": "HAPAG LLOYD EXPRESS V.12W",
            "currency": "USD",
            "incoterm": "FOB",
            "items": [
                {
                    "line": 1,
                    "sku": "COFFEE-ROBUSTA-G1",
                    "desc": "Vietnamese Robusta Green Coffee Grade 1",
                    "qty": Decimal("500.00"),
                    "unit": "BAGS",
                    "price": Decimal("180.00"),
                    "total": Decimal("90000.00"),
                    "gross_wt": Decimal("30250.00"),
                    "net_wt": Decimal("30000.00"),
                    "pkgs": 500,
                    "pkg_type": "JUTE BAGS",
                }
            ],
            "inv_qty_display": "500",
            "pl_qty_display": "480",  # MISMATCH: 480 bags
            "inv_gw_display": "30,250.00",
            "pl_gw_display": "29,040.00",
            "inv_nw_display": "30,000.00",
            "pl_nw_display": "28,800.00",
            "inv_total_display": "90,000.00",
            "pl_seller_name": "CENTRAL HIGHLANDS COFFEE EXPORT CORP",
            "pl_buyer_name": "HAMBURG BEAN ROASTERS GMBH",
            "pl_order_no": "PO-2026-DE-003",
        },
        {
            "pkg_id": "PKG-004",
            "lang": "vi",
            "split": "train",
            "template": "classic_standard",
            "scenario_id": "QTY_MISMATCH_VI",
            "category": "discrepancy",
            "desc": "Sai lệch số lượng: Hóa đơn ghi 1.500 Thùng nhưng Phiếu đóng gói ghi 1.450 Thùng.",
            "seller": {
                "name": "TỔNG CÔNG TY LƯƠNG THỰC MIỀN NAM",
                "addr": "42 Chu Mạnh Trinh, Bến Nghé, Quận 1, TP. Hồ Chí Minh, Việt Nam",
            },
            "buyer": {
                "name": "MANILA RICE TRADING CORP",
                "addr": "Roxas Boulevard, Manila 1000, Philippines",
            },
            "order_no": "DH-2026-MNL-04",
            "inv_no": "HD-2026-004",
            "pl_no": "PK-2026-004",
            "inv_date": "2026-10-20",
            "pl_date": "2026-10-20",
            "pol": "Cảng Sài Gòn, TP. Hồ Chí Minh",
            "pod": "Cảng Manila, Philippines",
            "vessel": "MEKONG STAR 88N",
            "currency": "USD",
            "incoterm": "CIF",
            "items": [
                {
                    "line": 1,
                    "sku": "RICE-JASMINE-50KG",
                    "desc": "Gạo thơm Jasmine đóng bao 50kg xuất khẩu",
                    "qty": Decimal("1500.00"),
                    "unit": "BAO",
                    "price": Decimal("32.00"),
                    "total": Decimal("48000.00"),
                    "gross_wt": Decimal("75750.00"),
                    "net_wt": Decimal("75000.00"),
                    "pkgs": 1500,
                    "pkg_type": "BAO PP",
                }
            ],
            "inv_qty_display": "1.500",
            "pl_qty_display": "1.450",  # MISMATCH: 1450 bao
            "inv_gw_display": "75.750,00",
            "pl_gw_display": "73.225,00",
            "inv_nw_display": "75.000,00",
            "pl_nw_display": "72.500,00",
            "inv_total_display": "48.000,00",
            "pl_seller_name": "TỔNG CÔNG TY LƯƠNG THỰC MIỀN NAM",
            "pl_buyer_name": "MANILA RICE TRADING CORP",
            "pl_order_no": "DH-2026-MNL-04",
        },
        {
            "pkg_id": "PKG-005",
            "lang": "en",
            "split": "train",
            "template": "classic_standard",
            "scenario_id": "GROSS_WEIGHT_MISMATCH_EN",
            "category": "discrepancy",
            "desc": "Gross weight mismatch: Invoice shows 25,500 KG while Packing List shows 26,800 KG.",
            "seller": {
                "name": "MEKONG DELTA AGRO PRODUCTS",
                "addr": "Lot B4, Tra Noc Industrial Zone, Can Tho, Vietnam",
            },
            "buyer": {
                "name": "LION CITY COMMODITIES PTE LTD",
                "addr": "10 Collyer Quay, #14-01 Ocean Financial Centre, Singapore 049315",
            },
            "order_no": "PO-2026-SG-005",
            "inv_no": "INV-2026-005",
            "pl_no": "PL-2026-005",
            "inv_date": "2026-10-20",
            "pl_date": "2026-10-20",
            "pol": "Can Tho Port, Can Tho",
            "pod": "Jurong Port, Singapore",
            "vessel": "STRAITS BRIDGE V.204S",
            "currency": "USD",
            "incoterm": "FOB",
            "items": [
                {
                    "line": 1,
                    "sku": "WHITE-RICE-5PCT",
                    "desc": "Vietnamese Long Grain White Rice 5% Broken",
                    "qty": Decimal("50.00"),
                    "unit": "MT",
                    "price": Decimal("520.00"),
                    "total": Decimal("26000.00"),
                    "gross_wt": Decimal("25500.00"),
                    "net_wt": Decimal("25000.00"),
                    "pkgs": 1000,
                    "pkg_type": "BAGS",
                }
            ],
            "inv_qty_display": "50.00",
            "pl_qty_display": "50.00",
            "inv_gw_display": "25,500.00",
            "pl_gw_display": "26,800.00",  # MISMATCH: 26800 kg
            "inv_nw_display": "25,000.00",
            "pl_nw_display": "25,000.00",
            "inv_total_display": "26,000.00",
            "pl_seller_name": "MEKONG DELTA AGRO PRODUCTS",
            "pl_buyer_name": "LION CITY COMMODITIES PTE LTD",
            "pl_order_no": "PO-2026-SG-005",
        },
        {
            "pkg_id": "PKG-006",
            "lang": "vi",
            "split": "train",
            "template": "modern_grid",
            "scenario_id": "NET_WEIGHT_MISMATCH_VI",
            "category": "discrepancy",
            "desc": "Sai lệch trọng lượng tịnh: Hóa đơn ghi 15.000 KG nhưng Phiếu đóng gói ghi 14.200 KG.",
            "seller": {
                "name": "CÔNG TY TNHH XNK HẠT ĐIỀU BÌNH PHƯỚC",
                "addr": "Khu công nghiệp Đồng Xoài 1, Bình Phước, Việt Nam",
            },
            "buyer": {
                "name": "BEIJING AGRI-IMPORT CORP",
                "addr": "No. 18 Jianguomenwai Avenue, Chaoyang District, Beijing, China",
            },
            "order_no": "DH-2026-BJS-006",
            "inv_no": "HD-2026-006",
            "pl_no": "PK-2026-006",
            "inv_date": "2026-10-21",
            "pl_date": "2026-10-21",
            "pol": "Cảng Cát Lái, TP. Hồ Chí Minh",
            "pod": "Cảng Thiên Tân, Trung Quốc",
            "vessel": "SITC TIANJIN V.2610N",
            "currency": "USD",
            "incoterm": "CIF",
            "items": [
                {
                    "line": 1,
                    "sku": "CASHEW-WS",
                    "desc": "Nhân điều vỡ đôi xuất khẩu loại WS",
                    "qty": Decimal("15.00"),
                    "unit": "TẤN",
                    "price": Decimal("5800.00"),
                    "total": Decimal("87000.00"),
                    "gross_wt": Decimal("15450.00"),
                    "net_wt": Decimal("15000.00"),
                    "pkgs": 600,
                    "pkg_type": "THÙNG CARTON",
                }
            ],
            "inv_qty_display": "15.00",
            "pl_qty_display": "15.00",
            "inv_gw_display": "15.450,00",
            "pl_gw_display": "15.450,00",
            "inv_nw_display": "15.000,00",
            "pl_nw_display": "14.200,00",  # MISMATCH: 14,200 kg
            "inv_total_display": "87.000,00",
            "pl_seller_name": "CÔNG TY TNHH XNK HẠT ĐIỀU BÌNH PHƯỚC",
            "pl_buyer_name": "BEIJING AGRI-IMPORT CORP",
            "pl_order_no": "DH-2026-BJS-006",
        },
        {
            "pkg_id": "PKG-007",
            "lang": "en",
            "split": "train",
            "template": "modern_grid",
            "scenario_id": "PARTY_BUYER_MISMATCH_EN",
            "category": "discrepancy",
            "desc": "Buyer/Consignee mismatch: Invoice lists Atlantic Foods Ltd while Packing List lists Pacific Maritime Ltd.",
            "seller": {
                "name": "SEAFOOD EXPORT ENTERPRISE NO 1",
                "addr": "D2 Street, Suoi Dau Industrial Zone, Khanh Hoa, Vietnam",
            },
            "buyer": {
                "name": "ATLANTIC FOODS LTD",
                "addr": "15 Royal Crescent, London W11 4SL, United Kingdom",
            },
            "order_no": "PO-2026-UK-007",
            "inv_no": "INV-2026-007",
            "pl_no": "PL-2026-007",
            "inv_date": "2026-10-21",
            "pl_date": "2026-10-21",
            "pol": "Nha Trang Port, Khanh Hoa",
            "pod": "Southampton, United Kingdom",
            "vessel": "CMA CGM ANTOINE V.98E",
            "currency": "USD",
            "incoterm": "FOB",
            "items": [
                {
                    "line": 1,
                    "sku": "PANGASIUS-FILLET-WELL",
                    "desc": "Frozen Pangasius Fillets Well Trimmed",
                    "qty": Decimal("2000.00"),
                    "unit": "CARTONS",
                    "price": Decimal("28.50"),
                    "total": Decimal("57000.00"),
                    "gross_wt": Decimal("22000.00"),
                    "net_wt": Decimal("20000.00"),
                    "pkgs": 2000,
                    "pkg_type": "MASTER CARTONS",
                }
            ],
            "inv_qty_display": "2,000",
            "pl_qty_display": "2,000",
            "inv_gw_display": "22,000.00",
            "pl_gw_display": "22,000.00",
            "inv_nw_display": "20,000.00",
            "pl_nw_display": "20,000.00",
            "inv_total_display": "57,000.00",
            "pl_seller_name": "SEAFOOD EXPORT ENTERPRISE NO 1",
            "pl_buyer_name": "PACIFIC MARITIME TRADERS INC",  # MISMATCH: Pacific Maritime Traders
            "pl_order_no": "PO-2026-UK-007",
        },
        {
            "pkg_id": "PKG-008",
            "lang": "vi",
            "split": "validation",
            "template": "classic_standard",
            "scenario_id": "PARTY_SELLER_MISMATCH_VI",
            "category": "discrepancy",
            "desc": "Sai lệch bên bán/người gửi: Hóa đơn ghi Cty Nông sản Sài Gòn nhưng Phiếu đóng gói ghi Cty Hoàng Gia.",
            "seller": {
                "name": "CÔNG TY CP NÔNG SẢN SÀI GÒN",
                "addr": "180 Đường Nguyễn Thị Minh Khai, Quận 3, TP. Hồ Chí Minh, Việt Nam",
            },
            "buyer": {
                "name": "DUBAI GENERAL TRADING LLC",
                "addr": "Al Rigga Road, Deira, P.O. Box 4521, Dubai, UAE",
            },
            "order_no": "DH-2026-DXB-008",
            "inv_no": "HD-2026-008",
            "pl_no": "PK-2026-008",
            "inv_date": "2026-10-21",
            "pl_date": "2026-10-21",
            "pol": "Cảng Cát Lái, TP. Hồ Chí Minh",
            "pod": "Cảng Jebel Ali, Dubai",
            "vessel": "ARABIAN CARRIER V.401W",
            "currency": "USD",
            "incoterm": "CIF",
            "items": [
                {
                    "line": 1,
                    "sku": "TEA-GREEN-OP",
                    "desc": "Chè xanh xuất khẩu Tân Cương loại OP",
                    "qty": Decimal("1000.00"),
                    "unit": "THÙNG",
                    "price": Decimal("45.00"),
                    "total": Decimal("45000.00"),
                    "gross_wt": Decimal("21500.00"),
                    "net_wt": Decimal("20000.00"),
                    "pkgs": 1000,
                    "pkg_type": "THÙNG CARTON",
                }
            ],
            "inv_qty_display": "1.000",
            "pl_qty_display": "1.000",
            "inv_gw_display": "21.500,00",
            "pl_gw_display": "21.500,00",
            "inv_nw_display": "20.000,00",
            "pl_nw_display": "20.000,00",
            "inv_total_display": "45.000,00",
            "pl_seller_name": "CÔNG TY TNHH XUẤT NHẬP KHẨU HOÀNG GIA",  # MISMATCH: Hoang Gia
            "pl_buyer_name": "DUBAI GENERAL TRADING LLC",
            "pl_order_no": "DH-2026-DXB-008",
        },
        {
            "pkg_id": "PKG-009",
            "lang": "en",
            "split": "validation",
            "template": "classic_standard",
            "scenario_id": "ARITHMETIC_LINE_TOTAL_EN",
            "category": "discrepancy",
            "desc": "Arithmetic error: Line item 50 MT x $1,650.00/MT is erroneously printed as $72,500.00 instead of $82,500.00.",
            "seller": {
                "name": "VIETNAM RUBBER GROUP CORP",
                "addr": "236 Hai Ba Trung, District 1, Ho Chi Minh City, Vietnam",
            },
            "buyer": {
                "name": "MUMBAI TIRE MANUFACTURING LTD",
                "addr": "Andheri Kurla Road, Andheri East, Mumbai 400059, India",
            },
            "order_no": "PO-2026-IN-009",
            "inv_no": "INV-2026-009",
            "pl_no": "PL-2026-009",
            "inv_date": "2026-10-22",
            "pl_date": "2026-10-22",
            "pol": "Cat Lai, Ho Chi Minh",
            "pod": "Nhava Sheva, India",
            "vessel": "INDIAN OCEAN V.302W",
            "currency": "USD",
            "incoterm": "FOB",
            "items": [
                {
                    "line": 1,
                    "sku": "RUBBER-SVR-3L",
                    "desc": "Natural Rubber Technical Specified SVR 3L",
                    "qty": Decimal("50.00"),
                    "unit": "MT",
                    "price": Decimal("1650.00"),
                    "total": Decimal(
                        "72500.00"
                    ),  # ARITHMETIC ERROR: 50 * 1650 = 82500, printed 72500
                    "gross_wt": Decimal("50500.00"),
                    "net_wt": Decimal("50000.00"),
                    "pkgs": 1500,
                    "pkg_type": "BALES",
                }
            ],
            "inv_qty_display": "50.00",
            "pl_qty_display": "50.00",
            "inv_gw_display": "50,500.00",
            "pl_gw_display": "50,500.00",
            "inv_nw_display": "50,000.00",
            "pl_nw_display": "50,000.00",
            "inv_total_display": "72,500.00",  # Matches the erroneous line total
            "pl_seller_name": "VIETNAM RUBBER GROUP CORP",
            "pl_buyer_name": "MUMBAI TIRE MANUFACTURING LTD",
            "pl_order_no": "PO-2026-IN-009",
        },
        {
            "pkg_id": "PKG-010",
            "lang": "vi",
            "split": "test",
            "template": "modern_grid",
            "scenario_id": "ARITHMETIC_TOTAL_SUM_VI",
            "category": "discrepancy",
            "desc": "Sai số học tổng hóa đơn: Hai dòng hàng 25.000 USD + 25.000 USD nhưng tổng cộng in 60.000 USD.",
            "seller": {
                "name": "CÔNG TY CP XUẤT NHẬP KHẨU BẾN TRE",
                "addr": "75 Đại lộ Đồng Khởi, TP. Bến Tre, Tỉnh Bến Tre, Việt Nam",
            },
            "buyer": {
                "name": "SEOUL FOOD DISTRIBUTION CO",
                "addr": "Teheran-ro 152, Gangnam-gu, Seoul 06236, South Korea",
            },
            "order_no": "DH-2026-KOR-010",
            "inv_no": "HD-2026-010",
            "pl_no": "PK-2026-010",
            "inv_date": "2026-10-22",
            "pl_date": "2026-10-22",
            "pol": "Cảng Cát Lái, TP. Hồ Chí Minh",
            "pod": "Cảng Busan, Hàn Quốc",
            "vessel": "KOREA EXPRESS V.112N",
            "currency": "USD",
            "incoterm": "CIF",
            "items": [
                {
                    "line": 1,
                    "sku": "COCONUT-DESICCATED-F",
                    "desc": "Cơm dừa sấy khô hạt mịn loại Fine Grade",
                    "qty": Decimal("10.00"),
                    "unit": "TẤN",
                    "price": Decimal("2500.00"),
                    "total": Decimal("25000.00"),
                    "gross_wt": Decimal("10200.00"),
                    "net_wt": Decimal("10000.00"),
                    "pkgs": 400,
                    "pkg_type": "BAO GIẤY",
                },
                {
                    "line": 2,
                    "sku": "COCONUT-DESICCATED-M",
                    "desc": "Cơm dừa sấy khô hạt trung Medium Grade",
                    "qty": Decimal("10.00"),
                    "unit": "TẤN",
                    "price": Decimal("2500.00"),
                    "total": Decimal("25000.00"),
                    "gross_wt": Decimal("10200.00"),
                    "net_wt": Decimal("10000.00"),
                    "pkgs": 400,
                    "pkg_type": "BAO GIẤY",
                },
            ],
            "inv_qty_display": "20.00",
            "pl_qty_display": "20.00",
            "inv_gw_display": "20.400,00",
            "pl_gw_display": "20.400,00",
            "inv_nw_display": "20.000,00",
            "pl_nw_display": "20.000,00",
            "inv_total_display": "60.000,00",  # ARITHMETIC ERROR: 25,000 + 25,000 = 50,000, printed 60,000
            "pl_seller_name": "CÔNG TY CP XUẤT NHẬP KHẨU BẾN TRE",
            "pl_buyer_name": "SEOUL FOOD DISTRIBUTION CO",
            "pl_order_no": "DH-2026-KOR-010",
        },
        {
            "pkg_id": "PKG-011",
            "lang": "vi",
            "split": "test",
            "template": "classic_standard",
            "scenario_id": "IDENTIFIER_ORDER_MISMATCH_VI",
            "category": "discrepancy",
            "desc": "Sai lệch mã đơn hàng: Hóa đơn tham chiếu DH-2026-LON-901 trong khi Phiếu đóng gói ghi DH-2026-LON-999.",
            "seller": {
                "name": "CÔNG TY TNHH TRÁI CÂY NHIỆT ĐỚI MEKONG",
                "addr": "Km 1964, Quốc lộ 1A, Châu Thành, Tiền Giang, Việt Nam",
            },
            "buyer": {
                "name": "SYDNEY FRESH MARKETS PTY",
                "addr": "250 Parramatta Road, Homebush NSW 2140, Australia",
            },
            "order_no": "DH-2026-LON-901",
            "inv_no": "HD-2026-011",
            "pl_no": "PK-2026-011",
            "inv_date": "2026-10-22",
            "pl_date": "2026-10-22",
            "pol": "Cảng Cát Lái, TP. Hồ Chí Minh",
            "pod": "Cảng Sydney, Úc",
            "vessel": "OCEANIA LEADER V.505S",
            "currency": "USD",
            "incoterm": "CIF",
            "items": [
                {
                    "line": 1,
                    "sku": "DRAGON-FRUIT-FD",
                    "desc": "Thanh long đỏ sấy thăng hoa xuất khẩu",
                    "qty": Decimal("800.00"),
                    "unit": "THÙNG",
                    "price": Decimal("48.00"),
                    "total": Decimal("38400.00"),
                    "gross_wt": Decimal("8800.00"),
                    "net_wt": Decimal("8000.00"),
                    "pkgs": 800,
                    "pkg_type": "THÙNG CARTON",
                }
            ],
            "inv_qty_display": "800",
            "pl_qty_display": "800",
            "inv_gw_display": "8.800,00",
            "pl_gw_display": "8.800,00",
            "inv_nw_display": "8.000,00",
            "pl_nw_display": "8.000,00",
            "inv_total_display": "38.400,00",
            "pl_seller_name": "CÔNG TY TNHH TRÁI CÂY NHIỆT ĐỚI MEKONG",
            "pl_buyer_name": "SYDNEY FRESH MARKETS PTY",
            "pl_order_no": "DH-2026-LON-999",  # MISMATCH: DH-2026-LON-999 vs DH-2026-LON-901
        },
        {
            "pkg_id": "PKG-012",
            "lang": "en",
            "split": "test",
            "template": "modern_grid",
            "scenario_id": "BENIGN_FORMATTING_VARIATIONS",
            "category": "benign_variation",
            "desc": "Benign formatting variations: Dates formatted as 2026-10-22 vs 22/10/2026, buyer case differences, decimal periods vs commas. Semantically identical match.",
            "seller": {
                "name": "VIETNAM SPICE TRADING LTD",
                "addr": "Hamlet 3, Xuan Loc, Dong Nai, Vietnam",
            },
            "buyer": {
                "name": "GLOBAL CONDIMENTS CORP",
                "addr": "742 Evergreen Terrace, Springfield, OR 97477, USA",
            },
            "order_no": "PO-2026-USA-012",
            "inv_no": "INV-2026-012",
            "pl_no": "PL-2026-012",
            "inv_date": "2026-10-22",
            "pl_date": "22/10/2026",  # BENIGN VARIATION: DD/MM/YYYY vs YYYY-MM-DD
            "pol": "Cat Lai, Ho Chi Minh",
            "pod": "Los Angeles, USA",
            "vessel": "PACIFIC TRADER V.012W",
            "currency": "USD",
            "incoterm": "FOB",
            "items": [
                {
                    "line": 1,
                    "sku": "CINNAMON-SPLIT",
                    "desc": "Split Cassia Cinnamon Premium Quality",
                    "qty": Decimal("10.00"),
                    "unit": "MT",
                    "price": Decimal("3800.00"),
                    "total": Decimal("38000.00"),
                    "gross_wt": Decimal("10300.00"),
                    "net_wt": Decimal("10000.00"),
                    "pkgs": 1000,
                    "pkg_type": "CARTONS",
                }
            ],
            "inv_qty_display": "10.00",
            "pl_qty_display": "10,00",  # BENIGN VARIATION: comma as decimal separator
            "inv_gw_display": "10,300.00",
            "pl_gw_display": "10300 kg",  # BENIGN VARIATION: unit suffix with no comma
            "inv_nw_display": "10,000.00",
            "pl_nw_display": "10.000,00",  # BENIGN VARIATION: European thousand separator
            "inv_total_display": "38,000.00",
            "pl_seller_name": "Vietnam Spice Trading Ltd",  # BENIGN: Title Case vs UPPERCASE
            "pl_buyer_name": "global condiments corp",  # BENIGN: lowercase vs UPPERCASE
            "pl_order_no": "PO-2026-USA-012",
        },
    ]


def render_document_pdf(pkg: dict, doc_type: str, pdf_path: Path) -> dict:
    """Render a single PDF invoice or packing list with exact bounding box calculation.

    Returns the field and line-item annotation dictionary.
    """
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    lang = pkg["lang"]
    template = pkg["template"]
    is_invoice = doc_type == "commercial_invoice"

    title_text = "COMMERCIAL INVOICE" if is_invoice else "PACKING LIST"
    if lang == "vi":
        title_text = "HÓA ĐƠN THƯƠNG MẠI" if is_invoice else "PHIẾU ĐÓNG GÓI HÀNG HÓA"

    doc_no = pkg["inv_no"] if is_invoice else pkg["pl_no"]
    date_val = pkg["inv_date"] if is_invoice else pkg["pl_date"]
    seller_name = pkg["seller"]["name"] if is_invoice else pkg["pl_seller_name"]
    buyer_name = pkg["buyer"]["name"] if is_invoice else pkg["pl_buyer_name"]
    order_no = pkg["order_no"] if is_invoice else pkg["pl_order_no"]

    fields_annot = []
    line_items_annot = []

    # 1. Header & Title Banner
    if template == "modern_grid":
        # Grey shaded top banner
        c.setFillColorRGB(0.92, 0.94, 0.96)
        c.rect(40, 770, 515, 45, fill=1, stroke=0)
        c.setFillColorRGB(0.1, 0.2, 0.35)
        c.setFont(FONT_BOLD, 18)
        c.drawString(55, 785, title_text)
    else:  # classic_standard
        c.setFillColorRGB(0, 0, 0)
        c.setFont(FONT_BOLD, 18)
        c.drawCentredString(PAGE_WIDTH / 2.0, 790, title_text)
        c.setLineWidth(1.5)
        c.line(40, 780, 555, 780)
        c.setLineWidth(0.5)
        c.line(40, 777, 555, 777)

    # 2. Document Reference Box (Top Right)
    c.setFont(FONT_BOLD, 10)
    c.setFillColorRGB(0, 0, 0)
    lbl_no = "Invoice No:" if is_invoice else "PL No:"
    if lang == "vi":
        lbl_no = "Số hóa đơn:" if is_invoice else "Số phiếu đóng gói:"
    c.drawString(360, 750, lbl_no)

    c.setFont(FONT_REGULAR, 10)
    c.drawString(450, 750, doc_no)
    fields_annot.append(
        {
            "canonical_name": "document_number",
            "raw_value": doc_no,
            "normalized_value": doc_no.strip(),
            "data_type": "string",
            "page": 1,
            "bbox": text_bbox(c, FONT_REGULAR, 10, 450, 750, doc_no),
            "status": "present",
        }
    )

    lbl_date = "Date:" if lang == "en" else "Ngày:"
    c.setFont(FONT_BOLD, 10)
    c.drawString(360, 735, lbl_date)
    c.setFont(FONT_REGULAR, 10)
    c.drawString(450, 735, str(date_val))
    # Normalized ISO date (handle both 2026-10-22 and 22/10/2026)
    norm_date = (
        "2026-10-22"
        if "22" in str(date_val) and "10" in str(date_val)
        else str(date_val)
    )
    fields_annot.append(
        {
            "canonical_name": "issue_date",
            "raw_value": str(date_val),
            "normalized_value": norm_date,
            "data_type": "date",
            "page": 1,
            "bbox": text_bbox(c, FONT_REGULAR, 10, 450, 735, str(date_val)),
            "status": "present",
        }
    )

    lbl_po = "Order / PO No:" if lang == "en" else "Số đơn hàng:"
    c.setFont(FONT_BOLD, 10)
    c.drawString(360, 720, lbl_po)
    c.setFont(FONT_REGULAR, 10)
    c.drawString(450, 720, order_no)
    fields_annot.append(
        {
            "canonical_name": "order_number",
            "raw_value": order_no,
            "normalized_value": order_no.strip(),
            "data_type": "string",
            "page": 1,
            "bbox": text_bbox(c, FONT_REGULAR, 10, 450, 720, order_no),
            "status": "present",
        }
    )

    # 3. Seller & Buyer Blocks
    lbl_seller = "SELLER / EXPORTER:" if is_invoice else "SHIPPER / CONSIGNOR:"
    lbl_buyer = "BUYER / IMPORTER:" if is_invoice else "CONSIGNEE:"
    if lang == "vi":
        lbl_seller = "NGƯỜI BÁN / XUẤT KHẨU:" if is_invoice else "NGƯỜI GỬI HÀNG:"
        lbl_buyer = "NGƯỜI MUA / NHẬP KHẨU:" if is_invoice else "NGƯỜI NHẬN HÀNG:"

    # Seller Block (Left)
    c.setFont(FONT_BOLD, 9)
    c.drawString(45, 750, lbl_seller)
    c.setFont(FONT_BOLD, 10)
    c.drawString(45, 735, seller_name)
    fields_annot.append(
        {
            "canonical_name": "seller_name",
            "raw_value": seller_name,
            "normalized_value": seller_name.strip().upper(),
            "data_type": "string",
            "page": 1,
            "bbox": text_bbox(c, FONT_BOLD, 10, 45, 735, seller_name),
            "status": "present",
        }
    )

    c.setFont(FONT_REGULAR, 8)
    seller_addr = pkg["seller"]["addr"]
    c.drawString(45, 722, seller_addr[:55])
    if len(seller_addr) > 55:
        c.drawString(45, 712, seller_addr[55:])
    fields_annot.append(
        {
            "canonical_name": "seller_address",
            "raw_value": seller_addr,
            "normalized_value": seller_addr.strip(),
            "data_type": "string",
            "page": 1,
            "bbox": pt_to_bbox(45, 712, 300, 20),
            "status": "present",
        }
    )

    # Buyer Block
    c.setFont(FONT_BOLD, 9)
    c.drawString(45, 690, lbl_buyer)
    c.setFont(FONT_BOLD, 10)
    c.drawString(45, 675, buyer_name)
    fields_annot.append(
        {
            "canonical_name": "buyer_name",
            "raw_value": buyer_name,
            "normalized_value": buyer_name.strip().upper(),
            "data_type": "string",
            "page": 1,
            "bbox": text_bbox(c, FONT_BOLD, 10, 45, 675, buyer_name),
            "status": "present",
        }
    )

    c.setFont(FONT_REGULAR, 8)
    buyer_addr = pkg["buyer"]["addr"]
    c.drawString(45, 662, buyer_addr[:55])
    if len(buyer_addr) > 55:
        c.drawString(45, 652, buyer_addr[55:])
    fields_annot.append(
        {
            "canonical_name": "buyer_address",
            "raw_value": buyer_addr,
            "normalized_value": buyer_addr.strip(),
            "data_type": "string",
            "page": 1,
            "bbox": pt_to_bbox(45, 652, 300, 20),
            "status": "present",
        }
    )

    # 4. Logistics Routing Details
    lbl_pol = "Port of Loading:" if lang == "en" else "Cảng bốc hàng:"
    lbl_pod = "Port of Discharge:" if lang == "en" else "Cảng dỡ hàng:"
    lbl_vessel = "Vessel / Voyage:" if lang == "en" else "Tàu / Chuyến:"
    lbl_term = "Terms:" if lang == "en" else "Điều kiện:"

    c.setFont(FONT_BOLD, 8)
    c.drawString(45, 630, lbl_pol)
    c.setFont(FONT_REGULAR, 8)
    c.drawString(125, 630, pkg["pol"])
    fields_annot.append(
        {
            "canonical_name": "port_of_loading",
            "raw_value": pkg["pol"],
            "normalized_value": pkg["pol"].strip(),
            "data_type": "string",
            "page": 1,
            "bbox": text_bbox(c, FONT_REGULAR, 8, 125, 630, pkg["pol"]),
            "status": "present",
        }
    )

    c.setFont(FONT_BOLD, 8)
    c.drawString(280, 630, lbl_pod)
    c.setFont(FONT_REGULAR, 8)
    c.drawString(365, 630, pkg["pod"])
    fields_annot.append(
        {
            "canonical_name": "port_of_discharge",
            "raw_value": pkg["pod"],
            "normalized_value": pkg["pod"].strip(),
            "data_type": "string",
            "page": 1,
            "bbox": text_bbox(c, FONT_REGULAR, 8, 365, 630, pkg["pod"]),
            "status": "present",
        }
    )

    c.setFont(FONT_BOLD, 8)
    c.drawString(45, 615, lbl_vessel)
    c.setFont(FONT_REGULAR, 8)
    c.drawString(125, 615, pkg["vessel"])

    term_val = f"{pkg['incoterm']} {pkg['pol']}"
    c.setFont(FONT_BOLD, 8)
    c.drawString(280, 615, lbl_term)
    c.setFont(FONT_REGULAR, 8)
    c.drawString(365, 615, term_val)
    fields_annot.append(
        {
            "canonical_name": "incoterm",
            "raw_value": pkg["incoterm"],
            "normalized_value": pkg["incoterm"].strip().upper(),
            "data_type": "string",
            "page": 1,
            "bbox": text_bbox(c, FONT_REGULAR, 8, 365, 615, pkg["incoterm"]),
            "status": "present",
        }
    )

    if is_invoice:
        fields_annot.append(
            {
                "canonical_name": "currency",
                "raw_value": pkg["currency"],
                "normalized_value": pkg["currency"].strip().upper(),
                "data_type": "currency",
                "page": 1,
                "bbox": text_bbox(c, FONT_REGULAR, 8, 510, 615, pkg["currency"]),
                "status": "present",
            }
        )
        c.drawString(510, 615, pkg["currency"])

    # Divider before table
    c.setLineWidth(0.8)
    c.line(40, 605, 555, 605)

    # 5. Line Items Table
    table_top = 590
    c.setFont(FONT_BOLD, 8)
    if is_invoice:
        # Columns: Line, SKU, Description, Quantity, Unit, Price, Total
        c.drawString(45, table_top, "No.")
        c.drawString(70, table_top, "Item / SKU")
        c.drawString(
            160, table_top, "Description of Goods" if lang == "en" else "Mô tả hàng hóa"
        )
        c.drawString(330, table_top, "Quantity" if lang == "en" else "Số lượng")
        c.drawString(380, table_top, "Unit" if lang == "en" else "ĐVT")
        c.drawString(
            420,
            table_top,
            f"Unit Price ({pkg['currency']})"
            if lang == "en"
            else f"Đơn giá ({pkg['currency']})",
        )
        c.drawString(
            500,
            table_top,
            f"Total ({pkg['currency']})" if lang == "en" else "Thành tiền",
        )
        c.line(40, table_top - 5, 555, table_top - 5)

        y_row = table_top - 20
        for itm in pkg["items"]:
            c.setFont(FONT_REGULAR, 8)
            c.drawString(45, y_row, str(itm["line"]))
            c.drawString(70, y_row, itm["sku"])
            c.drawString(160, y_row, itm["desc"][:28])

            qty_str = pkg["inv_qty_display"] if itm["line"] == 1 else str(itm["qty"])
            c.drawString(330, y_row, qty_str)
            c.drawString(380, y_row, itm["unit"])

            price_str = f"{itm['price']:,.2f}"
            c.drawString(420, y_row, price_str)

            total_str = f"{itm['total']:,.2f}"
            c.drawString(500, y_row, total_str)

            row_bbox = pt_to_bbox(40, y_row - 3, 515, 14)
            line_items_annot.append(
                {
                    "line_number": itm["line"],
                    "sku": itm["sku"],
                    "description": itm["desc"],
                    "quantity": float(itm["qty"]),
                    "unit": itm["unit"],
                    "unit_price": float(itm["price"]),
                    "line_total": float(itm["total"]),
                    "gross_weight": None,
                    "net_weight": None,
                    "package_count": itm.get("pkgs"),
                    "package_type": itm.get("pkg_type"),
                    "page": 1,
                    "bbox": row_bbox,
                }
            )
            y_row -= 18

    else:  # Packing List Table
        # Columns: Line, Description, Packages, Type, Net Wt (KG), Gross Wt (KG)
        c.drawString(45, table_top, "No.")
        c.drawString(
            70, table_top, "Description of Goods" if lang == "en" else "Mô tả hàng hóa"
        )
        c.drawString(240, table_top, "Quantity" if lang == "en" else "Số lượng")
        c.drawString(300, table_top, "Packages" if lang == "en" else "Số kiện")
        c.drawString(370, table_top, "Packaging" if lang == "en" else "Loại bao bì")
        c.drawString(440, table_top, "Net Wt (KG)" if lang == "en" else "TL Tịnh (KG)")
        c.drawString(
            500, table_top, "Gross Wt (KG)" if lang == "en" else "TL Cả bì (KG)"
        )
        c.line(40, table_top - 5, 555, table_top - 5)

        y_row = table_top - 20
        for itm in pkg["items"]:
            c.setFont(FONT_REGULAR, 8)
            c.drawString(45, y_row, str(itm["line"]))
            c.drawString(70, y_row, itm["desc"][:28])

            qty_str = pkg["pl_qty_display"] if itm["line"] == 1 else str(itm["qty"])
            c.drawString(240, y_row, f"{qty_str} {itm['unit']}")
            c.drawString(300, y_row, str(itm["pkgs"]))
            c.drawString(370, y_row, str(itm["pkg_type"])[:12])

            nw_str = (
                pkg["pl_nw_display"] if itm["line"] == 1 else f"{itm['net_wt']:,.2f}"
            )
            c.drawString(440, y_row, nw_str)

            gw_str = (
                pkg["pl_gw_display"] if itm["line"] == 1 else f"{itm['gross_wt']:,.2f}"
            )
            c.drawString(500, y_row, gw_str)

            row_bbox = pt_to_bbox(40, y_row - 3, 515, 14)
            line_items_annot.append(
                {
                    "line_number": itm["line"],
                    "sku": itm.get("sku"),
                    "description": itm["desc"],
                    "quantity": float(itm["qty"])
                    if pkg["pl_qty_display"] == pkg["inv_qty_display"]
                    else (
                        480.0
                        if "480" in pkg["pl_qty_display"]
                        else (
                            1450.0
                            if "1.450" in pkg["pl_qty_display"]
                            else float(itm["qty"])
                        )
                    ),
                    "unit": itm["unit"],
                    "unit_price": None,
                    "line_total": None,
                    "gross_weight": float(itm["gross_wt"])
                    if "MISMATCH" not in pkg["desc"]
                    or "GROSS" not in pkg["scenario_id"]
                    else 26800.0,
                    "net_weight": float(itm["net_wt"])
                    if "MISMATCH" not in pkg["desc"] or "NET" not in pkg["scenario_id"]
                    else 14200.0,
                    "package_count": itm.get("pkgs"),
                    "package_type": itm.get("pkg_type"),
                    "page": 1,
                    "bbox": row_bbox,
                }
            )
            y_row -= 18

    # 6. Totals Section
    c.line(40, y_row, 555, y_row)
    y_totals = y_row - 18
    c.setFont(FONT_BOLD, 9)

    if is_invoice:
        lbl_tot = "TOTAL AMOUNT:" if lang == "en" else "TỔNG TIỀN THANH TOÁN:"
        c.drawString(350, y_totals, lbl_tot)
        tot_val = pkg["inv_total_display"]
        tot_text = f"{pkg['currency']} {tot_val}"
        c.drawString(480, y_totals, tot_text)

        norm_total = 85000.0
        if "84.000" in tot_val:
            norm_total = 84000.0
        elif "90,000" in tot_val:
            norm_total = 90000.0
        elif "48.000" in tot_val:
            norm_total = 48000.0
        elif "26,000" in tot_val:
            norm_total = 26000.0
        elif "87.000" in tot_val:
            norm_total = 87000.0
        elif "57,000" in tot_val:
            norm_total = 57000.0
        elif "45.000" in tot_val:
            norm_total = 45000.0
        elif "72,500" in tot_val:
            norm_total = 72500.0
        elif "60.000" in tot_val:
            norm_total = 60000.0
        elif "38,400" in tot_val:
            norm_total = 38400.0
        elif "38,000" in tot_val:
            norm_total = 38000.0

        fields_annot.append(
            {
                "canonical_name": "total_amount",
                "raw_value": tot_text,
                "normalized_value": norm_total,
                "data_type": "number",
                "page": 1,
                "bbox": text_bbox(c, FONT_BOLD, 9, 480, y_totals, tot_text),
                "status": "present",
            }
        )
    else:
        lbl_gw = "TOTAL GROSS WEIGHT:" if lang == "en" else "TỔNG TRỌNG LƯỢNG CẢ BÌ:"
        lbl_nw = "TOTAL NET WEIGHT:" if lang == "en" else "TỔNG TRỌNG LƯỢNG TỊNH:"
        c.drawString(220, y_totals, lbl_nw)
        c.drawString(380, y_totals, f"{pkg['pl_nw_display']} KG")

        # Parse normalized net weight
        nw_raw = pkg["pl_nw_display"]
        nw_clean = nw_raw.replace(".", "").replace(",", ".").replace(" kg", "").strip()
        norm_nw = float(nw_clean)

        fields_annot.append(
            {
                "canonical_name": "total_net_weight",
                "raw_value": f"{pkg['pl_nw_display']} KG",
                "normalized_value": norm_nw,
                "data_type": "number",
                "page": 1,
                "bbox": text_bbox(
                    c, FONT_BOLD, 9, 380, y_totals, f"{pkg['pl_nw_display']} KG"
                ),
                "status": "present",
            }
        )

        y_totals -= 14
        c.drawString(220, y_totals, lbl_gw)
        c.drawString(380, y_totals, f"{pkg['pl_gw_display']} KG")

        gw_raw = pkg["pl_gw_display"]
        gw_clean = gw_raw.replace(".", "").replace(",", ".").replace(" kg", "").strip()
        norm_gw = float(gw_clean)

        fields_annot.append(
            {
                "canonical_name": "total_gross_weight",
                "raw_value": f"{pkg['pl_gw_display']} KG",
                "normalized_value": norm_gw,
                "data_type": "number",
                "page": 1,
                "bbox": text_bbox(
                    c, FONT_BOLD, 9, 380, y_totals, f"{pkg['pl_gw_display']} KG"
                ),
                "status": "present",
            }
        )

    # 7. Signature Footer
    y_footer = 120
    c.setFont(FONT_REGULAR, 8)
    lbl_sig = (
        "Authorized Signatory / For and on behalf of Seller"
        if lang == "en"
        else "Đại diện có thẩm quyền bên bán ký tên và đóng dấu"
    )
    c.drawRightString(540, y_footer + 40, lbl_sig)
    c.setLineWidth(0.5)
    c.line(380, y_footer, 540, y_footer)
    c.drawRightString(540, y_footer - 12, seller_name[:35])

    c.showPage()
    c.save()

    return {
        "dataset_version": "1.0.0",
        "package_id": pkg["pkg_id"],
        "document_id": f"{pkg['pkg_id']}_{'INV' if is_invoice else 'PL'}",
        "document_type": doc_type,
        "language": lang,
        "template_id": template,
        "file_name": pdf_path.name,
        "page_dimensions": {
            "unit": "point",
            "width": float(PAGE_WIDTH),
            "height": float(PAGE_HEIGHT),
            "page_count": 1,
        },
        "scenario": {
            "scenario_id": pkg["scenario_id"],
            "category": pkg["category"],
            "description": pkg["desc"],
        },
        "fields": fields_annot,
        "line_items": line_items_annot,
    }


def generate_dataset() -> None:
    """Generate all 12 packages, annotations, manifest, and comparisons."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)

    packages = build_package_definitions()
    manifest_packages = []
    all_comparisons = []
    comp_counter = 1

    for pkg in packages:
        pkg_id = pkg["pkg_id"]

        # 1. Generate Commercial Invoice
        inv_filename = f"{pkg_id}_commercial_invoice.pdf"
        inv_pdf_path = DOCS_DIR / inv_filename
        inv_annot = render_document_pdf(pkg, "commercial_invoice", inv_pdf_path)
        inv_annot_path = ANNOTATIONS_DIR / f"{pkg_id}_commercial_invoice.json"
        with open(inv_annot_path, "w", encoding="utf-8") as f:
            json.dump(inv_annot, f, ensure_ascii=False, indent=2)

        # 2. Generate Packing List
        pl_filename = f"{pkg_id}_packing_list.pdf"
        pl_pdf_path = DOCS_DIR / pl_filename
        pl_annot = render_document_pdf(pkg, "packing_list", pl_pdf_path)
        pl_annot_path = ANNOTATIONS_DIR / f"{pkg_id}_packing_list.json"
        with open(pl_annot_path, "w", encoding="utf-8") as f:
            json.dump(pl_annot, f, ensure_ascii=False, indent=2)

        # 3. Add to Manifest
        manifest_packages.append(
            {
                "package_id": pkg_id,
                "language": pkg["lang"],
                "split": pkg["split"],
                "scenario_id": pkg["scenario_id"],
                "scenario_category": pkg["category"],
                "description": pkg["desc"],
                "commercial_invoice": {
                    "document_id": f"{pkg_id}_INV",
                    "file_name": inv_filename,
                    "annotation_file": inv_annot_path.name,
                    "template_id": pkg["template"],
                },
                "packing_list": {
                    "document_id": f"{pkg_id}_PL",
                    "file_name": pl_filename,
                    "annotation_file": pl_annot_path.name,
                    "template_id": pkg["template"],
                },
            }
        )

        # 4. Define Cross-Document Expected Comparison Rules
        # Rule QTY-002: Invoice Quantity vs Packing List Quantity
        is_qty_mismatch = pkg["scenario_id"] in ["QTY_MISMATCH_EN", "QTY_MISMATCH_VI"]
        all_comparisons.append(
            {
                "comparison_id": f"CMP-{comp_counter:03d}",
                "package_id": pkg_id,
                "rule_id": "QTY-002",
                "rule_name": "Invoice Quantity vs Packing List Quantity",
                "source_document_id": f"{pkg_id}_INV",
                "source_field": "line_items.quantity",
                "target_document_id": f"{pkg_id}_PL",
                "target_field": "line_items.quantity",
                "expected_outcome": "discrepancy" if is_qty_mismatch else "match",
                "discrepancy_category": "quantity_mismatch"
                if is_qty_mismatch
                else "none",
                "explanation": (
                    f"Invoice quantity ({pkg['inv_qty_display']}) differs from Packing List quantity ({pkg['pl_qty_display']})"
                    if is_qty_mismatch
                    else "Quantities match across Invoice and Packing List."
                ),
                "expected_source_value": pkg["inv_qty_display"],
                "expected_target_value": pkg["pl_qty_display"],
            }
        )
        comp_counter += 1

        # Rule WT-001: Gross Weight Consistency
        is_gw_mismatch = pkg["scenario_id"] == "GROSS_WEIGHT_MISMATCH_EN"
        all_comparisons.append(
            {
                "comparison_id": f"CMP-{comp_counter:03d}",
                "package_id": pkg_id,
                "rule_id": "WT-001",
                "rule_name": "Comparable Gross Weight Consistency",
                "source_document_id": f"{pkg_id}_INV",
                "source_field": "line_items.gross_weight",
                "target_document_id": f"{pkg_id}_PL",
                "target_field": "total_gross_weight",
                "expected_outcome": "discrepancy" if is_gw_mismatch else "match",
                "discrepancy_category": "gross_weight_mismatch"
                if is_gw_mismatch
                else "none",
                "explanation": (
                    f"Gross weight on Invoice ({pkg['inv_gw_display']}) differs from Packing List ({pkg['pl_gw_display']})"
                    if is_gw_mismatch
                    else "Gross weight values are consistent."
                ),
                "expected_source_value": pkg["inv_gw_display"],
                "expected_target_value": pkg["pl_gw_display"],
            }
        )
        comp_counter += 1

        # Rule PARTY-001: Buyer and Seller Identity Consistency
        is_party_mismatch = pkg["scenario_id"] in [
            "PARTY_BUYER_MISMATCH_EN",
            "PARTY_SELLER_MISMATCH_VI",
        ]
        all_comparisons.append(
            {
                "comparison_id": f"CMP-{comp_counter:03d}",
                "package_id": pkg_id,
                "rule_id": "PARTY-001",
                "rule_name": "Buyer/Consignee and Seller/Shipper Identity Consistency",
                "source_document_id": f"{pkg_id}_INV",
                "source_field": "buyer_name"
                if "BUYER" in pkg["scenario_id"]
                else "seller_name",
                "target_document_id": f"{pkg_id}_PL",
                "target_field": "buyer_name"
                if "BUYER" in pkg["scenario_id"]
                else "seller_name",
                "expected_outcome": "discrepancy" if is_party_mismatch else "match",
                "discrepancy_category": "party_identity_mismatch"
                if is_party_mismatch
                else "none",
                "explanation": (
                    "Party name on Invoice differs from corresponding party on Packing List"
                    if is_party_mismatch
                    else "Party identities are consistent across documents."
                ),
                "expected_source_value": pkg["buyer"]["name"]
                if "BUYER" in pkg["scenario_id"]
                else pkg["seller"]["name"],
                "expected_target_value": pkg["pl_buyer_name"]
                if "BUYER" in pkg["scenario_id"]
                else pkg["pl_seller_name"],
            }
        )
        comp_counter += 1

        # Rule ID-001: Order Reference Consistency
        is_id_mismatch = pkg["scenario_id"] in [
            "IDENTIFIER_ORDER_MISMATCH_EN",
            "IDENTIFIER_ORDER_MISMATCH_VI",
        ]
        all_comparisons.append(
            {
                "comparison_id": f"CMP-{comp_counter:03d}",
                "package_id": pkg_id,
                "rule_id": "ID-001",
                "rule_name": "Order / PO Reference Consistency",
                "source_document_id": f"{pkg_id}_INV",
                "source_field": "order_number",
                "target_document_id": f"{pkg_id}_PL",
                "target_field": "order_number",
                "expected_outcome": "discrepancy" if is_id_mismatch else "match",
                "discrepancy_category": "identifier_mismatch"
                if is_id_mismatch
                else "none",
                "explanation": (
                    f"Order number on Invoice ({pkg['order_no']}) does not match Packing List ({pkg['pl_order_no']})"
                    if is_id_mismatch
                    else "Order reference is identical across documents."
                ),
                "expected_source_value": pkg["order_no"],
                "expected_target_value": pkg["pl_order_no"],
            }
        )
        comp_counter += 1

        # Rule MONEY-001 & MONEY-002: Arithmetic Consistency (checked on invoice)
        if pkg["scenario_id"] == "ARITHMETIC_LINE_TOTAL_EN":
            all_comparisons.append(
                {
                    "comparison_id": f"CMP-{comp_counter:03d}",
                    "package_id": pkg_id,
                    "rule_id": "MONEY-001",
                    "rule_name": "Line Item Quantity x Unit Price vs Line Total",
                    "source_document_id": f"{pkg_id}_INV",
                    "source_field": "line_items.unit_price",
                    "target_document_id": f"{pkg_id}_INV",
                    "target_field": "line_items.line_total",
                    "expected_outcome": "discrepancy",
                    "discrepancy_category": "arithmetic_error",
                    "explanation": "Calculated line total (50 * 1650 = 82500.00) differs from printed total (72500.00).",
                    "expected_source_value": 82500.00,
                    "expected_target_value": 72500.00,
                }
            )
            comp_counter += 1

        if pkg["scenario_id"] == "ARITHMETIC_TOTAL_SUM_VI":
            all_comparisons.append(
                {
                    "comparison_id": f"CMP-{comp_counter:03d}",
                    "package_id": pkg_id,
                    "rule_id": "MONEY-002",
                    "rule_name": "Sum of Line Totals vs Invoice Total",
                    "source_document_id": f"{pkg_id}_INV",
                    "source_field": "line_items.line_total_sum",
                    "target_document_id": f"{pkg_id}_INV",
                    "target_field": "total_amount",
                    "expected_outcome": "discrepancy",
                    "discrepancy_category": "arithmetic_error",
                    "explanation": "Sum of line totals (25000 + 25000 = 50000.00) differs from printed total (60000.00).",
                    "expected_source_value": 50000.00,
                    "expected_target_value": 60000.00,
                }
            )
            comp_counter += 1

    # 5. Write manifest.json
    manifest = {
        "dataset_name": "Synthetic Bilingual Export Document Pilot Dataset",
        "dataset_version": "1.0.0",
        "generation_seed": 42,
        "total_packages": len(manifest_packages),
        "total_documents": len(manifest_packages) * 2,
        "packages": manifest_packages,
    }
    with open(OUTPUT_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # 6. Write expected_comparisons.json
    comparisons_data = {
        "dataset_version": "1.0.0",
        "total_comparisons": len(all_comparisons),
        "comparisons": all_comparisons,
    }
    with open(OUTPUT_DIR / "expected_comparisons.json", "w", encoding="utf-8") as f:
        json.dump(comparisons_data, f, ensure_ascii=False, indent=2)

    print(
        f"Generated {len(manifest_packages)} packages ({len(manifest_packages) * 2} documents)."
    )
    print(f"Saved manifest: {OUTPUT_DIR / 'manifest.json'}")
    print(f"Saved comparisons: {OUTPUT_DIR / 'expected_comparisons.json'}")


if __name__ == "__main__":
    generate_dataset()
