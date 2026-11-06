import base64

import pytest

from upcloud.quickxor import QuickXorHash, quickxor_file

# Vectors from rclone backend/onedrive/quickxorhash/quickxorhash_test.go, an
# implementation of the algorithm published on Microsoft Learn (QuickXorHash snippet).
VECTORS = [
    ("", "AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
    ("Sg==", "SgAAAAAAAAAAAAAAAQAAAAAAAAA="),
    ("tbQ=", "taAFAAAAAAAAAAAAAgAAAAAAAAA="),
    ("T6LYJIfDh81JrAK309H2JMJTXis=", "zBTHrspn3mEcohlJdIUAbjGNaNg="),
    ("DWAAX5/CIfrmErgZa8ot6ZraeSbu", "LR2Z0PjuRYGKQB/mhQAuMrAGZbQ="),
    ("PfxMcUd0vIW6VbHG/uj/Y0W6qEoKmyBD0nYebEKazKaKG+UaDqBEcmQjbfQeVnVLuodMoPp7P7TR1htX5n2VnkHh22xDyoJ8C/ZQKiSNqQfXvh83judf4RVr9exJCud8Uvgip6aVZTaPrJHVjQhMCp/dEnGvqg0oN5OVkM2qqAXvA0teKUDhgNM71sDBVBCGXxNOR2bpbD1iM4dnuT0ey4L+loXEHTL0fqMeUcEi2asgImnlNakwenDzz0x57aBwyq3AspCFGB1ncX4yYCr/OaCcS5OKi/00WH+wNQU3",
     "QX/YEpG0gDsmhEpCdWhsxDzsfVE="),
    ("w0LGhqU1WXFbdavqDE4kAjEzWLGGzmTNikzqnsiXHx2KRReKVTxkv27u3UcEz9+lbMvYl4xFf2Z4aE1xRBBNd1Ke5C0zToSaYw5o4B/7X99nKK2/XaUX1byLow2aju2XJl2OpKpJg+tSJ2fmjIJTkfuYUz574dFX6/VXxSxwGH/xQEAKS5TCsBK3CwnuG1p5SAsQq3gGVozDWyjEBcWDMdy8/AIFrj/y03Lfc/RNRCQTAfZbnf2QwV7sluw4fH3XJr07UoD0YqN+7XZzidtrwqMY26fpLZnyZjnBEt1FAZWO7RnKG5asg8xRk9YaDdedXdQSJAOy6bWEWlABj+tVAigBxavaluUH8LOj+yfCFldJjNLdi90fVHkUD/m4Mr5OtmupNMXPwuG3EQlqWUVpQoYpUYKLsk7a5Mvg6UFkiH596y5IbJEVCI1Kb3D1",
     "e3+wo77iKcILiZegnzyUNcjCdoQ="),
]


@pytest.mark.parametrize("data_b64,expected", VECTORS)
def test_quickxor_matches_published_vectors(data_b64, expected):
    h = QuickXorHash()
    h.update(base64.b64decode(data_b64))
    assert h.b64digest() == expected


def test_quickxor_streaming_equals_one_shot():
    data = bytes((i * 7 + 3) % 256 for i in range(5000))
    one = QuickXorHash()
    one.update(data)
    streamed = QuickXorHash()
    for start in range(0, len(data), 333):
        streamed.update(data[start:start + 333])
    assert streamed.b64digest() == one.b64digest()


def test_quickxor_file(tmp_path):
    data = base64.b64decode(VECTORS[-1][0])
    p = tmp_path / "f.bin"
    p.write_bytes(data)
    assert quickxor_file(p, chunk_size=100) == VECTORS[-1][1]
