#print
	$execute if score @s oszu_fd_print matches 1.. at @s as @n[nbt={HurtTime:10s}] run tellraw @p ["",{"text":"$(damage_tense)"},{"text":"$(damage_prefix)$(damage_text)$(damage_suffix)","color":"#$(colour)"},{"text":"$(damage_type)damage to \""},{"text":"$(entity_prefix)","color":"aqua"},{"selector":"@s","color":"aqua"},{"text":"\""}]

#text display
	$execute at @n[nbt={HurtTime:10s}] positioned ~ ~1 ~ run summon text_display ~ ~ ~ {view_range:1f,billboard:"center",teleport_duration:10,alignment:"center",Tags:["oszu_fd_damage_text_display"],brightness:{sky:15,block:15},transformation:{left_rotation:[0f,0f,0f,1f],right_rotation:[0f,0f,0f,1f],translation:[0f,0f,0f],scale:[0f,0f,0f]},text:{"color":"#$(colour)","text":"$(damage_prefix)$(damage_text)$(damage_suffix)"},background:16711680}

#text aniamtion
	execute at @n[nbt={HurtTime:10s}] as @n[type=text_display,tag=oszu_fd_damage_text_display,tag=!oszu_fd_initiated] run data merge entity @s {start_interpolation:0,interpolation_duration:10,transformation:{scale:[1.5f,1.5f,1.5f]}}

	execute at @n[type=text_display,tag=oszu_fd_damage_text_display,tag=!oszu_fd_initiated] rotated as @s positioned ^ ^0.5 ^-2 run tp @n[type=text_display,tag=oszu_fd_damage_text_display] ~ ~ ~

#marking text as initiated so that it is not target again
	execute as @n[type=text_display,tag=oszu_fd_damage_text_display,tag=!oszu_fd_initiated] run tag @s add oszu_fd_initiated