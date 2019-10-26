# Copyright (C) 2019  Christopher S. Galpin.  See /NOTICE.
import os, re, yaml, pathlib, sys
# from autohotkey import Script
from collections import defaultdict
from lxml import etree
from lxml.builder import E

_global_path = os.path.join(os.getcwd(), r'global.yaml')
global_yaml = {}
if os.path.exists(_global_path):
    with open(_global_path, encoding='utf-8') as f:
        global_yaml = yaml.safe_load(f)
mod_yaml = {}


def main():
    global mod_yaml
    for yaml_path in sys.argv[1:]:
        if not os.path.isabs(yaml_path):
            yaml_path = os.path.join(os.getcwd(), yaml_path)
        if os.path.isdir(yaml_path):
            yaml_path = os.path.join(yaml_path, r'public.yaml')
        with open(yaml_path, encoding='utf-8') as f:
            mod_yaml = yaml.safe_load(f)

        markup = get_steam_markup()
        about = get_about()
        updates = get_updates()
        settings = get_settings()

        dir_name = os.path.dirname(yaml_path)
        write_xml(dir_name, [mod_yaml.get('about_path'), r'About\About.xml'], about)
        if updates.getchildren():
            write_xml(dir_name, [
                mod_yaml.get('updates_path'),
                r'Defs\UpdateFeatures.xml',
                r'Defs\UpdateFeatureDefs\UpdateFeatures.xml',
            ], updates)
        if settings.getchildren():
            write_xml(dir_name, [mod_yaml.get('settings_path'), r'Languages\English\Keyed\Settings.xml'], settings)

        # ahk = Script()
        # ahk.set('clipboard', markup)
        print('-' * 100)
        print(markup)
        print('-' * 100)


def wrap(tag, text):
    close_tag = tag.split(r'=', 1)[0]
    return "[{tag}]{text}[/{close_tag}]".format(**locals()) if text else ""


def text_from_lines(lines, for_xml=False):
    def depth(list_):
        return max(map(depth, list_)) + 1 if isinstance(list_, list) else 0

    def recurse(list_, count):
        if isinstance(list_, list):
            lines_ = [y for y in (recurse(x, count - 1) for x in list_ if x) if y]
            text = ("\n" * count).join(lines_)
            # treat \b as symbolically "backspacing" newlines between elements
            text = re.sub('\n{{0,{count}}}\b\n{{0,{count}}}'.format(**locals()), "\n" * (count - 1), text)
            return text
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


def get_about():
    supported_versions = etree.Element("supportedVersions")
    for v in mod_yaml['supported_versions']:
        supported_versions.append(E.li(str(v)))
    result = E.ModMetaData(
        E.name(mod_yaml['name']),
        E.author(mod_yaml.get('author', global_yaml['author'])),
        E.url(mod_yaml.get('url', mod_yaml.get('repo'))),
        supported_versions,
        E.description(text_from_lines(get_xml_features(x for x in mod_yaml['features'] if 'title' in x), for_xml=True))
    )
    return result


def get_updates():
    result = E.Defs(
        E("HugsLib.UpdateFeatureDef",
          {'Abstract': "true", 'Name': "UpdateFeatureBase"},
          E.modNameReadable(mod_yaml['name']),
          E.modIdentifier(mod_yaml['identifier']),
          E.linkUrl(mod_yaml.get('url', mod_yaml.get('repo'))),
          )
    )

    def version_features():
        versions = set(x['at'] for x in mod_yaml['features'] if 'at' in x)
        _version_features = {v: [f for f in mod_yaml['features'] if f.get('at') == v] for v in versions}
        return _version_features

    reverse = mod_yaml.get('descending_updates', global_yaml.get('descending_updates', True))
    for version, features in sorted(version_features().items(), reverse=reverse):
        element = E("HugsLib.UpdateFeatureDef",
                    {'ParentName': "UpdateFeatureBase"},
                    E.defName(mod_yaml['identifier'] + '_' + version.replace(r'.', r'_')),
                    E.assemblyVersion(version),
                    E.content(text_from_lines(get_xml_features(features), for_xml=True)),
                    )
        result.append(element)
    return result


def get_settings():
    def val(a, b):
        # so we can give a setting key an explicit blank value instead of inheriting the feature value
        return "" if a == "" else (a or b)

    result = E.LanguageData()
    gathered = defaultdict(lambda: defaultdict(str))
    for feature in mod_yaml['features']:
        for setting in feature.get('settings', []):
            name = setting['name']
            gathered[name]['title'] += (val(setting.get('title'), feature['title']))
            gathered[name]['desc'] += (val(setting.get('desc'), feature.get('desc')))

    for k in gathered:
        title = etree.Element("{}_{}Setting_title".format(mod_yaml['prefix'], k))
        title.text = etree.CDATA(markup_to_xml(re.sub(r'\.$', r'', gathered[k]['title'])))
        result.append(title)
        desc = etree.Element("{}_{}Setting_description".format(mod_yaml['prefix'], k))
        desc.text = etree.CDATA(markup_to_xml(gathered[k]['desc']))
        result.append(desc)

    return result


def write_xml(base_path, rel_paths, root):
    paths = [os.path.join(base_path, rel_path) for rel_path in rel_paths if rel_path]
    exist_paths = (path for path in paths if os.path.exists(path))
    path = next(exist_paths, None) or paths[0]

    pathlib.Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, mode='wb') as f:
        f.write(etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True))


def markup_to_xml(text):
    result = text.strip()
    result = re.sub(r'\[url=.*?](.*?)\[/url]', r'<color=grey><b>\1</b></color>', result, flags=re.DOTALL)
    result = re.sub(r'\[u](.*?)\[/u]', r'<color=grey>\1</color>', result, flags=re.DOTALL)

    count = -1
    while count != 0:
        result, count = re.subn(r'\[(\w+)(=\w+)?](.*?)\[/\1]', r'<\1\2>\3</\1>', result, flags=re.DOTALL)
    return result


if __name__ == '__main__':
    main()
