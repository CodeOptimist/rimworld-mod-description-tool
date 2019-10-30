# Annoyance

RimWorld mods need the same description in **four** locations with different formatting:

* **Steam**  
Your audience.
* **About**  
In-game mod list.
* **Settings**  
Tooltip explanations.
* **Updates**  
Notifications via HugsLib.

# Solution
Master file with a readable, ordered list of presentable features for Steam and About.  
Annotated with version numbers for notifications.  
Annotated with setting names for tooltips.  

Features can have multiple settings, settings can be on multiple features: text will be combined.

# Usage
Call the Python script with relative or absolute paths to your mods' yaml files.

## Example
* `main.py "C:\Mod\public.yaml"`  
* `main.py "C:\Mod"` (same as above)  
* `main.py "C:\Mods\global.yaml" "C:\Mods\Mod1\public.yaml" "C:\Mods\Mod2\public.yaml"`  
* `main.py "C:\Mods\global.yaml" "C:\Mods\Mod1" "C:\Mods\Mod2"` (same as above)  
* ```cmd
  cd "C:\Mods"
  C:\absolute\path\to\main.py "global.yaml" "Mod1" "Mod2"
  ```
  (same as above)

## Output
**Overwrites** (or creates) the following paths by default:  
* `About\About.xml`  
* `Defs\UpdateFeatures.xml` (or `Defs\UpdateFeatureDefs\UpdateFeatures.xml` if found)  
* `Languages\English\Keyed\Settings.xml`  

Can be set via `about_path`, `update_path`, and `settings_path` in yaml.

# File Examples
## Global
```yaml
---
global_author: ModGuy
global_steam_format: |-
  {my_intro_variable}
  {features}
  [url={url}]GitHub[/url]
  Thanks, hope you enjoy [b]{name}[/b]!
```

## Mod
```yaml
---
name: Mod Guy's Super Weapons!
identifier: ModGuySuperWeapons
supported_versions:
  - 1.0
url: https://github.com/ModGuy/rimworld-super-weapons

my_intro_variable: |+
  Super slashin' & gunnin'! Git 'em good!

features:
- title: Super gladius.
  at: 1.0.0
  desc: |-
    A super gladius: 2x vanilla damage.
  steam: |-
    Slashy slashy!
  settings:
    - name: enabled
      title: Enable mod
      desc: Enable all super weapons.
      
    - name: useSwords
      title: Enable super swords
    
- title: Super longsword.
  at: 1.2.0
  desc: |-
    A super longsword: 2x vanilla damage.
  settings:
    - name: useSwords
      title: 
      
- title: Super revolver.
  at: 1.1.0
  desc: |-
    A super revolver with settable damage multiplier.
  settings:
    - name: revolverDmgMult
      title: Revolver damage multiplier
      desc: Deals damage equal to this value * base vanilla damage.
      
- title: Spawn map with random super weapon.
  at: 1.3.0
  settings:
    - name: spawnWithMap

- at: 1.2.1
  desc: |-
    Fixed bug with super longsword.
```

`useSwords` inherits and combines into this:
```yaml
name: useSwords
title: Enable super swords
desc: |-
  A super gladius: 2x vanilla damage.
  A super longsword: 2x vanilla damage.
```

If you specify both `title` and `desc` it won't matter where you've put the setting.

# File Specification
## Mod
```yaml
---
# required for About <name> and UpdateFeatures <modNameReadable>
name: My Readable Mod Name
# required for UpdateFeatures <modIdentifier>, and used in default setting key format
identifier: MyModName

# required for mod
features:
  # optional but required to display in About and Steam, omit for pure updates; used in default feature formats
- title: Friendly feature title.
  # optional version number for grouping features into an update
  at: 1.0.0
  # user-defined, used in default about and update feature formats
  desc: Description of feature.
  # user-defined, used in default steam feature format
  steam: Some extra flavor text for Steam.
  
  # optional
  settings:
    # required unique portion of default setting key format and used to group title and desc
  - name: SomeSetting
    # defaults to feature title, either required; combined with others of this setting name for title
    title: Activate the thing
    # defaults to feature desc; combined with others of this setting name for tooltip
    desc: Activates it real good.
```

## Global or Mod
These can be set globally by prefixing with `global_`.  
The local value is always preferred.  

```yaml
---
# required author name for About <author>
author: ModGuy
# required version list for About <supportedVersions>
supported_versions: 
 - 1.0
# optional url for About <url> and UpdateFeatures <linkUrl>
url: https://example.com
# True or False, defaults to True; feature order in update file, no effect in-game
descending_updates: True

about_path:
updates_path:
settings_path:
```

### Format defaults
You may want to override some of these.  
Prefix with `global_` to set globally.  

```yaml
steam_format: {features}
about_format: {features}
update_format: {features}
steam_feature_format: |-
  [b]{feature_title}[/b]
  [i]{feature_steam}[/i]
  {feature_desc}
about_feature_format: &xml_feature_format |-
  <color=white><b>{feature_title}</b></color>
  {feature_desc}
update_feature_format: *xml_feature_format

# quoted because of beginning curly brace
setting_title_key_format: "{identifier}_{setting_name}_SettingTitle"
setting_desc_key_format: "{identifier}_{setting_name}_SettingDesc"
# version .'s replaced with _'s
update_defname_format: "{identifier}_{update_version}"
```

### Steam markup to xml
```yaml
# because RimWorld lacks xml hyperlinks; from [url={url}]{text}[/url]
xml_url_format: <color=grey><b>{text}</b></color>
# because RimWorld lacks xml underlining; from [u]{text}[/u]
xml_u_format: <color=grey>{text}</color>
```

All [Steam Workshop markup](https://steamcommunity.com/comment/Announcement/formattinghelp) will be converted before writing to xml, so you're welcome to use it anywhere, and can for example anchor and alias `steam_format` for `about_format`:
```yaml
global_steam_format: &my_anchor |-
  [i]Intro[/i]
  [h1]{name}[/h1]
  {features}
  Outro
global_about_format: *my_anchor
```
