#!/usr/bin/env python3
"""Generate the dwl configuration from Diego's current dwm configuration."""
import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def uncomment(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def array(text, name):
    match = re.search(r"static\s+[^;\n]+\b" + name + r"\[.*?\]\s*=\s*\{(.*?)\n\};", text, re.S)
    if not match:
        raise ValueError(f"Cannot find array {name}")
    return match.group(1)


def translate(text):
    for old, new in (
        ("XF86XK_", "XKB_KEY_XF86"), ("XK_", "XKB_KEY_"),
        ("ControlMask", "WLR_MODIFIER_CTRL"), ("ShiftMask", "WLR_MODIFIER_SHIFT"),
        ("ClkWinTitle", "ClkTitle"), ("ClkStatusText", "ClkStatus"),
        ("ClkClientWin", "ClkClient"), ("Button1", "BTN_LEFT"),
        ("Button2", "BTN_MIDDLE"), ("Button3", "BTN_RIGHT"),
    ):
        text = text.replace(old, new)
    return text


def generate(source_path, keyboard_layout):
    source = uncomment(source_path.read_text())
    config = (ROOT / "config.def.h").read_text()

    def value(name):
        match = re.search(r"\b" + name + r"(?:\[\])?\s*=\s*([^;]+);", source)
        if not match:
            raise ValueError(f"Cannot find dwm setting {name}")
        return match.group(1).strip()

    def replace_array(name, body):
        nonlocal config
        pattern = r"(static\s+[^;\n]+\b" + name + r"\[.*?\]\s*=\s*\{).*?\n\};"
        config, count = re.subn(pattern, lambda match: match.group(1) + body + "\n};", config, count=1, flags=re.S)
        if count != 1:
            raise ValueError(f"Cannot replace dwl array {name}")

    for name in ("borderpx", "snap", "gappx", "showbar", "topbar"):
        config, count = re.subn(r"(\b" + name + r"\s*=\s*)[^;]+;", lambda match: match.group(1) + value(name) + ";", config, count=1)
        if count != 1:
            raise ValueError(f"Cannot replace dwl setting {name}")

    fonts = re.search(r'\bfonts\[\]\s*=\s*\{(.*?)\};', source).group(1)
    config = re.sub(r'(\bfonts\[\]\s*=\s*\{).*?\};', lambda match: match.group(1) + fonts + "};", config, count=1)
    tags = re.search(r'\btags\[\]\s*=\s*\{(.*?)\};', source).group(1)
    config = re.sub(r'(\btags\[\]\s*=\s*\{).*?\};', lambda match: match.group(1) + tags + "};", config, count=1)
    if not 1 <= len(re.findall(r'"[^"]*"', tags)) <= 31:
        raise ValueError("dwl requires between 1 and 31 tags")

    def color(name):
        return value(name).strip('"').removeprefix("#") + "ff"

    replace_array("colors", "\n\t[SchemeNorm] = { 0x%s, 0x%s, 0x%s },\n\t[SchemeSel] = { 0x%s, 0x%s, 0x%s },\n\t[SchemeUrg] = { 0, 0, 0x770000ff }," % (color("col_gray3"), color("col_gray1"), color("col_gray2"), color("col_gray4"), color("col_cyan"), color("col_cyan")))
    config = re.sub(r'(rootcolor\[\]\s*=\s*COLOR\()[^)]+', r'\g<1>0x' + color("col_gray1"), config, count=1)

    rules = array(source, "rules")
    def rule(match):
        app_id, instance, title, remainder = match.groups()
        if instance.strip() != "NULL":
            raise ValueError("An X11 instance rule needs manual translation")
        return '{ "' + app_id.lower() + '", ' + title + ', ' + remainder + ' }'
    rules = re.sub(r'\{\s*"([^"]+)",\s*([^,]+),\s*([^,]+),\s*(.*?)\s*\}', rule, rules)
    replace_array("rules", rules)
    replace_array("layouts", array(source, "layouts"))
    replace_array("monrules", f'\n\t{{ NULL, {value("mfact")}f, {value("nmaster")}, 1, &layouts[0], WL_OUTPUT_TRANSFORM_NORMAL, -1, -1 }},')
    config = re.sub(r'(static const struct xkb_rule_names xkb_rules = \{).*?\n\};', lambda match: match.group(1) + '\n\t.layout = "' + keyboard_layout + '",\n\t.options = NULL,\n};', config, count=1, flags=re.S)
    config = config.replace("#define MODKEY WLR_MODIFIER_ALT", "#define MODKEY WLR_MODIFIER_LOGO")

    commands = re.findall(r"static const char \*(\w+)\[\]\s*=\s*\{(.*?)\};", source, re.S)
    native = {
        "dmenucmd": ' "wmenu-run", "-f", "GeistMono Nerd Font 12", "-N", "222222", "-n", "bbbbbb", "-S", "005577", "-s", "eeeeee", NULL ',
        "scrotcmd": ' "/usr/share/dwl/scripts/dwl-screenshot", "full", NULL ',
        "scrotsel": ' "/usr/share/dwl/scripts/dwl-screenshot", "region", NULL ',
        "slfull": ' "/usr/share/dwl/scripts/dwl-status-mode", "full", NULL ',
        "slmini": ' "/usr/share/dwl/scripts/dwl-status-mode", "mini", NULL ',
        "monitortoggle": ' "/usr/share/dwl/scripts/dwl-monitor-toggle", NULL ',
    }
    rendered = []
    for name, body in commands:
        if name in ("fonts", "tags"):
            continue
        body = native.get(name, body)
        body = re.sub(r'^\s*"st"', ' "foot", "--config", "/usr/share/dwl/foot.ini"', body)
        if name == "t3codecmd":
            body = body.replace('"t3code-nightly",', '"t3code-nightly", "--ozone-platform=wayland",')
        rendered.append(f"static const char *{name}[] = {{{body}}};")
    config = re.sub(r"/\* commands \*/.*?(?=static const Key keys\[\])", lambda match: "/* commands */\n" + "\n".join(rendered) + "\n\n", config, count=1, flags=re.S)

    keys = translate(array(source, "keys"))
    keys = re.sub(r'((?:focusmon|tagmon),\s*\{\.i = )([+-]?1)(\s*\})', lambda match: match.group(1) + ("WLR_DIRECTION_LEFT" if match.group(2) == "-1" else "WLR_DIRECTION_RIGHT") + match.group(3), keys)
    keys = re.sub(r'(\.f\s*=\s*[+-]?\d+\.\d+)(?=\s*\})', r'\1f', keys)
    keys = re.sub(r'(TAGKEYS\([^\n]+\))\s*(?=\n)', r'\1,', keys)
    keys += '\n\t{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_e, togglefullscreen, {0} },\n\t{ WLR_MODIFIER_CTRL|WLR_MODIFIER_ALT, XKB_KEY_BackSpace, quit, {0} },\n#define CHVT(n) { WLR_MODIFIER_CTRL|WLR_MODIFIER_ALT, XKB_KEY_F##n, chvt, {.ui = (n)} }\n\tCHVT(1), CHVT(2), CHVT(3), CHVT(4), CHVT(5), CHVT(6),\n\tCHVT(7), CHVT(8), CHVT(9), CHVT(10), CHVT(11), CHVT(12),'
    replace_array("keys", keys)
    buttons = translate(array(source, "buttons"))
    buttons = re.sub(r'(BTN_LEFT,\s*)movemouse,\s*\{0\}', r'\1moveresize, {.ui = CurMove}', buttons)
    buttons = re.sub(r'(BTN_RIGHT,\s*)resizemouse,\s*\{0\}', r'\1moveresize, {.ui = CurResize}', buttons)
    replace_array("buttons", buttons)
    replace_array("axes", "\n\t{ 0, AxisUp, NULL, {0} },")
    rendered = "/* Generated by scripts/port-dwm.py. Native Wayland configuration. */\n" + config
    return "\n".join(re.sub(r"^ +(?=\t)", "", line).rstrip() for line in rendered.splitlines()) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=pathlib.Path, default=ROOT.parent / "dwm" / "config.h")
    parser.add_argument("--layout", default="latam")
    parser.add_argument("--output", type=pathlib.Path, default=ROOT / "config.h")
    args = parser.parse_args()
    args.output.write_text(generate(args.source, args.layout))
    print(f"Ported {args.source} to {args.output}")
