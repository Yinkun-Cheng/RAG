"""测试配置是否正确加载"""
from app.config import settings

print(f"BRCONNECTOR_API_KEY: {settings.BRCONNECTOR_API_KEY[:20]}...")
print(f"BRCONNECTOR_BASE_URL: {settings.BRCONNECTOR_BASE_URL}")
print(f"BRCONNECTOR_MODEL: {settings.BRCONNECTOR_MODEL}")
