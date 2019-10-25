# Copyright (C) 2019  Christopher S. Galpin.  See /NOTICE.
import os, re, yaml
# from autohotkey import Script
from collections import defaultdict, namedtuple
from lxml import etree
from lxml.builder import E

parser = etree.XMLParser(remove_blank_text=True)
areUpdatesDescending = True
Project = namedtuple('Project', ['path', 'update_prefix', 'setting_prefix'])
_global_path = r'global.yaml'
global_yaml = {}
if os.path.exists(_global_path):
    with open(_global_path, encoding='utf-8') as f:
        global_yaml = yaml.safe_load(f)
mod_yaml = {}


def main():
    projects = [
        Project(r'C:\Dropbox\RimWorld\AssortedAlterations', r'COAssortedAlterations', r'COAA'),
        Project(r'C:\Dropbox\RimWorld\CustomThingFilters', r'COCustomThingFilters', r'COCTF'),
        Project(r'C:\Dropbox\RimWorld\ResourceGoalTracker', r'COResourceGoalTracker', r'CORGT'),
    ]
    for project in projects:
        write_files(project)
    pass


def write_files(project):
    global mod_yaml
    data_path = os.path.join(project.path, r'public.yaml')
    with open(data_path, encoding='utf8') as f:
        mod_yaml = yaml.safe_load(f)

    settings_path = os.path.join(project.path, r'Languages\English\Keyed\Settings.xml')
    if os.path.exists(settings_path):
        write_settings(project, settings_path)
    about_path = os.path.join(project.path, r'About\About.xml')
    write_about(about_path)
    updates_path = os.path.join(project.path, r'Defs\UpdateFeatureDefs\UpdateFeatures.xml')
    write_updates(project, updates_path)

    markup = get_steam_markup()
    # ahk = Script()
    # ahk.set('clipboard', markup)
    print('-' * 100)
    print(markup)
    print('-' * 100)


def write_updates(project, path):
    def version_features():
        versions = set(x['at'] for x in mod_yaml['features'] if 'at' in x)
        result = {v: [f for f in mod_yaml['features'] if f.get('at') == v] for v in versions}
        return result

    tree = etree.parse(path, parser)
    for version, features in version_features().items():
        content = tree.find(r"./HugsLib.UpdateFeatureDef[assemblyVersion='{}']/content".format(version))
        if content is None:
            content = etree.Element("content")
            element = E.HugsLibUpdateFeatureDef(
                {'ParentName': "UpdateFeatureBase"},
                E.defName(project.update_prefix + '_' + version.replace(r'.', r'_')),
                E.assemblyVersion(version),
                content,
            )
            element.tag = "HugsLib.UpdateFeatureDef"  # add the period
            if areUpdatesDescending:
                tree.getroot().insert(1, element)
            else:
                tree.getroot().append(element)

        content.text = text_from_lines(get_xml_features(features), for_xml=True)
    tree.write(path, encoding='utf-8', xml_declaration=True, pretty_print=True)


def write_about(path):
    tree = etree.parse(path, parser)
    description = tree.find(r'./description')
    description.text = text_from_lines(get_xml_features(x for x in mod_yaml['features'] if 'title' in x), for_xml=True)
    tree.write(path, encoding='utf-8', xml_declaration=True, pretty_print=True)


def write_settings(project, path):
    tree = etree.parse(path)
    root = tree.getroot()
    root.clear()
    elements = get_setting_elements(project)
    for element in elements:
        root.append(element)
    tree.write(path, encoding='utf-8', xml_declaration=True, pretty_print=True)


def wrap(tag, text):
    close_tag = tag.split(r'=', 1)[0]
    return "[{tag}]{text}[/{close_tag}]".format(**locals()) if text else ""


def get_steam_markup():
    lines = [
        [
            mod_yaml.get('desc'),  # first for Steam previews
            global_yaml.get('header', "").format(**mod_yaml),
        ],
        [
            wrap('h1', mod_yaml.get('heading')),
            '\b',
            wrap('i', mod_yaml.get('flavor')),
        ] + get_markup_features(x for x in mod_yaml['features'] if 'title' in x),
        [mod_yaml.get('footer')],
        [global_yaml.get('footer', "").format(**mod_yaml)],
    ]
    result = text_from_lines(lines)
    return result


def text_from_lines(lines, for_xml=False):
    def depth(list_):
        return max(map(depth, list_)) + 1 if isinstance(list_, list) else 0

    def recurse(list_, count):
        if isinstance(list_, list):
            lines_ = [y for y in (recurse(x, count - 1) for x in list_ if x) if y]
            result_ = ("\n" * count).join(lines_)
            # treat \b as symbolically "backspacing" newlines between elements
            result_ = re.sub('\n{{0,{count}}}\b\n{{0,{count}}}'.format(**locals()), "\n" * (count - 1), result_)
            return result_
        return list_

    depth = depth(lines)
    result = recurse(lines, depth)
    if for_xml:
        result = etree.CDATA(markup_to_xml(result) + "\n")  # without ending \n text can be cut off
    return result


def get_markup_features(features):
    result = []
    for feature in features:
        feature_lines = [
            wrap('b', feature.get('title')),
            wrap('i', feature.get('flavor')),
            " " if feature.get('desc') and '\n' in feature.get('flavor', "") else "",
            feature.get('desc'),
        ]
        result.append(feature_lines)
    return result


def markup_to_xml(text):
    result = text.strip()
    result = re.sub(r'\[url=.*?](.*?)\[/url]', r'<color=grey><b>\1</b></color>', result, flags=re.DOTALL)
    result = re.sub(r'\[u](.*?)\[/u]', r'<color=grey>\1</color>', result, flags=re.DOTALL)

    count = -1
    while count != 0:
        result, count = re.subn(r'\[(\w+)(=\w+)?](.*?)\[/\1]', r'<\1\2>\3</\1>', result, flags=re.DOTALL)
    return result


def get_xml_features(features):
    result = []
    for feature in features:
        feature_lines = [
            wrap('color=teal', wrap('b', feature.get('title'))),
            feature.get('desc'),
            wrap('i', feature.get('flavor')) if not feature.get('desc') else "",
        ]
        result.append(feature_lines)
    return result


def get_setting_elements(project):
    def val(a, b):
        # so we can give a setting key an explicit blank value instead of inheriting the feature value
        if a == "":
            return ""
        return a or b

    out_settings = defaultdict(lambda: defaultdict(str))
    for feature in mod_yaml['features']:
        for setting in feature.get('settings', []):
            name = setting['name']
            out_settings[name]['title'] += (val(setting.get('title'), feature['title']))
            out_settings[name]['desc'] += (val(setting.get('desc'), feature.get('desc')))

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
