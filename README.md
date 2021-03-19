# RimWorld Mod Description Tool
Generate *About*, *Settings*, *Updates*, and *Steam* from a central file.

## Features
1. Order your mod's features as you wish them presented on Steam/in-game.
1. Annotate with version numbers to include in updates - or write them separately.
1. Annotate with settings for easy tooltips - or write them separately.
   
See `defaults.yaml` for complete configuration, or start with examples.

## Usage
`cd C:\path\to\yaml\files\`  
`C:\path\to\tool\generate.exe my_mod.yaml`

See examples and their output below. _Steam_ will be copied to clipboard.

To centralize your files yet include them with mods, you may wish to [symbolic link (Windows)](https://www.howtogeek.com/howto/16226/complete-guide-to-symbolic-links-symlinks-on-windows-or-linux/) them from within each mod folder to a single working folder of all `.yaml` files, including `defaults.yaml`; this tool will resolve them correctly.

### Included

<details>
<summary><em>defaults.yaml</em></summary>

```yaml
---
## YAML Documentation
# |, |-, |+ block chomping indicators https://yaml.org/spec/1.2/spec.html#id2794534 (|- to strip final linebreaks)
# ~ null type https://yaml.org/type/null.html (~ is same as blank)
# "" vs '' https://yaml.org/spec/1.2/spec.html#id2787109 ("" will interpret \n as a newline)
# yaml multiline interactive summary http://yaml-multiline.info/

## MAIN
# {local_dir} is the (true) folder of the .yaml file given to the program
# {working_dir} is set by the user (generally where the program is executed from)
out_dir: '{local_dir}\_ModDescriptionTool' # for safety so as not to overwrite files unexpectedly

preview_path: '{out_dir}\About\Preview.png'
preview_from_path: ~ # when provided, copy an image to preview_path
published_file_id_path: '{out_dir}\About\PublishedFileId.txt'
published_file_id: ~ # when provided, write to PublishedFileId.txt

features: [ ]
updates: [ ] # standalone updates
settings: [ ] # standalone settings


## FORMATS
steam_format: |- # l.features
  {features}
# setting {steam} is optional '?' and when non-blank is replaced '=' with itself in italics with a trailing newline
# setting {desc} is required and when non-blank appended to '+' with a trailing newline
steam_feature_format: "[u]{title}[/u]\n\
 {steam?=[i]__value__[/i]\n}\
 {desc+\n}\
 \n"

# convenient way of setting {ModMetaData.description} below
about_format: |- # l.features
  {features}
about_feature_format: "<color=white><b>{title}</b></color>\n\
  {desc+\n}\
  \n"

# convenient way of setting {UpdateFeatureDef.content} below
update_format: |- # l.version, l.updates
  {updates}
update_feature_format: "{title?=<color=white><b>__value__</b></color>\n}\
  {desc+\n}\
  \n"

# see end of file for settings since they use dynamic keys


# translate unsupported steam markup to xml
xml_url_format: '<color=grey><b>{text}</b></color>' # l.url, l.text
xml_u_format: '<color=grey>{text}</color>' # l.text


## ABOUT
about_path: '{out_dir}\About\About.xml'
ModMetaData:
  name: ''
  packageId: ''
  author: ''
  url: ~
  supportedVersions:
    - 1.2
  modDependencies: [ ]
  incompatibleWith: [ ]
  loadBefore: [ ]
  loadAfter: [ ]
  description: !steam2xml "{about_format}\n" # \n avoids text cut-off in-game


## UPDATES
updates_path: '{out_dir}\1.2\News\UpdateFeatures.xml'
UpdateFeatureDefBase:
  _Abstract: true
  _Name: &update_base_name '{ModMetaData.packageId}_UpdateFeatureBase'
  # https://github.com/UnlimitedHugs/RimworldHugsLib/blob/477aa179dbedf5d02ce8ede361a42c45af24b746/Source/News/UpdateFeatureDef.cs#L23
  # doesn't hurt to include this
  modNameReadable: '{ModMetaData.name}'
  modIdentifier: '{ModMetaData.packageId}'
  linkUrl: '{ModMetaData.url}'

UpdateFeatureDef:
  _ParentName: *update_base_name
  # https://github.com/UnlimitedHugs/RimworldHugsLib/blob/477aa179dbedf5d02ce8ede361a42c45af24b746/Source/News/UpdateFeatureDef.cs#L106
  # doesn't seem optional in reality; get 'Adding duplicate HugsLib.UpdateFeatureDef name: UnnamedDef'
  defName: '{ModMetaData.packageId}_{version}'
  assemblyVersion: '{version}'
  content: !steam2xml "{update_format}\n" # \n avoids text cut-off in-game
  titleOverride: ~
  linkUrl: ~
  # https://github.com/UnlimitedHugs/RimworldHugsLib/blob/477aa179dbedf5d02ce8ede361a42c45af24b746/Source/News/UpdateFeatureDef.cs#L64
  #trimWhitespace: true # default


## SETTINGS
settings_path: '{out_dir}\1.2\Languages\English\Keyed\Settings.xml'
setting_prefix: '{ModMetaData.packageId}'
SettingLanguageData:
  '{setting_prefix}_SettingTitle_{name}': !steam2xml '{title}'
  '{setting_prefix}_SettingDesc_{name}': !steam2xml '{desc?}'
```
</details>

### Example

<details open>
<summary><em>example_global.yaml</em></summary>

```yaml
#parent=defaults.yaml
---
#out_dir: '{local_dir}'

ModMetaData: !merge
  <: !parent ModMetaData
  author: Jane Doe

steam_format: |-
  {intro}
  
  {features}
about_format: |-
  {intro}
  
  {features}
  Thanks for installing!
```
</details>
<details open>
<summary><em>example_mod.yaml</em></summary>

```yaml
#parent=example_global.yaml
---
ModMetaData: !merge
  <: !parent ModMetaData
  name: Super Swords
  packageId: modder.superswords
  url: https://example.com/rimworld-super-swords
  supportedVersions:
    - 1.1
  modDependencies:
    - packageId: brrainz.harmony
      displayName: Harmony
      steamWorkshopUrl: steam://url/CommunityFilePage/2009463077
      downloadUrl: https://github.com/pardeike/HarmonyRimWorld/releases/latest

# our own for {steam_format} and {about_format} (example_global.yaml)
intro: Super slashin'! Git 'em good!

# presented in order for Steam & About
features:
  # for {steam_feature_format} and {about_feature_format} (defaults.yaml)
  - title: Super gladius.
    at: 1.0.0
    desc: &gladius |-
      A super gladius: 2x vanilla damage.
    steam: |-
      Slashy slashy!
  
  - title: Super longsword.
    at: 1.2.0 # (special) to include with updates inheriting feature {title}, {desc}, etc.
    desc: &longsword |-
      A super longsword: 1.5x vanilla damage.
    settings: # (special) to include with settings inheriting feature {title}, {desc}, etc.
      - name: useLongsword
        title: Enable longsword
  
  - title: Spawn map with random super sword.
    desc:
    at: 1.1.0
    swords: !join [ "\n", [ *gladius, *longsword ] ]
    settings:
      - name: spawnWith
        desc: |-
          Spawn map with one of these swords:
          {swords}

updates:
  - at: 1.1.0
    desc: |-
      • Fixed bug with super gladius.
  - at: 1.2.1
    desc: |-
      • Fixed bug with super longsword.

settings:
  - name: enabled
    title: Enable mod
```
</details>

<details>
<summary>Output: <em>Steam</em></summary>

```
Super slashin'! Git 'em good!

[u]Super gladius.[/u]
[i]Slashy slashy![/i]
A super gladius: 2x vanilla damage.

[u]Super longsword.[/u]
A super longsword: 1.5x vanilla damage.

[u]Spawn map with random super sword.[/u]
```
</details>

<details>
<summary>Output: <em>About.xml</em></summary>

```xml
<?xml version='1.0' encoding='UTF-8'?>
<ModMetaData>
    <name>Super Swords</name>
    <packageId>modder.superswords</packageId>
    <author>Jane Doe</author>
    <url>https://example.com/rimworld-super-swords</url>
    <supportedVersions>
        <li>1.1</li>
    </supportedVersions>
    <modDependencies>
        <li>
            <packageId>brrainz.harmony</packageId>
            <displayName>Harmony</displayName>
            <steamWorkshopUrl>steam://url/CommunityFilePage/2009463077</steamWorkshopUrl>
            <downloadUrl>https://github.com/pardeike/HarmonyRimWorld/releases/latest</downloadUrl>
        </li>
    </modDependencies>
    <incompatibleWith/>
    <loadBefore/>
    <loadAfter/>
    <description><![CDATA[Super slashin'! Git 'em good!

<color=white><b>Super gladius.</b></color>
A super gladius: 2x vanilla damage.

<color=white><b>Super longsword.</b></color>
A super longsword: 1.5x vanilla damage.

<color=white><b>Spawn map with random super sword.</b></color>
Thanks for installing!
]]></description>
</ModMetaData>
```
</details>

<details>
<summary>Output: <em>UpdateFeatures.xml</em></summary>

```xml
<?xml version='1.0' encoding='UTF-8'?>
<Defs>
    <HugsLib.UpdateFeatureDef Abstract="True" Name="modder.superswords_UpdateFeatureBase">
        <modNameReadable>Super Swords</modNameReadable>
        <modIdentifier>modder.superswords</modIdentifier>
        <linkUrl>https://example.com/rimworld-super-swords</linkUrl>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords_UpdateFeatureBase">
        <defName>modder.superswords_1.0.0</defName>
        <assemblyVersion>1.0.0</assemblyVersion>
        <content><![CDATA[<color=white><b>Super gladius.</b></color>
A super gladius: 2x vanilla damage.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords_UpdateFeatureBase">
        <defName>modder.superswords_1.1.0</defName>
        <assemblyVersion>1.1.0</assemblyVersion>
        <content><![CDATA[<color=white><b>Spawn map with random super sword.</b></color>

• Fixed bug with super gladius.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords_UpdateFeatureBase">
        <defName>modder.superswords_1.2.0</defName>
        <assemblyVersion>1.2.0</assemblyVersion>
        <content><![CDATA[<color=white><b>Super longsword.</b></color>
A super longsword: 1.5x vanilla damage.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords_UpdateFeatureBase">
        <defName>modder.superswords_1.2.1</defName>
        <assemblyVersion>1.2.1</assemblyVersion>
        <content><![CDATA[• Fixed bug with super longsword.
]]></content>
    </HugsLib.UpdateFeatureDef>
</Defs>
```
</details>

<details>
<summary>Output: <em>Settings.xml</em></summary>

```xml
<?xml version='1.0' encoding='UTF-8'?>
<LanguageData>
    <modder.superswords_SettingTitle_useLongsword><![CDATA[Enable longsword]]></modder.superswords_SettingTitle_useLongsword>
    <modder.superswords_SettingDesc_useLongsword><![CDATA[A super longsword: 1.5x vanilla damage.]]></modder.superswords_SettingDesc_useLongsword>
    <modder.superswords_SettingTitle_spawnWith><![CDATA[Spawn map with random super sword]]></modder.superswords_SettingTitle_spawnWith>
    <modder.superswords_SettingDesc_spawnWith><![CDATA[Spawn map with one of these swords:
A super gladius: 2x vanilla damage.
A super longsword: 1.5x vanilla damage.]]></modder.superswords_SettingDesc_spawnWith>
    <modder.superswords_SettingTitle_enabled><![CDATA[Enable mod]]></modder.superswords_SettingTitle_enabled>
    <modder.superswords_SettingDesc_enabled><![CDATA[]]></modder.superswords_SettingDesc_enabled>
</LanguageData>
```
</details>

### Advanced Example
<details>
<summary><em>example_beta.yaml</em></summary>

```yaml
#parent=example_mod.yaml
---
# so we can reference these within format strings
stable:
  ModMetaData: !parent ModMetaData
  intro: !parent intro
beta:
  modDependencies: &beta_modDependencies
    - packageId: UnlimitedHugs.HugsLib
      displayName: HugsLib
      steamWorkshopUrl: steam://url/CommunityFilePage/818773962
      downloadUrl: https://github.com/UnlimitedHugs/RimworldHugsLib/releases/latest

ModMetaData: !merge
  <: !parent ModMetaData
  name: '{stable.ModMetaData.name} Beta'
  packageId: '{stable.ModMetaData.packageId}.beta'
  supportedVersions: !insert &supportedVersions
    - !parent ModMetaData.supportedVersions
    - 1.2
  # by using !concat instead of !insert we can reference beta.modDependencies elsewhere
  modDependencies: !concat
    - !parent ModMetaData.modDependencies
    - *beta_modDependencies


features: !insert &features
  # positions will determine the placement of these elements in the final result
  #  tilde ~ will leave in-place if found, otherwise append to end (same as omission)
  - [ !parent features, '{title}', [ ~, 2 ] ]
  - !merge &longsword
    <: !parent &parent_longsword features.title=Super longsword&period;
    title: Super colorful longsword.
    settings: !insert
      - !get [ *parent_longsword, settings ]
      - name: randomColor
        title: Randomize longsword color.
        desc: |-
          Red, green, or blue.
  
  - &spear
    title: Super spear.
    at: 1.3.0
    desc: |-
      - A super spear: 2x vanilla damage.
  
  - title: Less important addition.
    at: 1.3.0
    desc: Minor awesome.


published_file_id: 1234567890
preview_from_path: 'beta.png'
setting_prefix: '{stable.ModMetaData.packageId}'

debug:
  parent_longsword: *parent_longsword
  longsword: *longsword
  
  parent_gladius: !parent features.title=Super gladius&period;
  gladius: !get [ *features, title=Super gladius&period; ]
  
  longsword_colors: !get [ *longsword, settings.name=randomColor.desc ]
  feature_setting_names: !join [ ", ", !each [ *features, settings, False ], '{name}' ]
  parent_update_descriptions: !join [ "\n", !parent updates, '{desc}' ]
  supported_version_floats: !join [ ", ", *supportedVersions, '{l:.3f}' ]

intro: |
  Thanks for trying the beta!
  
  {stable.intro}
  
  
  Debugging:
  parent gladius version: {debug.parent_gladius.at}
  gladius version: {debug.gladius.at}
  
  parent longsword title: {debug.parent_longsword.title}
  longsword title: {debug.longsword.title}
  
  feature setting names: {debug.feature_setting_names}
  standalone settings: {settings!e}
  
  parent update descriptions:
  {debug.parent_update_descriptions}
  
  longsword colors: {debug.longsword_colors}
  supported versions as floats: {debug.supported_version_floats}
  published file id as hexadecimal: {published_file_id:x}
  first beta dependency id: {beta.modDependencies[0].packageId}
```
</details>

<details>
<summary>Output: <em>Steam</em></summary>

```
Thanks for trying the beta!

Super slashin'! Git 'em good!


Debugging:
parent gladius version: 1.0.0
gladius version: 1.0.0

parent longsword title: Super longsword.
longsword title: Super colorful longsword.

feature setting names: useLongsword, spawnWith, randomColor
standalone settings: [{'name': 'enabled', 'title': 'Enable mod'}]

parent update descriptions:
• Fixed bug with super gladius.
• Fixed bug with super longsword.

longsword colors: Red, green, or blue.
supported versions as floats: 1.100, 1.200
published file id as hexadecimal: 499602d2
first beta dependency id: UnlimitedHugs.HugsLib


[u]Super gladius.[/u]
[i]Slashy slashy![/i]
A super gladius: 2x vanilla damage.

[u]Super longsword.[/u]
A super longsword: 1.5x vanilla damage.

[u]Super spear.[/u]
- A super spear: 2x vanilla damage.

[u]Spawn map with random super sword.[/u]

[u]Super colorful longsword.[/u]
A super longsword: 1.5x vanilla damage.

[u]Less important addition.[/u]
Minor awesome.
```
</details>

<details>
<summary>Output: <em>About.xml</em></summary>

```xml
<?xml version='1.0' encoding='UTF-8'?>
<ModMetaData>
    <name>Super Swords Beta</name>
    <packageId>modder.superswords.beta</packageId>
    <author>Jane Doe</author>
    <url>https://example.com/rimworld-super-swords</url>
    <supportedVersions>
        <li>1.1</li>
        <li>1.2</li>
    </supportedVersions>
    <modDependencies>
        <li>
            <packageId>brrainz.harmony</packageId>
            <displayName>Harmony</displayName>
            <steamWorkshopUrl>steam://url/CommunityFilePage/2009463077</steamWorkshopUrl>
            <downloadUrl>https://github.com/pardeike/HarmonyRimWorld/releases/latest</downloadUrl>
        </li>
        <li>
            <packageId>UnlimitedHugs.HugsLib</packageId>
            <displayName>HugsLib</displayName>
            <steamWorkshopUrl>steam://url/CommunityFilePage/818773962</steamWorkshopUrl>
            <downloadUrl>https://github.com/UnlimitedHugs/RimworldHugsLib/releases/latest</downloadUrl>
        </li>
    </modDependencies>
    <incompatibleWith/>
    <loadBefore/>
    <loadAfter/>
    <description><![CDATA[Thanks for trying the beta!

Super slashin'! Git 'em good!


Debugging:
parent gladius version: 1.0.0
gladius version: 1.0.0

parent longsword title: Super longsword.
longsword title: Super colorful longsword.

feature setting names: useLongsword, spawnWith, randomColor
standalone settings: [{'name': 'enabled', 'title': 'Enable mod'}]

parent update descriptions:
• Fixed bug with super gladius.
• Fixed bug with super longsword.

longsword colors: Red, green, or blue.
supported versions as floats: 1.100, 1.200
published file id as hexadecimal: 499602d2
first beta dependency id: UnlimitedHugs.HugsLib


<color=white><b>Super gladius.</b></color>
A super gladius: 2x vanilla damage.

<color=white><b>Super longsword.</b></color>
A super longsword: 1.5x vanilla damage.

<color=white><b>Super spear.</b></color>
- A super spear: 2x vanilla damage.

<color=white><b>Spawn map with random super sword.</b></color>

<color=white><b>Super colorful longsword.</b></color>
A super longsword: 1.5x vanilla damage.

<color=white><b>Less important addition.</b></color>
Minor awesome.
Thanks for installing!
]]></description>
</ModMetaData>
```
</details>

<details>
<summary>Output: <em>UpdateFeatures.xml</em></summary>

```xml
<?xml version='1.0' encoding='UTF-8'?>
<Defs>
    <HugsLib.UpdateFeatureDef Abstract="True" Name="modder.superswords.beta_UpdateFeatureBase">
        <modNameReadable>Super Swords Beta</modNameReadable>
        <modIdentifier>modder.superswords.beta</modIdentifier>
        <linkUrl>https://example.com/rimworld-super-swords</linkUrl>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords.beta_UpdateFeatureBase">
        <defName>modder.superswords.beta_1.0.0</defName>
        <assemblyVersion>1.0.0</assemblyVersion>
        <content><![CDATA[<color=white><b>Super gladius.</b></color>
A super gladius: 2x vanilla damage.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords.beta_UpdateFeatureBase">
        <defName>modder.superswords.beta_1.1.0</defName>
        <assemblyVersion>1.1.0</assemblyVersion>
        <content><![CDATA[<color=white><b>Spawn map with random super sword.</b></color>

• Fixed bug with super gladius.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords.beta_UpdateFeatureBase">
        <defName>modder.superswords.beta_1.2.0</defName>
        <assemblyVersion>1.2.0</assemblyVersion>
        <content><![CDATA[<color=white><b>Super longsword.</b></color>
A super longsword: 1.5x vanilla damage.

<color=white><b>Super colorful longsword.</b></color>
A super longsword: 1.5x vanilla damage.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords.beta_UpdateFeatureBase">
        <defName>modder.superswords.beta_1.2.1</defName>
        <assemblyVersion>1.2.1</assemblyVersion>
        <content><![CDATA[• Fixed bug with super longsword.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords.beta_UpdateFeatureBase">
        <defName>modder.superswords.beta_1.3.0</defName>
        <assemblyVersion>1.3.0</assemblyVersion>
        <content><![CDATA[<color=white><b>Super spear.</b></color>
- A super spear: 2x vanilla damage.

<color=white><b>Less important addition.</b></color>
Minor awesome.
]]></content>
    </HugsLib.UpdateFeatureDef>
</Defs>
```
</details>

<details>
<summary>Output: <em>Settings.xml</em></summary>

```xml
<?xml version='1.0' encoding='UTF-8'?>
<LanguageData>
    <modder.superswords_SettingTitle_useLongsword><![CDATA[Enable longsword]]></modder.superswords_SettingTitle_useLongsword>
    <modder.superswords_SettingDesc_useLongsword><![CDATA[A super longsword: 1.5x vanilla damage.]]></modder.superswords_SettingDesc_useLongsword>
    <modder.superswords_SettingTitle_spawnWith><![CDATA[Spawn map with random super sword]]></modder.superswords_SettingTitle_spawnWith>
    <modder.superswords_SettingDesc_spawnWith><![CDATA[Spawn map with one of these swords:
A super gladius: 2x vanilla damage.
A super longsword: 1.5x vanilla damage.]]></modder.superswords_SettingDesc_spawnWith>
    <modder.superswords_SettingTitle_randomColor><![CDATA[Randomize longsword color]]></modder.superswords_SettingTitle_randomColor>
    <modder.superswords_SettingDesc_randomColor><![CDATA[Red, green, or blue.]]></modder.superswords_SettingDesc_randomColor>
    <modder.superswords_SettingTitle_enabled><![CDATA[Enable mod]]></modder.superswords_SettingTitle_enabled>
    <modder.superswords_SettingDesc_enabled><![CDATA[]]></modder.superswords_SettingDesc_enabled>
</LanguageData>
```
</details>