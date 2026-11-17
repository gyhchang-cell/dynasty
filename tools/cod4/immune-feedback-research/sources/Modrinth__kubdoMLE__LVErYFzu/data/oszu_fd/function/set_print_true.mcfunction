scoreboard players set @s oszu_fd_print 1
scoreboard players reset @s oszu_fd_print_on
scoreboard players enable @s oszu_fd_print_on
tellraw @a ["",{"text":"Enabled damage number chat printing for "},{"selector":"@s","color":"aqua"}]