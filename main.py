# Copyright (C) 2019  Christopher S. Galpin.  See /NOTICE.
import os, re, yaml
# from autohotkey import Script
from collections import defaultdict, namedtuple
from lxml import etree
from lxml.builder import E

parser = etree.XMLParser(remove_blank_text=True)
areUpdatesDescending = True
Project = namedtuple('Project', ['path', 'update_prefix', 'setting_prefix'])


def main():
    # aa_project = Project(r'C:\Dropbox\RimWorld\AssortedAlterations', r'COAssortedAlterations', r'COAA')
    # write_files(aa_project)
    # ctf_project = Project(r'C:\Dropbox\RimWorld\CustomThingFilters', r'COCustomThingFilters', r'COCTF')
    # write_files(ctf_project)
    pass


def write_files(project):
    data_path = os.path.join(project.path, r'public.yaml')
    with open(data_path, encoding='utf8') as f:
        data = yaml.safe_load(f)

    settings_path = os.path.join(project.path, r'Languages\English\Keyed\Settings.xml')
    write_settings(data, project, settings_path)
    about_path = os.path.join(project.path, r'About\About.xml')
    write_about(data, about_path)
    updates_path = os.path.join(project.path, r'Defs\UpdateFeatureDefs\UpdateFeatures.xml')
    write_updates(data, project, updates_path)

    # ahk = Script(ahk_path=os.path.join(os.environ['ProgramW6432'], r'AutoHotkey\AutoHotkey.exe'))
    # ahk.set('clipboard', get_steam_markup(data))
    print('-' * 100)
    print(get_steam_markup(data))
    print('-' * 100)


def write_updates(data, project, path):
    def version_features():
        versions = set(f['at'] for f in data['features'] if 'at' in f)
        result = {v: [f for f in data['features'] if 'at' in f and f['at'] == v] for v in versions}
        return result

    tree = etree.parse(path, parser)
    for version, features in version_features().items():
        content = tree.find(r"./HugsLib.UpdateFeatureDef[assemblyVersion='{}']/content".format(version))
        if content is None:
            content = etree.Element("content")
            element = E.HugsLibUpdateFeatureDef(
                {'ParentName': "UpdateFeatureBase"},
                E.defName(project.update_prefix + version.replace(r'.', r'_')),
                E.assemblyVersion(version),
                content,
            )
            element.tag = "HugsLib.UpdateFeatureDef"  # add the period
            if areUpdatesDescending:
                tree.getroot().insert(1, element)
            else:
                tree.getroot().append(element)

        content.text = get_features_text(features)
    tree.write(path, encoding='utf-8', xml_declaration=True, pretty_print=True)


def write_about(data, path):
    tree = etree.parse(path, parser)
    description = tree.find(r'./description')
    description.text = get_features_text(data['features'])
    tree.write(path, encoding='utf-8', xml_declaration=True, pretty_print=True)


def write_settings(data, project, path):
    tree = etree.parse(path)
    root = tree.getroot()
    root.clear()
    elements = get_setting_elements(data, project)
    for element in elements:
        root.append(element)
    tree.write(path, encoding='utf-8', xml_declaration=True, pretty_print=True)


def get_steam_markup(data):
    lines = [data['header']]
    for _feature in data['features']:
        feature = defaultdict(str, _feature)
        feature_markup = ["[u]{}[/u]".format(feature['title'])]
        flavor = feature['flavor']
        if flavor:
            feature_markup.append("[i]{}[/i]".format(flavor))
        desc = feature['desc']
        if desc:
            feature_markup.append("{}{}".format("\n" if '\n' in flavor else "", desc))

        lines.append("\n".join(feature_markup))

    lines.append(data['footer'])
    result = "\n\n".join(lines)
    return result


def markup_to_xml(text):
    result = text.strip()
    result = re.sub(r'\[url=.*?](.*?)\[/url]', r'<color=grey><b>\1</b></color>', result, flags=re.DOTALL)
    result = re.sub(r'\[b](.*?)\[/b]', r'<b>\1</b>', result, flags=re.DOTALL)
    result = re.sub(r'\[i](.*?)\[/i]', r'<i>\1</i>', result, flags=re.DOTALL)
    result = re.sub(r'\[u](.*?)\[/u]', r'<u>\1</u>', result, flags=re.DOTALL)
    return result


def get_features_text(features):
    lines = []
    for _feature in features:
        feature = defaultdict(str, _feature)
        feature_xml = ["<color=teal><b>{}</b></color>".format(markup_to_xml(feature['title']))]
        if 'desc' in feature:
            feature_xml.append(markup_to_xml(feature['desc']))
        elif 'flavor' in feature:
            feature_xml.append("<i>{}</i>".format(markup_to_xml(feature['flavor'])))
        lines.append("\n".join(feature_xml))
    result = etree.CDATA("\n\n".join(lines) + "\n")  # without ending \n the text can get cutoff
    return result


def get_setting_elements(data, project):
    def val(a, b):
        # so we can give a blank key in yaml to avoid inheritance
        if a is None:
            return ""
        return a or b

    out_settings = defaultdict(lambda: defaultdict(str))
    for _feature in data['features']:
        feature = defaultdict(str, _feature)
        for _setting in feature['settings']:
            setting = defaultdict(str, _setting)
            name = setting['name']
            out_settings[name]['title'] += (val(setting['title'], feature['title']))
            out_settings[name]['desc'] += (val(setting['desc'], feature['desc']))

    result = []
    for k in out_settings:
        title = etree.Element("{}_{}Setting_title".format(project.setting_prefix, k))
        title.text = etree.CDATA(markup_to_xml(re.sub(r'\.$', r'', out_settings[k]['title'])))
        result.append(title)
        desc = etree.Element("{}_{}Setting_description".format(project.setting_prefix, k))
        desc.text = etree.CDATA(markup_to_xml(out_settings[k]['desc']))
        result.append(desc)
    return result


if __name__ == '__main__':
    main()
