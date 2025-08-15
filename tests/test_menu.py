from qbpm.menus import Dmenu, custom_dmenu


def test_menu_prompt_formatting():
    dmenu = Dmenu(["my-menu", "--prompt", "{prompt}"])
    cmd = dmenu.command(["p1"], "qb ({qb_args})", "example.com")
    assert "--prompt" in cmd
    assert "qb (example.com)" in cmd


def test_known_custom_menu():
    assert custom_dmenu(["fuzzel"]).menu_command == ["fuzzel", "--dmenu"]
    assert custom_dmenu("fuzzel").menu_command == ["fuzzel", "--dmenu"]
    assert "--dmenu" in custom_dmenu("~/bin/fuzzel").menu_command


def test_custom_menu_list():
    menu = ["fuzzel", "--dmenu", "--prompt", "{prompt}>"]
    assert custom_dmenu(menu).menu_command == menu
