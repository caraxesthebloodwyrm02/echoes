#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Test Privacy Filter Implementation
"""

from packages.security.privacy_filter import PrivacyFilter
from packages.security.privacy_middleware import PrivacyMiddleware


def test_privacy_filter():
    """Test basic privacy filter functionality"""
    print("Testing Privacy Filter...")

    privacy_filter = PrivacyFilter()

    # Test text with various PII
    test_text = """
    Contact information:
    Email: john.doe@example.com
    Phone: (555) 123-4567
    SSN: 123-45-6789
    Credit Card: 4111 1111 1111 1111
    IP: 192.168.1.100
    DOB: 01/15/1990
    Address: 123 Main Street, Anytown, USA
    """

    print("Original text:")
    print(test_text)

    # Test redact mode
    redacted = privacy_filter.redact(test_text)
    print("\nRedacted:")
    print(redacted)

    # Test anonymize mode
    anonymized = privacy_filter.anonymize(test_text, deterministic=True)
    print("\nAnonymized:")
    print(anonymized)

    # Test mask mode
    masked = privacy_filter.mask(test_text)
    print("\nMasked:")
    print(masked)

    # Test consistency of anonymization
    anonymized_again = privacy_filter.anonymize(test_text, deterministic=True)
    print("\nAnonymized again (should be identical):")
    print(anonymized_again)
    print(f"Consistent: {anonymized == anonymized_again}")


def test_privacy_middleware():
    """Test privacy middleware functionality"""
    print("\n" + "=" * 50)
    print("Testing Privacy Middleware...")

    # Test with different modes
    for mode in ["redact", "anonymize", "mask"]:
        print(f"\nTesting {mode} mode:")

        middleware = PrivacyMiddleware(filter_mode=mode)

        @middleware.filter_response
        def get_user_data():
            return {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "555-123-4567",
                "details": {"ssn": "123-45-6789", "ip": "192.168.1.100"},
                "notes": "User john.doe@example.com called from (555) 123-4567",
            }

        result = get_user_data()
        print(f"Filtered result: {result}")


if __name__ == "__main__":
    test_privacy_filter()
    test_privacy_middleware()
    print("\n" + "=" * 50)
    print("Privacy filter tests completed!")
