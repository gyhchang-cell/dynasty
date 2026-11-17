scoreboard players set @s oszu_fd_print 0
scoreboard players reset @s oszu_fd_print_off
scoreboard players enable @s oszu_fd_print_off
tellraw @a ["",{"text":"Disabled damage number chat printing for "},{"selector":"@s","color":"aqua"}]