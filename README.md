# RimWorld Mod Description Tool
Generate *About*, *Settings*, *Updates*, and *Steam* from a central file.

Uses [codeoptimist.yaml](https://pypi.org/project/codeoptimist.yaml/) for nested fields, parent files, and advanced formatting.  
See `defaults.yaml` below for YAML basics.

## Usage
`cd C:\path\to\yaml\files\`  
`C:\path\to\tool\generate.exe ...`
```
usage: generate.exe [-h] [--auto-steam] path

positional arguments:
  path          path to mod yaml file

optional arguments:
  -h, --help    show this help message and exit
  --auto-steam  opens browser and updates mod description on Steam
```

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

updates: [ ]
settings: [ ]

update_format: "{desc+\n}\
  \n"

# translate steam markup to xml
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
    - 1.3
  modDependencies: [ ]
  incompatibleWith: [ ]
  loadBefore: [ ]
  loadAfter: [ ]
  description: !steam2xml "{description}\n" # \n avoids text cut-off in-game


## UPDATES
updates_path: '{out_dir}\1.3\News\UpdateFeatures.xml'
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
  content: !steam2xml "{content}\n" # \n avoids text cut-off in-game
  titleOverride: ~
  linkUrl: ~
  # https://github.com/UnlimitedHugs/RimworldHugsLib/blob/477aa179dbedf5d02ce8ede361a42c45af24b746/Source/News/UpdateFeatureDef.cs#L64
  #trimWhitespace: true # default


## KEYS
keys_path: '{out_dir}\1.3\Languages\English\Keyed\Keys.xml'
key_prefix: '{ModMetaData.packageId}'
KeyLanguageData:
  '{key_prefix}_{name}': !steam2xml '{value}'


## SETTINGS
settings_path: '{keys_path}'
setting_prefix: '{key_prefix}'
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

description: |-
  {intro}

  {features}{is_about?=

  Thanks for installing&excl;}
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
  modDependencies:
    - packageId: brrainz.harmony
      displayName: Harmony
      steamWorkshopUrl: steam://url/CommunityFilePage/2009463077
      downloadUrl: https://github.com/pardeike/HarmonyRimWorld/releases/latest


intro: Super slashin'! Git 'em good!

# mappings are easy to override in a child file
longsword:
  title: &longsword_title '[u]Super longsword.[/u]'
  desc: &longsword_desc 'A super longsword: 1.5x vanilla damage.'
_: &v1_2_0 !join [ "\n", [ *longsword_title, *longsword_desc ] ]

features: !join
  - "\n"
  - - &v1_0_0 !join
      - "\n"
      - - |-
          [u]Super gladius.[/u]
        - &gladius_desc |-
          A super gladius: 2x vanilla damage.
    - |-
      {is_steam?=Slashy slashy&excl;
      }
      {longsword.title}
      {longsword.desc}
    -
    - &v1_1_0 |-
      [u]Spawn map with random super sword.[/u]
      It's a neat feature!


updates:
  - at: 1.0.0
    desc: *v1_0_0

  - at: 1.1.0
    desc: !join
      - "\n"
      - - *v1_1_0
        - |-

          • Fixed bug with super gladius.

  - at: 1.2.0
    desc: *v1_2_0

  - at: 1.2.1
    desc: '• Fixed bug with super longsword.'


settings:
  - name: enabled
    title: Enable mod

  - name: useLongsword
    title: Enable longsword
    desc: '{longsword.desc}'

  - name: spawnWith
    title: *v1_1_0
    swords: !join [ "\n", [ *gladius_desc, '{longsword.desc}' ] ]
    desc: |-
      Spawn map with one of these swords:
      {swords}
```
</details>

<details>
<summary>Output: <em>Steam</em></summary>

```
Super slashin'! Git 'em good!

[u]Super gladius.[/u]
A super gladius: 2x vanilla damage.
Slashy slashy!

[u]Super longsword.[/u]
A super longsword: 1.5x vanilla damage.

[u]Spawn map with random super sword.[/u]
It's a neat feature!
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
        <li>1.3</li>
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

<color=grey>Super gladius.</color>
A super gladius: 2x vanilla damage.

<color=grey>Super longsword.</color>
A super longsword: 1.5x vanilla damage.

<color=grey>Spawn map with random super sword.</color>
It's a neat feature!

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
        <content><![CDATA[<color=grey>Super gladius.</color>
A super gladius: 2x vanilla damage.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords_UpdateFeatureBase">
        <defName>modder.superswords_1.1.0</defName>
        <assemblyVersion>1.1.0</assemblyVersion>
        <content><![CDATA[<color=grey>Spawn map with random super sword.</color>
It's a neat feature!

• Fixed bug with super gladius.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords_UpdateFeatureBase">
        <defName>modder.superswords_1.2.0</defName>
        <assemblyVersion>1.2.0</assemblyVersion>
        <content><![CDATA[<color=grey>Super longsword.</color>
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
<summary>Output: <em>Keys.xml</em></summary>

```xml
<?xml version='1.0' encoding='UTF-8'?>
<LanguageData>
    <modder.superswords_SettingTitle_enabled><![CDATA[Enable mod]]></modder.superswords_SettingTitle_enabled>
    <modder.superswords_SettingDesc_enabled><![CDATA[]]></modder.superswords_SettingDesc_enabled>
    <modder.superswords_SettingTitle_useLongsword><![CDATA[Enable longsword]]></modder.superswords_SettingTitle_useLongsword>
    <modder.superswords_SettingDesc_useLongsword><![CDATA[A super longsword: 1.5x vanilla damage.]]></modder.superswords_SettingDesc_useLongsword>
    <modder.superswords_SettingTitle_spawnWith><![CDATA[<color=grey>Spawn map with random super sword.</color>
It's a neat feature!]]></modder.superswords_SettingTitle_spawnWith>
    <modder.superswords_SettingDesc_spawnWith><![CDATA[Spawn map with one of these swords:
A super gladius: 2x vanilla damage.
A super longsword: 1.5x vanilla damage.]]></modder.superswords_SettingDesc_spawnWith>
</LanguageData>
```
</details>

### Advanced Example
<details>
<summary><em>example_beta.yaml</em></summary>

```yaml
#parent=example_mod.yaml
---
stable:
  ModMetaData: !parent ModMetaData
  intro: !parent intro
  features: !parent features

ModMetaData: !merge
  <: !parent ModMetaData
  name: '{stable.ModMetaData.name} Beta'
  packageId: '{stable.ModMetaData.packageId}.beta'
  modDependencies: !insert
    - [ !parent ModMetaData.modDependencies ]
    - packageId: UnlimitedHugs.HugsLib
      displayName: HugsLib
      steamWorkshopUrl: steam://url/CommunityFilePage/818773962
      downloadUrl: https://github.com/UnlimitedHugs/RimworldHugsLib/releases/latest

published_file_id: 1234567890
setting_prefix: '{stable.ModMetaData.packageId}'


intro: |-
  Thanks for trying the beta!

  {stable.intro}

longsword:
  title: 'Super colorful longsword.'
  desc: !parent longsword.desc

features: |-
  {stable.features}

  [u]Super spear.[/u]
  A super spear: 2x vanilla damage.


settings: !insert
  - [ !parent settings ]
  - name: randomColor
    title: Randomize longsword color.
    desc: |-
      Red, green, or blue.
```
</details>

<details>
<summary>Output: <em>Steam</em></summary>

```
Thanks for trying the beta!

Super slashin'! Git 'em good!

[u]Super gladius.[/u]
A super gladius: 2x vanilla damage.
Slashy slashy!

Super colorful longsword.
A super longsword: 1.5x vanilla damage.

[u]Spawn map with random super sword.[/u]
It's a neat feature!

[u]Super spear.[/u]
A super spear: 2x vanilla damage.
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
        <li>1.3</li>
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

<color=grey>Super gladius.</color>
A super gladius: 2x vanilla damage.

Super colorful longsword.
A super longsword: 1.5x vanilla damage.

<color=grey>Spawn map with random super sword.</color>
It's a neat feature!

<color=grey>Super spear.</color>
A super spear: 2x vanilla damage.

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
        <content><![CDATA[<color=grey>Super gladius.</color>
A super gladius: 2x vanilla damage.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords.beta_UpdateFeatureBase">
        <defName>modder.superswords.beta_1.1.0</defName>
        <assemblyVersion>1.1.0</assemblyVersion>
        <content><![CDATA[<color=grey>Spawn map with random super sword.</color>
It's a neat feature!

• Fixed bug with super gladius.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords.beta_UpdateFeatureBase">
        <defName>modder.superswords.beta_1.2.0</defName>
        <assemblyVersion>1.2.0</assemblyVersion>
        <content><![CDATA[<color=grey>Super longsword.</color>
A super longsword: 1.5x vanilla damage.
]]></content>
    </HugsLib.UpdateFeatureDef>
    <HugsLib.UpdateFeatureDef ParentName="modder.superswords.beta_UpdateFeatureBase">
        <defName>modder.superswords.beta_1.2.1</defName>
        <assemblyVersion>1.2.1</assemblyVersion>
        <content><![CDATA[• Fixed bug with super longsword.
]]></content>
    </HugsLib.UpdateFeatureDef>
</Defs>
```
</details>

<details>
<summary>Output: <em>Keys.xml</em></summary>

```xml
<?xml version='1.0' encoding='UTF-8'?>
<LanguageData>
    <modder.superswords_SettingTitle_enabled><![CDATA[Enable mod]]></modder.superswords_SettingTitle_enabled>
    <modder.superswords_SettingDesc_enabled><![CDATA[]]></modder.superswords_SettingDesc_enabled>
    <modder.superswords_SettingTitle_useLongsword><![CDATA[Enable longsword]]></modder.superswords_SettingTitle_useLongsword>
    <modder.superswords_SettingDesc_useLongsword><![CDATA[A super longsword: 1.5x vanilla damage.]]></modder.superswords_SettingDesc_useLongsword>
    <modder.superswords_SettingTitle_spawnWith><![CDATA[<color=grey>Spawn map with random super sword.</color>
It's a neat feature!]]></modder.superswords_SettingTitle_spawnWith>
    <modder.superswords_SettingDesc_spawnWith><![CDATA[Spawn map with one of these swords:
A super gladius: 2x vanilla damage.
A super longsword: 1.5x vanilla damage.]]></modder.superswords_SettingDesc_spawnWith>
    <modder.superswords_SettingTitle_randomColor><![CDATA[Randomize longsword color.]]></modder.superswords_SettingTitle_randomColor>
    <modder.superswords_SettingDesc_randomColor><![CDATA[Red, green, or blue.]]></modder.superswords_SettingDesc_randomColor>
</LanguageData>
```
</details>