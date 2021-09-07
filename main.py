# Copyright (C) 2019-2021  Christopher S. Galpin.  See /NOTICE.
import os
import re
import sys
from pathlib import Path
from shutil import copy
from typing import Any
from typing import Optional

import codeoptimist.yaml
import pyperclip
from codeoptimist.yaml import AttrDict
from codeoptimist.yaml import formatter as f
from lxml import etree
from lxml.builder import E
# noinspection PyProtectedMember
from lxml.etree import _Element
from yaml import SafeLoader
from yaml import add_constructor


class Steam2Xml(str):
    pass


g: AttrDict
# marks a scalar by wrapping it with a constructor we can check later
add_constructor('!steam2xml', lambda l, n: Steam2Xml(l.construct_scalar(n)), Loader=SafeLoader)


def main() -> None:
    global g
    yaml_path = Path(sys.argv[1]).resolve()
    if yaml_path.suffix != '.yaml':
        exit(1)
    g = codeoptimist.yaml.load(yaml_path)

    assert g['out_dir'] is not None
    g.setdefault('local_dir', yaml_path.parent)
    g.setdefault('working_dir', os.getcwd())

    # do this first to hit errors early
    steam = f.format(g.description, l={'is_steam': True})

    # noinspection PyShadowingBuiltins
    def populate_xml(xml_element: _Element, value: Any, *, locals: Optional[dict] = None) -> None:
        if isinstance(dict_ := value, dict):
            for k, v in dict_.items():
                if v is None:  # optional
                    continue
                k = f.format(k, l=locals)
                xml_child = E(k)
                populate_xml(xml_child, v, locals=locals)

                if isinstance(v, Steam2Xml):
                    def steam_to_xml(text: str) -> str:
                        result = text
                        url_format = f.format(g.xml_url_format, l={'url': r'\1', 'text': r'\2'})
                        result = re.sub(r'\[url=(.*?)](.*?)\[/url]', url_format, result, flags=re.DOTALL | re.IGNORECASE)
                        u_format = f.format(g.xml_u_format, l={'text': r'\1'})
                        result = re.sub(r'\[u](.*?)\[/u]', u_format, result, flags=re.DOTALL | re.IGNORECASE)

                        result = re.sub(r'\n\[img](.*?)\[/img]\n', '\n', result, flags=re.DOTALL | re.IGNORECASE)
                        result = re.sub(r'\[img](.*?)\[/img]', '', result, flags=re.DOTALL | re.IGNORECASE)

                        count = -1
                        while count != 0:
                            result, count = re.subn(r'\[(\w+)(=\w+)?](.*?)\[/\1]', r'<\1\2>\3</\1>', result, flags=re.DOTALL)
                        return result

                    # noinspection PyTypeChecker
                    xml_child.text = etree.CDATA(steam_to_xml(xml_child.text))

                is_attribute = k.startswith('_') and len(xml_child) == 0
                if is_attribute:
                    xml_element.set(k[1:], f.format(str(v), l=locals))
                else:
                    xml_element.append(xml_child)
        elif isinstance(list_ := value, list):
            for e in list_:
                xml_child = E.li()
                populate_xml(xml_child, e, locals=locals)
                xml_element.append(xml_child)
        else:
            assert value is not None, f'{xml_element}'
            xml_element.text = f.format(str(value), l=locals)

    about_xml = E.ModMetaData()
    populate_xml(about_xml, g.ModMetaData, locals={'is_about': True})

    def get_updates() -> _Element:
        update_parent = E('HugsLib.UpdateFeatureDef')
        populate_xml(update_parent, g.UpdateFeatureDefBase)
        root = E.Defs(update_parent)

        version_updates = {}
        versions = set(u['at'] for u in g.updates)
        for version in versions:
            version_updates[version] = [u for u in g.updates if u['at'] == version]

        # ascending sort is mandatory with HugsLib on 1.1 or LastSeenNews.xml will update wrong
        for version, updates in sorted(version_updates.items()):
            update_xml = E('HugsLib.UpdateFeatureDef')
            content = '\n'.join(f.format(g.update_format, l=update).strip() + '\n' for update in updates)
            # strip() to end the xml element with only one newline
            populate_xml(update_xml, g.UpdateFeatureDef, locals={'version': version, 'content': content.strip()})
            root.append(update_xml)
        return root

    updates_xml = get_updates()

    def get_keys() -> _Element:
        root = E.LanguageData()
        for key in g.get('keyed', []):
            key: dict
            assert key['name'], key
            assert 'value' in key, key  # permit ''

            xml_container = E('temp')
            populate_xml(xml_container, g.KeyLanguageData, locals=key)
            for key_element in xml_container:
                root.append(key_element)
        return root

    keys_xml = get_keys()

    def get_settings(root: _Element = None) -> _Element:
        if root is None:
            root = E.LanguageData()

        for setting in g.settings:
            setting: dict
            assert setting['name'], setting
            assert 'title' in setting, setting  # permit ''

            # setting['title'] = re.sub(r'\b\.$', '', setting['title'])
            xml_container = E('temp')
            populate_xml(xml_container, g.SettingLanguageData, locals=setting)
            for setting_element in xml_container:
                root.append(setting_element)
        return root

    settings_xml = get_settings(root=(keys_xml if f.format(g.settings_path) == f.format(g.keys_path) else None))

    if g.preview_from_path:
        preview_from_path = Path(f.format(g.preview_from_path))
        preview_path = Path(f.format(g.preview_path))
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        copy(preview_from_path, preview_path)

    if g.published_file_id:
        published_file_id_path = Path(f.format(g.published_file_id_path))
        published_file_id_path.parent.mkdir(parents=True, exist_ok=True)
        with published_file_id_path.open(mode='w', encoding='utf-8') as f_published:
            f_published.write(str(g.published_file_id))

    def write_xml(root: _Element, path_str: str) -> None:
        path = Path(path_str)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(mode='wb') as f_xml:
            f_xml.write(etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True))

    write_xml(about_xml, f.format(g.about_path))
    if updates_xml.getchildren():
        write_xml(updates_xml, f.format(g.updates_path))
    if keys_xml.getchildren():
        write_xml(keys_xml, f.format(g.keys_path))
    if f.format(g.settings_path) != f.format(g.keys_path):
        if settings_xml.getchildren():
            write_xml(settings_xml, f.format(g.settings_path))

    pyperclip.copy(steam)
    print('-' * 100)
    print(steam)
    print('-' * 100)


if __name__ == '__main__':
    main()
