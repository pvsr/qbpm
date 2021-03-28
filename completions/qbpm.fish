set -l commands new from-session desktop launch run list edit

complete -c qbpm -f
complete -c qbpm -n "not __fish_seen_subcommand_from $commands" -a "launch new from-session edit list"
complete -c qbpm -n "__fish_seen_subcommand_from launch edit" -a "(qbpm list)"
set -l data_home (set -q XDG_DATA_HOME; and echo $XDG_DATA_HOME; or echo ~/.local/share)
complete -c qbpm -n "__fish_seen_subcommand_from from-session" -a "(ls $data_home/qutebrowser/sessions | xargs basename -a -s .yml)"
