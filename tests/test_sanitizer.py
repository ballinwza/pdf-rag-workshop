import pytest
from src.sanitizer import DataSanitizer

def test_regex_redaction():
    sanitizer = DataSanitizer()
    text = "เลขบัตรประชาชนคือ 1100200300401 และเบอร์โทร 081-234-5678"
    result = sanitizer.sanitize(text)
    
    # ตรวจสอบว่าข้อมูลเดิมต้องหายไป
    assert "1100200300401" not in result
    assert "081-234-5678" not in result
    # ตรวจสอบว่าถูกแทนที่ด้วย Tag ป้องกัน
    assert "[REDACTED_NATIONAL_ID]" in result
    assert "[REDACTED_PHONE]" in result

def test_keyword_blacklist():
    sanitizer = DataSanitizer(custom_keywords=["Project Manhattan", "SecretCorp"])
    text = "เอกสารลับของ Project Manhattan โดยบริษัท SecretCorp"
    result = sanitizer.sanitize(text)
    
    assert "Project Manhattan" not in result
    assert "SecretCorp" not in result