# Copyright (C) 2020 BY - GitHub.com/code-rgb [TG - @deleteduser420]
# All rights reserved.


import os

from git import Repo

from userge import Config, Message, userge
from userge.utils import humanbytes


@userge.on_cmd(
    "cmdinfo",
    about={
        "header": "find plugin and other info for a given command",
        "description": "you can also provide optional text to search within the plugin",
        "usage": "{tr}cmdinfo [cmd] | [optional text]",
        "examples": "{tr}cmdinfo .ars\n" "  {tr}cmdinfo .ars | tracemoepy",
    },
)
async def see_info(message: Message):
    cmd_str = message.input_str
    if not cmd_str:
        return await message.err("Provide a Valid Command to Search", del_in=5)
    word = None
    if "|" in cmd_str:
        cmd_str, word = cmd_str.split("|", 1)
    cmd_str = cmd_str.strip()
    other_trigger = [".", Config.SUDO_TRIGGER]
    cmd_list = list(userge.manager.commands)
    found = True
    if not (cmd_str.startswith(Config.CMD_TRIGGER) and (cmd_str in cmd_list)):
        found = False
        for character in other_trigger:
            if cmd_str.startswith(character) and (
                cmd_str.replace(character, Config.CMD_TRIGGER) in cmd_list
            ):
                cmd_str = cmd_str.replace(character, Config.CMD_TRIGGER)
                found = True
                break
        if cmd_str.isalpha() and (Config.CMD_TRIGGER + cmd_str) in cmd_list:
            found = True
            cmd_str = Config.CMD_TRIGGER + cmd_str
    if not found:
        return await message.err("provide a valid command name", del_in=5)
    repo = Repo()
    branch = repo.active_branch.name
    if branch == "master":
        branch = "alpha"
    plugin_name = userge.manager.commands[cmd_str].plugin_name
    plugin_loc = ("/" + userge.manager.plugins[plugin_name].parent).replace(
        "/plugins", ""
    )
    if plugin_loc == "/unofficial":
        unofficial_repo = (
            "https://github.com/code-rgb/Userge-Plugins/blob/master/plugins/"
        )
        plugin_link = f"{unofficial_repo}/{plugin_name}.py"
    elif plugin_loc == "/temp":
        plugin_link = False
    else:
        plugin_link = "{}/blob/{}/userge/plugins{}/{}.py".format(
            Config.UPSTREAM_REPO, branch, plugin_loc, plugin_name
        )
    local_path = f"userge/plugins{plugin_loc}/{plugin_name}.py"
    f_size = humanbytes(os.stat(local_path).st_size)
    search_path = count_lines(local_path, word) if word else count_lines(local_path)
    result = f"""
<b>???>  CMD:</b>  <code>{cmd_str}</code>

???? <b>Path : </b><code>{local_path}</code><code>
  - Size on Disc: {f_size}
  - No. of lines: {search_path[0]}</code>
"""
    if plugin_link:
        result += f"\n???? <b>[View Code on Github]({plugin_link})</b>"
    if word:
        result += f"\n\n???? <b>Matches for:</b> {word}\n"
        s_result = ""
        if len(search_path[1]) == 0:
            s_result += "  ??? Not Found !"
        else:
            line_c = 0
            for line in search_path[1]:
                line_c += 1
                s_result += f"[#L{line}]({plugin_link}#L{line})  "
                if line_c > 5:
                    break
        result += "  <b>{}</b>".format(s_result)
    await message.edit(result, disable_web_page_preview=True)


def count_lines(cmd_path: str, word=None):
    arr = []
    num_lines = 0
    with open(cmd_path, "r") as f:
        for line in f:
            num_lines += 1
            if word and word in line:
                arr.append(num_lines)
    return num_lines, arr
