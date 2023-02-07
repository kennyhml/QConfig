import xml.dom.minidom
import xml.etree.ElementTree as ET
from collections import defaultdict


def write_to_xml_file(data: bytes, filepath: str) -> None:
    # Decode the bytes literal to a string
    xml_string = data.decode()

    # Use the xml.dom.minidom module to format the XML string
    xml_data = xml.dom.minidom.parseString(xml_string)
    pretty_xml_str = xml_data.toprettyxml()

    with open(filepath, "w") as f:
        f.write(pretty_xml_str)


def etree_to_dict(t):
    """Converts a XML element tree to a dictionary.

    Parameters
    ---------
    root :class:`ET.Element`:
        The element to convert to a dictionary

    Returns
    -------
    `dict`:
        A dictionary representation of the element tree
    """
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d
    
def dict_to_etree(d):
    """Convert a dictionary to an xml.etree.ElementTree object.
    
    Parameters
    ----------
    data :class:`dict`:
        The dictionary to conver to a xml element tree

    parent :class:`ElementTree.Element`:
        The current parent of the element tree

    Returns
    -------
    `ElementTree`:
        The dictionary represented as an element tree
    """
    def _to_etree(d, root):
        if not d:
            pass
        elif isinstance(d, str):
            root.text = d
        elif isinstance(d, dict):
            for k,v in d.items():
                assert isinstance(k, str)
                if k.startswith('#'):
                    assert k == '#text' and isinstance(v, str)
                    root.text = v
                elif k.startswith('@'):
                    assert isinstance(v, str)
                    root.set(k[1:], v)
                elif isinstance(v, list):
                    for e in v:
                        _to_etree(e, ET.SubElement(root, k))
                else:
                    _to_etree(v, ET.SubElement(root, k))
        else:
            raise TypeError('invalid type: ' + str(type(d)))
    assert isinstance(d, dict) and len(d) == 1
    tag, body = next(iter(d.items()))
    node = ET.Element(tag)
    _to_etree(body, node)
    return ET.tostring(node)