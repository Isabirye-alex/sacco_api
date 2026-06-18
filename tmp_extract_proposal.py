"""Module for tmp_extract_proposal."""

from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

path = Path('D:/Proposal_Formatted.docx')
print('exists=', path.exists(), 'size=', path.stat().st_size)

with zipfile.ZipFile(path) as zf:
    names = zf.namelist()
    print('entries=', len(names))
    doc_name = next((name for name in names if name.endswith('document.xml')), None)
    if doc_name is None:
        raise RuntimeError('No document.xml found')

    xml = zf.read(doc_name)
    root = ET.fromstring(xml)
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    texts = []
    for p in root.findall('.//w:p', ns):
        t = ''.join(node.text or '' for node in p.findall('.//w:t', ns))
        if t.strip():
            texts.append(t)
    print('paragraphs=', len(texts))
    for i, t in enumerate(texts[:800], 1):
        print(f'[{i}] {t}')
