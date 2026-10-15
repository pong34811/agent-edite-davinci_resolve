import zstandard
import pytest
from scripts.drt_prepend_cover import shift_blob
from scripts.drt_shift_subtitles import _write_varint

def envelope(payload, compressed=False):
    encoded=(b'\x81'+zstandard.ZstdCompressor().compress(payload)) if compressed else b'\x80'+payload
    return (b'\x00\x00\x00\x02'+len(encoded).to_bytes(4,'big')+encoded).hex()

@pytest.mark.parametrize('compressed',[False,True])
def test_nested_start_shift_preserves_source_metadata(compressed):
    # field 21 crosses a varint boundary; source range in field 3 must stay unchanged.
    source=b'\x1a\x03abc'; body=source+b'\xa8\x01'+_write_varint(120)+b'\x20\x01'
    payload=b'\x0a'+_write_varint(len(body))+body
    actual=bytes.fromhex(shift_blob(envelope(payload,compressed),120,150))
    decoded=zstandard.ZstdDecompressor().decompress(actual[9:]) if compressed else actual[9:]
    expected=source+b'\xa8\x01'+_write_varint(150)+b'\x20\x01'
    assert decoded==b'\x0a'+_write_varint(len(expected))+expected

def test_refuses_missing_start():
    with pytest.raises(AssertionError): shift_blob(envelope(b'\x20\x01'),0,30)
