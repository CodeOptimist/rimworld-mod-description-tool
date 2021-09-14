#SingleInstance force
#Warn
return


Send(keys) {
    if (WinActive())
        Send, % keys
}

WaitFor(winTitle, timeout=3) {
    WinWait, % winTitle,, % timeout
    if (ErrorLevel)
        throw "Timed out waiting for: " winTitle
}

WaitForClose(winTitle, timeout=3) {
    WinWaitClose, % winTitle,, % timeout
    if (ErrorLevel)
        throw "Timed out waiting for close: " winTitle
}

ClipboardVerify(keys, text) {
    Clipboard := ""
    Send(keys)
    ClipWait, 1
    if (ErrorLevel)
        throw "Nothing on clipboard."
    if (StrReplace(Clipboard, "`r`n", "`n") != text)
        throw "Clipboard didn't match text."
}

UpdateSteam(text) {
    try {
        Clipboard := text

        WaitFor("Steam Community :: Steam Workshop :: Edit Title & Description")
        ClipboardVerify("!d^c", "https://steamcommunity.com/sharedfiles/itemedittext/?id={{published_file_id}}")

        ; execute our JS to verify page and focus textarea
        ; missing 'j' is not a typo
        Clipboard = avascript:(function(){if(document.getElementById('id').value!='{{published_file_id}}')return;var f=document.getElementsByClassName('descField');if(!f.length)return;f[0].focus();document.title='{{published_file_id}} - focused';})();
        Send("!dj^v{enter}") ; have to type the j ourselves (paste protection)
        WaitFor("{{published_file_id}} - focused")

        Clipboard := text
        Send("^a^v")
        ClipboardVerify("^a^c", text)

        ; missing 'j' is not a typo
        Clipboard = avascript:ValidateForm()
        Send("!dj^v{enter}") ; have to type the j ourselves (paste protection)
        WaitForClose("{{published_file_id}} - focused")
        WaitFor("Steam Community :: Steam Workshop :: Edit Title & Description")

        ; success! let's refresh the Steam page
        Clipboard = https://steamcommunity.com/sharedfiles/filedetails/?id={{published_file_id}}
        Send("!d^v{enter}")
        ; already successful, so don't need the exception from WaitForClose()
        WinWaitClose, % "Steam Community :: Steam Workshop :: Edit Title & Description",, 1
        if not ErrorLevel
            Send("{f5}") ; manual refresh because of browser extensions that prevent tab duplicates
    } catch e {
        return e
    }
    return 0
}
