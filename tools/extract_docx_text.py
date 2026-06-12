import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

for p in sorted(Path('.').glob('*.docx')):
    print('\n===', p.name, '===')
    try:
        with zipfile.ZipFile(p) as z:
            text = []
            for name in z.namelist():
                if name.endswith('document.xml'):
                    root = ET.fromstring(z.read(name))
                    for t in root.findall('.//w:t', ns):
                        text.append(t.text or '')
            print(''.join(text)[:40000])
    except Exception as e:
        print('ERROR', e)
