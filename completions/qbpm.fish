function __fish_qbpm
  set -l saved_args $argv
  set -l global_args
  set -l cmd (commandline -opc)
  set -e cmd[1]
  argparse -si P/profile-dir= -- $cmd 2>/dev/null
  set -q _flag_P
  and set global_args "-P $_flag_P"
  echo qbpm $global_args $saved_args > /tmp/cmplog
  eval qbpm $global_args $saved_args
end

set -l commands new from-session desktop launch run list edit

complete -c qbpm -f
complete -c qbpm -n "not __fish_seen_subcommand_from $commands" -a "launch new from-session edit list"
complete -c qbpm -n "__fish_seen_subcommand_from launch edit" -a "(__fish_qbpm list)"
set -l data_home (set -q XDG_DATA_HOME; and echo $XDG_DATA_HOME; or echo ~/.local/share)
complete -c qbpm -n "__fish_seen_subcommand_from from-session" -a "(ls $data_home/qutebrowser/sessions | xargs basename -a -s .yml)"
