function __fish_qbpm
    set -l saved_args $argv
    set -l global_args
    set -l cmd (commandline -opc)
    set -e cmd[1]
    argparse -si P/profile-dir= -- $cmd 2>/dev/null
    set -q _flag_P
    and set global_args "-P $_flag_P"
    eval qbpm $global_args $saved_args
end

set -l commands new from-session desktop launch list edit choose
set -l data_home (set -q XDG_DATA_HOME; and echo $XDG_DATA_HOME; or echo ~/.local/share)

complete -c qbpm -f
complete -c qbpm -s h -l help
complete -c qbpm -s l -l log-level -a "debug info error"
complete -c qbpm -s C -l config-dir -r
complete -c qbpm -s P -l profile-dir -r

complete -c qbpm -n "not __fish_seen_subcommand_from $commands" -a "$commands"

complete -c qbpm -n "__fish_seen_subcommand_from new from_session" -s l -l launch
complete -c qbpm -n "__fish_seen_subcommand_from new from_session" -l desktop-file
complete -c qbpm -n "__fish_seen_subcommand_from new from_session" -l no-desktop-file
complete -c qbpm -n "__fish_seen_subcommand_from new from_session" -l overwrite
complete -c qbpm -n "__fish_seen_subcommand_from new from_session launch choose" -s f -l foreground

complete -c qbpm -n "__fish_seen_subcommand_from launch" -s c -l create
complete -c qbpm -n "__fish_seen_subcommand_from choose" -s m -l menu -r
complete -c qbpm -n "__fish_seen_subcommand_from launch choose" -w qutebrowser

complete -c qbpm -n "__fish_seen_subcommand_from launch edit desktop" -a "(__fish_qbpm list)"
complete -c qbpm -n "__fish_seen_subcommand_from from-session" -a "(ls $data_home/qutebrowser/sessions | xargs basename -a -s .yml)"
