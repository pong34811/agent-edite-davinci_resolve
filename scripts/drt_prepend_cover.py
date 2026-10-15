"""Shift all content in a disposable DRT by N frames, preserving source/Fusion data.

MCP-GAP: Studio Timeline API has no all-track ripple insertion including subtitles.
Only exported DRT archives are patched; Resolve import/readback is required.
"""
import copy
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import zstandard
from scripts.drt_shift_subtitles import _read_varint, _write_varint

def _shift_message(data, old, new, depth=0):
    if depth>8: return data,0
    out=bytearray(); pos=0; count=0
    try:
        while pos<len(data):
            begin=pos; key,pos=_read_varint(data,pos); field,wire=key>>3,key&7
            if not field: raise ValueError('zero field')
            if wire==0:
                val,end=_read_varint(data,pos)
                if field==21 and val==old:
                    out.extend(data[begin:pos]+_write_varint(new)); count+=1
                else: out.extend(data[begin:end])
                pos=end
            elif wire==2:
                size,start=_read_varint(data,pos); end=start+size
                if end>len(data): raise ValueError('length')
                # Start lives in the field-1 clip metadata, not in source ranges/effect payloads.
                nested,n=_shift_message(data[start:end],old,new,depth+1) if field==1 else (data[start:end],0)
                out.extend(data[begin:pos]+_write_varint(len(nested))+nested); count+=n; pos=end
            elif wire in (1,5):
                pos+=8 if wire==1 else 4
                if pos>len(data): raise ValueError('fixed')
                out.extend(data[begin:pos])
            else: raise ValueError('wire')
    except ValueError:
        return data,0
    return bytes(out),count

def shift_blob(text,old,new):
    b=bytes.fromhex(text)
    assert int.from_bytes(b[:4],'big')==2 and int.from_bytes(b[4:8],'big')==len(b)-8
    marker=b[8:9]
    assert marker in (b'\x80',b'\x81')
    payload=zstandard.ZstdDecompressor().decompress(b[9:]) if marker==b'\x81' else b[9:]
    updated,count=_shift_message(payload,old,new)
    assert count==1, f'expected one start field, found {count}, start {old}'
    encoded=marker+(zstandard.ZstdCompressor().compress(updated) if marker==b'\x81' else updated)
    return (b[:4]+len(encoded).to_bytes(4,'big')+encoded).hex()

def shift_drt(source,target,frames):
    assert frames>0
    with zipfile.ZipFile(source) as z:
        assert z.testzip() is None
        infos=z.infolist(); payloads={i.filename:z.read(i) for i in infos}; comment=z.comment
    name=next(n for n in payloads if n.startswith('SeqContainer/') and n.endswith('.xml'))
    root=ET.fromstring(payloads[name]); count=0
    for vector in ['VideoTrackVec','AudioTrackVec','SubtitleTrackVec','GeometryTrackVec']:
        for track in root.find(vector).findall('Element/Sm2TiTrack'):
            for wrapper in track.find('Items').findall('Element'):
                item=wrapper[0]; old=int(item.findtext('Start')); new=old+frames
                before=copy.deepcopy(item)
                item.find('FieldsBlob').text=shift_blob(item.findtext('FieldsBlob'),old,new)
                item.find('Start').text=str(new)
                # All fields except the two start representations must remain byte-identical.
                check=copy.deepcopy(item); check.find('Start').text=before.findtext('Start'); check.find('FieldsBlob').text=before.findtext('FieldsBlob')
                assert ET.tostring(check)==ET.tostring(before)
                count+=1
    payloads[name]=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    Path(target).parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,'w') as z:
        z.comment=comment
        for info in infos: z.writestr(info,payloads[info.filename])
    with zipfile.ZipFile(target) as z: assert z.testzip() is None
    return count
