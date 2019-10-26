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


def get_with_features(is_xml, features=None, feature_filter=lambda x: x, format_=None):
    format_ = global_yaml.get(format_, "{features}")
    if features is None:
        features = mod_yaml['features']
    xml_features = global_yaml.get('xml_feature_format', "<color=teal><b>{title}</b></color>\n{desc}")
    steam_features = global_yaml.get('steam_feature_format', "[b]{title}[/b]\n[i]{steam}[/i]\n{desc}")
    feature_format = xml_features if is_xml else steam_features

    lines = []
    for _feature in filter(feature_filter, features):
        feature = defaultdict(str, _feature)
        format_exist = "\n".join(l for l in feature_format.split("\n") if re.sub(r'</?.*?>' if is_xml else r'\[/?.*?]', '', l.format_map(feature)))
        lines.append(format_exist.format_map(feature) + "\n")
    feature_text = "\n".join(lines).strip()
    if is_xml:
        feature_text = markup_to_xml(feature_text) + "\n"  # without ending \n, text can be cut off

    all_data = defaultdict(str, {**mod_yaml, **global_yaml})
    all_data['features'] = feature_text  # for a friendly key name within formats
    text = format_.format_map(all_data).format_map(all_data)
    return text


def get_steam_markup():
    result = get_with_features(is_xml=False, feature_filter=lambda x: x.get('title'), format_='steam_format')
    return result


def get_about():
    description = get_with_features(is_xml=True, feature_filter=lambda x: x.get('title'), format_='about_format')
    supported_versions = E.supportedVersions()
    for v in mod_yaml['supported_versions']:
        supported_versions.append(E.li(str(v)))
    result = E.ModMetaData(
        E.name(mod_yaml['name']),
        E.author(mod_yaml.get('author', global_yaml['author'])),
        E.url(mod_yaml.get('url', mod_yaml.get('repo'))),
        supported_versions,
        E.description(etree.CDATA(description)),
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
        content = get_with_features(is_xml=True, features=features)
        element = E("HugsLib.UpdateFeatureDef",
                    {'ParentName': "UpdateFeatureBase"},
                    E.defName(mod_yaml['identifier'] + '_' + version.replace(r'.', r'_')),
                    E.assemblyVersion(version),
                    E.content(etree.CDATA(content)),
                    )
        result.append(element)
    return result


def get_settings():
    def val(a, b):
        # so we can give a setting key an explicit blank value instead of inheriting the feature value
        return "" if a == "" else (a or b)

    gathered = defaultdict(lambda: defaultdict(str))
    for feature in mod_yaml['features']:
        for setting in feature.get('settings', []):
            name = setting['name']
            gathered[name]['title'] += (val(setting.get('title'), feature['title']))
            gathered[name]['desc'] += (val(setting.get('desc'), feature.get('desc')))

    result = E.LanguageData()
    for setting in gathered:
        title = E("{}_{}Setting_title".format(mod_yaml['prefix'], setting),
                  etree.CDATA(markup_to_xml(re.sub(r'\.$', r'', gathered[setting]['title']))))
        result.append(title)
        desc = E("{}_{}Setting_description".format(mod_yaml['prefix'], setting),
                 etree.CDATA(markup_to_xml(gathered[setting]['desc'])))
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
    result = text
    url_format = global_yaml.get('xml_url_format', r'<color=grey><b>{text}</b></color>').format(url=r'\1', text=r'\2')
    result = re.sub(r'\[url=(.*?)](.*?)\[/url]', url_format, result, flags=re.DOTALL)
    u_format = global_yaml.get('xml_u_format', r'<color=grey>{text}</color>').format(text=r'\1')
    result = re.sub(r'\[u](.*?)\[/u]', u_format, result, flags=re.DOTALL)

    count = -1
    while count != 0:
        result, count = re.subn(r'\[(\w+)(=\w+)?](.*?)\[/\1]', r'<\1\2>\3</\1>', result, flags=re.DOTALL)
    return result


if __name__ == '__main__':
    main()
