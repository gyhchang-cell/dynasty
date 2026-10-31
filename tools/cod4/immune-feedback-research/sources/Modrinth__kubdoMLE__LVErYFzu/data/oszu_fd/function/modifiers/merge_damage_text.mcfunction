$execute unless score temp oszu_fd_damage_delt matches 0 unless score @s oszu_fd_damage_delt matches 0 run data modify storage minecraft:oszu_storage oszu_fd.damage_text set value " $(damage_text_whole).$(damage_text_decimal) "


$execute if score temp oszu_fd_damage_delt matches 0 if score @s oszu_fd_damage_delt matches 0.. run data modify storage minecraft:oszu_storage oszu_fd.damage_text set value " $(damage_text_whole).$(damage_text_decimal) "

$execute if score temp oszu_fd_damage_delt matches 0.. if score @s oszu_fd_damage_delt matches 0 run data modify storage minecraft:oszu_storage oszu_fd.damage_text set value " $(damage_text_whole) "